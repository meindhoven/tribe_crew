#!/usr/bin/env python
# main.py
# This is the main execution script for the Event Pitch Crew with enhanced folder-based input and RAG support.

from .crew import EventPitchCrew
import json
import os
from datetime import datetime
from pathlib import Path

class EventPitchOrchestrator:
    """Orchestrates the event pitch development process with proper handover management and folder-based inputs"""
    
    def __init__(self):
        self.event_crew_manager = EventPitchCrew()
        self.results_dir = "results"
        self.input_dir = "input_files"
        self.knowledge_dir = "knowledge_base"
        self.ensure_directories()
        self._validate_environment()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [self.results_dir, self.input_dir, self.knowledge_dir, "rag_storage"]
        for directory in directories:
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    print(f"Created directory: {directory}")
                # Ensure directories are writable
                if not os.access(directory, os.W_OK):
                    print(f"Warning: Directory '{directory}' is not writable")
            except PermissionError:
                print(f"Error: Permission denied creating directory '{directory}'")
                raise
            except Exception as e:
                print(f"Error creating directory '{directory}': {e}")
                raise
    
    def check_input_files(self) -> bool:
        """Check if there are any files in the input_files directory"""
        input_path = Path(self.input_dir)
        allowed_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.yaml', '.yml'}
        
        for file_path in input_path.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                return True
        return False
    
    def list_input_files(self) -> list:
        """List all valid files in the input_files directory"""
        input_path = Path(self.input_dir)
        allowed_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.yaml', '.yml'}
        files = []
        
        for file_path in input_path.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                files.append(file_path.name)
        
        return files
    
    def check_knowledge_base(self) -> bool:
        """Check if there are any files in the knowledge_base directory"""
        knowledge_path = Path(self.knowledge_dir)
        allowed_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.yaml', '.yml'}
        
        for file_path in knowledge_path.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                return True
        return False
    
    def save_results(self, data, filename):
        """Save results to file for handover purposes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.results_dir, f"{timestamp}_{filename}")
        
        if isinstance(data, str):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def run_separated_crews(self):
        """Run the crews separately with proper handover"""
        print("## Welcome to the Creative Event Pitch Crew! ##")
        print("------------------------------------------------")
        
        # Check for input files
        if not self.check_input_files():
            print(f"\n⚠️  No briefing documents found in the '{self.input_dir}' folder!")
            print(f"Please place your client briefing documents in the '{self.input_dir}' folder.")
            print("Supported formats: .txt, .md, .pdf, .doc, .docx, .json, .yaml, .yml")
            
            choice = input("\nWould you like to continue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                print("Exiting. Please add briefing documents and try again.")
                return None
        else:
            files = self.list_input_files()
            print(f"\n📁 Found {len(files)} briefing document(s) in '{self.input_dir}':")
            for file in files:
                print(f"  • {file}")
        
        # Check knowledge base
        if not self.check_knowledge_base():
            print(f"\n📚 No files found in the '{self.knowledge_dir}' folder.")
            print("Consider adding company knowledge, past projects, and brand documents for better results.")
        else:
            print(f"\n📚 Knowledge base folder '{self.knowledge_dir}' contains company information.")
        
        # Phase 1: Debrief and Concepting
        print("\n🚀 Phase 1: Debrief and Concepting 🚀")
        client_name = input("Enter the client's name: ")

        inputs_crew1 = {
            'client_name': client_name,
            'input_folder': self.input_dir,
            'knowledge_folder': self.knowledge_dir
        }

        print("\n🚀 Kicking off the Debrief and Concepting Crew... 🚀\n")
        debrief_crew = self.event_crew_manager.debrief_and_concept_crew()
        concept_results = debrief_crew.kickoff(inputs=inputs_crew1)

        # Save the handover results
        handover_file = self.save_results(concept_results, "concept_handover.txt")
        print(f"\n📁 Handover results saved to: {handover_file}")

        print("\n\n✅ Debrief and Concepting Crew Finished! ✅")
        print("------------------------------------------------")
        print("Here are the generated concepts and handover package:\n")
        print(concept_results)
        print("------------------------------------------------\n")

        # Phase 2: Human Review and Selection
        print("🧑‍💻 Human Review Step 🧑‍💻")
        print("Please review the concepts above.")
        selected_concept = input("Which concept do you want to develop? (e.g., 'Concept 1'): ")
        human_feedback = input("Provide any specific feedback or adjustments: ")

        # Phase 3: Proposal Development
        print("\n🚀 Phase 2: Proposal Development 🚀")
        inputs_crew2 = {
            'selected_concept': selected_concept,
            'human_feedback': human_feedback,
            'handover_package': str(concept_results)  # Pass the handover data
        }

        print("\n🚀 Kicking off the Proposal Development Crew... 🚀\n")
        proposal_crew = self.event_crew_manager.proposal_development_crew()
        final_pitch = proposal_crew.kickoff(inputs=inputs_crew2)

        # Save the final results
        final_file = self.save_results(final_pitch, "final_pitch.txt")
        print(f"\n📁 Final pitch saved to: {final_file}")

        print("\n\n🎉 Final Pitch Document Ready! 🎉")
        print("------------------------------------------------")
        print(final_pitch)
        print("------------------------------------------------")

        return final_pitch
    
    def run_integrated_crew(self):
        """Run the integrated crew that handles the entire process"""
        print("## Welcome to the Integrated Event Pitch Crew! ##")
        print("------------------------------------------------")
        
        # Check for input files
        if not self.check_input_files():
            print(f"\n⚠️  No briefing documents found in the '{self.input_dir}' folder!")
            print(f"Please place your client briefing documents in the '{self.input_dir}' folder.")
            print("Supported formats: .txt, .md, .pdf, .doc, .docx, .json, .yaml, .yml")
            
            choice = input("\nWould you like to continue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                print("Exiting. Please add briefing documents and try again.")
                return None
        else:
            files = self.list_input_files()
            print(f"\n📁 Found {len(files)} briefing document(s) in '{self.input_dir}':")
            for file in files:
                print(f"  • {file}")
        
        # Check knowledge base
        if not self.check_knowledge_base():
            print(f"\n📚 No files found in the '{self.knowledge_dir}' folder.")
            print("Consider adding company knowledge, past projects, and brand documents for better results.")
        else:
            print(f"\n📚 Knowledge base folder '{self.knowledge_dir}' contains company information.")
        
        client_name = input("\nEnter the client's name: ")
        selected_concept = input("Which concept should be prioritized? (optional - leave blank for AI decision): ")
        human_feedback = input("Any initial feedback or requirements? (optional): ")

        inputs = {
            'client_name': client_name,
            'input_folder': self.input_dir,
            'knowledge_folder': self.knowledge_dir,
            'selected_concept': selected_concept or "Best concept based on strategic fit",
            'human_feedback': human_feedback or "Follow the strategic brief and ensure professional presentation"
        }

        print("\n🚀 Kicking off the Integrated Event Pitch Crew... 🚀\n")
        integrated_crew = self.event_crew_manager.integrated_event_pitch_crew()
        final_results = integrated_crew.kickoff(inputs=inputs)

        # Save the final results
        final_file = self.save_results(final_results, "integrated_pitch.txt")
        print(f"\n📁 Final results saved to: {final_file}")

        print("\n\n🎉 Complete Event Pitch Ready! 🎉")
        print("------------------------------------------------")
        print(final_results)
        print("------------------------------------------------")

        return final_results

    def _validate_environment(self):
        """Validate environment configuration and API keys"""
        required_keys = ['PERPLEXITY_API_KEY', 'GEMINI_API_KEY']
        missing_keys = []
        invalid_keys = []
        
        for key in required_keys:
            value = os.getenv(key)
            if not value:
                missing_keys.append(key)
            elif value == f"your_{key.lower()}_here" or len(value) < 10:
                invalid_keys.append(key)
        
        if missing_keys or invalid_keys:
            print("⚠️  Environment Configuration Issues:")
            if missing_keys:
                print(f"   Missing API keys: {', '.join(missing_keys)}")
            if invalid_keys:
                print(f"   Invalid API keys (still using template values): {', '.join(invalid_keys)}")
            print("\n🔧 To fix:")
            print("   1. Copy .env.example to .env: cp .env.example .env")
            print("   2. Edit .env file and add your actual API keys")
            print("   3. Get Perplexity key: https://www.perplexity.ai/settings/api")
            print("   4. Get Gemini key: https://makersuite.google.com/app/apikey")
            
            choice = input("\nContinue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                print("Exiting. Please set up your API keys and try again.")
                exit(1)

def main():
    """Main execution function with user choice"""
    orchestrator = EventPitchOrchestrator()
    
    print("Choose your execution mode:")
    print("1. Separated Crews (with human review between phases)")
    print("2. Integrated Crew (automated end-to-end process)")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        return orchestrator.run_separated_crews()
    elif choice == "2":
        return orchestrator.run_integrated_crew()
    else:
        print("Invalid choice. Defaulting to separated crews.")
        return orchestrator.run_separated_crews()

if __name__ == "__main__":
    main()

