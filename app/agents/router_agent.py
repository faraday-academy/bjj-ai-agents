from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Optional
from app.llm_utils import load_prompt, use_llm_clean
from app.agents.coach_agent import run_coach_agent
from app.agents.game_plan_agent import run_game_plan_agent


class TournamentInfo(BaseModel):
    division: str = ""
    weight_class: str = ""
    opponent_style: str = ""
    tournament_name: str = ""


class SharedState(BaseModel):
    input: str
    output: str = ""
    agent_type: str = ""
    tournament_info: Optional[TournamentInfo] = None


def llm_router(state: SharedState) -> str:
    """Use LLM to determine which agent should handle the query"""
    try:
        router_prompt = load_prompt("router_prompt")

        formatted_prompt = router_prompt.format(user_input=state.input)

        response = use_llm_clean(formatted_prompt)

        # Parse the response to determine agent type
        response_lower = response.lower()

        if "coach" in response_lower:
            return "coach"
        elif "game_plan" in response_lower or "tournament" in response_lower:
            return "game_plan"
        elif "injury" in response_lower or "health" in response_lower:
            return "injury"
        else:
            return "coach"  # Default to coach
    except Exception as e:
        print(f"Error in router: {e}")
        return "coach"


def coach_node_simple(state: SharedState) -> dict:
    """Simple coach node"""
    try:
        response = run_coach_agent(state.input)
        state.output = response
        state.agent_type = "coach"
        return {"output": response, "agent_type": "coach"}
    except Exception as e:
        error_msg = f"Error in coach agent: {str(e)}"
        state.output = error_msg
        return {"output": error_msg, "agent_type": "coach"}


def game_plan_node_simple(state: SharedState) -> dict:
    """Simple game plan node"""
    try:
        response = run_game_plan_agent(state.input)
        state.output = response
        state.agent_type = "game_plan"
        return {"output": response, "agent_type": "game_plan"}
    except Exception as e:
        error_msg = f"Error in game plan agent: {str(e)}"
        state.output = error_msg
        return {"output": error_msg, "agent_type": "game_plan"}


def injury_node_simple(state: SharedState) -> dict:
    """Simple injury/health node"""
    try:
        # Load injury agent prompt
        injury_prompt = load_prompt("injury_agent_prompt")

        formatted_prompt = injury_prompt.format(user_input=state.input)

        response = use_llm_clean(formatted_prompt)
        state.output = response
        state.agent_type = "injury"
        return {"output": response, "agent_type": "injury"}
    except Exception as e:
        error_msg = f"Error in injury agent: {str(e)}"
        state.output = error_msg
        return {"output": error_msg, "agent_type": "injury"}


def build_router_graph():
    """Build the router graph"""
    workflow = StateGraph(SharedState)

    # Add nodes
    workflow.add_node("router", llm_router)
    workflow.add_node("coach", coach_node_simple)
    workflow.add_node("game_plan", game_plan_node_simple)
    workflow.add_node("injury", injury_node_simple)

    # Set entry point
    workflow.set_entry_point("router")

    # Add conditional edges
    workflow.add_conditional_edges(
        "router",
        lambda x: x["router"],
        {"coach": "coach", "game_plan": "game_plan", "injury": "injury"},
    )

    # Add edges to end
    workflow.add_edge("coach", END)
    workflow.add_edge("game_plan", END)
    workflow.add_edge("injury", END)

    return workflow.compile()


def run_router(user_input: str) -> str:
    """Run the router agent"""
    try:
        graph = build_router_graph()
        result = graph.invoke({"input": user_input})
        return result["output"]
    except Exception as e:
        return f"Error running router: {str(e)}"


def should_delegate_to_game_plan(state: SharedState) -> bool:
    """Determine if query should be delegated to game plan agent"""
    user_input_lower = state.input.lower()

    game_plan_keywords = [
        "tournament",
        "competition",
        "game plan",
        "strategy",
        "division",
        "weight class",
        "opponent",
        "match",
    ]

    return any(keyword in user_input_lower for keyword in game_plan_keywords)


def should_delegate_to_injury(state: SharedState) -> bool:
    """Determine if query should be delegated to injury agent"""
    user_input_lower = state.input.lower()

    injury_keywords = [
        "injury",
        "pain",
        "hurt",
        "recovery",
        "health",
        "medical",
        "doctor",
        "treatment",
        "rehab",
    ]

    return any(keyword in user_input_lower for keyword in injury_keywords)
