from langgraph.graph import StateGraph
from pydantic import BaseModel
from src.llm_utils import load_prompt, use_llm_clean


class InjuryInput(BaseModel):
    message: str


class InjuryOutput(BaseModel):
    response: str


class InjuryState(BaseModel):
    input: InjuryInput
    output: InjuryOutput = InjuryOutput(response="")


def injury_node(state: InjuryState) -> InjuryState:
    """Injury agent node that processes user input"""
    try:
        # Load the injury agent prompt
        injury_prompt = load_prompt("injury_agent_prompt")

        formatted_prompt = injury_prompt.format(user_input=state.input.message)

        response = use_llm_clean(formatted_prompt)
        state.output = InjuryOutput(response=response)
        return state
    except Exception as e:
        state.output = InjuryOutput(response=f"Error: {str(e)}")
        return state


def build_injury_graph():
    """Build the injury agent graph"""
    workflow = StateGraph(InjuryState)
    workflow.add_node("injury", injury_node)
    workflow.set_entry_point("injury")
    workflow.set_finish_point("injury")
    return workflow.compile()


def run_injury_agent(user_input: str) -> str:
    """Run the injury agent with user input"""
    try:
        graph = build_injury_graph()
        initial_state = InjuryState(
            input=InjuryInput(message=user_input), output=InjuryOutput(response="")
        )
        result = graph.invoke(initial_state)
        return result.output.response
    except Exception as e:
        return f"Error running injury agent: {str(e)}"
