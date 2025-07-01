import re
from typing import Tuple
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from src.llm_utils import load_prompt, use_llm_clean
from src.database import save_data_to_sqlite


class CoachInput(BaseModel):
    message: str
    personality: str = "james"  # Default personality


class CoachOutput(BaseModel):
    response: str


class CoachState(BaseModel):
    input: CoachInput
    output: CoachOutput = CoachOutput(response="")


def load_personality_prompt(personality: str) -> str:
    """Load a personality prompt from the personalities directory"""
    try:
        personality_path = f"prompts/personalities/{personality}.txt"
        with open(personality_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        # Return default personality if file not found
        return load_prompt("personalities/james")


def coach_node(state: CoachState) -> CoachState:
    """Coach agent node that processes user input"""
    try:
        # Load the personality prompt
        personality_prompt = load_personality_prompt(state.input.personality)

        # Load the base coach prompt
        coach_prompt = load_prompt("coach_prompt_template")

        # Combine personality and coach prompt
        combined_prompt = f"""
{personality_prompt}

{coach_prompt}

User Input: {state.input.message}

Please respond in character as the coach with the personality described above.
"""

        # Get response from LLM
        response = use_llm_clean(combined_prompt)

        # Update state
        state.output = CoachOutput(response=response)
        return state
    except Exception as e:
        state.output = CoachOutput(response=f"Error: {str(e)}")
        return state


def build_coach_graph():
    """Build the coach agent graph"""
    workflow = StateGraph(CoachState)
    workflow.add_node("coach", coach_node)
    workflow.set_entry_point("coach")
    workflow.set_finish_point("coach")
    return workflow.compile()


def run_coach_agent(user_input: str, personality: str = "james") -> str:
    """Run the coach agent with user input and personality"""
    try:
        graph = build_coach_graph()
        # Initialize state with both input and output
        initial_state = CoachState(
            input=CoachInput(message=user_input, personality=personality),
            output=CoachOutput(response=""),
        )
        result = graph.invoke(initial_state)

        # Handle different result types
        if hasattr(result, "output"):
            # Result is a state object
            return result.output.response
        elif isinstance(result, dict) and "output" in result:
            # Result is a dictionary
            return result["output"].response
        elif isinstance(result, dict) and "coach" in result:
            # Result has coach node output
            return result["coach"]["output"].response
        else:
            # Fallback - try to extract response from result
            return str(result)
    except Exception as e:
        return f"Error running coach agent: {str(e)}"


def parse_tracking_input(user_input: str) -> Tuple[str, str, str]:
    """Parse user input for progress tracking"""
    # Simple parsing - can be enhanced
    technique = ""
    level = "Beginner"
    notes = ""

    # Look for technique mentions
    technique_patterns = [
        r"technique[:\s]+([^,\n]+)",
        r"working on[:\s]+([^,\n]+)",
        r"learning[:\s]+([^,\n]+)",
        r"practicing[:\s]+([^,\n]+)",
    ]

    for pattern in technique_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            technique = match.group(1).strip()
            break

    # Look for level mentions
    level_patterns = {
        r"beginner": "Beginner",
        r"intermediate": "Intermediate",
        r"advanced": "Advanced",
        r"mastered": "Mastered",
    }

    for pattern, level_value in level_patterns.items():
        if re.search(pattern, user_input, re.IGNORECASE):
            level = level_value
            break

    # Extract notes (everything else)
    if technique:
        # Remove technique and level from notes
        notes = user_input.replace(technique, "").strip()
        for level_value in level_patterns.values():
            notes = notes.replace(level_value, "").strip()
    else:
        notes = user_input

    return technique, level, notes


def retrieve_technique_video(query: str) -> str:
    """Retrieve technique video information"""
    try:
        # This would integrate with a video database
        # For now, return a placeholder response
        video_prompt = f"""
        Based on the query: "{query}"
        
        Provide information about BJJ techniques that would be helpful.
        Include:
        1. Technique name and description
        2. Key points to remember
        3. Common mistakes to avoid
        4. Suggested video resources (if available)
        """

        return use_llm_clean(video_prompt)
    except Exception as e:
        return f"Error retrieving video: {str(e)}"


def track_student_progress(technique: str, level: str, notes: str = "") -> str:
    """Track student progress in the database"""
    try:
        # Save to database
        progress_data = {
            "technique": technique,
            "level": level,
            "notes": notes,
            "user_id": 1,  # Default user ID
        }

        success = save_data_to_sqlite("progress_tracking", progress_data)

        if success:
            return f"Progress tracked successfully!\nTechnique: {technique}\nLevel: {level}\nNotes: {notes}"
        else:
            return "Error saving progress to database"
    except Exception as e:
        return f"Error tracking progress: {str(e)}"


def coach_node_with_tools(state: CoachState) -> CoachState:
    """Coach agent node with additional tools"""
    try:
        user_input = state.input.message.lower()

        # Check if user wants to track progress
        if any(
            word in user_input
            for word in ["track", "progress", "learning", "practicing"]
        ):
            technique, level, notes = parse_tracking_input(state.input.message)

            if technique:
                progress_response = track_student_progress(technique, level, notes)
                state.output = CoachOutput(response=progress_response)
                return state

        # Check if user wants video information
        if any(
            word in user_input for word in ["video", "show me", "demonstrate", "how to"]
        ):
            video_response = retrieve_technique_video(state.input.message)
            state.output = CoachOutput(response=video_response)
            return state

        # Default coach response with personality
        return coach_node(state)
    except Exception as e:
        state.output = CoachOutput(response=f"Error: {str(e)}")
        return state


def build_coach_graph_with_tools():
    """Build the coach agent graph with tools"""
    workflow = StateGraph(CoachState)
    workflow.add_node("coach", coach_node_with_tools)
    workflow.set_entry_point("coach")
    workflow.set_finish_point("coach")
    return workflow.compile()


def run_coach_agent_with_tools(user_input: str, personality: str = "james") -> str:
    """Run the coach agent with tools"""
    try:
        graph = build_coach_graph_with_tools()
        # Initialize state with both input and output
        initial_state = CoachState(
            input=CoachInput(message=user_input, personality=personality),
            output=CoachOutput(response=""),
        )
        result = graph.invoke(initial_state)

        # Handle different result types
        if hasattr(result, "output"):
            # Result is a state object
            return result.output.response
        elif isinstance(result, dict) and "output" in result:
            # Result is a dictionary
            return result["output"].response
        elif isinstance(result, dict) and "coach" in result:
            # Result has coach node output
            return result["coach"]["output"].response
        else:
            # Fallback - try to extract response from result
            return str(result)
    except Exception as e:
        return f"Error running coach agent with tools: {str(e)}"
