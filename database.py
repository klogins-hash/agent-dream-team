"""Database connections and utilities for PostgreSQL and Redis."""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import redis
from contextlib import contextmanager


class DatabaseConfig:
    """Database configuration from environment variables."""
    
    # PostgreSQL
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "agent_team")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "agent_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "agent_secure_password_change_me")
    
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redis_secure_password_change_me")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))


class PostgresDB:
    """PostgreSQL database manager."""
    
    def __init__(self):
        """Initialize PostgreSQL connection."""
        self.config = DatabaseConfig()
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(
                host=self.config.POSTGRES_HOST,
                port=self.config.POSTGRES_PORT,
                database=self.config.POSTGRES_DB,
                user=self.config.POSTGRES_USER,
                password=self.config.POSTGRES_PASSWORD
            )
        return self.conn
    
    @contextmanager
    def get_cursor(self):
        """Get a database cursor with automatic cleanup."""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
    
    # Conversation methods
    def save_conversation(self, session_id: str, user_message: str, 
                         agent_response: str = None, agent_name: str = None,
                         metadata: dict = None):
        """Save a conversation entry."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO conversations (session_id, user_message, agent_response, agent_name, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (session_id, user_message, agent_response, agent_name, Json(metadata or {})))
            return cursor.fetchone()['id']
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for a session."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE session_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (session_id, limit))
            return cursor.fetchall()
    
    # Memory methods
    def save_memory(self, key: str, value: str, category: str = 'general', metadata: dict = None):
        """Save or update a memory entry."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO agent_memory (key, value, category, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (key) 
                DO UPDATE SET value = EXCLUDED.value, 
                             category = EXCLUDED.category,
                             metadata = EXCLUDED.metadata,
                             updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (key, value, category, Json(metadata or {})))
            return cursor.fetchone()['id']
    
    def get_memory(self, key: str) -> Optional[Dict]:
        """Retrieve a memory entry."""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM agent_memory WHERE key = %s", (key,))
            return cursor.fetchone()
    
    def search_memory(self, category: str = None, limit: int = 50) -> List[Dict]:
        """Search memory entries."""
        with self.get_cursor() as cursor:
            if category:
                cursor.execute("""
                    SELECT * FROM agent_memory 
                    WHERE category = %s 
                    ORDER BY updated_at DESC 
                    LIMIT %s
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT * FROM agent_memory 
                    ORDER BY updated_at DESC 
                    LIMIT %s
                """, (limit,))
            return cursor.fetchall()
    
    # Preference methods
    def save_preference(self, user_id: str, key: str, value: str):
        """Save or update a user preference."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_preferences (user_id, preference_key, preference_value)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, preference_key)
                DO UPDATE SET preference_value = EXCLUDED.preference_value,
                             updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (user_id, key, value))
            return cursor.fetchone()['id']
    
    def get_preference(self, user_id: str, key: str) -> Optional[str]:
        """Get a user preference."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT preference_value FROM user_preferences 
                WHERE user_id = %s AND preference_key = %s
            """, (user_id, key))
            result = cursor.fetchone()
            return result['preference_value'] if result else None
    
    def get_all_preferences(self, user_id: str) -> Dict[str, str]:
        """Get all preferences for a user."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT preference_key, preference_value 
                FROM user_preferences 
                WHERE user_id = %s
            """, (user_id,))
            return {row['preference_key']: row['preference_value'] for row in cursor.fetchall()}
    
    # Task history methods
    def save_task(self, task_description: str, status: str, execution_time_ms: int = None,
                  handoff_count: int = None, agents_involved: List[str] = None,
                  result: str = None, metadata: dict = None):
        """Save task execution history."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO task_history 
                (task_description, status, execution_time_ms, handoff_count, agents_involved, result, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (task_description, status, execution_time_ms, handoff_count, 
                  agents_involved, result, Json(metadata or {})))
            return cursor.fetchone()['id']
    
    def get_recent_tasks(self, limit: int = 20) -> List[Dict]:
        """Get recent task history."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM task_history 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()


class RedisCache:
    """Redis cache manager."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.config = DatabaseConfig()
        self.client = redis.Redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            password=self.config.REDIS_PASSWORD,
            db=self.config.REDIS_DB,
            decode_responses=True
        )
    
    def set(self, key: str, value: Any, expire: int = None):
        """Set a cache value with optional expiration (seconds)."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.set(key, value, ex=expire)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cache value."""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def delete(self, key: str):
        """Delete a cache key."""
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return self.client.exists(key) > 0
    
    def expire(self, key: str, seconds: int):
        """Set expiration on a key."""
        self.client.expire(key, seconds)
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        return self.client.incrby(key, amount)
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching a pattern."""
        return self.client.keys(pattern)
    
    def flush_db(self):
        """Clear all keys in current database."""
        self.client.flushdb()
    
    # Session management
    def save_session(self, session_id: str, data: dict, expire: int = 3600):
        """Save session data."""
        self.set(f"session:{session_id}", data, expire=expire)
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        return self.get(f"session:{session_id}")
    
    def delete_session(self, session_id: str):
        """Delete session data."""
        self.delete(f"session:{session_id}")
    
    # Rate limiting
    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if rate limit is exceeded.
        
        Args:
            key: Rate limit key (e.g., user_id)
            limit: Maximum requests
            window: Time window in seconds
            
        Returns:
            True if under limit, False if exceeded
        """
        rate_key = f"rate:{key}"
        current = self.client.get(rate_key)
        
        if current is None:
            self.client.setex(rate_key, window, 1)
            return True
        
        if int(current) < limit:
            self.client.incr(rate_key)
            return True
        
        return False
    
    # Caching helpers
    def cache_result(self, key: str, value: Any, expire: int = 300):
        """Cache a computation result."""
        self.set(f"cache:{key}", value, expire=expire)
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """Get a cached result."""
        return self.get(f"cache:{key}")


# Singleton instances
_postgres_db = None
_redis_cache = None


def get_postgres() -> PostgresDB:
    """Get PostgreSQL database instance."""
    global _postgres_db
    if _postgres_db is None:
        _postgres_db = PostgresDB()
    return _postgres_db


def get_redis() -> RedisCache:
    """Get Redis cache instance."""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache
