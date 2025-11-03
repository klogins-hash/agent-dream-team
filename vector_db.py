"""Vector database operations using pgvector."""

import os
import uuid
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import openai

from database import get_postgres


class VectorDB:
    """Vector database operations using pgvector."""
    
    def __init__(self):
        """Initialize vector database."""
        self.db = get_postgres()
        self.openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
        self._setup_vector_extension()
    
    def _setup_vector_extension(self):
        """Setup pgvector extension in PostgreSQL."""
        try:
            self.db.connect()
            with self.db.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        except Exception as e:
            print(f"Error setting up pgvector: {e}")
    
    def create_vector_tables(self):
        """Create tables for vector storage."""
        with self.db.engine.connect() as conn:
            # Documents table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agent_documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    agent_name VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Conversations table for semantic search
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS conversation_embeddings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Knowledge base table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(100),
                    tags TEXT[],
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_docs_embedding 
                ON agent_documents USING ivfflat (embedding vector_cosine_ops);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversation_embedding 
                ON conversation_embeddings USING ivfflat (embedding vector_cosine_ops);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_embedding 
                ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
            """))
            
            conn.commit()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def store_document(self, agent_name: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """Store document with embedding."""
        embedding = self.generate_embedding(content)
        if not embedding:
            return None
        
        doc_id = str(uuid.uuid4())
        
        with self.db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO agent_documents (id, agent_name, content, metadata, embedding)
                VALUES (:id, :agent_name, :content, :metadata, :embedding)
            """), {
                "id": doc_id,
                "agent_name": agent_name,
                "content": content,
                "metadata": metadata or {},
                "embedding": embedding
            })
            conn.commit()
        
        return doc_id
    
    def store_conversation(self, session_id: str, message: str, role: str):
        """Store conversation message with embedding."""
        embedding = self.generate_embedding(message)
        if not embedding:
            return
        
        with self.db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO conversation_embeddings (session_id, message, role, embedding)
                VALUES (:session_id, :message, :role, :embedding)
            """), {
                "session_id": session_id,
                "message": message,
                "role": role,
                "embedding": embedding
            })
            conn.commit()
    
    def store_knowledge(self, title: str, content: str, category: str = None, tags: List[str] = None) -> str:
        """Store knowledge base entry with embedding."""
        embedding = self.generate_embedding(content)
        if not embedding:
            return None
        
        kb_id = str(uuid.uuid4())
        
        with self.db.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO knowledge_base (id, title, content, category, tags, embedding)
                VALUES (:id, :title, :content, :category, :tags, :embedding)
            """), {
                "id": kb_id,
                "title": title,
                "content": content,
                "category": category,
                "tags": tags or [],
                "embedding": embedding
            })
            conn.commit()
        
        return kb_id
    
    def search_similar_documents(self, query: str, agent_name: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        with self.db.engine.connect() as conn:
            sql = text("""
                SELECT id, agent_name, content, metadata, 
                       1 - (embedding <=> :embedding) as similarity
                FROM agent_documents
                WHERE (agent_name = :agent_name OR :agent_name IS NULL)
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """)
            
            result = conn.execute(sql, {
                "embedding": query_embedding,
                "agent_name": agent_name,
                "limit": limit
            })
            
            return [
                {
                    "id": row.id,
                    "agent_name": row.agent_name,
                    "content": row.content,
                    "metadata": row.metadata,
                    "similarity": float(row.similarity)
                }
                for row in result
            ]
    
    def search_conversations(self, query: str, session_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search similar conversations."""
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        with self.db.engine.connect() as conn:
            sql = text("""
                SELECT session_id, message, role, created_at,
                       1 - (embedding <=> :embedding) as similarity
                FROM conversation_embeddings
                WHERE (session_id = :session_id OR :session_id IS NULL)
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """)
            
            result = conn.execute(sql, {
                "embedding": query_embedding,
                "session_id": session_id,
                "limit": limit
            })
            
            return [
                {
                    "session_id": row.session_id,
                    "message": row.message,
                    "role": row.role,
                    "created_at": row.created_at,
                    "similarity": float(row.similarity)
                }
                for row in result
            ]
    
    def search_knowledge(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base."""
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        with self.db.engine.connect() as conn:
            sql = text("""
                SELECT id, title, content, category, tags,
                       1 - (embedding <=> :embedding) as similarity
                FROM knowledge_base
                WHERE (category = :category OR :category IS NULL)
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """)
            
            result = conn.execute(sql, {
                "embedding": query_embedding,
                "category": category,
                "limit": limit
            })
            
            return [
                {
                    "id": row.id,
                    "title": row.title,
                    "content": row.content,
                    "category": row.category,
                    "tags": row.tags,
                    "similarity": float(row.similarity)
                }
                for row in result
            ]
    
    def get_agent_memory_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get summary of agent's stored knowledge."""
        with self.db.engine.connect() as conn:
            # Count documents
            doc_count = conn.execute(text("""
                SELECT COUNT(*) FROM agent_documents WHERE agent_name = :agent_name
            """), {"agent_name": agent_name}).scalar()
            
            # Get recent documents
            recent_docs = conn.execute(text("""
                SELECT content, created_at FROM agent_documents
                WHERE agent_name = :agent_name
                ORDER BY created_at DESC LIMIT 5
            """), {"agent_name": agent_name}).fetchall()
            
            return {
                "agent_name": agent_name,
                "document_count": doc_count,
                "recent_content": [doc.content for doc in recent_docs],
                "last_updated": recent_docs[0].created_at if recent_docs else None
            }


# Singleton instance
_vector_db = None

def get_vector_db() -> VectorDB:
    """Get vector database instance."""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDB()
        _vector_db.create_vector_tables()
    return _vector_db
