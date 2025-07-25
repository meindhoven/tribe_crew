# tools.py
# This file defines your custom tools with enhanced RAG and folder scanning capabilities.

import os
import requests
import hashlib
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from crewai_tools import BaseTool
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# RAG and embedding imports
try:
    import chromadb
    from chromadb.config import Settings
    import google.generativeai as genai
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    import numpy as np
    HAS_RAG_DEPS = True
except ImportError as e:
    print(f"Warning: RAG dependencies not available: {e}")
    HAS_RAG_DEPS = False

class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events for RAG updates"""
    
    def __init__(self, rag_manager):
        self.rag_manager = rag_manager
        
    def on_modified(self, event):
        if (not event.is_directory and 
            event.src_path.endswith(('.txt', '.md', '.pdf', '.doc', '.docx')) and
            not Path(event.src_path).name.lower() in {'readme.md', 'readme.txt'}):
            self.rag_manager.update_file_if_changed(event.src_path)
    
    def on_created(self, event):
        if (not event.is_directory and 
            event.src_path.endswith(('.txt', '.md', '.pdf', '.doc', '.docx')) and
            not Path(event.src_path).name.lower() in {'readme.md', 'readme.txt'}):
            self.rag_manager.update_file_if_changed(event.src_path)

class RAGManager:
    """Manages RAG functionality with SQLite storage and Gemini embeddings"""
    
    def __init__(self, storage_path: str = "./rag_storage", gemini_api_key: Optional[str] = None):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize Gemini for embeddings
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
        else:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
        
        # Initialize SQLite for metadata storage
        self.db_path = self.storage_path / "rag_metadata.db"
        self._init_database()
        
        # Initialize ChromaDB for vector storage
        if HAS_RAG_DEPS:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.storage_path / "chroma_db")
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def _init_database(self):
        """Initialize SQLite database for storing file metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    file_path TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    chunk_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using Gemini"""
        try:
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            return embeddings
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            # Fallback to zero embeddings if Gemini fails
            return [[0.0] * 768 for _ in texts]
    
    def file_needs_update(self, file_path: str) -> bool:
        """Check if file needs to be updated in RAG based on hash"""
        if not os.path.exists(file_path):
            return False
            
        current_hash = self._get_file_hash(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT file_hash FROM file_metadata WHERE file_path = ?",
                (file_path,)
            )
            result = cursor.fetchone()
            
            if result is None:
                return True  # New file
            
            return result[0] != current_hash  # Hash changed
    
    def update_file_if_changed(self, file_path: str) -> bool:
        """Update file in RAG if it has changed"""
        if not self.file_needs_update(file_path):
            return False
            
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Remove existing chunks for this file
            self._remove_file_from_rag(file_path)
            
            # Split into chunks
            documents = [Document(page_content=content, metadata={"source": file_path})]
            chunks = self.text_splitter.split_documents(documents)
            
            if not chunks:
                return False
            
            # Get embeddings
            texts = [chunk.page_content for chunk in chunks]
            embeddings = self._get_embeddings(texts)
            
            # Store in ChromaDB
            if HAS_RAG_DEPS:
                ids = [f"{file_path}_{i}" for i in range(len(chunks))]
                metadatas = [
                    {
                        "source": file_path,
                        "chunk_index": i,
                        "timestamp": datetime.now().isoformat()
                    }
                    for i in range(len(chunks))
                ]
                
                self.collection.add(
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            
            # Update metadata in SQLite
            current_hash = self._get_file_hash(file_path)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO file_metadata 
                    (file_path, file_hash, last_updated, chunk_count)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                """, (file_path, current_hash, len(chunks)))
                conn.commit()
            
            print(f"Updated RAG with {len(chunks)} chunks from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error updating file {file_path} in RAG: {e}")
            return False
    
    def _remove_file_from_rag(self, file_path: str):
        """Remove all chunks for a file from RAG"""
        if HAS_RAG_DEPS:
            try:
                # Query for existing chunks
                results = self.collection.get(
                    where={"source": file_path}
                )
                
                if results['ids']:
                    self.collection.delete(ids=results['ids'])
                    print(f"Removed {len(results['ids'])} existing chunks for {file_path}")
            except Exception as e:
                print(f"Error removing file {file_path} from RAG: {e}")
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the RAG system"""
        if not HAS_RAG_DEPS:
            return []
            
        try:
            # Get query embedding
            query_embedding = self._get_embeddings([query_text])[0]
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'source': results['metadatas'][0][i]['source'],
                        'distance': results['distances'][0][i] if 'distances' in results else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error querying RAG: {e}")
            return []

class PerplexityTool(BaseTool):
    name: str = "Perplexity Search Tool"
    description: str = (
        "A tool to perform in-depth web research using the Perplexity API with sonar-deep-research model. "
        "Use this for any research task about companies, competitors, markets, or audiences."
    )

    def _run(self, query: str) -> str:
        """
        Search using Perplexity's sonar-deep-research model.
        """
        try:
            # Input validation
            if not query or not query.strip():
                return "Error: Query cannot be empty."
            
            # Limit query length to prevent abuse
            max_query_length = 500
            if len(query) > max_query_length:
                return f"Error: Query too long (max {max_query_length} characters)."
            
            # Check API key
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                return "Error: PERPLEXITY_API_KEY environment variable not set."
            
            # Validate API key format (basic check)
            if not api_key.startswith(('pplx-', 'sk-')) or len(api_key) < 20:
                return "Error: Invalid PERPLEXITY_API_KEY format. Please check your API key."
            
            url = "https://api.perplexity.ai/chat/completions"
            
            payload = {
                "model": "sonar-deep-research",
                "messages": [
                    {
                        "role": "user",
                        "content": query.strip()
                    }
                ],
                "max_tokens": 4000,  # Increased for deep research
                "temperature": 0.2,
                "top_p": 0.9,
                "search_domain_filter": ["perplexity.ai"],
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "month",
                "top_k": 0,
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 1
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Make request with timeout
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            return "Error: Request to Perplexity API timed out. Please try again."
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
        except KeyError:
            return "Error: Unexpected response format from Perplexity API"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class FolderReadTool(BaseTool):
    name: str = "Folder Read Tool"
    description: str = "A tool to read all files in a specified folder. Use this to read multiple briefing documents or knowledge base files."
    
    def __init__(self, default_folder: str = "./input_files"):
        super().__init__()
        self.default_folder = default_folder

    def _run(self, folder_path: str = None) -> str:
        """Reads all files in the specified folder or default input folder."""
        try:
            # Use provided folder or default
            folder_to_scan = folder_path if folder_path else self.default_folder
            folder = Path(folder_to_scan).resolve()
            
            # Security: Check if folder exists
            if not folder.exists():
                return f"Error: Folder not found at path '{folder_to_scan}'."
            
            if not folder.is_dir():
                return f"Error: Path '{folder_to_scan}' is not a directory."
            
            # Security: Only allow specific file extensions
            allowed_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.yaml', '.yml'}
            # Ignore README files as they are documentation, not content to be processed
            ignored_filenames = {'readme.md', 'readme.txt'}
            
            files_content = []
            for file_path in folder.glob('*'):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in allowed_extensions and 
                    file_path.name.lower() not in ignored_filenames):
                    # Security: Check file size (max 10MB per file)
                    max_size = 10 * 1024 * 1024  # 10MB
                    if file_path.stat().st_size > max_size:
                        files_content.append(f"File '{file_path.name}' skipped: too large (max 10MB allowed).")
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            files_content.append(f"=== FILE: {file_path.name} ===\n{content}\n")
                    except Exception as e:
                        files_content.append(f"Error reading file '{file_path.name}': {e}")
            
            if not files_content:
                return f"No readable files found in folder '{folder_to_scan}'. Allowed extensions: {', '.join(allowed_extensions)}"
            
            return "\n".join(files_content)
                
        except Exception as e:
            return f"An unexpected error occurred while reading folder: {e}"

class FileReadTool(BaseTool):
    name: str = "File Read Tool"
    description: str = "A tool to read the content of a specific file given its path. Use this to read individual briefing documents."

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
        "A tool to search our company's internal knowledge base using RAG (Retrieval Augmented Generation). "
        "This tool automatically monitors the knowledge_base folder for changes and updates the vector database. "
        "Use this to ground creative concepts in our company's identity, past projects, and brand values."
    )
    
    def __init__(self, knowledge_folder: str = "./knowledge_base"):
        self.knowledge_folder = Path(knowledge_folder)
        self.knowledge_folder.mkdir(exist_ok=True)
        
        # Initialize RAG manager
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.rag_manager = RAGManager(gemini_api_key=gemini_api_key)
        
        # Start file monitoring
        self.observer = None
        self._start_file_monitoring()
        
        # Perform initial scan
        self._initial_scan()

    def _start_file_monitoring(self):
        """Start monitoring the knowledge base folder for changes"""
        if not HAS_RAG_DEPS:
            print("Warning: File monitoring disabled - RAG dependencies not available")
            return
            
        try:
            from watchdog.observers import Observer
            
            self.observer = Observer()
            event_handler = FileChangeHandler(self.rag_manager)
            self.observer.schedule(
                event_handler, 
                str(self.knowledge_folder), 
                recursive=True
            )
            self.observer.start()
            print(f"Started file monitoring for: {self.knowledge_folder}")
            
        except ImportError:
            print("Warning: Watchdog not available - file monitoring disabled")
        except Exception as e:
            print(f"Warning: Could not start file monitoring: {e}")
    
    def _initial_scan(self):
        """Perform initial scan of knowledge base folder"""
        try:
            allowed_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.yaml', '.yml'}
            # Ignore README files as they are documentation, not content to be processed
            ignored_filenames = {'readme.md', 'readme.txt'}
            
            for file_path in self.knowledge_folder.rglob('*'):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in allowed_extensions and 
                    file_path.name.lower() not in ignored_filenames):
                    self.rag_manager.update_file_if_changed(str(file_path))
                    
        except Exception as e:
            print(f"Error during initial knowledge base scan: {e}")

    def _run(self, query: str) -> str:
        """
        Search the company knowledge base using RAG.
        """
        try:
            # Input validation
            if not query or not query.strip():
                return "Error: Query cannot be empty."
            
            # Limit query length
            max_query_length = 500
            if len(query) > max_query_length:
                return f"Error: Query too long (max {max_query_length} characters)."
            
            if not HAS_RAG_DEPS:
                return self._fallback_search(query.strip())
            
            # Query RAG system
            results = self.rag_manager.query(query.strip(), n_results=5)
            
            if not results:
                return self._fallback_search(query.strip())
            
            # Format results
            response = f"Knowledge Base Search Results for: '{query.strip()}'\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"Result {i} (from {Path(result['source']).name}):\n"
                response += f"{result['content']}\n"
                response += f"Relevance: {1 - result['distance']:.3f}\n\n"
            
            return response
                
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return self._fallback_search(query.strip())
    
    def _fallback_search(self, query: str) -> str:
        """Fallback search when RAG is not available"""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['past', 'project', 'success', 'case', 'study']):
            return (
                "Past Project Examples (Fallback):\n"
                "• 'Future Forward Summit' - A major tech client event featuring interactive AI art installations, holographic displays, and VR networking spaces\n"
                "• 'Green Horizon Gala' - Environmental NGO event that was fully carbon-neutral with sustainable materials and zero-waste catering\n"
                "• 'Innovation Nexus Conference' - B2B tech conference with AI-powered matchmaking and real-time collaboration tools\n"
                "Our brand ethos: 'Meaningful Moments, Measurable Impact'\n\n"
                "Note: This is fallback data. For full knowledge base access, ensure RAG dependencies are installed and knowledge_base folder contains relevant files."
            )
        elif any(keyword in query_lower for keyword in ['brand', 'value', 'ethos', 'identity']):
            return (
                "Company Brand Values (Fallback):\n"
                "• Core Ethos: 'Meaningful Moments, Measurable Impact'\n"
                "• Focus: Immersive, technology-driven brand experiences\n"
                "• Specialization: Corporate events, conferences, and brand activations\n"
                "• Differentiator: Integration of cutting-edge technology with human-centered design\n"
                "• Commitment: Sustainable and socially responsible event practices\n\n"
                "Note: This is fallback data. For full knowledge base access, ensure RAG dependencies are installed and knowledge_base folder contains relevant files."
            )
        elif any(keyword in query_lower for keyword in ['technology', 'tech', 'innovation', 'digital']):
            return (
                "Technology Capabilities (Fallback):\n"
                "• AI-powered event personalization and matchmaking\n"
                "• Interactive installations and digital art\n"
                "• VR/AR experiences and immersive environments\n"
                "• Real-time analytics and engagement tracking\n"
                "• Sustainable tech solutions and carbon footprint monitoring\n\n"
                "Note: This is fallback data. For full knowledge base access, ensure RAG dependencies are installed and knowledge_base folder contains relevant files."
            )
        else:
            return (
                "Our company excels at creating immersive, technology-driven brand experiences. "
                "Past successes include the 'Future Forward Summit' for a major tech client, "
                "which featured interactive AI art installations, and the 'Green Horizon Gala' "
                "for an environmental NGO, which was a fully carbon-neutral event. Our brand "
                "ethos is 'Meaningful Moments, Measurable Impact'.\n\n"
                "Note: This is fallback data. For full knowledge base access, ensure RAG dependencies are installed and knowledge_base folder contains relevant files."
            )
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'observer') and self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=5.0)  # Add timeout to prevent hanging
            except Exception as e:
                print(f"Warning: Error stopping file observer: {e}")

    def __del__(self):
        """Cleanup file monitoring when tool is destroyed"""
        self.cleanup()

