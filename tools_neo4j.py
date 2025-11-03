"""Neo4j-backed tools for knowledge graphs and relationships."""

from strands import tool
from neo4j_graph import get_knowledge_graph
import json


@tool
def add_knowledge_to_graph(concept: str, description: str, category: str = "general") -> str:
    """Add knowledge to the knowledge graph.
    
    Args:
        concept: The concept name
        description: Description of the concept
        category: Category (general, technical, business, etc.)
        
    Returns:
        Confirmation message
    """
    try:
        kg = get_knowledge_graph()
        kg.add_knowledge(concept, description, category)
        return f"✅ Added to knowledge graph: {concept} ({category})"
    except Exception as e:
        return f"❌ Error adding to graph: {str(e)}"


@tool
def link_concepts(from_concept: str, to_concept: str, relationship: str, strength: float = 1.0) -> str:
    """Create a relationship between two concepts in the knowledge graph.
    
    Args:
        from_concept: Source concept
        to_concept: Target concept
        relationship: Type of relationship (related_to, causes, requires, etc.)
        strength: Relationship strength (0.0 to 1.0)
        
    Returns:
        Confirmation message
    """
    try:
        kg = get_knowledge_graph()
        kg.link_knowledge(from_concept, to_concept, relationship, strength)
        return f"✅ Linked: {from_concept} --[{relationship}]--> {to_concept}"
    except Exception as e:
        return f"❌ Error linking concepts: {str(e)}"


@tool
def explore_knowledge_graph(concept: str, depth: int = 2) -> str:
    """Explore the knowledge graph around a concept.
    
    Args:
        concept: Starting concept
        depth: How many hops to explore (default: 2)
        
    Returns:
        Related concepts and relationships
    """
    try:
        kg = get_knowledge_graph()
        graph = kg.get_knowledge_graph(concept, depth)
        
        if not graph:
            return f"No connections found for: {concept}"
        
        result = f"Knowledge graph for '{concept}':\n\n"
        for item in graph[:20]:  # Limit to 20 results
            result += f"• {item['from_concept']} → {item['to_concept']}\n"
            if 'relationships' in item:
                result += f"  Relationships: {', '.join(item['relationships'])}\n"
        
        return result
    except Exception as e:
        return f"❌ Error exploring graph: {str(e)}"


@tool
def find_concept_path(from_concept: str, to_concept: str) -> str:
    """Find the shortest path between two concepts.
    
    Args:
        from_concept: Starting concept
        to_concept: Target concept
        
    Returns:
        Path description or message if no path found
    """
    try:
        kg = get_knowledge_graph()
        path = kg.find_shortest_path(from_concept, to_concept)
        
        if not path:
            return f"No path found between {from_concept} and {to_concept}"
        
        concepts = path['concepts']
        relationships = path['relationships']
        distance = path['distance']
        
        result = f"Path from '{from_concept}' to '{to_concept}' (distance: {distance}):\n\n"
        for i in range(len(concepts) - 1):
            result += f"{concepts[i]} --[{relationships[i]}]--> {concepts[i+1]}\n"
        
        return result
    except Exception as e:
        return f"❌ Error finding path: {str(e)}"


@tool
def get_popular_concepts(limit: int = 10) -> str:
    """Get the most connected concepts in the knowledge graph.
    
    Args:
        limit: Number of concepts to return
        
    Returns:
        List of popular concepts
    """
    try:
        kg = get_knowledge_graph()
        concepts = kg.get_popular_concepts(limit)
        
        if not concepts:
            return "No concepts found in knowledge graph"
        
        result = f"Top {len(concepts)} most connected concepts:\n\n"
        for i, concept in enumerate(concepts, 1):
            result += f"{i}. {concept['concept']} ({concept['category']})\n"
            result += f"   Connections: {concept['connections']}\n"
        
        return result
    except Exception as e:
        return f"❌ Error getting popular concepts: {str(e)}"


@tool
def track_agent_collaboration(from_agent: str, to_agent: str, collaboration_type: str) -> str:
    """Track collaboration between agents in the graph.
    
    Args:
        from_agent: Source agent name
        to_agent: Target agent name
        collaboration_type: Type of collaboration (handoff, consultation, review)
        
    Returns:
        Confirmation message
    """
    try:
        kg = get_knowledge_graph()
        kg.connect_agents(from_agent, to_agent, collaboration_type)
        return f"✅ Tracked collaboration: {from_agent} → {to_agent} ({collaboration_type})"
    except Exception as e:
        return f"❌ Error tracking collaboration: {str(e)}"


@tool
def get_agent_network(agent_name: str = None) -> str:
    """Get the agent collaboration network.
    
    Args:
        agent_name: Specific agent to query (optional, shows all if not specified)
        
    Returns:
        Agent network information
    """
    try:
        kg = get_knowledge_graph()
        network = kg.get_agent_network(agent_name)
        
        if not network:
            return "No agent collaborations found"
        
        result = "Agent Collaboration Network:\n\n"
        for collab in network:
            result += f"• {collab['agent']} ↔ {collab['collaborator']}\n"
            result += f"  Type: {collab['relationship']}\n"
        
        return result
    except Exception as e:
        return f"❌ Error getting agent network: {str(e)}"


@tool
def get_agent_statistics(agent_name: str) -> str:
    """Get performance statistics for an agent.
    
    Args:
        agent_name: Agent name
        
    Returns:
        Agent statistics
    """
    try:
        kg = get_knowledge_graph()
        stats = kg.get_agent_stats(agent_name)
        
        if not stats:
            return f"No statistics found for agent: {agent_name}"
        
        result = f"Statistics for {agent_name}:\n\n"
        result += f"• Tasks handled: {stats.get('tasks_handled', 0)}\n"
        result += f"• Tasks completed: {stats.get('tasks_completed', 0)}\n"
        result += f"• Conversations: {stats.get('conversations_handled', 0)}\n"
        
        return result
    except Exception as e:
        return f"❌ Error getting statistics: {str(e)}"
