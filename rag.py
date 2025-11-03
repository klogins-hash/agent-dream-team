"""RAG (Retrieval Augmented Generation) implementation."""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import openai

from vector_db import get_vector_db
from database import get_postgres


@dataclass
class RAGContext:
    """RAG context for generation."""
    query: str
    relevant_docs: List[Dict[str, Any]]
    knowledge_base: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]


class RAGEngine:
    """RAG engine for enhanced agent responses."""
    
    def __init__(self):
        """Initialize RAG engine."""
        self.vector_db = get_vector_db()
        self.db = get_postgres()
        self.openai_client = openai.Client(api_key=os.getenv("OPENROUTER_API_KEY"))
    
    def retrieve_context(self, query: str, agent_name: str = None, session_id: str = None) -> RAGContext:
        """Retrieve relevant context for query."""
        # Search agent documents
        agent_docs = self.vector_db.search_similar_documents(
            query=query,
            agent_name=agent_name,
            limit=5
        )
        
        # Search knowledge base
        knowledge = self.vector_db.search_knowledge(
            query=query,
            limit=5
        )
        
        # Search conversation history
        conversations = self.vector_db.search_conversations(
            query=query,
            session_id=session_id,
            limit=3
        )
        
        return RAGContext(
            query=query,
            relevant_docs=agent_docs,
            knowledge_base=knowledge,
            conversation_history=conversations
        )
    
    def generate_response_with_context(self, query: str, context: RAGContext, agent_name: str = None) -> str:
        """Generate response using retrieved context."""
        # Build context prompt
        context_text = self._build_context_prompt(context)
        
        # Create enhanced prompt
        system_prompt = f"""You are {agent_name or 'an AI assistant'} with access to relevant context.

Use the following context to provide accurate and helpful responses:

CONTEXT:
{context_text}

Your task is to answer the user's query using the provided context when relevant. 
If the context doesn't contain relevant information, use your general knowledge.

User Query: {query}

Provide a comprehensive and helpful response:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=os.getenv("MODEL_ID", "anthropic/claude-3.5-sonnet"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _build_context_prompt(self, context: RAGContext) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        
        # Add relevant documents
        if context.relevant_docs:
            context_parts.append("RELEVANT DOCUMENTS:")
            for doc in context.relevant_docs:
                context_parts.append(f"- {doc['content'][:500]}... (similarity: {doc['similarity']:.2f})")
        
        # Add knowledge base
        if context.knowledge_base:
            context_parts.append("\nKNOWLEDGE BASE:")
            for kb in context.knowledge_base:
                context_parts.append(f"- {kb['title']}: {kb['content'][:300]}... (similarity: {kb['similarity']:.2f})")
        
        # Add conversation history
        if context.conversation_history:
            context_parts.append("\nRELEVANT CONVERSATIONS:")
            for conv in context.conversation_history:
                context_parts.append(f"- {conv['role']}: {conv['message'][:200]}... (similarity: {conv['similarity']:.2f})")
        
        return "\n".join(context_parts)
    
    def store_interaction(self, session_id: str, user_message: str, agent_response: str, agent_name: str):
        """Store interaction in vector database."""
        # Store user message
        self.vector_db.store_conversation(
            session_id=session_id,
            message=user_message,
            role="user"
        )
        
        # Store agent response
        self.vector_db.store_conversation(
            session_id=session_id,
            message=agent_response,
            role="assistant"
        )
        
        # Store as agent document if significant
        if len(agent_response) > 100:
            self.vector_db.store_document(
                agent_name=agent_name,
                content=agent_response,
                metadata={
                    "session_id": session_id,
                    "type": "response",
                    "original_query": user_message
                }
            )
    
    def add_knowledge(self, title: str, content: str, category: str = None, tags: List[str] = None) -> str:
        """Add knowledge to the knowledge base."""
        return self.vector_db.store_knowledge(
            title=title,
            content=content,
            category=category,
            tags=tags
        )
    
    def search_all_knowledge(self, query: str, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all knowledge sources."""
        return {
            "agent_documents": self.vector_db.search_similar_documents(query, limit=limit),
            "knowledge_base": self.vector_db.search_knowledge(query, limit=limit),
            "conversations": self.vector_db.search_conversations(query, limit=limit)
        }
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about stored knowledge."""
        with self.db.engine.connect() as conn:
            # Count documents
            doc_count = conn.execute(text("SELECT COUNT(*) FROM agent_documents")).scalar()
            
            # Count knowledge base entries
            kb_count = conn.execute(text("SELECT COUNT(*) FROM knowledge_base")).scalar()
            
            # Count conversations
            conv_count = conn.execute(text("SELECT COUNT(*) FROM conversation_embeddings")).scalar()
            
            # Count unique agents
            agent_count = conn.execute(text("SELECT COUNT(DISTINCT agent_name) FROM agent_documents")).scalar()
            
            return {
                "total_documents": doc_count,
                "knowledge_entries": kb_count,
                "conversation_messages": conv_count,
                "unique_agents": agent_count
            }


# Singleton instance
_rag_engine = None

def get_rag_engine() -> RAGEngine:
    """Get RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
