import os
import json
from openai import OpenAI
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()
load_dotenv(dotenv_path='../.env') # since my .env file is up one directory level

# Confirm of accessing the environment variable
# print(os.getenv('XAI_API_KEY'))
# print(os.getenv('OPENAI_API_KEY'))

XAI_API_KEY = os.getenv("XAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Step 1: Define Function Interfaces
functions = [
    {
        "name": "open_website",
        "description": "Open a website and return the HTML as a string",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "A URL to open",
                    "example_value": "https://x.ai/",
                },
            },
            "required": ["url"],
            "optional": [],
        },
    },
    {
        "name": "click",
        "description": "Click any button on a website and return the updated HTML",
        "parameters": {
            "type": "object",
            "properties": {
                "html": {
                    "type": "string",
                    "description": "The HTML content of the current page",
                },
                "button": {
                    "type": "string",
                    "description": "A text description of the button to click on the HTML page",
                },
            },
            "required": ["html", "button"],
            "optional": [],
        },
    },
]

# Step 2: Implement the Functions

def open_website(url):
    """
    Opens the specified URL and returns the HTML content.

    Args:
        url (str): The URL of the website to open.

    Returns:
        str: HTML content of the website or an error message.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        # Log the detailed error internally
        print(f"Error fetching the website {url}: {e}")
        return "Sorry, I couldn't fetch the website content."

def click(html, button):
    """
    Simulates clicking a button on the webpage.

    Args:
        html (str): The current HTML content of the page.
        button (str): The text description of the button to click.

    Returns:
        str: Updated HTML content after clicking the button or an error message.
    """
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        # Find the button by its text
        btn = soup.find('button', text=button)
        if not btn:
            return f"Button '{button}' not found on the page."

        # Simulate the button click by performing the relevant action
        # Placeholder: In real scenarios, this might involve triggering JavaScript or navigating to a new URL
        # Here, we'll just return a message
        return f"Clicked on the button '{button}'. Updated HTML content would be displayed here."
    except Exception as e:
        # Log the detailed error internally
        print(f"Error simulating button click: {e}")
        return "Sorry, I couldn't simulate the button click."

# Step 3: Program the Assistant

def main():
    MODEL_NAME = "gpt-4o"  # Updated model name
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        raise EnvironmentError("Please set the OPENAI_API_KEY environment variable.")


    # Define tools with functions
    tools = functions  # OpenAI expects function definitions as passed

    # Initial user message
    messages = [
        {
            "role": "system",
            "content": "You are a helpful webpage navigation assistant. Use the supplied tools to assist the user."
        },
        {
            "role": "user",
            "content": "Hi, can you go to the career page of the xAI website?"
        }
    ]

    # Function to handle function calls
    def handle_response(response):
        if not response.choices:
            print("No response from the assistant.")
            return

        choice = response.choices[0]
        message = choice.message

        if hasattr(message, 'function_call') and message.function_call:
            function_name = message.function_call.name
            arguments = json.loads(message.function_call.arguments)

            if function_name == "open_website":
                url = arguments.get("url")
                html = open_website(url)
                tool_call_result_message = {
                    "role": "function",
                    "name": "open_website",
                    "content": html
                }
                messages.append({
                    "role": "assistant",
                    "content": "",
                    "function_call": message.function_call
                })
                messages.append(tool_call_result_message)
                return
            elif function_name == "click":
                html = arguments.get("html")
                button = arguments.get("button")
                updated_html = click(html, button)
                tool_call_result_message = {
                    "role": "function",
                    "name": "click",
                    "content": updated_html
                }
                messages.append({
                    "role": "assistant",
                    "content": "",
                    "function_call": message.function_call
                })
                messages.append(tool_call_result_message)
                return
            else:
                print(f"Unknown function: {function_name}")
                return
        else:
            # Direct response to the user
            print(f"Assistant: {message.content}")

    try:
        # Initial call to the assistant
        response = client.chat.completions.create(model=MODEL_NAME,
        messages=messages,
        functions=tools,
        function_call="auto")
        handle_response(response)

        # Continue the loop if there are more tool calls
        while True:
            response = client.chat.completions.create(model=MODEL_NAME,
            messages=messages,
            functions=tools,
            function_call="auto")
            handle_response(response)
            # Example termination condition: stop if assistant provides an answer without needing to call a function
            last_message = response.choices[0].message
            if not hasattr(last_message, 'function_call') or not last_message.function_call:
                break

    except KeyboardInterrupt:
        print("\nConversation terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
