---
title: BJJ AI Agents
short_description: An AI-enabled BJJ coaching app with specialized agents.
emoji: 🥋
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.35.0
app_file: main.py
pinned: false
---

# BJJ AI Agents

**NOTE**: This originated from a talk I gave at the Kansas City AI Agents Conference on June 25, 2025. [Here is the original notebook](https://github.com/faraday-academy/bjj-ai-agents-notebook) used for that talk.

Run app locally with: `uv run uvicorn main:demo --reload --host 0.0.0.0 --port 7860`

A comprehensive Brazilian Jiu-Jitsu AI coaching system with multiple specialized agents for different aspects of BJJ training and competition.

## Features

- **🤖 Coach Agent**: Interactive BJJ coaching with technique explanations
- **📋 Game Plan Agent**: Tournament strategy generation with RAG enhancement
- **🎯 Smart Router**: Intelligent query routing to appropriate agents
- **📊 Progress Tracking**: Learning progress monitoring and storage
- **🗄️ Database Management**: Comprehensive data storage and retrieval
- **🎲 Training Examples**: Generation of diverse training scenarios

## Quick Start

1. Set your OpenAI API key in the environment variables
2. Ask questions about BJJ techniques, strategies, or tournament planning
3. Use the Smart Router for automatic agent selection
4. Track your learning progress over time

## Agents

### Coach Agent
Handles general BJJ questions, technique explanations, and training advice.

### Game Plan Agent
Creates personalized tournament strategies based on division, weight class, and opponent style.

### Smart Router
Automatically routes queries to the most appropriate agent based on content analysis.

## Database

The system maintains comprehensive records of:
- Student information and progress
- Generated game plans
- Learning progress tracking
- Agent performance evaluations

## Project Structure

```
ai_agent_conference/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # Gradio entry point (was app.py)
│   ├── config.py
│   ├── database.py
│   ├── llm_utils.py
│   ├── evaluation.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── coach_agent.py
│   │   ├── game_plan_agent.py
│   │   └── router_agent.py
│
├── prompts/
│   └── ...
├── requirements.txt
├── pyproject.toml
├── README.md
└── README_webapp.md
```
