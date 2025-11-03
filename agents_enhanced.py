"""Enhanced agent definitions with advanced capabilities."""

from strands import Agent
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
from tools_advanced import (
    web_search,
    read_file,
    write_file,
    list_files,
    get_current_time,
    calculate,
    create_json,
    parse_json,
    summarize_text,
    word_count
)
from memory import TeamMemory, create_memory_tools
from prompts_enhanced import (
    COORDINATOR_ENHANCED,
    RESEARCHER_ENHANCED,
    WRITER_ENHANCED,
    REVIEWER_ENHANCED
)


def create_enhanced_agents():
    """Create enhanced agents with advanced capabilities.
    
    Returns:
        Dictionary of enhanced agent instances
    """
    # Shared model
    model = create_model()
    
    # Shared memory system
    memory = TeamMemory()
    memory_tools = create_memory_tools(memory)
    
    # Coordinator Agent - Strategic oversight
    coordinator = Agent(
        name="coordinator",
        model=model,
        system_prompt=COORDINATOR_ENHANCED,
        tools=memory_tools + [
            get_current_time,
            calculate,
            list_files
        ]
    )
    
    # Researcher Agent - Information gathering
    researcher = Agent(
        name="researcher",
        model=model,
        system_prompt=RESEARCHER_ENHANCED,
        tools=memory_tools + [
            research_topic,
            analyze_data,
            web_search,
            read_file,
            calculate,
            summarize_text
        ]
    )
    
    # Writer Agent - Content creation
    writer = Agent(
        name="writer",
        model=model,
        system_prompt=WRITER_ENHANCED,
        tools=memory_tools + [
            write_content,
            format_document,
            write_file,
            word_count,
            create_json
        ]
    )
    
    # Reviewer Agent - Quality assurance
    reviewer = Agent(
        name="reviewer",
        model=model,
        system_prompt=REVIEWER_ENHANCED,
        tools=memory_tools + [
            review_content,
            save_to_file,
            read_file,
            word_count,
            parse_json
        ]
    )
    
    return {
        "coordinator": coordinator,
        "researcher": researcher,
        "writer": writer,
        "reviewer": reviewer,
        "memory": memory
    }
