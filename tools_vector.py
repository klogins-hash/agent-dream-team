"""Vector database and RAG tools for agents."""

from typing import List, Dict, Any, Optional
from strands import tool

from vector_db import get_vector_db
from rag import get_rag_engine


@tool
def remember_knowledge(title: str, content: str, category: str = None, tags: List[str] = None) -> str:
    """Store important knowledge in the vector database.
    
    Args:
        title: Title of the knowledge entry
        content: Content to store
        category: Category for organization
        tags: List of tags for better search
        
    Returns:
        Success message with knowledge ID
    """
    rag = get_rag_engine()
    kb_id = rag.add_knowledge(title, content, category, tags)
    
    return f"Knowledge stored successfully with ID: {kb_id}"


@tool
def search_knowledge(query: str, category: str = None, limit: int = 10) -> str:
    """Search the knowledge base for relevant information.
    
    Args:
        query: Search query
        category: Filter by category
        limit: Maximum results to return
        
    Returns:
        Formatted search results
    """
    vector_db = get_vector_db()
    results = vector_db.search_knowledge(query, category, limit)
    
    if not results:
        return "No relevant knowledge found."
    
    output = f"Found {len(results)} relevant knowledge entries:\n\n"
    
    for i, result in enumerate(results, 1):
        output += f"{i}. **{result['title']}** (Similarity: {result['similarity']:.2f})\n"
        output += f"   Category: {result['category'] or 'Uncategorized'}\n"
        output += f"   Content: {result['content'][:300]}...\n"
        if result['tags']:
            output += f"   Tags: {', '.join(result['tags'])}\n"
        output += "\n"
    
    return output


@tool
def find_similar_conversations(query: str, session_id: str = None, limit: int = 5) -> str:
    """Find similar conversations from the past.
    
    Args:
        query: Search query
        session_id: Specific session to search
        limit: Maximum results
        
    Returns:
        Formatted conversation history
    """
    vector_db = get_vector_db()
    results = vector_db.search_conversations(query, session_id, limit)
    
    if not results:
        return "No similar conversations found."
    
    output = f"Found {len(results)} similar conversations:\n\n"
    
    for i, result in enumerate(results, 1):
        output += f"{i}. **Session**: {result['session_id']} (Similarity: {result['similarity']:.2f})\n"
        output += f"   **{result['role'].upper()}**: {result['message'][:200]}...\n"
        output += f"   **Time**: {result['created_at']}\n\n"
    
    return output


@tool
def get_agent_memory(agent_name: str) -> str:
    """Get summary of an agent's stored memory and knowledge.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Memory summary
    """
    vector_db = get_vector_db()
    summary = vector_db.get_agent_memory_summary(agent_name)
    
    output = f"**Memory Summary for {agent_name}**\n\n"
    output += f"Documents stored: {summary['document_count']}\n"
    
    if summary['last_updated']:
        output += f"Last updated: {summary['last_updated']}\n"
    
    if summary['recent_content']:
        output += "\n**Recent content**:\n"
        for i, content in enumerate(summary['recent_content'][:3], 1):
            output += f"{i}. {content[:150]}...\n"
    
    return output


@tool
def enhanced_search(query: str) -> str:
    """Search across all knowledge sources (documents, knowledge base, conversations).
    
    Args:
        query: Search query
        
    Returns:
        Comprehensive search results
    """
    rag = get_rag_engine()
    results = rag.search_all_knowledge(query, limit=5)
    
    output = f"**Comprehensive Search Results for: {query}**\n\n"
    
    # Agent documents
    if results['agent_documents']:
        output += "**Agent Documents**:\n"
        for i, doc in enumerate(results['agent_documents'], 1):
            output += f"{i}. {doc['agent_name']}: {doc['content'][:200]}... (similarity: {doc['similarity']:.2f})\n"
        output += "\n"
    
    # Knowledge base
    if results['knowledge_base']:
        output += "**Knowledge Base**:\n"
        for i, kb in enumerate(results['knowledge_base'], 1):
            output += f"{i}. {kb['title']}: {kb['content'][:200]}... (similarity: {kb['similarity']:.2f})\n"
        output += "\n"
    
    # Conversations
    if results['conversations']:
        output += "**Conversations**:\n"
        for i, conv in enumerate(results['conversations'], 1):
            output += f"{i}. {conv['role']}: {conv['message'][:150]}... (similarity: {conv['similarity']:.2f})\n"
    
    if not any(results.values()):
        return "No results found across all knowledge sources."
    
    return output


@tool
def get_knowledge_stats() -> str:
    """Get statistics about the knowledge base.
    
    Returns:
        Knowledge base statistics
    """
    rag = get_rag_engine()
    stats = rag.get_knowledge_stats()
    
    output = "**Knowledge Base Statistics**\n\n"
    output += f"Total documents: {stats['total_documents']}\n"
    output += f"Knowledge entries: {stats['knowledge_entries']}\n"
    output += f"Conversation messages: {stats['conversation_messages']}\n"
    output += f"Unique agents: {stats['unique_agents']}\n"
    
    return output


@tool
def contextual_response(query: str, agent_name: str = None) -> str:
    """Generate a response using retrieved context (RAG).
    
    Args:
        query: User query
        agent_name: Name of the responding agent
        
    Returns:
        Contextual response
    """
    rag = get_rag_engine()
    context = rag.retrieve_context(query, agent_name)
    response = rag.generate_response_with_context(query, context, agent_name)
    
    return response
