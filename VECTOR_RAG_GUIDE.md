# 🧠 Vector Database & RAG Guide

## Overview

Phase 3 adds semantic search and Retrieval Augmented Generation (RAG) capabilities using pgvector.

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Agent     │    │  Vector DB   │    │   OpenAI    │
│   Team      │───▶│  (pgvector)  │───▶│ Embeddings  │
└─────────────┘    └──────────────┘    └─────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   RAG       │    │  PostgreSQL  │    │   Storage   │
│   Engine    │    │   Database   │    │   Layer     │
└─────────────┘    └──────────────┘    └─────────────┘
```

## Features

### 1. Vector Storage
- **Agent Documents**: Store agent outputs and knowledge
- **Conversation History**: Embed all conversations for semantic search
- **Knowledge Base**: Persistent knowledge storage with categories and tags

### 2. Semantic Search
- **Similar Documents**: Find similar agent outputs
- **Conversation Search**: Search by meaning, not just keywords
- **Knowledge Retrieval**: Quick access to relevant information

### 3. RAG Pipeline
- **Context Retrieval**: Automatically fetch relevant context
- **Enhanced Responses**: Generate responses using retrieved context
- **Memory Integration**: Agents remember and reference past interactions

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements_vector.txt
```

### 2. Initialize Vector Database

```bash
# PostgreSQL with pgvector must be running
psql -h localhost -U agent_user -d agent_team -f init-vector-db.sql
```

### 3. Configure Environment

```bash
# Add to .env
OPENAI_API_KEY=your-openai-api-key
# Or use OpenRouter for embeddings
OPENROUTER_API_KEY=your-openrouter-key
```

## Usage

### Basic Vector Operations

```python
from vector_db import get_vector_db

# Get vector database instance
vector_db = get_vector_db()

# Store a document
doc_id = vector_db.store_document(
    agent_name="researcher",
    content="Quantum computing uses quantum mechanics...",
    metadata={"topic": "quantum", "confidence": 0.9}
)

# Search similar documents
results = vector_db.search_similar_documents(
    query="quantum physics applications",
    agent_name="researcher",
    limit=5
)

# Store knowledge
kb_id = vector_db.store_knowledge(
    title="Machine Learning Basics",
    content="Machine learning is a subset of AI...",
    category="technology",
    tags=["ML", "AI", "basics"]
)
```

### RAG Engine

```python
from rag import get_rag_engine

# Get RAG engine
rag = get_rag_engine()

# Retrieve context for query
context = rag.retrieve_context(
    query="How does quantum computing work?",
    agent_name="researcher",
    session_id="user-session-123"
)

# Generate contextual response
response = rag.generate_response_with_context(
    query="How does quantum computing work?",
    context=context,
    agent_name="researcher"
)

# Store interaction
rag.store_interaction(
    session_id="user-session-123",
    user_message="How does quantum computing work?",
    agent_response=response,
    agent_name="researcher"
)
```

### Agent Tools

```python
from tools_vector import remember_knowledge, search_knowledge, enhanced_search

# Remember important information
remember_knowledge(
    title="Project Deadline",
    content="The AI project deadline is December 15th",
    category="project",
    tags=["deadline", "AI", "project"]
)

# Search knowledge base
results = search_knowledge("project deadlines", category="project")

# Enhanced search across all sources
comprehensive = enhanced_search("quantum computing applications")
```

## API Integration

### New API Endpoints

```python
# Store knowledge
POST /api/knowledge
{
    "title": "New Knowledge",
    "content": "Content to store",
    "category": "general",
    "tags": ["tag1", "tag2"]
}

# Search knowledge
GET /api/knowledge/search?query=quantum&category=technology

# Get agent memory
GET /api/agents/{name}/memory

# Enhanced chat with RAG
POST /api/chat/rag
{
    "message": "Tell me about quantum computing",
    "use_rag": true,
    "agent_name": "researcher"
}
```

## Performance Optimization

### 1. Indexing
- IVFFlat indexes for similarity search
- Composite indexes for metadata queries
- GIN indexes for array types

### 2. Batch Operations
```python
# Batch store documents
documents = [
    {"content": "doc1", "metadata": {}},
    {"content": "doc2", "metadata": {}}
]
vector_db.batch_store_documents(documents)
```

### 3. Caching
- Embedding caching for repeated content
- Result caching for frequent queries
- Redis integration for fast access

## Monitoring

### Vector DB Metrics
- Document count by agent
- Search query performance
- Embedding generation rate
- Storage usage

### RAG Performance
- Context relevance scores
- Response quality metrics
- Knowledge retrieval accuracy

## Use Cases

### 1. Long-term Memory
- Agents remember past conversations
- Persistent knowledge across sessions
- Learning from user interactions

### 2. Knowledge Management
- Centralized knowledge base
- Semantic search capabilities
- Tag-based organization

### 3. Enhanced Responses
- Context-aware responses
- Reference to past interactions
- Accurate information retrieval

## Best Practices

### 1. Data Quality
- Clean and preprocess text before embedding
- Use meaningful metadata
- Regular knowledge base maintenance

### 2. Search Optimization
- Use specific queries for better results
- Filter by agent or category when possible
- Adjust similarity thresholds

### 3. Storage Management
- Regular cleanup of old embeddings
- Monitor storage usage
- Archive old conversations

## Troubleshooting

### Common Issues

1. **pgvector not installed**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Embedding generation fails**
   - Check OpenAI API key
   - Verify internet connection
   - Check rate limits

3. **Slow search performance**
   - Rebuild indexes
   - Check query complexity
   - Consider reducing dimensionality

4. **Memory usage high**
   - Implement embedding cleanup
   - Use batch operations
   - Monitor storage growth

## Next Steps

1. Implement advanced RAG techniques
2. Add multi-modal embeddings
3. Implement knowledge graph integration
4. Add real-time learning capabilities

---

**Phase 3 Complete**: Vector database and RAG capabilities integrated! 🎉
