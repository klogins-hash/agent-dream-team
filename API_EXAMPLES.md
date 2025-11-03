# 📚 API Usage Examples

## Python

### Basic Chat

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{API_URL}/api/chat",
    headers=headers,
    json={"message": "Write a haiku about AI"}
)

print(response.json()["response"])
```

### Streaming Response

```python
import requests

response = requests.post(
    f"{API_URL}/api/chat/stream",
    headers=headers,
    json={"message": "Tell me about quantum computing"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### Async Task

```python
import requests
import time

# Create task
response = requests.post(
    f"{API_URL}/api/tasks",
    headers=headers,
    json={
        "task_description": "Research AI trends and write a report",
        "priority": 5
    }
)

task_id = response.json()["task_id"]

# Poll for completion
while True:
    status = requests.get(
        f"{API_URL}/api/tasks/{task_id}",
        headers=headers
    ).json()
    
    if status["status"] in ["completed", "failed"]:
        print(status["result"])
        break
    
    time.sleep(2)
```

## JavaScript/TypeScript

### Fetch API

```javascript
const API_URL = 'http://localhost:8000';
const API_KEY = 'your-api-key';

async function chat(message) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  return data.response;
}

chat('Write a poem about robots').then(console.log);
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: 'Hello, agent team!'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${API_KEY}`
  }
});

// Chat
const response = await api.post('/api/chat', {
  message: 'Explain machine learning'
});

console.log(response.data.response);

// Get history
const history = await api.get('/api/chat/history/session-123');
console.log(history.data);
```

## cURL

### Basic Request

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, agents!"}'
```

### With Session ID

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Continue our conversation",
    "session_id": "my-session-123"
  }'
```

### Get History

```bash
curl -X GET "http://localhost:8000/api/chat/history/my-session-123?limit=10" \
  -H "Authorization: Bearer your-api-key"
```

### Create Async Task

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Research and summarize AI trends",
    "priority": 5
  }'
```

## Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type ChatRequest struct {
    Message string `json:"message"`
}

type ChatResponse struct {
    Response string `json:"response"`
}

func main() {
    apiURL := "http://localhost:8000/api/chat"
    apiKey := "your-api-key"
    
    reqBody, _ := json.Marshal(ChatRequest{
        Message: "Write a haiku about Go",
    })
    
    req, _ := http.NewRequest("POST", apiURL, bytes.NewBuffer(reqBody))
    req.Header.Set("Authorization", "Bearer "+apiKey)
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    
    var chatResp ChatResponse
    json.NewDecoder(resp.Body).Decode(&chatResp)
    
    fmt.Println(chatResp.Response)
}
```

## Rust

```rust
use reqwest;
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct ChatRequest {
    message: String,
}

#[derive(Deserialize)]
struct ChatResponse {
    response: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let api_url = "http://localhost:8000/api/chat";
    let api_key = "your-api-key";
    
    let req_body = ChatRequest {
        message: "Write a haiku about Rust".to_string(),
    };
    
    let response = client
        .post(api_url)
        .header("Authorization", format!("Bearer {}", api_key))
        .json(&req_body)
        .send()
        .await?
        .json::<ChatResponse>()
        .await?;
    
    println!("{}", response.response);
    
    Ok(())
}
```

## Error Handling

```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        f"{API_URL}/api/chat",
        headers=headers,
        json={"message": "Hello"},
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded")
    elif e.response.status_code == 401:
        print("Invalid API key")
    else:
        print(f"HTTP error: {e}")
except RequestException as e:
    print(f"Request failed: {e}")
```

## Rate Limiting

The API implements rate limiting:
- **Default**: 60 requests/minute with burst of 10
- **429 Response**: Rate limit exceeded

```python
import time

def chat_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_URL}/api/chat",
                headers=headers,
                json={"message": message}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 60))
                print(f"Rate limited. Retrying in {retry_after}s...")
                time.sleep(retry_after)
            else:
                raise
    
    raise Exception("Max retries exceeded")
```
