# Knowledge Base Folder

This folder contains your company's internal knowledge that will be used by the creative strategist to ground concepts in your company's identity and past successes.

## RAG (Retrieval Augmented Generation) Features
- **Automatic Monitoring**: The system monitors this folder for changes and updates the vector database automatically
- **File Change Detection**: Only changed files are re-processed to maintain efficiency  
- **Intelligent Search**: Uses Gemini embeddings for semantic search of your knowledge base
- **SQLite Storage**: Long-term memory is stored in SQLite with vector embeddings

## Supported File Types
- `.txt` - Plain text files
- `.md` - Markdown files  
- `.pdf` - PDF documents
- `.doc/.docx` - Microsoft Word documents
- `.json` - JSON files
- `.yaml/.yml` - YAML files

## What to Include
Add files containing:
- **Past Project Case Studies** - Successful events you've organized
- **Brand Guidelines** - Your company's brand values and identity
- **Technology Capabilities** - Your technical offerings and innovations
- **Client Testimonials** - Success stories and feedback
- **Company Values** - Mission, vision, and core principles
- **Team Expertise** - Specialized skills and experience
- **Vendor Relationships** - Preferred partners and suppliers

## Example Files Structure
```
knowledge_base/
├── projects/
│   ├── tech_summit_2023.md
│   ├── green_gala_casestudy.txt
│   └── innovation_conference.pdf
├── brand/
│   ├── brand_guidelines.md
│   ├── company_values.txt
│   └── visual_identity.pdf
├── capabilities/
│   ├── technology_stack.md
│   ├── event_types.yaml
│   └── service_offerings.json
└── testimonials/
    ├── client_feedback.txt
    └── success_metrics.md
```

## How It Works
1. **Initial Scan**: When the system starts, it scans all files and creates vector embeddings
2. **File Monitoring**: The system watches for file changes in real-time
3. **Smart Updates**: Only changed files are re-processed and updated in the vector database
4. **Semantic Search**: The creative strategist can query this knowledge using natural language
5. **Context-Aware**: Results are ranked by relevance to the query

## Environment Setup
Make sure you have your `GEMINI_API_KEY` set in your environment variables for the embedding functionality to work properly.