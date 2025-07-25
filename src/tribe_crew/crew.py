from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Import your custom tools
from tools import PerplexityTool, FileReadTool, CompanyKnowledgeBaseTool

@CrewBase
class EventPitchCrew:
    """A class to manage the agents and tasks for creating an event pitch."""
    agents_config = 'agents.yaml'
    tasks_config = 'tasks.yaml'

    def __init__(self):
        # Instantiate your custom tools
        self.perplexity_tool = PerplexityTool()
        self.file_read_tool = FileReadTool()
        self.company_knowledge_tool = CompanyKnowledgeBaseTool()

    # --- Define Agents ---
    @agent
    def briefing_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['briefing_analyst'],
            tools=[self.file_read_tool],
            verbose=True
        )

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'],
            tools=[self.perplexity_tool],
            verbose=True
        )

    @agent
    def audience_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['audience_analyst'],
            verbose=True
        )

    @agent
    def debrief_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['debrief_synthesizer'],
            verbose=True
        )

    @agent
    def creative_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['creative_strategist'],
            tools=[self.company_knowledge_tool],
            verbose=True
        )

    @agent
    def concept_refiner(self) -> Agent:
        return Agent(
            config=self.agents_config['concept_refiner'],
            verbose=True
        )
    
    @agent
    def proposal_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['proposal_manager'],
            verbose=True
        )

    @agent
    def art_director(self) -> Agent:
        return Agent(
            config=self.agents_config['art_director'],
            verbose=True
        )

    @agent
    def copywriter(self) -> Agent:
        return Agent(
            config=self.agents_config['copywriter'],
            verbose=True
        )

    @agent
    def event_producer(self) -> Agent:
        return Agent(
            config=self.agents_config['event_producer'],
            verbose=True
        )

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
        """Creates the debrief and concepting crew"""
        return Crew(
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
                self.concept_refinement_task()
            ],
            process=Process.hierarchical,
            manager_llm=None, # You can specify a manager LLM here if needed
            verbose=2
        )

    @crew
    def proposal_development_crew(self) -> Crew:
        """Creates the proposal development crew"""
        return Crew(
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
            manager_llm=None,
            verbose=2
        )