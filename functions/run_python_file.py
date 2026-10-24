import os
import subprocess
import sys

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a Python file relative to the working directory, optionally with command-line arguments",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to execute, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of command-line arguments to pass to the Python file",
                },
            },
            "required": ["file_path"],
        },
    },
}

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:

    try:
        absolute_path = os.path.abspath(working_directory)
        absolute_file_path = os.path.normpath(os.path.join(absolute_path, file_path))

        if os.path.commonpath([absolute_path, absolute_file_path]) != absolute_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(absolute_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not absolute_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = [sys.executable, absolute_file_path]
        if args:
            command.extend(args)

        result = subprocess.run(
            command,
            cwd=absolute_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output_parts = []
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")
        if not result.stdout and not result.stderr:
            output_parts.append("No output produced")
        else:
            if result.stdout:
                output_parts.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")
        return "\n".join(output_parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"
