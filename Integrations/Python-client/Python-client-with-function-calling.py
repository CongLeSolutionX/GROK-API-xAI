import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()
load_dotenv(dotenv_path='../.env') # since my .env file is up one directory level

# Confirm of accessing the environment variable
print(os.getenv('XAI_API_KEY'))


XAI_API_KEY = os.getenv("XAI_API_KEY")

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
        str: HTML content of the website.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching the website: {e}"

def click(html, button):
    """
    Simulates clicking a button on the webpage.

    Args:
        html (str): The current HTML content of the page.
        button (str): The text description of the button to click.

    Returns:
        str: Updated HTML content after clicking the button.
    """
    # Placeholder implementation.
    # In a real scenario, you might use BeautifulSoup or Selenium to parse and interact with the HTML.
    # For security reasons, actual browser interactions are not implemented here.
    return f"Clicked on the button '{button}'. Updated HTML content."

# Step 3: Program the Assistant

def main():
    MODEL_NAME = "grok-beta"
    XAI_API_KEY = os.getenv("XAI_API_KEY")

    if not XAI_API_KEY:
        raise EnvironmentError("Please set the XAI_API_KEY environment variable.")

    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    # Define tools with functions
    tools = [{"type": "function", "function": func} for func in functions]

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

        if 'tool_calls' in message and message['tool_calls']:
            tool_call = message['tool_calls'][0]
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])

            if function_name == "open_website":
                url = arguments.get("url")
                html = open_website(url)
                tool_call_result_message = {
                    "role": "tool",
                    "content": html,
                    "tool_call_id": tool_call['id']
                }
                messages.append(message)
                messages.append(tool_call_result_message)
                return
            elif function_name == "click":
                html = arguments.get("html")
                button = arguments.get("button")
                updated_html = click(html, button)
                tool_call_result_message = {
                    "role": "tool",
                    "content": updated_html,
                    "tool_call_id": tool_call['id']
                }
                messages.append(message)
                messages.append(tool_call_result_message)
                return
            else:
                print(f"Unknown function: {function_name}")
                return
        else:
            # Direct response to the user
            print(f"Assistant: {message['content']}")

    # Initial call to the assistant
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
    )
    handle_response(response)

    # Continue the loop if there are more tool calls
    while True:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
        )
        handle_response(response)
        # Here, you might want to add a condition to break the loop
        # For example, based on user input or a termination message
        break

if __name__ == "__main__":
    main()
