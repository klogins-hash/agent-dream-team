"""Swarm team configuration."""

from strands.multiagent.swarm import Swarm
import config
from agents import create_agents


def create_team():
    """Create and configure the agent dream team.
    
    Returns:
        Configured Swarm instance
    """
    # Create all agents
    agents_dict = create_agents()
    
    # Extract agents in order
    coordinator = agents_dict["coordinator"]
    researcher = agents_dict["researcher"]
    writer = agents_dict["writer"]
    reviewer = agents_dict["reviewer"]
    
    # Create the swarm
    team = Swarm(
        nodes=[coordinator, researcher, writer, reviewer],
        entry_point=coordinator,
        max_handoffs=config.MAX_HANDOFFS,
        max_iterations=config.MAX_ITERATIONS,
        execution_timeout=config.EXECUTION_TIMEOUT,
        node_timeout=config.NODE_TIMEOUT,
        repetitive_handoff_detection_window=config.REPETITIVE_HANDOFF_WINDOW,
        repetitive_handoff_min_unique_agents=config.MIN_UNIQUE_AGENTS
    )
    
    return team


def run_task(task: str, verbose: bool = True):
    """Run a task with the agent dream team.
    
    Args:
        task: The task description
        verbose: Whether to print progress
        
    Returns:
        SwarmResult with the final output
    """
    if verbose:
        print(f"🚀 Starting Agent Dream Team...")
        print(f"📋 Task: {task}\n")
    
    team = create_team()
    result = team(task)
    
    if verbose:
        print(f"\n✅ Task completed!")
        print(f"📊 Execution time: {result.execution_time}ms")
        print(f"🔄 Total handoffs: {len(result.node_history)}")
        print(f"\n📝 Final Result:")
        print("-" * 80)
        
        # Get the last agent result
        if result.results:
            last_node_id = result.node_history[-1].node_id if result.node_history else None
            if last_node_id and last_node_id in result.results:
                node_result = result.results[last_node_id]
                if hasattr(node_result.result, 'message'):
                    message = node_result.result.message
                    if message and "content" in message:
                        for content_block in message["content"]:
                            if "text" in content_block:
                                print(content_block["text"])
        
        print("-" * 80)
    
    return result
