#!/usr/bin/env python
# main.py
# This is the main execution script for the Event Pitch Crew.

from crew import EventPitchCrew

# This is the main execution block
if __name__ == "__main__":
    print("## Welcome to the Creative Event Pitch Crew! ##")
    print("------------------------------------------------")
    
    # Define the inputs for the first crew
    briefing_doc_path = input("Enter the path to the client briefing document: ")
    client_name = input("Enter the client's name: ")

    inputs_crew1 = {
        'briefing_doc_path': briefing_doc_path,
        'client_name': client_name
    }

    # Instantiate the main class from crew.py
    event_crew_manager = EventPitchCrew()
    
    # Kick off the first crew
    print("\n🚀 Kicking off the Debrief and Concepting Crew... 🚀\n")
    debrief_crew = event_crew_manager.debrief_and_concept_crew()
    concept_results = debrief_crew.kickoff(inputs=inputs_crew1)

    print("\n\n✅ Debrief and Concepting Crew Finished! ✅")
    print("------------------------------------------------")
    print("Here are the generated concepts:\n")
    print(concept_results)
    print("------------------------------------------------\n")

    # --- HUMAN-IN-THE-LOOP ---
    print("🧑‍💻 Human Review Step 🧑‍💻")
    print("Please review the concepts above.")
    selected_concept = input("Which concept do you want to develop? (e.g., 'Concept 1'): ")
    human_feedback = input("Provide any specific feedback or adjustments: ")

    # Define the inputs for the second crew
    inputs_crew2 = {
        'selected_concept': selected_concept,
        'human_feedback': human_feedback
    }

    # Kick off the second crew
    print("\n🚀 Kicking off the Proposal Development Crew... 🚀\n")
    proposal_crew = event_crew_manager.proposal_development_crew()
    final_pitch = proposal_crew.kickoff(inputs=inputs_crew2)

    print("\n\n🎉 Final Pitch Document Ready! 🎉")
    print("------------------------------------------------")
    print(final_pitch)
    print("------------------------------------------------")

