"""Shared memory system for agent collaboration."""

import json
from datetime import datetime
from pathlib import Path


class TeamMemory:
    """Persistent memory for the agent team."""
    
    def __init__(self, memory_file: str = "./team_memory.json"):
        """Initialize team memory.
        
        Args:
            memory_file: Path to memory file
        """
        self.memory_file = Path(memory_file)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> dict:
        """Load memory from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "facts": {},
            "preferences": {},
            "history": [],
            "context": {}
        }
    
    def _save_memory(self):
        """Save memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")
    
    def remember_fact(self, key: str, value: str):
        """Store a fact in memory.
        
        Args:
            key: Fact identifier
            value: Fact content
        """
        self.memory["facts"][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save_memory()
    
    def recall_fact(self, key: str) -> str:
        """Retrieve a fact from memory.
        
        Args:
            key: Fact identifier
            
        Returns:
            Fact value or None
        """
        fact = self.memory["facts"].get(key)
        return fact["value"] if fact else None
    
    def set_preference(self, key: str, value: str):
        """Store a user preference.
        
        Args:
            key: Preference name
            value: Preference value
        """
        self.memory["preferences"][key] = value
        self._save_memory()
    
    def get_preference(self, key: str) -> str:
        """Get a user preference.
        
        Args:
            key: Preference name
            
        Returns:
            Preference value or None
        """
        return self.memory["preferences"].get(key)
    
    def add_to_history(self, entry: str):
        """Add an entry to conversation history.
        
        Args:
            entry: History entry
        """
        self.memory["history"].append({
            "entry": entry,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 50 entries
        self.memory["history"] = self.memory["history"][-50:]
        self._save_memory()
    
    def get_recent_history(self, count: int = 5) -> list:
        """Get recent history entries.
        
        Args:
            count: Number of entries to retrieve
            
        Returns:
            List of recent entries
        """
        return self.memory["history"][-count:]
    
    def set_context(self, key: str, value: any):
        """Store context information.
        
        Args:
            key: Context key
            value: Context value
        """
        self.memory["context"][key] = value
        self._save_memory()
    
    def get_context(self, key: str) -> any:
        """Get context information.
        
        Args:
            key: Context key
            
        Returns:
            Context value or None
        """
        return self.memory["context"].get(key)
    
    def clear_memory(self):
        """Clear all memory."""
        self.memory = {
            "facts": {},
            "preferences": {},
            "history": [],
            "context": {}
        }
        self._save_memory()
    
    def get_summary(self) -> str:
        """Get a summary of stored memory.
        
        Returns:
            Memory summary
        """
        return f"""Team Memory Summary:
- Facts stored: {len(self.memory['facts'])}
- Preferences: {len(self.memory['preferences'])}
- History entries: {len(self.memory['history'])}
- Context items: {len(self.memory['context'])}
"""


# Create memory tools
def create_memory_tools(memory: TeamMemory):
    """Create tools that use shared memory.
    
    Args:
        memory: TeamMemory instance
        
    Returns:
        List of memory tools
    """
    from strands import tool
    
    @tool
    def remember(key: str, value: str) -> str:
        """Remember a fact for future reference.
        
        Args:
            key: What to remember (e.g., 'user_name', 'project_goal')
            value: The information to remember
            
        Returns:
            Confirmation message
        """
        memory.remember_fact(key, value)
        return f"✅ Remembered: {key} = {value}"
    
    @tool
    def recall(key: str) -> str:
        """Recall a previously remembered fact.
        
        Args:
            key: What to recall
            
        Returns:
            The remembered information or a message if not found
        """
        value = memory.recall_fact(key)
        if value:
            return f"Recalled: {key} = {value}"
        return f"No memory found for: {key}"
    
    @tool
    def set_preference(key: str, value: str) -> str:
        """Set a user preference.
        
        Args:
            key: Preference name (e.g., 'writing_style', 'detail_level')
            value: Preference value
            
        Returns:
            Confirmation message
        """
        memory.set_preference(key, value)
        return f"✅ Preference set: {key} = {value}"
    
    @tool
    def get_preference(key: str) -> str:
        """Get a user preference.
        
        Args:
            key: Preference name
            
        Returns:
            Preference value or message if not found
        """
        value = memory.get_preference(key)
        if value:
            return f"Preference: {key} = {value}"
        return f"No preference set for: {key}"
    
    return [remember, recall, set_preference, get_preference]
