import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse


def generate_content(client: OpenAI, messages: list, verbose: bool):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
    )

    if response.usage is None:
        raise RuntimeError("Failed API request")

    if verbose:
        print("Prompt tokens:", response.usage.prompt_tokens)
        print("Response tokens:", response.usage.completion_tokens)
    print(f"Response:\n{response.choices[0].message.content}")
        
        

def main():
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if api_key is None:
        raise RuntimeError("Failed to load OPENROUTER_API_KEY")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    parser = argparse.ArgumentParser(description="AI assistant")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

       
    messages = [
        {"role": "user", "content": args.user_prompt},
    ]

    if args.verbose:
        print("User prompt:", args.user_prompt)

    generate_content(client, messages, args.verbose)    
    

if __name__ == "__main__":
    main()
