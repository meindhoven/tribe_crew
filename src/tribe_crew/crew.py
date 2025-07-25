from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import LongTermMemory, ShortTermMemory
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(override=True)

# Import your custom tools
from .tools.tools import PerplexityTool, FileReadTool, FolderReadTool, CompanyKnowledgeBaseTool, RAGManager

@CrewBase
class EventPitchCrew:
    """A class to manage the agents and tasks for creating an event pitch with RAG memory."""
    agents_config = 'agents.yaml'
    tasks_config = 'tasks.yaml'

    def __init__(self):
        # Instantiate your custom tools
        self.perplexity_tool = PerplexityTool()
        self.file_read_tool = FileReadTool()
        self.folder_read_tool = FolderReadTool(default_folder="./input_files")  # Points to input_files folder
        self.company_knowledge_tool = CompanyKnowledgeBaseTool(knowledge_folder="./knowledge_base")  # Points to knowledge_base folder
        
        # Initialize RAG manager for crew-wide memory
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.rag_manager = RAGManager(storage_path="./rag_storage", gemini_api_key=gemini_api_key)
        
        # Setup memory systems
        self._setup_memory()

    def _setup_memory(self):
        """Setup short-term and long-term memory with RAG"""
        try:
            # Short-term memory for current session
            self.short_term_memory = ShortTermMemory()
            
            # Long-term memory with SQLite storage and Gemini embeddings
            self.long_term_memory = LongTermMemory(
                storage=self.rag_manager,
                embedder={
                    "provider": "google",
                    "config": {
                        "model": "models/embedding-001",
                        "api_key": os.getenv("GEMINI_API_KEY")
                    }
                }
            )
        except Exception as e:
            print(f"Warning: Could not initialize advanced memory systems: {e}")
            print("Falling back to basic memory configuration.")
            self.short_term_memory = None
            self.long_term_memory = None

    def _safe_get_agent_config(self, agent_name: str):
        """Safely get agent configuration with error handling"""
        try:
            return self.agents_config[agent_name]
        except KeyError:
            raise ValueError(f"Agent '{agent_name}' not found in agents.yaml configuration")
        except Exception as e:
            raise ValueError(f"Error loading agent '{agent_name}' configuration: {e}")

    # --- Define Agents ---
    @agent
    def project_director(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('project_director'),
            verbose=True
        )
        
        # Add memory if available
        if self.long_term_memory:
            agent_config.memory = self.long_term_memory
            
        return agent_config

    @agent
    def briefing_analyst(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('briefing_analyst'),
            tools=[self.folder_read_tool, self.file_read_tool],  # Added FolderReadTool for scanning input_files
            verbose=True
        )
        
        # Add memory if available
        if self.short_term_memory:
            agent_config.memory = self.short_term_memory
            
        return agent_config

    @agent
    def market_researcher(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('market_researcher'),
            tools=[self.perplexity_tool],  # Now uses sonar-deep-research model
            verbose=True
        )
        
        # Add memory if available
        if self.short_term_memory:
            agent_config.memory = self.short_term_memory
            
        return agent_config

    @agent
    def audience_analyst(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('audience_analyst'),
            verbose=True
        )
        
        # Add memory if available
        if self.short_term_memory:
            agent_config.memory = self.short_term_memory
            
        return agent_config

    @agent
    def debrief_synthesizer(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('debrief_synthesizer'),
            verbose=True
        )
        
        # Add memory if available
        if self.long_term_memory:
            agent_config.memory = self.long_term_memory
            
        return agent_config

    @agent
    def creative_strategist(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('creative_strategist'),
            tools=[self.company_knowledge_tool],  # Now uses RAG-enabled knowledge base tool
            verbose=True
        )
        
        # Add long-term memory for storing creative insights
        if self.long_term_memory:
            agent_config.memory = self.long_term_memory
            
        return agent_config

    @agent
    def concept_refiner(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('concept_refiner'),
            verbose=True
        )
        
        # Add memory if available
        if self.short_term_memory:
            agent_config.memory = self.short_term_memory
            
        return agent_config
    
    @agent
    def proposal_manager(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('proposal_manager'),
            verbose=True
        )
        
        # Add memory if available
        if self.long_term_memory:
            agent_config.memory = self.long_term_memory
            
        return agent_config

    @agent
    def art_director(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('art_director'),
            verbose=True
        )
        
        # Add memory if available
        if self.short_term_memory:
            agent_config.memory = self.short_term_memory
            
        return agent_config

    @agent
    def copywriter(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('copywriter'),
            verbose=True
        )
        
        # Add memory if available
        if self.short_term_memory:
            agent_config.memory = self.short_term_memory
            
        return agent_config

    @agent
    def event_producer(self) -> Agent:
        agent_config = Agent(
            config=self._safe_get_agent_config('event_producer'),
            verbose=True
        )
        
        # Add memory if available
        if self.short_term_memory:
            agent_config.memory = self.short_term_memory
            
        return agent_config

    # --- Define Tasks ---
    @task
    def brief_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['brief_analysis_task'],
            agent=self.briefing_analyst()
        )

    @task
    def client_and_competitor_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['client_and_competitor_research_task'],
            agent=self.market_researcher()
        )

    @task
    def audience_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['audience_analysis_task'],
            agent=self.audience_analyst()
        )
    
    @task
    def debrief_synthesis_task(self) -> Task:
        return Task(
            config=self.tasks_config['debrief_synthesis_task'],
            agent=self.debrief_synthesizer()
        )

    @task
    def creative_concepting_task(self) -> Task:
        return Task(
            config=self.tasks_config['creative_concepting_task'],
            agent=self.creative_strategist()
        )

    @task
    def concept_refinement_task(self) -> Task:
        return Task(
            config=self.tasks_config['concept_refinement_task'],
            agent=self.concept_refiner()
        )

    @task
    def concept_handover_task(self) -> Task:
        return Task(
            config=self.tasks_config['concept_handover_task'],
            agent=self.debrief_synthesizer()
        )

    # --- Proposal Development Tasks ---
    @task
    def visual_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['visual_development_task'],
            agent=self.art_director()
        )

    @task
    def copywriting_task(self) -> Task:
        return Task(
            config=self.tasks_config['copywriting_task'],
            agent=self.copywriter()
        )
    
    @task
    def production_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['production_planning_task'],
            agent=self.event_producer()
        )

    @task
    def final_pitch_assembly_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_pitch_assembly_task'],
            agent=self.proposal_manager()
        )

    # --- Define Crews ---
    @crew
    def debrief_and_concept_crew(self) -> Crew:
        """Creates the debrief and concepting crew with proper manager and memory"""
        crew_config = Crew(
            agents=[
                self.briefing_analyst(),
                self.market_researcher(),
                self.audience_analyst(),
                self.debrief_synthesizer(),
                self.creative_strategist(),
                self.concept_refiner()
            ],
            tasks=[
                self.brief_analysis_task(),
                self.client_and_competitor_research_task(),
                self.audience_analysis_task(),
                self.debrief_synthesis_task(),
                self.creative_concepting_task(),
                self.concept_refinement_task(),
                self.concept_handover_task()
            ],
            process=Process.hierarchical,
            manager_agent=self.project_director(),
            verbose=2
        )
        
        # Add memory systems if available
        if self.short_term_memory:
            crew_config.short_term_memory = self.short_term_memory
        if self.long_term_memory:
            crew_config.long_term_memory = self.long_term_memory
            
        return crew_config

    @crew
    def proposal_development_crew(self) -> Crew:
        """Creates the proposal development crew with proper manager and memory"""
        crew_config = Crew(
            agents=[
                self.proposal_manager(),
                self.art_director(),
                self.copywriter(),
                self.event_producer()
            ],
            tasks=[
                self.visual_development_task(),
                self.copywriting_task(),
                self.production_planning_task(),
                self.final_pitch_assembly_task()
            ],
            process=Process.hierarchical,
            manager_agent=self.project_director(),
            verbose=2
        )
        
        # Add memory systems if available
        if self.short_term_memory:
            crew_config.short_term_memory = self.short_term_memory
        if self.long_term_memory:
            crew_config.long_term_memory = self.long_term_memory
            
        return crew_config

    @crew
    def integrated_event_pitch_crew(self) -> Crew:
        """Creates an integrated crew that handles the entire process from debrief to final pitch with memory"""
        crew_config = Crew(
            agents=[
                self.briefing_analyst(),
                self.market_researcher(),
                self.audience_analyst(),
                self.debrief_synthesizer(),
                self.creative_strategist(),
                self.concept_refiner(),
                self.proposal_manager(),
                self.art_director(),
                self.copywriter(),
                self.event_producer()
            ],
            tasks=[
                self.brief_analysis_task(),
                self.client_and_competitor_research_task(),
                self.audience_analysis_task(),
                self.debrief_synthesis_task(),
                self.creative_concepting_task(),
                self.concept_refinement_task(),
                self.concept_handover_task(),
                self.visual_development_task(),
                self.copywriting_task(),
                self.production_planning_task(),
                self.final_pitch_assembly_task()
            ],
            process=Process.hierarchical,
            manager_agent=self.project_director(),
            verbose=2
        )
        
        # Add memory systems if available
        if self.short_term_memory:
            crew_config.short_term_memory = self.short_term_memory
        if self.long_term_memory:
            crew_config.long_term_memory = self.long_term_memory
            
        return crew_config