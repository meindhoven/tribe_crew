# tools.py
# This file defines your custom tools.

import os
import requests
from crewai_tools import BaseTool

class PerplexityTool(BaseTool):
    name: str = "Perplexity Search Tool"
    description: str = (
        "A tool to perform in-depth web research using the Perplexity API. "
        "Use this for any research task about companies, competitors, markets, or audiences."
    )

    def _run(self, query: str) -> str:
        """
        Executes a search query using the Perplexity API.
        Requires PERPLEXITY_API_KEY to be set in the environment.
        """
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return "Error: PERPLEXITY_API_KEY environment variable not set."

        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "llama-3-sonar-large-32k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI research assistant. Provide concise and factual information.",
                },
                {"role": "user", "content": query},
            ],
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}",
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            # Extract the content from the response
            if result.get('choices') and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "No content found in Perplexity response."
        except requests.exceptions.RequestException as e:
            return f"Error calling Perplexity API: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class FileReadTool(BaseTool):
    name: str = "File Read Tool"
    description: str = "A tool to read the content of a file given its path. Use this to read the client briefing."

    def _run(self, file_path: str) -> str:
        """Reads content from a specified file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found at path '{file_path}'."
        except Exception as e:
            return f"An error occurred while reading the file: {e}"

class CompanyKnowledgeBaseTool(BaseTool):
    name: str = "Company Knowledge Base"
    description: str = (
        "A tool to search our company's internal knowledge base for past projects, "
        "brand values, and successful case studies. Use this to ground creative "
        "concepts in our company's identity."
    )

    def _run(self, query: str) -> str:
        """
        Simulates a search in a company knowledge base.
        In a real-world scenario, this would query a vector database (e.g., RAG).
        """
        # --- Placeholder Implementation ---
        # In a real application, you would replace this with a call to your
        # vector store or knowledge base API.
        print(f"--- Querying Knowledge Base with: '{query}' ---")
        return (
            "Our company excels at creating immersive, technology-driven brand experiences. "
            "Past successes include the 'Future Forward Summit' for a major tech client, "
            "which featured interactive AI art installations, and the 'Green Horizon Gala' "
            "for an environmental NGO, which was a fully carbon-neutral event. Our brand "
            "ethos is 'Meaningful Moments, Measurable Impact'."
        )

