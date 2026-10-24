import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import argparse

from prompts import system_prompt
from call_function import available_functions, call_function

MAX_ITERATIONS = 20

# Defaults point at the local model server. Override with LLM_BASE_URL /
# LLM_MODEL (and LLM_API_KEY, for providers that need one) in .env, e.g.
#   LLM_BASE_URL=https://openrouter.ai/api/v1
#   LLM_MODEL=openrouter/free
DEFAULT_BASE_URL = "http://100.102.128.112:11434/v1"
DEFAULT_MODEL = "qwen/qwen3.8-27b"


def generate_content(client: OpenAI, model: str, messages: list, verbose: bool):
    for _ in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=available_functions,
            temperature=0,
        )

        if response.usage is None:
            raise RuntimeError("Failed API request")

        if verbose:
            print("Prompt tokens:", response.usage.prompt_tokens)
            print("Response tokens:", response.usage.completion_tokens)

        message = response.choices[0].message

        # Keep the conversation in sync: the model must see its own
        # assistant turn (including any tool_calls) in later iterations.
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(tool_call, verbose)

                if not result_message["content"]:
                    raise RuntimeError(f"Tool call {tool_call.id} returned empty content")

                if verbose:
                    print(f"-> {result_message['content']}")

                # One tool message per tool call, in the same order,
                # so the model can match each result to its request.
                messages.append(result_message)
        else:
            if message.content is None or not message.content.strip():
                # Degenerate case: the model ended its turn without an
                # answer. Nudge it to continue instead of returning an
                # empty result.
                if verbose:
                    print("Warning: model returned an empty response; asking it to continue")
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "You ended your turn without an answer. "
                            "Continue the task: either call the tools you "
                            "still need, or give your final response to the user."
                        ),
                    }
                )
                continue

            print(f"Final response:\n{message.content}")
            return message.content

    print(
        f"Error: the agent reached the maximum of {MAX_ITERATIONS} iterations "
        "without producing a final response. It is likely still requesting "
        "tool calls in a loop, so the program is exiting to avoid wasting tokens."
    )
    sys.exit(1)


def main():
    load_dotenv()

    client = OpenAI(
        base_url=os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL),
        # Local servers ignore the key; real providers need one.
        api_key=os.environ.get("LLM_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
        or "local-model",
    )
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)

    parser = argparse.ArgumentParser(description="AI assistant")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    if args.verbose:
        print("Model:", model)
        print("User prompt:", args.user_prompt)

    generate_content(client, model, messages, args.verbose)


if __name__ == "__main__":
    main()
