"""Test script for Agent Dream Team API."""

import requests
import json
import time

API_URL = "http://localhost:8000"

# For testing, we'll use a simple bearer token
# In production, use proper API keys
API_KEY = "test-key-123"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_health():
    """Test health endpoint."""
    print("Testing /health...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_list_agents():
    """Test list agents endpoint."""
    print("Testing /api/agents...")
    response = requests.get(f"{API_URL}/api/agents", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_chat():
    """Test chat endpoint."""
    print("Testing /api/chat...")
    
    payload = {
        "message": "Write a haiku about AI agents",
        "user_id": "test_user"
    }
    
    response = requests.post(
        f"{API_URL}/api/chat",
        headers=headers,
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response']}")
        print(f"Execution time: {data['execution_time_ms']}ms")
        print(f"Handoffs: {data['handoff_count']}")
        print(f"Agents: {data['agents_involved']}\n")
    else:
        print(f"Error: {response.text}\n")


def test_async_task():
    """Test async task creation and status."""
    print("Testing /api/tasks...")
    
    # Create task
    payload = {
        "task_description": "Research quantum computing and write a brief summary",
        "user_id": "test_user",
        "priority": 5
    }
    
    response = requests.post(
        f"{API_URL}/api/tasks",
        headers=headers,
        json=payload
    )
    
    print(f"Create task status: {response.status_code}")
    if response.status_code == 200:
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"Task ID: {task_id}")
        print(f"Status: {task_data['status']}\n")
        
        # Poll for completion
        print("Polling task status...")
        for i in range(10):
            time.sleep(2)
            status_response = requests.get(
                f"{API_URL}/api/tasks/{task_id}",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Status: {status_data['status']}")
                
                if status_data['status'] in ['completed', 'failed']:
                    if status_data['status'] == 'completed':
                        print(f"Result: {status_data['result'][:200]}...")
                    else:
                        print(f"Error: {status_data['error']}")
                    break
    else:
        print(f"Error: {response.text}\n")


def test_conversation_history():
    """Test conversation history endpoint."""
    print("Testing /api/chat/history...")
    
    # First send a message
    payload = {
        "message": "Hello, agent team!",
        "session_id": "test-session-123",
        "user_id": "test_user"
    }
    
    requests.post(f"{API_URL}/api/chat", headers=headers, json=payload)
    
    # Get history
    response = requests.get(
        f"{API_URL}/api/chat/history/test-session-123?limit=5",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Session: {data['session_id']}")
        print(f"History entries: {len(data['history'])}\n")
    else:
        print(f"Error: {response.text}\n")


def test_agent_stats():
    """Test agent statistics endpoint."""
    print("Testing /api/agents/{name}/stats...")
    
    response = requests.get(
        f"{API_URL}/api/agents/coordinator/stats",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Stats: {json.dumps(response.json(), indent=2)}\n")
    else:
        print(f"Error: {response.text}\n")


def run_all_tests():
    """Run all API tests."""
    print("=" * 80)
    print("AGENT DREAM TEAM API TESTS")
    print("=" * 80 + "\n")
    
    try:
        test_health()
        test_list_agents()
        test_chat()
        test_conversation_history()
        test_agent_stats()
        # test_async_task()  # Uncomment for full test (takes longer)
        
        print("=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("Make sure the API server is running: python api.py")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_all_tests()
