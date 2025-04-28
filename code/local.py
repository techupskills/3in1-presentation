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

# System prompt to guide LLM behavior
system_prompt = (
    "You are a helpful travel assistant. "
    "Provide exactly 3 interesting facts about the location the user mentions, "
    "formatted as bullet points (-). "
    "Do not include any reasoning steps—only output the final 3 bullets."
)

# 🧑 Build the starting conversation with user input
def build_initial_messages(user_input):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

# 🧠 Ask LLM for facts
def get_facts(messages):
    # note: no 'tools' passed
    return client.chat.completions.create(
        model="llama3.2",
        messages=messages
    )

# ✨ Final user-visible output
def display_facts(completion):
    content = completion.choices[0].message.content.strip()
    # assume the model already formats bullets as "- fact"
    print(f"\n{GREEN}Here are 3 facts for you:{RESET}\n")
    print(f"{BLUE}{content}{RESET}")

# 🧑 Main user interaction loop
print("\nTravel Assistant ready! (Type 'exit' to quit)")

while True:
    user_input = input("\nUser: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # Ask the LLM for facts
    messages   = build_initial_messages(user_input)
    completion = get_facts(messages)
    display_facts(completion)
