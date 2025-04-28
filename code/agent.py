# Import necessary libraries

import json
import requests
import math
from openai import OpenAI

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
system_prompt = (
    "You are a helpful travel assistant. "
    "Think step-by-step internally to identify the location and reason about it, "
    "but only output the final clean answer to the user. "
    "The final user-facing output should include: "
    "1. Exactly 3 interesting facts about the location, formatted as bullet points (-). "
    "2. The distance from Raleigh, NC to the location in miles. "
    "Do not explain how you calculated the distance. "
    "Do not show your internal reasoning. Only show the final answer."
)

# Tool specification for LLM tool use
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

# 🧑 Build the starting conversation with user input
def build_initial_messages(user_input):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

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

# 🛠 Tool: Find distance between Raleigh and user location
def calculate_distance_tool(destination_query):
    """Helper function for calculating distance from Raleigh, NC."""
    lat2, lon2 = geocode_location(destination_query)
    if lat2 is None or lon2 is None:
        return {"error": "Could not find destination."}
    miles = haversine_distance(CURRENT_LAT, CURRENT_LON, lat2, lon2)
    return {"destination": destination_query, "distance_miles": round(miles, 2)}

# 🧠 Ask LLM for initial action planning
def get_initial_llm_response(messages):
    return client.chat.completions.create(
        model="llama3.2",
        messages=messages,
        tools=travel_tools,
    )

# Print the initial "thoughts" from the Assistant
def print_assistant_thinking(completion):
    print(f"\nAssistant thinking: {completion.choices[0].message.content}")

# Check if the LLM dictated a tool call
def tool_call_required(completion):
    return bool(completion.choices[0].message.tool_calls)

# 🛠 Handle tool execution and capture results
def handle_tool_calls(completion, messages):
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        print(f"{RED}{BOLD}Tool call: {name} with args: {args}{RESET}")

        if name == "calculate_distance_tool":
            result = calculate_distance_tool(**args)
            print(f"{RED}{BOLD}Tool call result: {result}{RESET}")

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
    return result

# 🧠 After tool use, ask LLM for final answer
def get_final_llm_response(messages):
    return client.chat.completions.create(
        model="llama3.2",
        messages=messages,
    )

# Format the assistant final user-facing answer
def format_final_output(location_name, facts_list, distance_miles):
    facts_section = f"{BOLD}{BLUE}Facts about {location_name}:\n\n{RESET}"
    for fact in facts_list:
        facts_section += f"{BLUE}\u2022 {fact.strip()}\n{RESET}"
    distance_section = f"{BOLD}{BLUE}\nDistance from Raleigh, NC: {RESET}{BLUE}{distance_miles} miles{RESET}"
    return f"{facts_section}{distance_section}"

# ✨ Final user-visible formatted output
def display_final_response(final_completion, tool_result):
    raw_output = final_completion.choices[0].message.content
    lines = raw_output.split('\n')
    facts = []

    for line in lines:
        line = line.strip()
        if line.startswith('-') or line.startswith('•'):
            facts.append(line[1:].strip())

    if facts and "distance_miles" in tool_result:
        final_output = format_final_output(tool_result.get("destination", "Destination"), facts, tool_result.get("distance_miles"))
        print(f"\n{GREEN}Assistant Final Response:{RESET}\n\n{final_output}")
    else:
        print(f"\n{GREEN}Assistant Final Response:{RESET}\n\n{raw_output}")

# Direct output if no tool was needed
def display_direct_response(completion):
    print(f"\n{GREEN}Assistant Final Response:{RESET}\n{BLUE}{completion.choices[0].message.content}{RESET}")

# 🧑 Main user interaction loop
print("\nTravel Assistant ready! (Type 'exit' to quit)")

while True:
    # 🧑 User prompt
    user_input = input("\nUser: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # 🧠 LLM plans tool call
    messages = build_initial_messages(user_input)
    completion = get_initial_llm_response(messages)
    print_assistant_thinking(completion)

    if tool_call_required(completion):
        # 🛠 Tool runs
        tool_result = handle_tool_calls(completion, messages)

        # 🛠 Tool result added back into conversation
        final_completion = get_final_llm_response(messages)

        # 🧠 LLM reasons with tool output → ✨ Assistant final answer
        display_final_response(final_completion, tool_result)
    else:
        display_direct_response(completion)





