-- Initialize pgvector extension and create vector tables

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Agent documents table
CREATE TABLE IF NOT EXISTS agent_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation embeddings table
CREATE TABLE IF NOT EXISTS conversation_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    role VARCHAR(50) NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base table
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

-- Create indexes for efficient similarity search
CREATE INDEX IF NOT EXISTS idx_agent_docs_embedding 
ON agent_documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_conversation_embedding 
ON conversation_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_knowledge_embedding 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Additional indexes
CREATE INDEX IF NOT EXISTS idx_agent_docs_name ON agent_documents(agent_name);
CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_embeddings(session_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_base USING GIN(tags);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agent_documents_updated_at 
    BEFORE UPDATE ON agent_documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at 
    BEFORE UPDATE ON knowledge_base 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON agent_documents TO agent_user;
GRANT ALL ON conversation_embeddings TO agent_user;
GRANT ALL ON knowledge_base TO agent_user;
