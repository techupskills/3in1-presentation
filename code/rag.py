# Import necessary libraries
import os
import json
import requests
import math
from openai import OpenAI
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

# System prompt to guide LLM behavior
system_prompt_template = (
    "You are a helpful travel assistant. "
    "Based on user query and office documents, your tasks are: "
    "1. Present office facts (from documents). "
    "2. Present city facts (from your own knowledge). "
    "3. Calculate distance to Raleigh, NC."
)

# Define available tools for the agent (just distance calculation)
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

#  Index the uploaded offices.pdf into ChromaDB
print("\nLoading and indexing PDF into ChromaDB...")
pdf_text = ""
with pdfplumber.open("../data/offices.pdf") as pdf:
    for page in pdf.pages:
        pdf_text += page.extract_text() + "\n"

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Create ChromaDB collection
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="office_docs",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
)

# Clean up and embed the PDF lines
docs = [line.strip() for line in pdf_text.split('\n') if len(line.strip()) > 20]
ids = [f"doc_{i}" for i in range(len(docs))]
collection.add(documents=docs, ids=ids)
print(f"Indexed {len(docs)} office documents.")

#  Functions

def build_initial_messages(user_input, context_snippets):
    """Builds structured prompt with system context and user query."""
    context = "\n".join(context_snippets)
    system_prompt = system_prompt_template + f"\n\nOffice Context:\n{context}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

def search_vector_db(query):
    """Search ChromaDB for relevant office document snippets."""
    results = collection.query(query_texts=[query], n_results=1)
    return results["documents"][0] if results["documents"] else []

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

# Helper: Geocode destination using OpenStreetMap
def geocode_location(location_query):
    """Use OpenStreetMap Nominatim API to convert a city name into lat/lon."""
    headers = {'User-Agent': 'SimpleAgent/1.0'}
    geo = requests.get(f"https://nominatim.openstreetmap.org/search?q={location_query}&format=json", headers=headers).json()
    if geo:
        return float(geo[0]['lat']), float(geo[0]['lon'])
    return None, None

# Helper: Calculate straight-line distance (haversine formula)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

#  Tool: Find distance between Raleigh and user location
def calculate_distance_tool(destination_query):
    """Helper function for calculating distance from Raleigh, NC."""
    lat2, lon2 = geocode_location(destination_query)
    if lat2 is None or lon2 is None:
        return {"error": "Could not find destination."}
    miles = haversine_distance(CURRENT_LAT, CURRENT_LON, lat2, lon2)
    return {"destination": destination_query, "distance_miles": round(miles, 2)}

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

def get_city_facts_list(location_name):
    """Clean up LLM output into a list of 3 facts."""
    text = get_city_facts(location_name)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not any(line.startswith('-') or line.startswith('•') for line in lines):
        return lines[:3]
    else:
        return [line[1:].strip() for line in lines if line.startswith('-') or line.startswith('•')]

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

def display_final_response(location, office_facts, city_facts, distance_miles):
    """Nicely print the final result to the user."""
    final_output = format_final_output(location, office_facts, city_facts, distance_miles)
    print(f"\n{GREEN}Assistant Final Response:{RESET}\n\n{BLUE}{final_output}{RESET}")

#  Main user interaction loop
print("\nTravel Assistant ready! (Type 'exit' to quit)")

while True:
    #  User prompt
    user_input = input("\nUser: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # 1. Search vector DB (office documents) first
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

    # 2. Try to extract city name from RAG first
    detected_city = extract_city_from_rag(rag_snippets)

    # 3. If RAG fails, fallback to user prompt
    if not detected_city:
        detected_city = fallback_detect_city_with_llm(user_input)

    if detected_city:
        # 4. Prepare office facts (from RAG)
        office_facts = [snippet for snippet in rag_snippets if detected_city.lower() in snippet.lower()]
        if not office_facts:
            office_facts = ["(No office information found)"]

        # 5. Prepare city facts (from LLM)
        city_facts = get_city_facts_list(detected_city)

        # 6. Calculate distance
        dist = calculate_distance_tool(detected_city)
        distance_miles = dist.get("distance_miles", "unknown")

        # 7. Output everything nicely
        display_final_response(detected_city, office_facts, city_facts, distance_miles)

    else:
        print(f"\n{GREEN}Assistant Final Response:{RESET}\n{BOLD}Sorry, I couldn't find a relevant location.{RESET}")
