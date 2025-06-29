# 🥋 BJJ AI Agents Web App

A comprehensive Brazilian Jiu-Jitsu AI coaching system built with Gradio and LangGraph, designed for deployment on Hugging Face Spaces.

## Features

### 🤖 Coach Chat
- Interactive BJJ coaching with AI
- Technique explanations and advice
- Progress tracking capabilities
- Video retrieval suggestions

### 📋 Game Plan Generator
- Tournament strategy creation
- Division and weight class specific plans
- RAG-enhanced responses for better context
- Historical plan storage

### 🎯 Smart Router
- Intelligent query routing to appropriate agents
- Automatic agent selection based on query content
- Seamless user experience

### 📊 Progress Tracking
- Technique learning progress
- Skill level assessment
- Notes and feedback storage
- Historical progress review

### 🗄️ Database Viewer
- View stored student data
- Access game plans
- Review progress tracking entries
- Evaluation results

### 🎲 Training Examples
- Generate diverse training scenarios
- Agent response examples
- Testing and evaluation tools

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. Run the application:
```bash
python app.py
```

## Deployment to Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Choose Gradio as the SDK
3. Upload all the Python files and requirements.txt
4. Set the following environment variables in your Space settings:
   - `OPENAI_API_KEY`: Your OpenAI API key

## File Structure

```
├── app.py                 # Main Gradio web app
├── database.py            # Database operations
├── llm_utils.py           # LLM utilities and prompt loading
├── coach_agent.py         # BJJ coach agent
├── game_plan_agent.py     # Tournament game plan agent
├── router_agent.py        # Smart query router
├── evaluation.py          # Evaluation and training tools
├── requirements.txt       # Python dependencies
├── prompts/               # Prompt templates
│   ├── coach_prompt_template.txt
│   ├── game_plan_agent_prompt.txt
│   ├── injury_agent_prompt.txt
│   ├── router_prompt.txt
│   └── advanced/
└── README_webapp.md       # This file
```

## Usage

1. **Coach Chat**: Ask questions about BJJ techniques, strategies, or general advice
2. **Game Plan Generator**: Provide tournament information to get personalized strategies
3. **Smart Router**: Ask any BJJ-related question and let the AI route it to the best agent
4. **Progress Tracking**: Track your learning progress for specific techniques
5. **Database Viewer**: View stored data and historical information
6. **Training Examples**: Generate examples for testing and training

## Configuration

The app uses several prompt templates located in the `prompts/` directory. You can customize these to modify agent behavior:

- `coach_prompt_template.txt`: Main coach agent prompt
- `game_plan_agent_prompt.txt`: Game plan generation prompt
- `injury_agent_prompt.txt`: Health and injury advice prompt
- `router_prompt.txt`: Query routing logic prompt

## Database

The app uses SQLite for data storage with the following tables:
- `students`: Student information
- `game_plans`: Generated tournament strategies
- `progress_tracking`: Learning progress
- `evaluation_results`: Agent performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the GitHub repository. 