#!/usr/bin/env python
# main.py
# This is the main execution script for the Event Pitch Crew.

from crew import EventPitchCrew
import json
import os
from datetime import datetime

class EventPitchOrchestrator:
    """Orchestrates the event pitch development process with proper handover management"""
    
    def __init__(self):
        self.event_crew_manager = EventPitchCrew()
        self.handover_data = {}
        self.results_dir = "results"
        self.ensure_results_directory()
    
    def ensure_results_directory(self):
        """Create results directory if it doesn't exist"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
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
        
        # Phase 1: Debrief and Concepting
        print("\n🚀 Phase 1: Debrief and Concepting 🚀")
        briefing_doc_path = input("Enter the path to the client briefing document: ")
        client_name = input("Enter the client's name: ")

        inputs_crew1 = {
            'briefing_doc_path': briefing_doc_path,
            'client_name': client_name
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
        
        briefing_doc_path = input("Enter the path to the client briefing document: ")
        client_name = input("Enter the client's name: ")
        selected_concept = input("Which concept should be prioritized? (optional - leave blank for AI decision): ")
        human_feedback = input("Any initial feedback or requirements? (optional): ")

        inputs = {
            'briefing_doc_path': briefing_doc_path,
            'client_name': client_name,
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

