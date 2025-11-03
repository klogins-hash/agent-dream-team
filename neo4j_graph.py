"""Neo4j graph database for knowledge graphs and relationships."""

import os
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from datetime import datetime


class Neo4jConfig:
    """Neo4j configuration from environment variables."""
    
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j_secure_password_change_me")


class KnowledgeGraph:
    """Neo4j knowledge graph manager for agent team."""
    
    def __init__(self):
        """Initialize Neo4j connection."""
        self.config = Neo4jConfig()
        self.driver = GraphDatabase.driver(
            self.config.NEO4J_URI,
            auth=(self.config.NEO4J_USER, self.config.NEO4J_PASSWORD)
        )
        self._initialize_constraints()
    
    def close(self):
        """Close Neo4j connection."""
        self.driver.close()
    
    def _initialize_constraints(self):
        """Create indexes and constraints."""
        with self.driver.session() as session:
            # Constraints for uniqueness
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Agent) REQUIRE a.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE")
            
            # Indexes for performance
            session.run("CREATE INDEX IF NOT EXISTS FOR (c:Conversation) ON (c.session_id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (k:Knowledge) ON (k.category)")
    
    # Agent nodes
    def create_agent(self, name: str, role: str, capabilities: List[str] = None):
        """Create an agent node."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (a:Agent {name: $name})
                SET a.role = $role,
                    a.capabilities = $capabilities,
                    a.created_at = datetime()
                RETURN a
            """, name=name, role=role, capabilities=capabilities or [])
            return result.single()
    
    def connect_agents(self, from_agent: str, to_agent: str, relationship: str, properties: Dict = None):
        """Create relationship between agents."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a1:Agent {name: $from_agent})
                MATCH (a2:Agent {name: $to_agent})
                MERGE (a1)-[r:COLLABORATES_WITH {type: $relationship}]->(a2)
                SET r += $properties
                SET r.created_at = datetime()
                RETURN r
            """, from_agent=from_agent, to_agent=to_agent, 
                 relationship=relationship, properties=properties or {})
            return result.single()
    
    # Knowledge nodes
    def add_knowledge(self, concept: str, description: str, category: str = "general", 
                     source: str = None, confidence: float = 1.0):
        """Add a knowledge node."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (k:Knowledge {concept: $concept})
                SET k.description = $description,
                    k.category = $category,
                    k.source = $source,
                    k.confidence = $confidence,
                    k.created_at = datetime(),
                    k.updated_at = datetime()
                RETURN k
            """, concept=concept, description=description, category=category,
                 source=source, confidence=confidence)
            return result.single()
    
    def link_knowledge(self, from_concept: str, to_concept: str, relationship: str, 
                      strength: float = 1.0):
        """Create relationship between knowledge concepts."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (k1:Knowledge {concept: $from_concept})
                MATCH (k2:Knowledge {concept: $to_concept})
                MERGE (k1)-[r:RELATES_TO {type: $relationship}]->(k2)
                SET r.strength = $strength,
                    r.created_at = datetime()
                RETURN r
            """, from_concept=from_concept, to_concept=to_concept,
                 relationship=relationship, strength=strength)
            return result.single()
    
    # Task tracking
    def create_task_node(self, task_id: str, description: str, status: str = "pending"):
        """Create a task node."""
        with self.driver.session() as session:
            result = session.run("""
                CREATE (t:Task {id: $task_id})
                SET t.description = $description,
                    t.status = $status,
                    t.created_at = datetime()
                RETURN t
            """, task_id=task_id, description=description, status=status)
            return result.single()
    
    def assign_task_to_agent(self, task_id: str, agent_name: str, role: str = "executor"):
        """Assign task to an agent."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Task {id: $task_id})
                MATCH (a:Agent {name: $agent_name})
                MERGE (a)-[r:WORKS_ON {role: $role}]->(t)
                SET r.assigned_at = datetime()
                RETURN r
            """, task_id=task_id, agent_name=agent_name, role=role)
            return result.single()
    
    def update_task_status(self, task_id: str, status: str, result: str = None):
        """Update task status."""
        with self.driver.session() as session:
            result_data = session.run("""
                MATCH (t:Task {id: $task_id})
                SET t.status = $status,
                    t.result = $result,
                    t.updated_at = datetime()
                RETURN t
            """, task_id=task_id, status=status, result=result)
            return result_data.single()
    
    # Conversation flow
    def track_conversation(self, session_id: str, user_message: str, agent_name: str,
                          agent_response: str = None):
        """Track conversation in graph."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (u:User {id: $session_id})
                MERGE (a:Agent {name: $agent_name})
                CREATE (c:Conversation {
                    session_id: $session_id,
                    user_message: $user_message,
                    agent_response: $agent_response,
                    timestamp: datetime()
                })
                CREATE (u)-[:SENT]->(c)
                CREATE (c)-[:HANDLED_BY]->(a)
                RETURN c
            """, session_id=session_id, user_message=user_message,
                 agent_name=agent_name, agent_response=agent_response)
            return result.single()
    
    # Query methods
    def get_agent_network(self, agent_name: str = None) -> List[Dict]:
        """Get agent collaboration network."""
        with self.driver.session() as session:
            if agent_name:
                result = session.run("""
                    MATCH (a:Agent {name: $agent_name})-[r:COLLABORATES_WITH]-(other:Agent)
                    RETURN a.name as agent, other.name as collaborator, 
                           r.type as relationship, r.created_at as since
                """, agent_name=agent_name)
            else:
                result = session.run("""
                    MATCH (a:Agent)-[r:COLLABORATES_WITH]-(other:Agent)
                    RETURN a.name as agent, other.name as collaborator,
                           r.type as relationship, r.created_at as since
                """)
            return [dict(record) for record in result]
    
    def get_knowledge_graph(self, concept: str = None, depth: int = 2) -> List[Dict]:
        """Get knowledge graph around a concept."""
        with self.driver.session() as session:
            if concept:
                result = session.run("""
                    MATCH path = (k:Knowledge {concept: $concept})-[r:RELATES_TO*1..$depth]-(related:Knowledge)
                    RETURN k.concept as from_concept, related.concept as to_concept,
                           [rel in relationships(path) | rel.type] as relationships,
                           length(path) as distance
                    ORDER BY distance
                """, concept=concept, depth=depth)
            else:
                result = session.run("""
                    MATCH (k1:Knowledge)-[r:RELATES_TO]->(k2:Knowledge)
                    RETURN k1.concept as from_concept, k2.concept as to_concept,
                           r.type as relationship, r.strength as strength
                    ORDER BY r.strength DESC
                    LIMIT 50
                """)
            return [dict(record) for record in result]
    
    def find_shortest_path(self, from_concept: str, to_concept: str) -> Optional[Dict]:
        """Find shortest path between two concepts."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (k1:Knowledge {concept: $from_concept})-[*]-(k2:Knowledge {concept: $to_concept})
                )
                RETURN [node in nodes(path) | node.concept] as concepts,
                       [rel in relationships(path) | rel.type] as relationships,
                       length(path) as distance
            """, from_concept=from_concept, to_concept=to_concept)
            record = result.single()
            return dict(record) if record else None
    
    def get_task_flow(self, task_id: str) -> List[Dict]:
        """Get task execution flow."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Task {id: $task_id})<-[r:WORKS_ON]-(a:Agent)
                RETURN a.name as agent, r.role as role, 
                       r.assigned_at as assigned_at, t.status as task_status
                ORDER BY r.assigned_at
            """, task_id=task_id)
            return [dict(record) for record in result]
    
    def get_conversation_flow(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Get conversation flow for a session."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $session_id})-[:SENT]->(c:Conversation)-[:HANDLED_BY]->(a:Agent)
                RETURN c.user_message as user_message, 
                       c.agent_response as agent_response,
                       a.name as agent, c.timestamp as timestamp
                ORDER BY c.timestamp DESC
                LIMIT $limit
            """, session_id=session_id, limit=limit)
            return [dict(record) for record in result]
    
    # Analytics
    def get_agent_stats(self, agent_name: str) -> Dict:
        """Get statistics for an agent."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Agent {name: $agent_name})
                OPTIONAL MATCH (a)-[:WORKS_ON]->(t:Task)
                OPTIONAL MATCH (a)<-[:HANDLED_BY]-(c:Conversation)
                RETURN a.name as agent,
                       count(DISTINCT t) as tasks_handled,
                       count(DISTINCT c) as conversations_handled,
                       count(DISTINCT CASE WHEN t.status = 'completed' THEN t END) as tasks_completed
            """, agent_name=agent_name)
            record = result.single()
            return dict(record) if record else {}
    
    def get_popular_concepts(self, limit: int = 10) -> List[Dict]:
        """Get most connected knowledge concepts."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (k:Knowledge)-[r:RELATES_TO]-()
                RETURN k.concept as concept, k.category as category,
                       count(r) as connections
                ORDER BY connections DESC
                LIMIT $limit
            """, limit=limit)
            return [dict(record) for record in result]


# Singleton instance
_knowledge_graph = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get KnowledgeGraph instance."""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph
