<<<<<<< HEAD
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
=======
from crewai_tools import tool
import os
>>>>>>> 89b659b (Added docs)

@tool("Read a file's content")
def file_read_tool(file_path: str) -> str:
    """
    A tool that can be used to read a file's content.
    The input to this tool should be a string representing the file path.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"An error occurred while trying to read the file: {e}"

# You can add more tools here using the @tool decorator
# For example:
#
# @tool("Another tool description")
# def another_tool(argument1: str, argument2: int) -> str:
#     """A brief description of what another tool does."""
#     # Tool implementation here
#     return "Result from another tool"

