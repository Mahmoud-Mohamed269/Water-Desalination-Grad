from google import genai
from google.genai import types

import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

print("Chatbot is ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting the chatbot. Goodbye!")
        break
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_input
        )
        print(f"Chatbot: {response.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")