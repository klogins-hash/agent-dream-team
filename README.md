# 🌟 Agent Dream Team

A robust multi-agent system powered by Strands Agents and OpenRouter, featuring self-organizing collaborative agents with shared working memory.

## Features

- **Swarm Intelligence**: Self-organizing agent teams that coordinate autonomously
- **OpenRouter Integration**: Access to 200+ models with automatic routing
- **Specialized Agents**: Coordinator, Researcher, Writer, and Reviewer working together
- **Shared Context**: Agents share information seamlessly
- **Session Persistence**: Conversation history saved automatically

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the agent team:
```bash
python main.py
```

3. Or use the interactive demo:
```bash
python demo.py
```

## Architecture

- **Coordinator**: Analyzes tasks and delegates to specialists
- **Researcher**: Gathers information and conducts analysis
- **Writer**: Creates content based on research findings
- **Reviewer**: Quality checks and provides feedback

## Configuration

Edit `config.py` to customize:
- Model selection
- Temperature and token limits
- Timeout settings
- Agent prompts
