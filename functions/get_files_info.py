import os

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}

def get_files_info(working_directory: str, directory: str = ".") -> str:

    try:
        absolute_path = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(absolute_path, directory))

        if os.path.commonpath([absolute_path, target_dir]) != absolute_path:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        lines = []
        for item in os.listdir(target_dir):
            path = os.path.join(target_dir, item)
            size = os.path.getsize(path)
            is_dir = os.path.isdir(path)
            lines.append(f"- {item}: file_size={size} bytes, is_dir={is_dir}")
        return "\n".join(lines)

    except ValueError:
        return "Error: Invalid path provided"
    except OSError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"
