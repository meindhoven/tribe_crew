# tools.py
# This file defines your custom tools.

import os
import requests
from pathlib import Path
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
        # Input validation
        if not query or not query.strip():
            return "Error: Query cannot be empty."
        
        # Limit query length to prevent abuse
        max_query_length = 1000
        if len(query) > max_query_length:
            return f"Error: Query too long (max {max_query_length} characters)."
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return "Error: PERPLEXITY_API_KEY environment variable not set."
        
        # Basic API key format validation
        if not api_key.startswith(('pplx-', 'sk-')) or len(api_key) < 10:
            return "Error: Invalid PERPLEXITY_API_KEY format."

        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "llama-3-sonar-large-32k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI research assistant. Provide concise and factual information.",
                },
                {"role": "user", "content": query.strip()},
            ],
            "max_tokens": 2000,  # Limit response size
            "temperature": 0.1   # Make responses more deterministic
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}",
        }

        try:
            # Add timeout to prevent hanging
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            
            # Extract the content from the response
            if result.get('choices') and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                if content and content.strip():
                    return content.strip()
                else:
                    return "No content found in Perplexity response."
            else:
                return "No content found in Perplexity response."
                
        except requests.exceptions.Timeout:
            return "Error: Request to Perplexity API timed out."
        except requests.exceptions.ConnectionError:
            return "Error: Unable to connect to Perplexity API. Check your internet connection."
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return "Error: Invalid API key. Please check your PERPLEXITY_API_KEY."
            elif e.response.status_code == 429:
                return "Error: Rate limit exceeded. Please try again later."
            else:
                return f"Error: HTTP {e.response.status_code} - {e.response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error calling Perplexity API: {e}"
        except ValueError as e:
            return f"Error: Invalid JSON response from Perplexity API: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class FileReadTool(BaseTool):
    name: str = "File Read Tool"
    description: str = "A tool to read the content of a file given its path. Use this to read the client briefing."

    def _run(self, file_path: str) -> str:
        """Reads content from a specified file with security validation."""
        try:
            # Security: Validate and resolve the file path
            path = Path(file_path).resolve()
            
            # Security: Check if the file exists and is actually a file
            if not path.exists():
                return f"Error: File not found at path '{file_path}'."
            
            if not path.is_file():
                return f"Error: Path '{file_path}' is not a file."
            
            # Security: Check file size (max 10MB to prevent memory issues)
            max_size = 10 * 1024 * 1024  # 10MB
            if path.stat().st_size > max_size:
                return f"Error: File '{file_path}' is too large (max 10MB allowed)."
            
            # Security: Only allow specific file extensions
            allowed_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.yaml', '.yml'}
            if path.suffix.lower() not in allowed_extensions:
                return f"Error: File type '{path.suffix}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
            
            # Read the file
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
                
        except FileNotFoundError:
            return f"Error: File not found at path '{file_path}'."
        except PermissionError:
            return f"Error: Permission denied accessing file '{file_path}'."
        except UnicodeDecodeError:
            return f"Error: Unable to decode file '{file_path}'. Please ensure it's a text file with UTF-8 encoding."
        except OSError as e:
            return f"Error: Operating system error accessing file '{file_path}': {e}"
        except Exception as e:
            return f"An unexpected error occurred while reading the file: {e}"

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
        try:
            # Input validation
            if not query or not query.strip():
                return "Error: Query cannot be empty."
            
            # Limit query length
            max_query_length = 500
            if len(query) > max_query_length:
                return f"Error: Query too long (max {max_query_length} characters)."
            
            # --- Placeholder Implementation ---
            # In a real application, you would replace this with a call to your
            # vector store or knowledge base API.
            print(f"--- Querying Knowledge Base with: '{query.strip()}' ---")
            
            # Simulate some basic query matching for better responses
            query_lower = query.lower().strip()
            
            if any(keyword in query_lower for keyword in ['past', 'project', 'success', 'case', 'study']):
                return (
                    "Past Project Examples:\n"
                    "• 'Future Forward Summit' - A major tech client event featuring interactive AI art installations, holographic displays, and VR networking spaces\n"
                    "• 'Green Horizon Gala' - Environmental NGO event that was fully carbon-neutral with sustainable materials and zero-waste catering\n"
                    "• 'Innovation Nexus Conference' - B2B tech conference with AI-powered matchmaking and real-time collaboration tools\n"
                    "Our brand ethos: 'Meaningful Moments, Measurable Impact'"
                )
            elif any(keyword in query_lower for keyword in ['brand', 'value', 'ethos', 'identity']):
                return (
                    "Company Brand Values:\n"
                    "• Core Ethos: 'Meaningful Moments, Measurable Impact'\n"
                    "• Focus: Immersive, technology-driven brand experiences\n"
                    "• Specialization: Corporate events, conferences, and brand activations\n"
                    "• Differentiator: Integration of cutting-edge technology with human-centered design\n"
                    "• Commitment: Sustainable and socially responsible event practices"
                )
            elif any(keyword in query_lower for keyword in ['technology', 'tech', 'innovation', 'digital']):
                return (
                    "Technology Capabilities:\n"
                    "• AI-powered event personalization and matchmaking\n"
                    "• Interactive installations and digital art\n"
                    "• VR/AR experiences and immersive environments\n"
                    "• Real-time analytics and engagement tracking\n"
                    "• Sustainable tech solutions and carbon footprint monitoring"
                )
            else:
                return (
                    "Our company excels at creating immersive, technology-driven brand experiences. "
                    "Past successes include the 'Future Forward Summit' for a major tech client, "
                    "which featured interactive AI art installations, and the 'Green Horizon Gala' "
                    "for an environmental NGO, which was a fully carbon-neutral event. Our brand "
                    "ethos is 'Meaningful Moments, Measurable Impact'."
                )
                
        except Exception as e:
            return f"Error accessing company knowledge base: {e}"

