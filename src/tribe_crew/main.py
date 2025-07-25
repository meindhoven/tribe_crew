#!/usr/bin/env python3
"""
Enhanced Main Orchestrator for Creative Event Organizer Crew
Provides user-friendly interface with error handling and progress tracking
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from .crew import create_enhanced_crew, EnvironmentValidator
except ImportError as e:
    logger.error(f"Failed to import enhanced crew: {e}")
    sys.exit(1)


class WorkflowOrchestrator:
    """Orchestrates the entire Creative Event Organizer workflow"""
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.crew = None
        self.results_dir = Path("./results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def initialize_crew(self) -> bool:
        """Initialize the enhanced crew with error handling"""
        try:
            logger.info("Initializing Enhanced Event Pitch Crew...")
            self.crew = create_enhanced_crew()
            
            # Check system health
            health = self.crew.get_health_status()
            logger.info(f"System health status: {health['status']}")
            
            if health['status'] == 'error':
                logger.error(f"Crew initialization failed: {health.get('error', 'Unknown error')}")
                return False
            
            if health['status'] == 'degraded':
                logger.warning("System is running in degraded mode - some features may not work")
            
            logger.info("Crew initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize crew: {e}")
            return False
    
    def save_results(self, results: Dict[str, Any], filename_prefix: str = "workflow_results"):
        """Save workflow results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return None
    
    def display_progress(self, phase: str, status: str, message: str = ""):
        """Display progress information"""
        print(f"\n{'='*60}")
        print(f"PHASE {phase}: {status.upper()}")
        if message:
            print(f"Message: {message}")
        print(f"{'='*60}\n")
    
    def run_separated_workflow(self) -> Dict[str, Any]:
        """Run the workflow with separated crews (allows human review between phases)"""
        logger.info("Starting separated workflow execution")
        all_results = {}
        
        try:
            # Phase A: Strategic Analysis
            self.display_progress("A", "Starting", "Strategic Analysis and Research")
            phase_a_start = time.time()
            
            phase_a_result = self.crew.run_phase_a()
            phase_a_duration = time.time() - phase_a_start
            
            all_results['phase_a'] = phase_a_result
            all_results['phase_a']['duration_seconds'] = phase_a_duration
            
            if phase_a_result['status'] == 'completed':
                self.display_progress("A", "Completed", f"Duration: {phase_a_duration:.1f}s")
                print("Strategic Analysis Summary:")
                print("- Client briefing analyzed")
                print("- Market research completed")
                print("- Audience analysis finished")
                print("- Strategic debrief synthesized")
            else:
                self.display_progress("A", "Failed", phase_a_result.get('error', 'Unknown error'))
                return all_results
            
            # Phase B: Creative Concepting
            self.display_progress("B", "Starting", "Creative Concept Development")
            phase_b_start = time.time()
            
            phase_b_result = self.crew.run_phase_b(phase_a_result)
            phase_b_duration = time.time() - phase_b_start
            
            all_results['phase_b'] = phase_b_result
            all_results['phase_b']['duration_seconds'] = phase_b_duration
            
            if phase_b_result['status'] == 'completed':
                self.display_progress("B", "Completed", f"Duration: {phase_b_duration:.1f}s")
                print("Creative Concepting Summary:")
                print("- Three unique concepts developed")
                print("- Brand alignment validated")
                print("- Cultural relevance confirmed")
                print("- Concepts ready for human review")
                
                # Human review simulation
                print("\n" + "="*60)
                print("HUMAN CREATIVE TEAM REVIEW")
                print("="*60)
                print("The three concepts are now ready for your creative team to review.")
                print("Please review the concepts and select one for proposal development.")
                
                # Get user input for concept selection
                selected_concept = self.get_concept_selection()
                human_feedback = self.get_human_feedback()
                
                all_results['human_review'] = {
                    'selected_concept': selected_concept,
                    'feedback': human_feedback,
                    'timestamp': datetime.now().isoformat()
                }
                
            else:
                self.display_progress("B", "Failed", phase_b_result.get('error', 'Unknown error'))
                return all_results
            
            # Phase D: Proposal Development
            self.display_progress("D", "Starting", "Commercial Proposal Development")
            phase_d_start = time.time()
            
            phase_d_result = self.crew.run_phase_d(selected_concept, human_feedback)
            phase_d_duration = time.time() - phase_d_start
            
            all_results['phase_d'] = phase_d_result
            all_results['phase_d']['duration_seconds'] = phase_d_duration
            
            if phase_d_result['status'] == 'completed':
                self.display_progress("D", "Completed", f"Duration: {phase_d_duration:.1f}s")
                print("Proposal Development Summary:")
                print("- Experience design completed")
                print("- Visual identity developed")
                print("- Operational plan created")
                print("- Commercial proposal assembled")
                print("- Client-ready pitch document prepared")
            else:
                self.display_progress("D", "Failed", phase_d_result.get('error', 'Unknown error'))
            
            # Calculate total duration
            total_duration = phase_a_duration + phase_b_duration + phase_d_duration
            all_results['workflow_summary'] = {
                'total_duration_seconds': total_duration,
                'phase_count': 3,
                'status': 'completed' if phase_d_result['status'] == 'completed' else 'partial',
                'timestamp': datetime.now().isoformat()
            }
            
            self.display_progress("WORKFLOW", "Completed", f"Total Duration: {total_duration:.1f}s")
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            all_results['error'] = str(e)
            self.display_progress("WORKFLOW", "Failed", str(e))
        
        return all_results
    
    def run_integrated_workflow(self) -> Dict[str, Any]:
        """Run the complete workflow automatically (no human review pause)"""
        logger.info("Starting integrated workflow execution")
        
        try:
            self.display_progress("WORKFLOW", "Starting", "Automated End-to-End Execution")
            start_time = time.time()
            
            # Run full workflow with default selections
            results = self.crew.run_full_workflow(
                selected_concept="Concept 1 - Primary Recommendation",
                human_feedback="Approved with minor refinements for Dutch market"
            )
            
            duration = time.time() - start_time
            results['workflow_summary'] = {
                'total_duration_seconds': duration,
                'execution_mode': 'integrated',
                'timestamp': datetime.now().isoformat()
            }
            
            if all(phase.get('status') == 'completed' for phase in results.values() if isinstance(phase, dict) and 'status' in phase):
                self.display_progress("WORKFLOW", "Completed", f"Duration: {duration:.1f}s")
                print("Integrated Workflow Summary:")
                print("- All phases executed successfully")
                print("- Strategic analysis completed")
                print("- Creative concepts developed")
                print("- Commercial proposal ready")
            else:
                self.display_progress("WORKFLOW", "Partial", "Some phases failed")
            
            return results
            
        except Exception as e:
            logger.error(f"Integrated workflow failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def get_concept_selection(self) -> str:
        """Get concept selection from user"""
        print("\nAvailable concepts:")
        print("1. Concept 1 - Innovation-Focused Experience")
        print("2. Concept 2 - Culture & Community Driven")
        print("3. Concept 3 - Future-Forward Technology Showcase")
        
        while True:
            try:
                choice = input("\nSelect concept (1-3) or press Enter for default [1]: ").strip()
                if not choice:
                    return "Concept 1 - Innovation-Focused Experience"
                
                choice_num = int(choice)
                if 1 <= choice_num <= 3:
                    concepts = [
                        "Concept 1 - Innovation-Focused Experience",
                        "Concept 2 - Culture & Community Driven", 
                        "Concept 3 - Future-Forward Technology Showcase"
                    ]
                    return concepts[choice_num - 1]
                else:
                    print("Please enter 1, 2, or 3")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                return "Concept 1 - Innovation-Focused Experience"
    
    def get_human_feedback(self) -> str:
        """Get human feedback from user"""
        print("\nPlease provide feedback for the selected concept:")
        print("(Press Enter for default feedback or type your own)")
        
        try:
            feedback = input("Feedback: ").strip()
            if not feedback:
                return "Approved - proceed with proposal development with focus on Dutch market preferences"
            return feedback
        except KeyboardInterrupt:
            return "Approved - proceed with proposal development"
    
    def cleanup(self):
        """Cleanup resources"""
        if self.crew:
            self.crew.cleanup()


def display_banner():
    """Display application banner"""
    print("\n" + "="*80)
    print("🎭 ENHANCED CREATIVE EVENT ORGANIZER")
    print("   AI-Powered Pitch Development for Dutch Market")
    print("="*80)


def check_environment():
    """Check environment and display status"""
    print("\n📋 Environment Check:")
    print("-" * 40)
    
    if EnvironmentValidator.validate_environment():
        print("✅ Environment validation: PASSED")
    else:
        print("❌ Environment validation: FAILED")
        print("   Some features may not work properly")
    
    api_status = EnvironmentValidator.test_api_connectivity()
    for service, status in api_status.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.title()} API: {'Connected' if status else 'Failed'}")


def get_execution_mode() -> str:
    """Get execution mode from user"""
    print("\n🚀 Execution Mode Selection:")
    print("-" * 40)
    print("1. Separated Crews (Recommended)")
    print("   - Allows human review between phases")
    print("   - Interactive concept selection")
    print("   - Full control over process")
    print("\n2. Integrated Crew")
    print("   - Fully automated execution")
    print("   - No human intervention")
    print("   - Faster completion")
    
    while True:
        try:
            choice = input("\nSelect mode (1-2) or press Enter for default [1]: ").strip()
            if not choice or choice == "1":
                return "separated"
            elif choice == "2":
                return "integrated"
            else:
                print("Please enter 1 or 2")
        except KeyboardInterrupt:
            return "separated"


def run():
    """Entry point for uv run command"""
    return main()


def train():
    """Train the crew (placeholder for future implementation)"""
    print("🎓 Training functionality is not implemented yet.")
    return 0


def test():
    """Test the crew (placeholder for future implementation)"""
    print("🧪 Testing functionality is not implemented yet.")
    return 0


def replay():
    """Replay the crew (placeholder for future implementation)"""
    print("🔄 Replay functionality is not implemented yet.")
    return 0


def main():
    """Main execution function"""
    display_banner()
    check_environment()
    
    # Get execution mode
    mode = get_execution_mode()
    
    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator()
    
    try:
        # Initialize crew
        if not orchestrator.initialize_crew():
            print("\n❌ Failed to initialize crew. Please check your configuration.")
            return 1
        
        # Execute workflow based on mode
        if mode == "separated":
            print("\n🎬 Starting Separated Crews Workflow...")
            results = orchestrator.run_separated_workflow()
        else:
            print("\n🤖 Starting Integrated Crew Workflow...")
            results = orchestrator.run_integrated_workflow()
        
        # Save results
        results_file = orchestrator.save_results(results, f"workflow_{mode}")
        
        # Display final summary
        print("\n" + "="*80)
        print("📊 WORKFLOW EXECUTION SUMMARY")
        print("="*80)
        
        if 'workflow_summary' in results:
            summary = results['workflow_summary']
            duration = summary.get('total_duration_seconds', 0)
            print(f"⏱️  Total Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print(f"📁 Results saved to: {results_file}")
            print(f"🎯 Execution mode: {mode}")
            
            if summary.get('status') == 'completed':
                print("✅ Status: COMPLETED SUCCESSFULLY")
                print("\n🎉 Your creative event pitch is ready for client presentation!")
            else:
                print("⚠️  Status: PARTIALLY COMPLETED")
                print("   Check the results file for details on any issues.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        orchestrator.cleanup()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

