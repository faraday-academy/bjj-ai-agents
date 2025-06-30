from fastapi import FastAPI
import gradio as gr
from gradio_modal import Modal

from app.database import (
    init_database,
    view_all_rows,
    save_student_profile,
    get_student_by_name,
    get_all_students,
)
from app.agents.coach_agent import run_coach_agent, run_coach_agent_with_tools
from app.agents.game_plan_agent import run_game_plan_agent, run_game_plan_agent_rag
from app.agents.router_agent import run_router
from app.evaluation import generate_examples
from config import Config
from app.user_guide import USER_GUIDE_CONTENT
from app.llm_utils import use_llm_clean

Config.validate()
init_database()


def chat_with_coach(message: str, personality: str, use_tools: bool = False) -> str:
    try:
        if use_tools:
            return run_coach_agent_with_tools(message, personality)
        else:
            return run_coach_agent(message, personality)
    except Exception as e:
        return f"Error: {str(e)}"


def get_game_plan(tournament_info: str, use_rag: bool = False) -> str:
    try:
        if use_rag:
            return run_game_plan_agent_rag(tournament_info)
        else:
            return run_game_plan_agent(tournament_info)
    except Exception as e:
        return f"Error: {str(e)}"


def route_query(history) -> str:
    # Extract the latest user message from the chat history
    user_message = ""
    for msg in reversed(history):
        if msg["role"] == "user":
            user_message = msg["content"]
            break
    # Call the router agent with the latest user message
    return run_router(user_message)


def track_progress(technique: str, level: str, no_gi_level: str, notes: str) -> str:
    try:
        from app.agents.coach_agent import track_student_progress

        return track_student_progress(technique, level, no_gi_level, notes)
    except Exception as e:
        return f"Error: {str(e)}"


def view_database(table_name: str) -> str:
    try:
        data = view_all_rows(table_name)
        if isinstance(data, list) and data:
            return "\n".join([str(row) for row in data])
        else:
            return "No data found or table doesn't exist"
    except Exception as e:
        return f"Error: {str(e)}"


def generate_training_examples(count: int = 5) -> str:
    try:
        return generate_examples(count)
    except Exception as e:
        return f"Error: {str(e)}"


def save_student_info(
    name: str, age: int, weight: float, belt: str, gender: str, no_gi_level: str
) -> str:
    """Save student information to database and local storage"""
    try:
        if not name.strip():
            return "Error: Name is required"

        # Prepare student data
        student_data = {
            "name": name.strip(),
            "age": age if age > 0 else None,
            "weight": int(round(weight)) if weight > 0 else None,
            "belt_color": belt,
            "gender": gender,
            "no_gi_level": no_gi_level,
        }

        # Save to database
        student_id = save_student_profile(student_data)

        if student_id > 0:
            # Save to local storage (simulated with a message)
            storage_message = f"Profile saved to local storage for {name}"
            return f"✅ Profile saved successfully! Student ID: {student_id}\n{storage_message}"
        else:
            return "❌ Error saving profile to database"

    except Exception as e:
        return f"Error: {str(e)}"


def load_student_info(name: str) -> str:
    """Load student information from database"""
    try:
        if not name.strip():
            return "Please enter a name to search"

        student = get_student_by_name(name.strip())

        if student:
            info = f"📋 Student Profile for {student['name']}:\n"
            info += f"Age: {student['age'] or 'Not specified'}\n"
            info += f"Weight: {student['weight_class'] or 'Not specified'} lbs\n"
            info += f"Belt: {student['belt_color'] or 'Not specified'}\n"
            info += f"Gender: {student['gender'] or 'Not specified'}\n"
            info += f"No-Gi Level: {student.get('no_gi_level', 'Not specified')}\n"
            info += f"Student ID: {student['id']}"
            return info
        else:
            return f"No student found with name: {name}"

    except Exception as e:
        return f"Error: {str(e)}"


def list_all_students() -> str:
    """List all students in the database"""
    try:
        students = get_all_students()

        if students:
            result = "📚 All Students:\n\n"
            for student in students:
                result += f"• {student['name']} - {student['belt_color'] or 'No belt'} - {student['gender'] or 'Not specified'}\n"
            return result
        else:
            return "No students found in database"

    except Exception as e:
        return f"Error: {str(e)}"


# Import UI components
from app.ui_components import (
    create_help_section,
    create_enhanced_ai_chat_tab,
    create_coach_chat_tab,
    create_game_plan_tab,
    create_progress_tracking_tab,
    create_student_profile_tab,
    create_student_search_tab,
    create_list_students_tab,
    create_database_viewer_tab,
    create_training_examples_tab,
)

# Override placeholder functions with actual implementations
import app.ui_components as ui_components

ui_components.route_query = route_query
ui_components.chat_with_coach = chat_with_coach
ui_components.get_game_plan = get_game_plan
ui_components.track_progress = track_progress
ui_components.save_student_info = save_student_info
ui_components.load_student_info = load_student_info
ui_components.list_all_students = list_all_students
ui_components.view_database = view_database
ui_components.generate_training_examples = generate_training_examples


with gr.Blocks(title="BJJ AI Agents", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🥋 BJJ AI Agents System")

    # Help button in top right
    with gr.Row():
        gr.Markdown("Welcome to the Brazilian Jiu-Jitsu AI coaching system!")
        help_button = gr.Button("❓ Help & Info", size="sm", variant="secondary")

    with Modal(visible=False) as help_modal:
        gr.Markdown(USER_GUIDE_CONTENT)

    help_button.click(lambda: gr.update(visible=True), None, help_modal)

    user_profile_state = gr.State({})

    with gr.Tabs():
        # Enhanced AI Chat tab (first)
        create_enhanced_ai_chat_tab()
        # Student Profile Management tab (second)
        create_student_profile_tab(user_profile_state=user_profile_state)
        # Other tabs
        create_coach_chat_tab()
        create_game_plan_tab()
        create_progress_tracking_tab(user_profile_state=user_profile_state)
        create_database_viewer_tab()
        create_training_examples_tab()


demo.queue()

app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=Config.GRADIO_SERVER_NAME,
        port=Config.GRADIO_SERVER_PORT,
        reload=True,
    )
