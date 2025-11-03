"""Agent definitions for the Dream Team."""

from strands import Agent
from strands.session.file_session_manager import FileSessionManager
import config
from models import create_model
from tools import (
    research_topic,
    analyze_data,
    write_content,
    format_document,
    review_content,
    save_to_file
)


def create_session_manager():
    """Create a session manager for agent persistence."""
    import uuid
    session_id = str(uuid.uuid4())
    return FileSessionManager(
        session_id=session_id,
        base_path=config.SESSION_PATH,
        auto_save=config.AUTO_SAVE
    )


def create_agents():
    """Create and return all agents in the dream team.
    
    Returns:
        Dictionary of agent instances
    """
    # Shared model
    model = create_model()
    
    # Coordinator Agent
    coordinator = Agent(
        name="coordinator",
        model=model,
        system_prompt=config.COORDINATOR_PROMPT
    )
    
    # Researcher Agent
    researcher = Agent(
        name="researcher",
        model=model,
        system_prompt=config.RESEARCHER_PROMPT,
        tools=[research_topic, analyze_data]
    )
    
    # Writer Agent
    writer = Agent(
        name="writer",
        model=model,
        system_prompt=config.WRITER_PROMPT,
        tools=[write_content, format_document]
    )
    
    # Reviewer Agent
    reviewer = Agent(
        name="reviewer",
        model=model,
        system_prompt=config.REVIEWER_PROMPT,
        tools=[review_content, save_to_file]
    )
    
    return {
        "coordinator": coordinator,
        "researcher": researcher,
        "writer": writer,
        "reviewer": reviewer
    }
