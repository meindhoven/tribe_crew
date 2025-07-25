#!/usr/bin/env python3
"""
Test script to verify the enhanced Event Pitch Crew setup.
Run this script to check if all components are working correctly.
"""

import os
import sys
from pathlib import Path

def test_directory_structure():
    """Test that all required directories exist"""
    required_dirs = ['input_files', 'knowledge_base', 'rag_storage', 'results']
    print("🔍 Checking directory structure...")
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✅ {dir_name}/ exists")
        else:
            print(f"  ❌ {dir_name}/ missing")
            return False
    return True

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n🔍 Checking dependencies...")
    
    dependencies = [
        ('crewai', 'CrewAI'),
        ('requests', 'Requests'),
        ('watchdog', 'Watchdog'),
        ('pathlib', 'Pathlib'),
        ('sqlite3', 'SQLite3'),
        ('hashlib', 'Hashlib'),
        ('json', 'JSON'),
        ('datetime', 'Datetime')
    ]
    
    optional_deps = [
        ('chromadb', 'ChromaDB'),
        ('google.generativeai', 'Google Generative AI'),
        ('langchain', 'LangChain'),
        ('numpy', 'NumPy')
    ]
    
    # Test required dependencies
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - Required dependency missing")
            return False
    
    # Test optional dependencies (for RAG features)
    rag_available = True
    for module, name in optional_deps:
        try:
            __import__(module)
            print(f"  ✅ {name} (RAG feature)")
        except ImportError:
            print(f"  ⚠️  {name} - Optional RAG dependency missing")
            rag_available = False
    
    if not rag_available:
        print("  ℹ️  RAG features will run in fallback mode")
    
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔍 Checking environment variables...")
    
    required_env = {
        'PERPLEXITY_API_KEY': 'Market research (required)',
        'GEMINI_API_KEY': 'RAG embeddings (required for RAG features)'
    }
    
    optional_env = {
        'OPENAI_API_KEY': 'OpenAI models (optional)',
        'CREWAI_API_KEY': 'CrewAI advanced features (optional)'
    }
    
    all_good = True
    for key, description in required_env.items():
        if os.getenv(key):
            print(f"  ✅ {key} - {description}")
        else:
            print(f"  ❌ {key} - {description} - Missing!")
            all_good = False
    
    for key, description in optional_env.items():
        if os.getenv(key):
            print(f"  ✅ {key} - {description}")
        else:
            print(f"  ⚠️  {key} - {description} - Optional")
    
    return all_good

def test_file_examples():
    """Test that example files exist"""
    print("\n🔍 Checking example files...")
    
    example_files = [
        'input_files/README.md',
        'input_files/sample_client_brief.md',
        'knowledge_base/README.md',
        'knowledge_base/company_brand_values.md',
        '.env.example'
    ]
    
    for file_path in example_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Example file missing")
            return False
    
    return True

def test_tools_import():
    """Test that enhanced tools can be imported"""
    print("\n🔍 Testing tool imports...")
    
    try:
        sys.path.append('src')
        from tribe_crew.tools.tools import (
            PerplexityTool, 
            FileReadTool, 
            FolderReadTool, 
            CompanyKnowledgeBaseTool,
            RAGManager
        )
        print("  ✅ All enhanced tools imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Tool import failed: {e}")
        return False

def test_crew_import():
    """Test that enhanced crew can be imported"""
    print("\n🔍 Testing crew import...")
    
    try:
        sys.path.append('src')
        from tribe_crew.crew import EventPitchCrew
        print("  ✅ Enhanced EventPitchCrew imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Crew import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Event Pitch Crew Setup\n")
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Dependencies", test_dependencies),
        ("Environment Variables", test_environment),
        ("Example Files", test_file_examples),
        ("Tool Imports", test_tools_import),
        ("Crew Import", test_crew_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your enhanced Event Pitch Crew is ready to use.")
        print("\nNext steps:")
        print("1. Add your briefing documents to input_files/")
        print("2. Add your company knowledge to knowledge_base/")
        print("3. Run: python src/tribe_crew/main.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip install -e .")
        print("- Set up environment variables: cp .env.example .env")
        print("- Check file permissions and directory structure")

if __name__ == "__main__":
    main()