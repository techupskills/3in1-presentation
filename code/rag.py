# Import necessary libraries
import os  # ADDED: For file path handling
import json
import requests
import math
from openai import OpenAI
# ADDED: RAG-specific imports
import chromadb
import pdfplumber
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

# ANSI color codes for terminal output
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Connect to local Ollama server (running Llama3.2 model)
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # dummy key (Ollama ignores it)
)

# Set hardcoded current location (Raleigh, NC)
CURRENT_LAT = 35.7796
CURRENT_LON = -78.6382

# MODIFIED: Enhanced system prompt for RAG workflow
system_prompt_template = (
    "You are a helpful travel assistant. "
    "Think step-by-step internally to identify the location and reason about it, "
    "but only output the final clean answer to the user. "
    "The final user-facing output should include: "
    "1. Present office facts (from the document)."
    "2. Exactly 3 interesting facts about the location, formatted as bullet points (-). "
    "3. The distance from Raleigh, NC to the location in miles. "
    "Do not explain how you calculated the distance. "
    "Do not show your internal reasoning. Only show the final answer."
)

# KEPT: Same tool specification (unchanged from agent.py)
travel_tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_distance_tool",
            "description": "Calculate straight-line (haversine) distance in miles from Raleigh, NC to a provided destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_query": {"type": "string"},
                },
                "required": ["destination_query"],
            },
            "strict": True,
        },
    }
]

# ADDED: Helper function to find PDF file with fallback paths
def find_pdf_file(filename="offices.pdf"):
    """Look for PDF file in current directory, then ../data/, then data/"""
    possible_paths = [
        filename,  # Current directory
        f"../data/{filename}",  # One level back + data folder
        f"data/{filename}"  # data folder in current directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found PDF at: {path}")
            return path
    
    raise FileNotFoundError(f"Could not find {filename} in any of these locations: {possible_paths}")

# ADDED: Initialize RAG system - Index the uploaded offices.pdf into ChromaDB
print("\nLoading and indexing PDF into ChromaDB...")

# Find and load PDF with fallback paths
pdf_path = find_pdf_file("offices.pdf")
pdf_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        pdf_text += page.extract_text() + "\n"

# ADDED: Initialize sentence transformer model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# ADDED: Create ChromaDB collection
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="office_docs",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
)

# ADDED: Clean up and embed the PDF lines
docs = [line.strip() for line in pdf_text.split('\n') if len(line.strip()) > 20]
ids = [f"doc_{i}" for i in range(len(docs))]
collection.add(documents=docs, ids=ids)
print(f"Indexed {len(docs)} office documents.")

# MODIFIED: Build messages with RAG context (instead of simple user input)
def build_initial_messages(user_input, context_snippets):
    """Builds structured prompt with system context and user query."""
    context = "\n".join(context_snippets)
    system_prompt = system_prompt_template + f"\n\nOffice Context:\n{context}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

# ADDED: Search vector database for relevant office documents
def search_vector_db(query):
    """Search ChromaDB for relevant office document snippets."""
    results = collection.query(query_texts=[query], n_results=1)
    return results["documents"][0] if results["documents"] else []

# ADDED: Extract city name from RAG snippets
def extract_city_from_rag(snippets):
    """Try to extract known cities directly from office snippets."""
    possible_cities = []
    for snippet in snippets:
        for city in ["New York", "San Francisco", "Chicago", "Austin", "Boston",
                     "London", "Toronto", "Tokyo", "Sydney", "Berlin"]:
            if city.lower() in snippet.lower():
                possible_cities.append(city)
    if possible_cities:
        return possible_cities[0]  # Return first match found
    else:
        return None

# ADDED: Fallback city detection using LLM
def fallback_detect_city_with_llm(text):
    """If RAG fails, use LLM to detect a city from user query."""
    messages = [
        {"role": "system", "content": "Identify a city mentioned in the user query. Only reply with the city name."},
        {"role": "user", "content": text}
    ]
    completion = client.chat.completions.create(
        model="llama3.2",
        messages=messages
    )
    raw = completion.choices[0].message.content
    return raw.strip()

# KEPT: Same helper functions (unchanged from agent.py)
def geocode_location(location_query):
    """Use OpenStreetMap Nominatim API to convert a city name into lat/lon."""
    headers = {'User-Agent': 'SimpleAgent/1.0'}
    geo = requests.get(f"https://nominatim.openstreetmap.org/search?q={location_query}&format=json", headers=headers).json()
    if geo:
        return float(geo[0]['lat']), float(geo[0]['lon'])
    return None, None

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_distance_tool(destination_query):
    """Helper function for calculating distance from Raleigh, NC."""
    lat2, lon2 = geocode_location(destination_query)
    if lat2 is None or lon2 is None:
        return {"error": "Could not find destination."}
    miles = haversine_distance(CURRENT_LAT, CURRENT_LON, lat2, lon2)
    return {"destination": destination_query, "distance_miles": round(miles, 2)}

# ADDED: Get city facts using LLM
def get_city_facts(location_name):
    """Use LLM to retrieve 3 interesting facts about a city."""
    messages = [
        {"role": "system", "content": "Provide exactly 3 interesting facts about the city. Each fact starts with a dash (-)."},
        {"role": "user", "content": f"Tell me 3 interesting facts about {location_name}."}
    ]
    completion = client.chat.completions.create(
        model="llama3.2",
        messages=messages,
    )
    return completion.choices[0].message.content

# ADDED: Clean up LLM output into a list of facts
def get_city_facts_list(location_name):
    """Clean up LLM output into a list of 3 facts."""
    text = get_city_facts(location_name)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not any(line.startswith('-') or line.startswith('•') for line in lines):
        return lines[:3]
    else:
        return [line[1:].strip() for line in lines if line.startswith('-') or line.startswith('•')]

# MODIFIED: Enhanced formatting for both office and city facts
def format_final_output(location_name, office_facts_list, city_facts_list, distance_miles):
    """Format final combined response for the user."""
    output = f"{BOLD}{BLUE}Facts about the Office in {location_name}:{RESET}{BLUE}\n\n"
    for fact in office_facts_list:
        output += f"• {fact.strip()}\n"
    output += f"\n{BOLD}{BLUE}Facts about {location_name}:{RESET}{BLUE}\n\n"
    for fact in city_facts_list:
        output += f"• {fact.strip()}\n"
    output += f"\n{BOLD}{BLUE}Distance from Raleigh, NC:{RESET}{BLUE} {distance_miles} miles"
    return output

# MODIFIED: Display response with both office and city information
def display_final_response(location, office_facts, city_facts, distance_miles):
    """Nicely print the final result to the user."""
    final_output = format_final_output(location, office_facts, city_facts, distance_miles)
    print(f"\n{GREEN}Assistant Final Response:{RESET}\n\n{BLUE}{final_output}{RESET}")

# COMPLETELY MODIFIED: Main interaction loop now uses RAG workflow
print("\nTravel Assistant ready! (Type 'exit' to quit)")

while True:
    # User prompt
    user_input = input("\nUser: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # STEP 1: Search vector DB (office documents) first
    rag_snippets = search_vector_db(user_input)
    
    # Show what query was used
    print(f"\n{RED}RAG Search Query:{RESET} {user_input}")

    # Show retrieved office snippets
    if rag_snippets:
        print(f"\n{RED}RAG Retrieved Snippets:{RESET}")
        for idx, snippet in enumerate(rag_snippets, start=1):
            print(f"{RED}{BOLD}{idx}. {snippet}{RESET}")
    else:
        print(f"\n{RED}No snippets retrieved from RAG.{RESET}")

    # STEP 2: Try to extract city name from RAG first
    detected_city = extract_city_from_rag(rag_snippets)

    # STEP 3: If RAG fails, fallback to user prompt
    if not detected_city:
        detected_city = fallback_detect_city_with_llm(user_input)

    if detected_city:
        # STEP 4: Prepare office facts (from RAG)
        office_facts = [snippet for snippet in rag_snippets if detected_city.lower() in snippet.lower()]
        if not office_facts:
            office_facts = ["(No office information found)"]

        # STEP 5: Prepare city facts (from LLM)
        city_facts = get_city_facts_list(detected_city)

        # STEP 6: Calculate distance (same as agent.py)
        dist = calculate_distance_tool(detected_city)
        distance_miles = dist.get("distance_miles", "unknown")

        # STEP 7: Output everything nicely
        display_final_response(detected_city, office_facts, city_facts, distance_miles)

    else:
        print(f"\n{GREEN}Assistant Final Response:{RESET}\n{BOLD}Sorry, I couldn't find a relevant location.{RESET}")