"""Database-backed tools for agents."""

from strands import tool
from database import get_postgres, get_redis
import json


@tool
def db_remember(key: str, value: str, category: str = "general") -> str:
    """Remember information in the database permanently.
    
    Args:
        key: Memory key identifier
        value: Information to remember
        category: Category (general, user, system, project)
        
    Returns:
        Confirmation message
    """
    try:
        db = get_postgres()
        db.save_memory(key, value, category)
        return f"✅ Remembered in database: {key} = {value} (category: {category})"
    except Exception as e:
        return f"❌ Error saving to database: {str(e)}"


@tool
def db_recall(key: str) -> str:
    """Recall information from the database.
    
    Args:
        key: Memory key to recall
        
    Returns:
        The remembered information or error message
    """
    try:
        db = get_postgres()
        memory = db.get_memory(key)
        if memory:
            return f"Recalled from database: {key} = {memory['value']} (category: {memory['category']})"
        return f"No memory found in database for: {key}"
    except Exception as e:
        return f"❌ Error reading from database: {str(e)}"


@tool
def db_search_memories(category: str = None, limit: int = 10) -> str:
    """Search memories in the database.
    
    Args:
        category: Filter by category (optional)
        limit: Maximum results to return
        
    Returns:
        List of matching memories
    """
    try:
        db = get_postgres()
        memories = db.search_memory(category, limit)
        
        if not memories:
            return "No memories found"
        
        result = f"Found {len(memories)} memories:\n\n"
        for mem in memories:
            result += f"- {mem['key']}: {mem['value']} ({mem['category']})\n"
        
        return result
    except Exception as e:
        return f"❌ Error searching database: {str(e)}"


@tool
def save_user_preference(preference_key: str, preference_value: str, user_id: str = "default") -> str:
    """Save a user preference to the database.
    
    Args:
        preference_key: Preference name (e.g., writing_style, detail_level)
        preference_value: Preference value
        user_id: User identifier (default: "default")
        
    Returns:
        Confirmation message
    """
    try:
        db = get_postgres()
        db.save_preference(user_id, preference_key, preference_value)
        return f"✅ Saved preference: {preference_key} = {preference_value}"
    except Exception as e:
        return f"❌ Error saving preference: {str(e)}"


@tool
def get_user_preference(preference_key: str, user_id: str = "default") -> str:
    """Get a user preference from the database.
    
    Args:
        preference_key: Preference name
        user_id: User identifier (default: "default")
        
    Returns:
        Preference value or message if not found
    """
    try:
        db = get_postgres()
        value = db.get_preference(user_id, preference_key)
        if value:
            return f"Preference: {preference_key} = {value}"
        return f"No preference found for: {preference_key}"
    except Exception as e:
        return f"❌ Error getting preference: {str(e)}"


@tool
def cache_data(key: str, value: str, expire_seconds: int = 300) -> str:
    """Cache data in Redis for fast retrieval.
    
    Args:
        key: Cache key
        value: Data to cache
        expire_seconds: Expiration time in seconds (default: 300)
        
    Returns:
        Confirmation message
    """
    try:
        cache = get_redis()
        cache.cache_result(key, value, expire=expire_seconds)
        return f"✅ Cached: {key} (expires in {expire_seconds}s)"
    except Exception as e:
        return f"❌ Error caching data: {str(e)}"


@tool
def get_cached_data(key: str) -> str:
    """Retrieve cached data from Redis.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or message if not found
    """
    try:
        cache = get_redis()
        value = cache.get_cached_result(key)
        if value:
            return f"Cached data for {key}: {value}"
        return f"No cached data found for: {key}"
    except Exception as e:
        return f"❌ Error getting cached data: {str(e)}"


@tool
def get_conversation_history(session_id: str, limit: int = 5) -> str:
    """Get recent conversation history from database.
    
    Args:
        session_id: Session identifier
        limit: Number of recent messages to retrieve
        
    Returns:
        Conversation history
    """
    try:
        db = get_postgres()
        history = db.get_conversation_history(session_id, limit)
        
        if not history:
            return "No conversation history found"
        
        result = f"Recent conversation history ({len(history)} messages):\n\n"
        for msg in reversed(history):  # Show oldest first
            result += f"[{msg['created_at']}]\n"
            result += f"User: {msg['user_message']}\n"
            if msg['agent_response']:
                result += f"Agent ({msg['agent_name']}): {msg['agent_response']}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"❌ Error getting history: {str(e)}"


@tool
def get_task_history(limit: int = 10) -> str:
    """Get recent task execution history.
    
    Args:
        limit: Number of recent tasks to retrieve
        
    Returns:
        Task history summary
    """
    try:
        db = get_postgres()
        tasks = db.get_recent_tasks(limit)
        
        if not tasks:
            return "No task history found"
        
        result = f"Recent tasks ({len(tasks)}):\n\n"
        for task in tasks:
            result += f"[{task['created_at']}] Status: {task['status']}\n"
            result += f"Task: {task['task_description'][:100]}...\n"
            result += f"Time: {task['execution_time_ms']}ms, Handoffs: {task['handoff_count']}\n"
            if task['agents_involved']:
                result += f"Agents: {', '.join(task['agents_involved'])}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"❌ Error getting task history: {str(e)}"
