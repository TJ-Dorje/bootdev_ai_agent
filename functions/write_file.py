import os

schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Writes the given content to a file relative to the working directory, creating or overwriting it",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write, relative to the working directory",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["file_path", "content"],
        },
    },
}

def write_file(working_directory: str, file_path: str, content: str) -> str:

    try:
        absolute_path = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(absolute_path, file_path))

        if os.path.commonpath([absolute_path, target_file]) != absolute_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if os.path.isdir(target_file):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        parent_dir = os.path.dirname(target_file)
        os.makedirs(parent_dir, exist_ok=True)

        with open(target_file, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except ValueError:
        return "Error: Invalid path provided"
    except OSError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"
