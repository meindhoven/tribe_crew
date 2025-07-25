# Tribe Crew: Enhanced Event Pitch Development System

An AI-powered event pitch development system built with CrewAI, featuring advanced RAG (Retrieval Augmented Generation) capabilities, intelligent file monitoring, and folder-based workflow management.

## 🚀 Recent Enhancements

### 1. Folder-Based Input System
- **Input Files Folder**: The briefing analyst now scans the `input_files/` folder for all briefing documents
- **Multiple File Support**: Process multiple briefing documents simultaneously
- **Auto-Detection**: Automatically detects and processes new files

### 2. Enhanced Market Research
- **Sonar Deep Research**: Market researcher now uses Perplexity's `sonar-deep-research` model for comprehensive research
- **Better Quality**: Improved research depth with longer context and better sourcing
- **Citations**: Enhanced response quality with proper citations and references

### 3. RAG-Enabled Knowledge Base
- **Smart Knowledge Base**: Creative strategist uses RAG-powered company knowledge search
- **File Change Detection**: Only processes changed files to maintain efficiency
- **Vector Embeddings**: Uses Google Gemini embeddings for semantic search
- **Real-time Monitoring**: Automatically monitors `knowledge_base/` folder for changes

### 4. Advanced Memory Systems
- **Short-term Memory**: Session-based memory for current project context
- **Long-term Memory**: Persistent RAG storage using SQLite and ChromaDB
- **Gemini Embeddings**: Uses Google's embedding model for high-quality vector representations
- **Intelligent Retrieval**: Context-aware memory retrieval for better agent performance

### 5. File Change Detection
- **Hash-based Tracking**: SHA-256 file hashing to detect content changes
- **Incremental Updates**: Only re-processes files that have actually changed
- **Real-time Monitoring**: File system watching for immediate updates
- **Efficient Storage**: Avoids redundant processing and storage

## 📁 Folder Structure

```
workspace/
├── input_files/          # Place client briefing documents here
│   ├── README.md         # Instructions for using input files
│   └── sample_client_brief.md  # Example briefing document
├── knowledge_base/       # Company knowledge for RAG system
│   ├── README.md         # Instructions for knowledge base
│   └── company_brand_values.md  # Example company knowledge
├── rag_storage/          # RAG vector database and metadata (auto-created)
│   ├── chroma_db/        # ChromaDB vector storage
│   └── rag_metadata.db   # SQLite metadata storage
├── results/              # Output folder for generated pitches
├── src/tribe_crew/       # Main application code
│   ├── crew.py           # Enhanced crew with RAG memory
│   ├── main.py           # Updated orchestrator
│   ├── tools/            # Enhanced tools with RAG
│   └── config/           # Agent and task configurations
└── .env                  # Environment variables (create from .env.example)
```

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
# Install the enhanced dependencies
pip install -e .
```

### 2. Environment Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required API keys:
- **PERPLEXITY_API_KEY**: For enhanced market research
- **GEMINI_API_KEY**: For RAG embeddings and memory

### 3. Prepare Your Folders

```bash
# Input files folder (briefing documents)
mkdir -p input_files
# Add your client briefing documents here

# Knowledge base folder (company knowledge)
mkdir -p knowledge_base
# Add your company knowledge files here
```

## 🎯 How to Use

### 1. Prepare Your Input Files
Place client briefing documents in the `input_files/` folder:
- `client_brief.txt` - Main briefing document
- `requirements.md` - Additional requirements
- `budget_info.yaml` - Budget constraints
- `audience_data.json` - Target audience information

### 2. Set Up Your Knowledge Base
Add company knowledge to the `knowledge_base/` folder:
- Past project case studies
- Brand guidelines and values
- Technology capabilities
- Client testimonials
- Company values and mission

### 3. Run the System

```bash
# Navigate to the project directory
cd src/tribe_crew

# Run the enhanced crew system
python main.py
```

Choose your execution mode:
1. **Separated Crews**: Review concepts between phases
2. **Integrated Crew**: End-to-end automated process

## 🔧 Key Features

### Briefing Analyst Enhancements
- **Folder Scanning**: Automatically scans `input_files/` folder
- **Multiple File Processing**: Handles multiple briefing documents
- **Smart Analysis**: Comprehensive analysis across all input documents

### Market Researcher Improvements
- **Deep Research Model**: Uses `sonar-deep-research` for enhanced quality
- **Extended Context**: 4000 token responses for comprehensive research
- **Better Citations**: Improved sourcing and reference quality

### Creative Strategist RAG Integration
- **Semantic Search**: Natural language querying of company knowledge
- **Real-time Updates**: Automatic processing of new/changed knowledge files
- **Context-Aware Results**: Relevant company information for concept development
- **File Change Detection**: Efficient updates only when content changes

### Memory System Features
- **Persistent Memory**: Long-term storage across sessions
- **Vector Search**: Semantic similarity search in memory
- **SQLite Backend**: Reliable, file-based storage
- **Automatic Embeddings**: Gemini-powered vector generation

## 🎛️ Configuration

### Memory Settings
The system automatically configures:
- **Short-term Memory**: Current session context
- **Long-term Memory**: Persistent RAG storage
- **Vector Database**: ChromaDB for embeddings
- **Metadata Storage**: SQLite for file tracking

### File Monitoring
Automatic monitoring includes:
- **Supported Formats**: .txt, .md, .pdf, .doc, .docx, .json, .yaml, .yml
- **Change Detection**: SHA-256 hash comparison
- **Real-time Updates**: File system event monitoring
- **Incremental Processing**: Only changed files are re-processed

## 🚨 Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure PERPLEXITY_API_KEY and GEMINI_API_KEY are set
2. **Empty Folders**: Add files to `input_files/` and `knowledge_base/` folders
3. **Permission Errors**: Check file permissions for created directories
4. **Memory Errors**: Ensure sufficient disk space for vector database

### Fallback Mode
If RAG dependencies fail:
- System falls back to basic knowledge base responses
- File reading still works without RAG features
- Basic memory functionality is maintained

### Debug Mode
Enable verbose logging:
```python
# In crew.py, set verbose=True for all agents
verbose=True
```

## 📊 Performance Optimization

### RAG Efficiency
- **File Change Detection**: Only re-processes modified files
- **Vector Caching**: Embeddings are cached in ChromaDB
- **Batch Processing**: Multiple files processed efficiently
- **Memory Management**: Optimized for large knowledge bases

### Resource Usage
- **SQLite Storage**: Lightweight, serverless database
- **ChromaDB**: Efficient vector storage and retrieval
- **File Monitoring**: Low-overhead file system watching
- **Gemini Embeddings**: High-quality, cost-effective embeddings

## 🔮 Future Enhancements

Planned improvements:
- **Multi-modal RAG**: Support for images and videos in knowledge base
- **Advanced Analytics**: Detailed memory usage and search analytics
- **Cloud Storage**: Integration with cloud storage providers
- **API Interface**: REST API for external integrations
- **Advanced Monitoring**: Health checks and performance metrics

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the folder README files
3. Create an issue in the repository
4. Contact the development team

---

## 🎉 Getting Started Checklist

- [ ] Install dependencies (`pip install -e .`)
- [ ] Copy `.env.example` to `.env` and add API keys
- [ ] Add client briefing documents to `input_files/`
- [ ] Add company knowledge to `knowledge_base/`
- [ ] Run the system (`python src/tribe_crew/main.py`)
- [ ] Choose execution mode and follow prompts
- [ ] Review generated results in `results/` folder

The enhanced system is now ready to deliver more intelligent, context-aware event pitch development with advanced RAG capabilities!
