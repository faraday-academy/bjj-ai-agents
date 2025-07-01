import re
from typing import Optional
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from src.llm_utils import load_prompt, use_llm_clean
from src.database import save_data_to_sqlite, get_game_plans_by_user


class GamePlanInput(BaseModel):
    message: str


class GamePlanOutput(BaseModel):
    response: str


class GamePlanState(BaseModel):
    input: GamePlanInput
    output: GamePlanOutput = GamePlanOutput(response="")


class TournamentInfo(BaseModel):
    division: str = ""
    weight_class: str = ""
    opponent_style: str = ""
    tournament_name: str = ""
    user_style: str = ""
    goals: str = ""
    gender: str = ""
    no_gi_level: str = ""


def extract_tournament_info(user_input: str) -> TournamentInfo:
    """Extract tournament information from user input"""
    info = TournamentInfo()

    # Simple extraction - can be enhanced with more sophisticated parsing
    user_input_lower = user_input.lower()

    # Extract division
    divisions = ["white belt", "blue belt", "purple belt", "brown belt", "black belt"]
    for division in divisions:
        if division in user_input_lower:
            info.division = division
            break

    # Extract gender
    gender_patterns = {
        r"male": "male",
        r"female": "female",
        r"men": "male",
        r"women": "female",
        r"guy": "male",
        r"girl": "female",
    }

    for pattern, gender in gender_patterns.items():
        if re.search(pattern, user_input_lower):
            info.gender = gender
            break

    # Extract no-gi level
    no_gi_levels = ["beginner", "intermediate", "advanced"]
    for level in no_gi_levels:
        if level in user_input_lower:
            info.no_gi_level = level
            break

    # Extract weight class
    weight_patterns = [
        r"(\d+)\s*lbs",
        r"(\d+)\s*kg",
        r"featherweight",
        r"lightweight",
        r"middleweight",
        r"heavyweight",
    ]

    for pattern in weight_patterns:
        if re.search(pattern, user_input_lower):
            info.weight_class = pattern
            break

    # Extract opponent style
    style_keywords = {
        "aggressive": "aggressive",
        "defensive": "defensive",
        "technical": "technical",
        "athletic": "athletic",
        "experienced": "experienced",
    }

    for keyword, style in style_keywords.items():
        if keyword in user_input_lower:
            info.opponent_style = style
            break

    return info


def get_missing_info_prompt(info: TournamentInfo) -> Optional[str]:
    """Generate prompt for missing information"""
    missing = []

    if not info.division:
        missing.append("belt division")
    if not info.weight_class:
        missing.append("weight class")
    if not info.opponent_style:
        missing.append("opponent style")
    if not info.gender:
        missing.append("gender")
    if not info.no_gi_level:
        missing.append("no-gi level")

    if missing:
        return f"Please provide: {', '.join(missing)}"
    return None


def build_game_plan(info: TournamentInfo) -> str:
    """Build a game plan based on tournament information"""
    try:
        # Load the game plan prompt
        game_plan_prompt = load_prompt("game_plan_agent_prompt")

        # Format the prompt with tournament info
        formatted_prompt = game_plan_prompt.format(
            division=info.division or "your division",
            weight_class=info.weight_class or "your weight class",
            opponent_style=info.opponent_style or "various styles",
            tournament_name=info.tournament_name or "the tournament",
            user_style=info.user_style or "your style",
            goals=info.goals or "winning",
            gender=info.gender or "your gender",
            no_gi_level=info.no_gi_level or "your no-gi level",
        )

        return use_llm_clean(formatted_prompt)
    except Exception as e:
        return f"Error building game plan: {str(e)}"


def game_plan_node(state: GamePlanState) -> GamePlanState:
    """Game plan agent node"""
    try:
        user_input = state.input.message

        # Extract tournament information
        info = extract_tournament_info(user_input)

        # Check for missing information
        missing_prompt = get_missing_info_prompt(info)
        if missing_prompt:
            response = (
                f"I need more information to create a game plan. {missing_prompt}"
            )
            state.output = GamePlanOutput(response=response)
            return state

        # Build the game plan
        game_plan = build_game_plan(info)
        state.output = GamePlanOutput(response=game_plan)
        return state
    except Exception as e:
        state.output = GamePlanOutput(response=f"Error: {str(e)}")
        return state


def build_game_plan_graph():
    """Build the game plan agent graph"""
    workflow = StateGraph(GamePlanState)
    workflow.add_node("game_plan", game_plan_node)
    workflow.set_entry_point("game_plan")
    workflow.set_finish_point("game_plan")
    return workflow.compile()


def run_game_plan_agent(user_input: str) -> str:
    """Run the game plan agent"""
    try:
        graph = build_game_plan_graph()
        initial_state = GamePlanState(
            input=GamePlanInput(message=user_input), output=GamePlanOutput(response="")
        )
        result = graph.invoke(initial_state)
        return result.output.response
    except Exception as e:
        return f"Error running game plan agent: {str(e)}"


# RAG-enhanced game plan agent
class GamePlanStateRAG(BaseModel):
    input: GamePlanInput
    output: GamePlanOutput
    context: str = ""


def get_examples_by_age_belt(user_id: int, age: int, belt: str, limit: int = 1) -> str:
    """Get examples from database based on age and belt"""
    try:
        # This would query the database for relevant examples
        # For now, return a placeholder
        return f"Examples for {age} year old {belt} belt practitioners"
    except Exception as e:
        return f"Error getting examples: {str(e)}"


def run_game_plan_agent_rag(user_input: str) -> str:
    """Run the game plan agent with RAG"""
    try:
        # Load the RAG-enhanced prompt
        rag_prompt = load_prompt("advanced/game_plan_agent_with_rag")

        # Get context from database (simplified)
        context = get_examples_by_age_belt(1, 25, "blue belt", 3)

        # Format the prompt with context
        formatted_prompt = rag_prompt.format(user_input=user_input, context=context)

        return use_llm_clean(formatted_prompt)
    except Exception as e:
        return f"Error running RAG game plan agent: {str(e)}"


def save_game_plan(user_id: int, info: TournamentInfo, plan: str):
    """Save game plan to database"""
    try:
        game_plan_data = {
            "user_id": user_id,
            "tournament_name": info.tournament_name,
            "division": info.division,
            "weight_class": info.weight_class,
            "opponent_style": info.opponent_style,
            "game_plan": plan,
        }

        return save_data_to_sqlite("game_plans", game_plan_data)
    except Exception as e:
        print(f"Error saving game plan: {e}")
        return False


def view_gameplan_by_id(plan_id: int):
    """View a specific game plan by ID"""
    try:
        # This would query the database for a specific game plan
        # For now, return a placeholder
        return f"Game plan {plan_id} details would be displayed here"
    except Exception as e:
        return f"Error viewing game plan: {str(e)}"
