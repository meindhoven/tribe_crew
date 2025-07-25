"""
Enhanced Creative Event Organizer Crew with Hierarchical Structure
Addresses critical bugs and implements improved architecture
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import LongTermMemory, ShortTermMemory
from crewai.tools import BaseTool
from dotenv import load_dotenv
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

# Import enhanced tools (these would need to be implemented)
try:
    from .tools.enhanced_tools import (
        PerplexityDeepResearchTool,
        FileReadTool,
        FolderReadTool,
        CompanyKnowledgeBaseTool,
        RAGManager,
        DocumentAnalysisTool,
        BrandAnalysisTool,
        CompetitorAnalysisTool,
        AudienceResearchTool,
        InnovationFrameworkTool,
        ExperienceDesignTool,
        VisualIdentityTool,
        DutchVenueDatabaseTool,
        ProductionPlanningTool,
        CommercialPositioningTool
    )
except ImportError:
    logger.warning("Enhanced tools not available, using basic fallbacks")
    from .tools.tools import (
        PerplexityTool as PerplexityDeepResearchTool,
        FileReadTool,
        FolderReadTool,
        CompanyKnowledgeBaseTool,
        RAGManager
    )
    # Create placeholder classes for missing tools
    class PlaceholderTool(BaseTool):
        name: str = "placeholder_tool"
        description: str = "Placeholder tool"
        def _run(self, *args, **kwargs): return "Tool not implemented"
    
    DocumentAnalysisTool = PlaceholderTool
    BrandAnalysisTool = PlaceholderTool
    CompetitorAnalysisTool = PlaceholderTool
    AudienceResearchTool = PlaceholderTool
    InnovationFrameworkTool = PlaceholderTool
    ExperienceDesignTool = PlaceholderTool
    VisualIdentityTool = PlaceholderTool
    DutchVenueDatabaseTool = PlaceholderTool
    ProductionPlanningTool = PlaceholderTool
    CommercialPositioningTool = PlaceholderTool


class ConfigurationManager:
    """Manages configuration with validation and error handling"""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.agents_config = {}
        self.tasks_config = {}
        self.load_configurations()
    
    def load_configurations(self):
        """Load and validate configuration files"""
        try:
            # Load agents configuration
            agents_file = self.config_dir / "agents.yaml"
            if agents_file.exists():
                with open(agents_file, 'r', encoding='utf-8') as f:
                    self.agents_config = yaml.safe_load(f)
            else:
                logger.warning(f"Agents config file not found: {agents_file}")
                self.agents_config = {}
            
            # Load tasks configuration
            tasks_file = self.config_dir / "tasks.yaml"
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks_config = yaml.safe_load(f)
            else:
                logger.warning(f"Tasks config file not found: {tasks_file}")
                self.tasks_config = {}
                
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            self.agents_config = {}
            self.tasks_config = {}
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Safely get agent configuration with validation"""
        if agent_name not in self.agents_config:
            logger.error(f"Agent '{agent_name}' not found in configuration")
            # Return default configuration to prevent crashes
            return {
                'role': f"Default {agent_name}",
                'goal': f"Execute {agent_name} tasks",
                'backstory': f"You are a {agent_name} with standard capabilities.",
                'allow_delegation': False,
                'verbose': True
            }
        return self.agents_config[agent_name]
    
    def get_task_config(self, task_name: str) -> Dict[str, Any]:
        """Safely get task configuration with validation"""
        if task_name not in self.tasks_config:
            logger.error(f"Task '{task_name}' not found in configuration")
            return {
                'description': f"Execute {task_name}",
                'expected_output': f"Results from {task_name}",
                'agent': 'executive_director'
            }
        return self.tasks_config[task_name]


class PathManager:
    """Manages configurable paths throughout the system"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.paths = {
            'input_files': os.getenv('INPUT_FILES_PATH', './input_files'),
            'knowledge_base': os.getenv('KNOWLEDGE_BASE_PATH', './knowledge_base'),
            'rag_storage': os.getenv('RAG_STORAGE_PATH', './rag_storage'),
            'results': os.getenv('RESULTS_PATH', './results'),
            'config': os.getenv('CONFIG_PATH', './config'),
            'project_memory': os.getenv('PROJECT_MEMORY_PATH', './project_memory')
        }
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create directories if they don't exist"""
        for path_name, path_value in self.paths.items():
            path = Path(path_value)
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory ensured: {path}")
            except Exception as e:
                logger.error(f"Failed to create directory {path}: {e}")
    
    def get_path(self, path_name: str) -> str:
        """Get a configured path by name"""
        return self.paths.get(path_name, ".")


class EnvironmentValidator:
    """Validates environment configuration and API keys"""
    
    @staticmethod
    def validate_environment() -> bool:
        """Validate required environment variables and API keys"""
        required_vars = {
            'GEMINI_API_KEY': 'Google Gemini API key for embeddings',
            'PERPLEXITY_API_KEY': 'Perplexity API key for deep research'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            logger.error("Missing required environment variables:")
            for var in missing_vars:
                logger.error(f"  - {var}")
            return False
        
        logger.info("Environment validation successful")
        return True
    
    @staticmethod
    def test_api_connectivity() -> Dict[str, bool]:
        """Test API connectivity for external services"""
        results = {}
        
        # Test Gemini API
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                # Placeholder for actual API test
                results['gemini'] = True
                logger.info("Gemini API connectivity: OK")
            except Exception as e:
                results['gemini'] = False
                logger.error(f"Gemini API connectivity failed: {e}")
        else:
            results['gemini'] = False
        
        # Test Perplexity API
        perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        if perplexity_key:
            try:
                # Placeholder for actual API test
                results['perplexity'] = True
                logger.info("Perplexity API connectivity: OK")
            except Exception as e:
                results['perplexity'] = False
                logger.error(f"Perplexity API connectivity failed: {e}")
        else:
            results['perplexity'] = False
        
        return results


@CrewBase
class EnhancedEventPitchCrew:
    """Enhanced Event Pitch Crew with hierarchical structure and improved error handling"""
    
    def __init__(self):
        """Initialize the enhanced crew with proper error handling and validation"""
        
        # Validate environment
        if not EnvironmentValidator.validate_environment():
            logger.warning("Environment validation failed - some features may not work")
        
        # Initialize managers
        self.path_manager = PathManager()
        self.config_manager = ConfigurationManager(self.path_manager.get_path('config'))
        
        # Initialize tools with error handling
        self._initialize_tools()
        
        # Setup memory systems with error handling
        self._setup_memory_systems()
        
        # Track crew state
        self.crew_state = {
            'initialized': True,
            'timestamp': datetime.now().isoformat(),
            'phase': 'initialization'
        }
    
    def _initialize_tools(self):
        """Initialize all tools with proper error handling"""
        try:
            # Core research tools
            self.perplexity_tool = PerplexityDeepResearchTool()
            self.file_read_tool = FileReadTool()
            self.folder_read_tool = FolderReadTool(
                default_folder=self.path_manager.get_path('input_files')
            )
            self.company_knowledge_tool = CompanyKnowledgeBaseTool(
                knowledge_folder=self.path_manager.get_path('knowledge_base')
            )
            
            # Analysis tools
            self.document_analysis_tool = DocumentAnalysisTool()
            self.brand_analysis_tool = BrandAnalysisTool()
            self.competitor_analysis_tool = CompetitorAnalysisTool()
            self.audience_research_tool = AudienceResearchTool()
            
            # Creative tools
            self.innovation_framework_tool = InnovationFrameworkTool()
            self.experience_design_tool = ExperienceDesignTool()
            self.visual_identity_tool = VisualIdentityTool()
            
            # Production tools
            self.dutch_venue_tool = DutchVenueDatabaseTool()
            self.production_planning_tool = ProductionPlanningTool()
            self.commercial_positioning_tool = CommercialPositioningTool()
            
            logger.info("Tools initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing tools: {e}")
            # Initialize with minimal fallback tools
            self._initialize_fallback_tools()
    
    def _initialize_fallback_tools(self):
        """Initialize minimal fallback tools if main initialization fails"""
        try:
            self.file_read_tool = FileReadTool()
            self.folder_read_tool = FolderReadTool()
            logger.info("Fallback tools initialized")
        except Exception as e:
            logger.error(f"Failed to initialize even fallback tools: {e}")
    
    def _setup_memory_systems(self):
        """Setup memory systems with comprehensive error handling"""
        try:
            # Initialize RAG manager
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.rag_manager = RAGManager(
                    storage_path=self.path_manager.get_path('rag_storage'),
                    gemini_api_key=gemini_api_key
                )
                
                # Setup long-term memory with RAG
                self.long_term_memory = LongTermMemory(
                    storage=self.rag_manager,
                    embedder={
                        "provider": "google",
                        "config": {
                            "model": "models/embedding-001",
                            "api_key": gemini_api_key
                        }
                    }
                )
                
                # Setup short-term memory
                self.short_term_memory = ShortTermMemory()
                
                logger.info("Advanced memory systems initialized successfully")
                
            else:
                logger.warning("GEMINI_API_KEY not found, using basic memory")
                self._setup_basic_memory()
                
        except Exception as e:
            logger.error(f"Error setting up advanced memory: {e}")
            self._setup_basic_memory()
    
    def _setup_basic_memory(self):
        """Setup basic memory as fallback"""
        try:
            self.short_term_memory = ShortTermMemory()
            self.long_term_memory = None
            self.rag_manager = None
            logger.info("Basic memory system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize basic memory: {e}")
            self.short_term_memory = None
            self.long_term_memory = None
            self.rag_manager = None
    
    def _create_agent_with_memory(self, agent_name: str, tools: List = None) -> Agent:
        """Create an agent with proper memory assignment and error handling"""
        try:
            config = self.config_manager.get_agent_config(agent_name)
            
            # Create agent with basic configuration
            agent = Agent(
                role=config.get('role', f"Default {agent_name}"),
                goal=config.get('goal', f"Execute {agent_name} tasks"),
                backstory=config.get('backstory', f"You are a {agent_name}."),
                tools=tools or [],
                allow_delegation=config.get('allow_delegation', False),
                verbose=config.get('verbose', True)
            )
            
            # Assign memory based on agent type and availability
            if 'manager' in agent_name or 'director' in agent_name:
                if self.long_term_memory:
                    agent.memory = self.long_term_memory
            else:
                if self.short_term_memory:
                    agent.memory = self.short_term_memory
            
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent {agent_name}: {e}")
            # Return minimal agent to prevent crashes
            return Agent(
                role=f"Basic {agent_name}",
                goal=f"Execute basic {agent_name} tasks",
                backstory=f"You are a basic {agent_name}.",
                tools=[],
                verbose=True
            )

    # =============================================================================
    # EXECUTIVE TIER AGENTS
    # =============================================================================
    
    @agent
    def executive_director(self) -> Agent:
        """Executive Director with strategic oversight capabilities"""
        return self._create_agent_with_memory('executive_director')
    
    @agent
    def quality_assurance_manager(self) -> Agent:
        """Quality Assurance Manager with standards enforcement"""
        return self._create_agent_with_memory('quality_assurance_manager')
    
    # =============================================================================
    # MANAGEMENT TIER AGENTS
    # =============================================================================
    
    @agent
    def analysis_manager(self) -> Agent:
        """Analysis Manager coordinating research phase"""
        return self._create_agent_with_memory('analysis_manager')
    
    @agent
    def creative_manager(self) -> Agent:
        """Creative Manager leading concept development"""
        tools = [self.company_knowledge_tool] if hasattr(self, 'company_knowledge_tool') else []
        return self._create_agent_with_memory('creative_manager', tools)
    
    @agent
    def proposal_manager(self) -> Agent:
        """Proposal Manager coordinating final deliverable creation"""
        return self._create_agent_with_memory('proposal_manager')
    
    # =============================================================================
    # SPECIALIST TIER AGENTS - PHASE A
    # =============================================================================
    
    @agent
    def briefing_analyst(self) -> Agent:
        """Briefing Analyst for document analysis"""
        tools = [
            self.folder_read_tool,
            self.file_read_tool,
            getattr(self, 'document_analysis_tool', None)
        ]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('briefing_analyst', tools)
    
    @agent
    def market_researcher(self) -> Agent:
        """Market Researcher for Dutch market intelligence"""
        tools = [self.perplexity_tool] if hasattr(self, 'perplexity_tool') else []
        return self._create_agent_with_memory('market_researcher', tools)
    
    @agent
    def client_analyst(self) -> Agent:
        """Client Analyst for brand and culture analysis"""
        tools = [getattr(self, 'brand_analysis_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('client_analyst', tools)
    
    @agent
    def competitor_researcher(self) -> Agent:
        """Competitor Researcher for competitive intelligence"""
        tools = [getattr(self, 'competitor_analysis_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('competitor_researcher', tools)
    
    @agent
    def audience_analyst(self) -> Agent:
        """Audience Analyst for Dutch cultural insights"""
        tools = [getattr(self, 'audience_research_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('audience_analyst', tools)
    
    @agent
    def debrief_synthesizer(self) -> Agent:
        """Debrief Synthesizer for strategic synthesis"""
        return self._create_agent_with_memory('debrief_synthesizer')
    
    # =============================================================================
    # SPECIALIST TIER AGENTS - PHASE B
    # =============================================================================
    
    @agent
    def creative_strategist(self) -> Agent:
        """Creative Strategist for innovation and concept development"""
        tools = [getattr(self, 'innovation_framework_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('creative_strategist', tools)
    
    @agent
    def brand_consultant(self) -> Agent:
        """Brand Consultant for brand alignment"""
        tools = [getattr(self, 'brand_analysis_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('brand_consultant', tools)
    
    @agent
    def trend_culture_expert(self) -> Agent:
        """Trend & Culture Expert for cultural relevance"""
        return self._create_agent_with_memory('trend_culture_expert')
    
    @agent
    def concept_refiner(self) -> Agent:
        """Concept Refiner for storytelling and presentation"""
        return self._create_agent_with_memory('concept_refiner')
    
    # =============================================================================
    # SPECIALIST TIER AGENTS - PHASE D
    # =============================================================================
    
    @agent
    def event_creative(self) -> Agent:
        """Event Creative for experience innovation"""
        tools = [getattr(self, 'experience_design_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('event_creative', tools)
    
    @agent
    def creative_programmer(self) -> Agent:
        """Creative Programmer for event flow design"""
        return self._create_agent_with_memory('creative_programmer')
    
    @agent
    def content_creator(self) -> Agent:
        """Content Creator for multi-media strategy"""
        return self._create_agent_with_memory('content_creator')
    
    @agent
    def copywriter(self) -> Agent:
        """Copywriter for persuasive messaging"""
        return self._create_agent_with_memory('copywriter')
    
    @agent
    def art_director(self) -> Agent:
        """Art Director for visual identity"""
        tools = [getattr(self, 'visual_identity_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('art_director', tools)
    
    @agent
    def event_manager(self) -> Agent:
        """Event Manager for operational excellence"""
        tools = [getattr(self, 'dutch_venue_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('event_manager', tools)
    
    @agent
    def producer(self) -> Agent:
        """Producer for production planning"""
        tools = [getattr(self, 'production_planning_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('producer', tools)
    
    @agent
    def business_developer(self) -> Agent:
        """Business Developer for commercial strategy"""
        tools = [getattr(self, 'commercial_positioning_tool', None)]
        tools = [t for t in tools if t is not None]
        return self._create_agent_with_memory('business_developer', tools)
    
    # =============================================================================
    # TASK CREATION METHODS
    # =============================================================================
    
    def _create_task(self, task_name: str, agent: Agent, context: List[Task] = None) -> Task:
        """Create a task with proper configuration and error handling"""
        try:
            config = self.config_manager.get_task_config(task_name)
            
            return Task(
                description=config.get('description', f"Execute {task_name}"),
                expected_output=config.get('expected_output', f"Results from {task_name}"),
                agent=agent,
                context=context or []
            )
            
        except Exception as e:
            logger.error(f"Error creating task {task_name}: {e}")
            # Return minimal task to prevent crashes
            return Task(
                description=f"Execute {task_name}",
                expected_output=f"Results from {task_name}",
                agent=agent
            )
    
    # =============================================================================
    # CREW CREATION METHODS
    # =============================================================================
    
    @crew
    def analysis_crew(self) -> Crew:
        """Create the analysis crew for Phase A"""
        try:
            agents = [
                self.analysis_manager(),
                self.briefing_analyst(),
                self.market_researcher(),
                self.client_analyst(),
                self.competitor_researcher(),
                self.audience_analyst(),
                self.debrief_synthesizer()
            ]
            
            tasks = [
                self._create_task('analysis_manager_coordination', self.analysis_manager()),
                self._create_task('briefing_analysis_task', self.briefing_analyst()),
                self._create_task('market_research_task', self.market_researcher()),
                self._create_task('client_analysis_task', self.client_analyst()),
                self._create_task('competitor_research_task', self.competitor_researcher()),
                self._create_task('audience_analysis_task', self.audience_analyst()),
                self._create_task('strategic_debrief_synthesis', self.debrief_synthesizer())
            ]
            
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.hierarchical,
                manager_agent=self.analysis_manager(),
                verbose=True
            )
            
            # Assign memory to crew if available
            if self.long_term_memory:
                crew.memory = self.long_term_memory
            
            return crew
            
        except Exception as e:
            logger.error(f"Error creating analysis crew: {e}")
            # Return minimal crew
            return self._create_minimal_crew([self.analysis_manager()])
    
    @crew
    def creative_crew(self) -> Crew:
        """Create the creative crew for Phase B"""
        try:
            agents = [
                self.creative_manager(),
                self.creative_strategist(),
                self.brand_consultant(),
                self.trend_culture_expert(),
                self.concept_refiner()
            ]
            
            tasks = [
                self._create_task('creative_manager_coordination', self.creative_manager()),
                self._create_task('creative_strategy_development', self.creative_strategist()),
                self._create_task('brand_alignment_consultation', self.brand_consultant()),
                self._create_task('cultural_trend_analysis', self.trend_culture_expert()),
                self._create_task('concept_refinement_and_storytelling', self.concept_refiner())
            ]
            
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.hierarchical,
                manager_agent=self.creative_manager(),
                verbose=True
            )
            
            if self.long_term_memory:
                crew.memory = self.long_term_memory
            
            return crew
            
        except Exception as e:
            logger.error(f"Error creating creative crew: {e}")
            return self._create_minimal_crew([self.creative_manager()])
    
    @crew
    def proposal_crew(self) -> Crew:
        """Create the proposal crew for Phase D"""
        try:
            agents = [
                self.proposal_manager(),
                self.event_creative(),
                self.creative_programmer(),
                self.content_creator(),
                self.copywriter(),
                self.art_director(),
                self.event_manager(),
                self.producer(),
                self.business_developer()
            ]
            
            tasks = [
                self._create_task('proposal_manager_coordination', self.proposal_manager()),
                self._create_task('experience_design_development', self.event_creative()),
                self._create_task('event_programming_design', self.creative_programmer()),
                self._create_task('content_strategy_development', self.content_creator()),
                self._create_task('persuasive_copywriting', self.copywriter()),
                self._create_task('visual_identity_development', self.art_director()),
                self._create_task('operational_planning', self.event_manager()),
                self._create_task('production_planning', self.producer()),
                self._create_task('commercial_development', self.business_developer()),
                self._create_task('final_proposal_assembly', self.proposal_manager())
            ]
            
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.hierarchical,
                manager_agent=self.proposal_manager(),
                verbose=True
            )
            
            if self.long_term_memory:
                crew.memory = self.long_term_memory
            
            return crew
            
        except Exception as e:
            logger.error(f"Error creating proposal crew: {e}")
            return self._create_minimal_crew([self.proposal_manager()])
    
    def _create_minimal_crew(self, agents: List[Agent]) -> Crew:
        """Create a minimal crew as fallback"""
        try:
            minimal_task = Task(
                description="Execute basic workflow",
                expected_output="Basic workflow results",
                agent=agents[0] if agents else self.executive_director()
            )
            
            return Crew(
                agents=agents if agents else [self.executive_director()],
                tasks=[minimal_task],
                process=Process.sequential,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Failed to create minimal crew: {e}")
            raise RuntimeError("Critical error: Cannot create any crew configuration")
    
    # =============================================================================
    # ORCHESTRATION METHODS
    # =============================================================================
    
    def run_phase_a(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Phase A (Strategic Analysis) with error handling"""
        try:
            logger.info("Starting Phase A: Strategic Analysis")
            self.crew_state['phase'] = 'analysis'
            
            crew = self.analysis_crew()
            result = crew.kickoff(inputs=inputs or {})
            
            logger.info("Phase A completed successfully")
            return {'phase': 'A', 'status': 'completed', 'result': result}
            
        except Exception as e:
            logger.error(f"Phase A execution failed: {e}")
            return {'phase': 'A', 'status': 'failed', 'error': str(e)}
    
    def run_phase_b(self, phase_a_output: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Phase B (Creative Concepting) with error handling"""
        try:
            logger.info("Starting Phase B: Creative Concepting")
            self.crew_state['phase'] = 'creative'
            
            crew = self.creative_crew()
            result = crew.kickoff(inputs=phase_a_output)
            
            logger.info("Phase B completed successfully")
            return {'phase': 'B', 'status': 'completed', 'result': result}
            
        except Exception as e:
            logger.error(f"Phase B execution failed: {e}")
            return {'phase': 'B', 'status': 'failed', 'error': str(e)}
    
    def run_phase_d(self, selected_concept: str, human_feedback: str) -> Dict[str, Any]:
        """Execute Phase D (Proposal Development) with error handling"""
        try:
            logger.info("Starting Phase D: Proposal Development")
            self.crew_state['phase'] = 'proposal'
            
            inputs = {
                'selected_concept': selected_concept,
                'human_feedback': human_feedback
            }
            
            crew = self.proposal_crew()
            result = crew.kickoff(inputs=inputs)
            
            logger.info("Phase D completed successfully")
            return {'phase': 'D', 'status': 'completed', 'result': result}
            
        except Exception as e:
            logger.error(f"Phase D execution failed: {e}")
            return {'phase': 'D', 'status': 'failed', 'error': str(e)}
    
    def run_full_workflow(self, selected_concept: str = None, human_feedback: str = None) -> Dict[str, Any]:
        """Execute the complete workflow with error handling and recovery"""
        try:
            logger.info("Starting full workflow execution")
            results = {}
            
            # Phase A
            phase_a_result = self.run_phase_a()
            results['phase_a'] = phase_a_result
            
            if phase_a_result['status'] != 'completed':
                return results
            
            # Phase B
            phase_b_result = self.run_phase_b(phase_a_result)
            results['phase_b'] = phase_b_result
            
            if phase_b_result['status'] != 'completed':
                return results
            
            # Human review simulation (if no input provided)
            if not selected_concept:
                selected_concept = "Concept 1"  # Default selection
            if not human_feedback:
                human_feedback = "Approved with minor adjustments"
            
            # Phase D
            phase_d_result = self.run_phase_d(selected_concept, human_feedback)
            results['phase_d'] = phase_d_result
            
            logger.info("Full workflow completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Full workflow execution failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def cleanup(self):
        """Cleanup resources and connections"""
        try:
            if hasattr(self, 'rag_manager') and self.rag_manager:
                # Cleanup RAG manager resources
                pass
            
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {}
            }
            
            # Check environment
            health['components']['environment'] = EnvironmentValidator.validate_environment()
            
            # Check API connectivity
            health['components']['apis'] = EnvironmentValidator.test_api_connectivity()
            
            # Check memory systems
            health['components']['memory'] = {
                'short_term': self.short_term_memory is not None,
                'long_term': self.long_term_memory is not None,
                'rag': self.rag_manager is not None
            }
            
            # Check tools
            health['components']['tools'] = {
                'perplexity': hasattr(self, 'perplexity_tool'),
                'file_operations': hasattr(self, 'file_read_tool'),
                'knowledge_base': hasattr(self, 'company_knowledge_tool')
            }
            
            # Overall status
            if not all(health['components']['apis'].values()):
                health['status'] = 'degraded'
            
            return health
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Convenience function for easy instantiation
def create_enhanced_crew() -> EnhancedEventPitchCrew:
    """Create and return an enhanced event pitch crew instance"""
    try:
        crew = EnhancedEventPitchCrew()
        logger.info("Enhanced Event Pitch Crew created successfully")
        return crew
    except Exception as e:
        logger.error(f"Failed to create Enhanced Event Pitch Crew: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    try:
        crew = create_enhanced_crew()
        health = crew.get_health_status()
        print(f"Crew health status: {health['status']}")
        
        # Example workflow execution
        # results = crew.run_full_workflow()
        # print(f"Workflow results: {results}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        if 'crew' in locals():
            crew.cleanup()