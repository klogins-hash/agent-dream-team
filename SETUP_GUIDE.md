# 🚀 Agent Dream Team - Complete Setup Guide

## What Makes This Team Special?

Your agent team now has **enterprise-grade capabilities**:

### 🧠 **Persistent Memory**
- Agents remember facts across conversations
- User preferences are stored and applied
- Conversation history is maintained
- Shared context between all agents

### 🛠️ **Advanced Tools**
- **File Operations**: Read, write, and list files
- **Web Search**: Access current information (ready for API integration)
- **Calculations**: Math and data processing
- **JSON Handling**: Parse and create structured data
- **Text Analysis**: Word counts, summaries, statistics
- **Time Awareness**: Current date/time

### 💬 **Enhanced Prompts**
- Detailed role definitions
- Best practices built-in
- Clear handoff protocols
- Quality standards

### 🎯 **Smart Coordination**
- Strategic task breakdown
- Optimal agent selection
- Context preservation
- Quality assurance

## Quick Start Options

### Option 1: Standard Team (Original)
```bash
cd ~/CascadeProjects/agent-dream-team
source .venv/bin/activate
python chat.py
```

### Option 2: Enhanced Team (Recommended)
```bash
cd ~/CascadeProjects/agent-dream-team
source .venv/bin/activate
python chat_enhanced.py
```

## Feature Comparison

| Feature | Standard | Enhanced |
|---------|----------|----------|
| Basic Tools | ✅ | ✅ |
| Advanced Tools | ❌ | ✅ |
| Memory System | ❌ | ✅ |
| File Operations | ❌ | ✅ |
| Enhanced Prompts | ❌ | ✅ |
| Web Search Ready | ❌ | ✅ |

## Memory System Usage

The enhanced team can:

```
You: Remember that my name is Frank and I prefer technical writing

Agent: ✅ Remembered: user_name = Frank
       ✅ Preference set: writing_style = technical

You: What's my name?

Agent: Recalled: user_name = Frank
```

## Advanced Tool Examples

### File Operations
```
You: Create a file called notes.txt with my project ideas

Agent: [Uses write_file tool]
       ✅ Successfully wrote to notes.txt
```

### Calculations
```
You: Calculate the compound interest on $10000 at 5% for 3 years

Agent: [Uses calculate tool]
       10000 * (1.05 ** 3) = 11576.25
```

### Text Analysis
```
You: Analyze this text and give me statistics

Agent: [Uses word_count tool]
       Text Statistics:
       - Words: 150
       - Characters: 850
       - Sentences: 8
```

## Customization Tips

### 1. Add Your Own Tools
Edit `tools_advanced.py` to add custom tools:
```python
@tool
def my_custom_tool(param: str) -> str:
    """Your tool description."""
    # Your implementation
    return result
```

### 2. Modify Agent Prompts
Edit `prompts_enhanced.py` to customize agent behavior

### 3. Adjust Team Configuration
Edit `config.py` to change:
- Model selection
- Timeout settings
- Handoff limits
- Temperature/creativity

### 4. Integrate Real APIs

#### Web Search (DuckDuckGo - Free)
```python
# In tools_advanced.py
from duckduckgo_search import DDGS

@tool
def web_search(query: str, num_results: int = 5) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=num_results))
        # Format and return results
```

#### Other API Integrations
- **Brave Search**: Fast, privacy-focused
- **Tavily AI**: AI-optimized search
- **SerpAPI**: Google results
- **News APIs**: Current events
- **Weather APIs**: Real-time weather
- **Database connections**: PostgreSQL, MongoDB, etc.

## Performance Optimization

### For Faster Responses
```python
# In config.py
MODEL_ID = "anthropic/claude-3.5-haiku"  # Faster, cheaper
MAX_TOKENS = 2048  # Shorter responses
```

### For Better Quality
```python
# In config.py
MODEL_ID = "anthropic/claude-3.7-sonnet"  # Best reasoning
MAX_TOKENS = 8192  # Longer, detailed responses
TEMPERATURE = 0.3  # More focused
```

### For Creative Tasks
```python
# In config.py
TEMPERATURE = 0.9  # More creative
```

## Monitoring & Debugging

### View Memory Contents
```python
from memory import TeamMemory

memory = TeamMemory()
print(memory.get_summary())
```

### Clear Memory
```python
memory.clear_memory()
```

### Check Agent Performance
The team automatically tracks:
- Execution time
- Number of handoffs
- Token usage (via OpenRouter dashboard)

## Production Deployment

### Environment Variables
```bash
export OPENROUTER_API_KEY="your-key"
export MODEL_ID="anthropic/claude-3.5-sonnet"
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "chat_enhanced.py"]
```

### API Wrapper
Create a FastAPI wrapper:
```python
from fastapi import FastAPI
from team_enhanced import run_enhanced_task

app = FastAPI()

@app.post("/chat")
async def chat(message: str):
    result, memory = run_enhanced_task(message, verbose=False)
    return {"response": result}
```

## Troubleshooting

### Issue: Agents not coordinating well
- **Solution**: Adjust prompts in `prompts_enhanced.py`
- Add more specific handoff instructions

### Issue: Responses too slow
- **Solution**: Use faster model (Haiku)
- Reduce MAX_TOKENS
- Decrease MAX_HANDOFFS

### Issue: Memory not persisting
- **Solution**: Check file permissions
- Verify `team_memory.json` is writable

### Issue: Tool errors
- **Solution**: Check tool implementations
- Verify file paths are absolute
- Test tools individually

## Next Steps

1. **Try the enhanced team** with `chat_enhanced.py`
2. **Integrate real APIs** (web search, databases)
3. **Customize prompts** for your use case
4. **Add domain-specific tools**
5. **Deploy to production**

## Support & Resources

- **OpenRouter Docs**: https://openrouter.ai/docs
- **Strands Agents Docs**: https://strandsagents.com
- **LiteLLM Docs**: https://docs.litellm.ai

---

Your Agent Dream Team is ready for anything! 🌟
