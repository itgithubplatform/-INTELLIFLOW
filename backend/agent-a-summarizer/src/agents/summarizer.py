"""
Summarizer Agent
================

LangGraph-based agent for email summarization workflow.
"""

from typing import Any, Literal, TypedDict

from langgraph.graph import StateGraph, END

from shared.utils import get_logger

logger = get_logger(__name__)


class SummarizerState(TypedDict):
    """State for the summarizer agent workflow."""
    
    # Input
    email_id: str
    email_content: dict[str, Any]
    user_id: str
    
    # Processing
    summary: str
    key_points: list[str]
    action_items: list[dict[str, Any]]
    detected_events: list[dict[str, Any]]
    sentiment: str
    priority: str
    
    # Output
    calendar_events_created: list[dict[str, Any]]
    success: bool
    error: str | None


class SummarizerAgent:
    """
    LangGraph agent for email summarization workflow.
    
    Workflow:
    1. Fetch email content
    2. Generate AI summary
    3. Extract action items
    4. Detect calendar events
    5. Optionally create calendar events via Agent B
    """
    
    def __init__(
        self,
        gmail_service,
        llm_service,
        agent_b_client
    ):
        """
        Initialize summarizer agent.
        
        Args:
            gmail_service: Gmail service instance
            llm_service: LLM service instance
            agent_b_client: Agent B client instance
        """
        self.gmail_service = gmail_service
        self.llm_service = llm_service
        self.agent_b_client = agent_b_client
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        
        workflow = StateGraph(SummarizerState)
        
        # Add nodes
        workflow.add_node("fetch_email", self.fetch_email_node)
        workflow.add_node("generate_summary", self.generate_summary_node)
        workflow.add_node("create_events", self.create_events_node)
        
        # Set entry point
        workflow.set_entry_point("fetch_email")
        
        # Add edges
        workflow.add_edge("fetch_email", "generate_summary")
        workflow.add_conditional_edges(
            "generate_summary",
            self.should_create_events,
            {
                "create": "create_events",
                "skip": END
            }
        )
        workflow.add_edge("create_events", END)
        
        return workflow.compile()
    
    async def fetch_email_node(self, state: SummarizerState) -> dict:
        """Fetch email content from Gmail."""
        logger.info(f"Fetching email {state['email_id']}")
        
        try:
            email = await self.gmail_service.get_email(
                user_id=state["user_id"],
                email_id=state["email_id"]
            )
            
            return {
                "email_content": email,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error fetching email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_summary_node(self, state: SummarizerState) -> dict:
        """Generate AI summary of the email."""
        logger.info("Generating email summary")
        
        if not state.get("success", True):
            return {}
        
        try:
            email = state["email_content"]
            
            result = await self.llm_service.summarize_email(
                subject=email.get("subject", ""),
                body=email.get("body", ""),
                sender=email.get("sender", ""),
                include_action_items=True,
                include_events=True
            )
            
            return {
                "summary": result.get("summary", ""),
                "key_points": result.get("key_points", []),
                "action_items": result.get("action_items", []),
                "detected_events": result.get("detected_events", []),
                "sentiment": result.get("sentiment", "neutral"),
                "priority": result.get("priority", "medium")
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def should_create_events(self, state: SummarizerState) -> Literal["create", "skip"]:
        """Decide whether to create calendar events."""
        if state.get("detected_events") and len(state["detected_events"]) > 0:
            # Check if events have high confidence
            high_confidence = any(
                e.get("confidence", 0) >= 0.7
                for e in state["detected_events"]
            )
            return "create" if high_confidence else "skip"
        return "skip"
    
    async def create_events_node(self, state: SummarizerState) -> dict:
        """Create calendar events via Agent B."""
        logger.info("Creating calendar events")
        
        created_events = []
        
        for event in state.get("detected_events", []):
            if event.get("confidence", 0) >= 0.7:
                try:
                    # Get delegated token (simplified for this node)
                    # In real implementation, pass token through state
                    created = await self.agent_b_client.create_event(
                        token="delegated_token",  # Placeholder
                        event_data=event
                    )
                    if created:
                        created_events.append(created)
                except Exception as e:
                    logger.warning(f"Failed to create event: {e}")
        
        return {
            "calendar_events_created": created_events
        }
    
    async def run(
        self,
        email_id: str,
        user_id: str,
        **kwargs
    ) -> SummarizerState:
        """
        Run the summarization workflow.
        
        Args:
            email_id: Gmail message ID
            user_id: User ID
            **kwargs: Additional options
            
        Returns:
            Final workflow state
        """
        initial_state: SummarizerState = {
            "email_id": email_id,
            "user_id": user_id,
            "email_content": {},
            "summary": "",
            "key_points": [],
            "action_items": [],
            "detected_events": [],
            "sentiment": "neutral",
            "priority": "medium",
            "calendar_events_created": [],
            "success": False,
            "error": None
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result


def create_summarizer_graph(
    gmail_service,
    llm_service,
    agent_b_client
) -> SummarizerAgent:
    """
    Factory function to create summarizer agent.
    
    Args:
        gmail_service: Gmail service instance
        llm_service: LLM service instance
        agent_b_client: Agent B client instance
        
    Returns:
        Configured SummarizerAgent
    """
    return SummarizerAgent(
        gmail_service=gmail_service,
        llm_service=llm_service,
        agent_b_client=agent_b_client
    )
