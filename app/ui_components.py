"""
Gradio UI components for the BJJ AI Agents System
"""

import gradio as gr
from app.user_guide import USER_GUIDE_CONTENT


def create_help_section():
    """Create the help section with accordion"""
    with gr.Accordion("📖 User Guide & Help", open=False) as help_section:
        gr.Markdown(USER_GUIDE_CONTENT)
    return help_section


def _create_agent_badge(agent_type: str, badge_color: str, text_color: str) -> str:
    """Create HTML badge for agent type"""
    return (
        f"<div style='text-align: center; padding: 8px; background: {badge_color}; "
        f"border-radius: 8px; margin-bottom: 10px;'><span style='font-size: 14px; "
        f"color: {text_color};'>{agent_type}</span></div>"
    )


def _determine_agent_type(response: str) -> tuple:
    """Determine which agent was used based on response content"""
    response_lower = response.lower()

    if (
        "coach" in response_lower
        or "technique" in response_lower
        or "training" in response_lower
    ):
        return "👨‍🏫 Coach Agent", "#d1ecf1", "#0c5460"
    elif (
        "tournament" in response_lower
        or "game plan" in response_lower
        or "strategy" in response_lower
    ):
        return "📋 Game Plan Agent", "#d4edda", "#155724"
    elif (
        "injury" in response_lower
        or "health" in response_lower
        or "recovery" in response_lower
    ):
        return "🏥 Injury Agent", "#f8d7da", "#721c24"
    else:
        return "🤖 AI Assistant", "#e2e3e5", "#383d41"


def create_enhanced_ai_chat_tab():
    """Create the Enhanced AI Chat tab"""
    with gr.TabItem("🤖 Enhanced AI Chat"):
        gr.Markdown(
            "### Premium AI Assistant - Automatically routes your query to the best specialized agent"
        )
        with gr.Row():
            with gr.Column():
                router_input = gr.Textbox(
                    label="Ask anything about BJJ",
                    placeholder="e.g., I need help with my tournament strategy...",
                    lines=3,
                )
                router_button = gr.Button("Get AI Response", variant="primary")
            with gr.Column():
                # Agent badge to show which agent is working
                ready_badge = _create_agent_badge(
                    "🤖 Ready to assist", "#f0f0f0", "#666"
                )
                agent_badge = gr.HTML(value=ready_badge, label="Current Agent")
                router_output = gr.Textbox(
                    label="AI Response", lines=10, interactive=False
                )

        # Custom function to update badge and get response
        def get_ai_response_with_badge(message):
            if not message.strip():
                return ready_badge, "Please enter a question to get started."

            try:
                # Get response from router
                response = route_query(message)

                # Determine which agent was used
                agent_type, badge_color, text_color = _determine_agent_type(response)

                # Create final badge
                final_badge = _create_agent_badge(agent_type, badge_color, text_color)

                return final_badge, response

            except Exception as e:
                error_badge = _create_agent_badge("❌ Error", "#f8d7da", "#721c24")
                return error_badge, f"Error: {str(e)}"

        router_button.click(
            fn=get_ai_response_with_badge,
            inputs=router_input,
            outputs=[agent_badge, router_output],
        )
        return router_input, router_output, router_button


def create_coach_chat_tab():
    """Create the Coach Chat tab"""
    with gr.TabItem("🤖 Coach Chat"):
        gr.Markdown("### Chat with your BJJ Coach")
        with gr.Row():
            with gr.Column():
                coach_input = gr.Textbox(
                    label="Ask your coach anything about BJJ",
                    placeholder="e.g., How do I escape from mount?",
                    lines=3,
                )
                personality_input = gr.Dropdown(
                    choices=["james", "lacey", "mat", "ryan"],
                    label="Coach Personality",
                    value="james",
                    info="Choose your coach's personality and teaching style",
                )
                use_tools_checkbox = gr.Checkbox(
                    label="Use advanced tools (video retrieval, progress tracking)",
                    value=False,
                )
                coach_button = gr.Button("Ask Coach", variant="primary")
            with gr.Column():
                coach_output = gr.Textbox(
                    label="Coach's Response", lines=10, interactive=False
                )
        coach_button.click(
            fn=chat_with_coach,
            inputs=[coach_input, personality_input, use_tools_checkbox],
            outputs=coach_output,
        )
        return coach_input, coach_output, coach_button


def create_game_plan_tab():
    """Create the Game Plan Generator tab"""
    with gr.TabItem("📋 Game Plan Generator"):
        gr.Markdown("### Generate Tournament Game Plans")
        with gr.Row():
            with gr.Column():
                game_plan_input = gr.Textbox(
                    label="Tournament Information",
                    placeholder="e.g., I'm competing in the blue belt division, 155 lbs, male, intermediate no-gi level, against aggressive opponents...",
                    lines=5,
                )
                use_rag_checkbox = gr.Checkbox(
                    label="Use RAG (Retrieval Augmented Generation) for better plans",
                    value=True,
                )
                game_plan_button = gr.Button("Generate Game Plan", variant="primary")
            with gr.Column():
                game_plan_output = gr.Textbox(
                    label="Generated Game Plan", lines=15, interactive=False
                )
        game_plan_button.click(
            fn=get_game_plan,
            inputs=[game_plan_input, use_rag_checkbox],
            outputs=game_plan_output,
        )
        return game_plan_input, game_plan_output, game_plan_button


def create_progress_tracking_tab():
    """Create the Progress Tracking tab"""
    with gr.TabItem("📊 Progress Tracking"):
        gr.Markdown("### Track Your BJJ Progress")
        with gr.Row():
            with gr.Column():
                technique_input = gr.Textbox(
                    label="Technique Name",
                    placeholder="e.g., Triangle Choke",
                    lines=1,
                )
                level_input = gr.Dropdown(
                    choices=["Beginner", "Intermediate", "Advanced", "Mastered"],
                    label="Current Level",
                    value="Beginner",
                )
                no_gi_level_input = gr.Dropdown(
                    choices=["Beginner", "Intermediate", "Advanced"],
                    label="No-Gi Level",
                    value="Beginner",
                )
                notes_input = gr.Textbox(
                    label="Notes",
                    placeholder="e.g., Struggling with the setup...",
                    lines=3,
                )
                track_button = gr.Button("Track Progress", variant="primary")
            with gr.Column():
                track_output = gr.Textbox(
                    label="Progress Update", lines=5, interactive=False
                )
        track_button.click(
            fn=track_progress,
            inputs=[technique_input, level_input, no_gi_level_input, notes_input],
            outputs=track_output,
        )
        return technique_input, track_output, track_button


def create_student_profile_tab():
    """Create the Student Profile Management tab"""
    with gr.TabItem("👤 Student Profile Management"):
        gr.Markdown("### Manage Student Profiles")
        with gr.Row():
            with gr.Column():
                name_input = gr.Textbox(
                    label="Student Name",
                    placeholder="e.g., John Doe",
                    lines=1,
                )
                age_input = gr.Number(
                    label="Age",
                    value=0,
                    minimum=0,
                    maximum=100,
                )
                weight_input = gr.Number(
                    label="Weight (lbs)",
                    value=0,
                    minimum=0,
                    maximum=300,
                )
                belt_input = gr.Dropdown(
                    choices=["White", "Blue", "Purple", "Brown", "Black", "Other"],
                    label="Belt Color",
                    value="White",
                )
                gender_input = gr.Dropdown(
                    choices=["Male", "Female"],
                    label="Gender",
                    value="Male",
                )
                no_gi_level_input = gr.Dropdown(
                    choices=["Beginner", "Intermediate", "Advanced"],
                    label="No-Gi Level",
                    value="Beginner",
                )
                save_button = gr.Button("Save Student Info", variant="primary")
            with gr.Column():
                save_output = gr.Textbox(label="Result", lines=5, interactive=False)
        save_button.click(
            fn=save_student_info,
            inputs=[
                name_input,
                age_input,
                weight_input,
                belt_input,
                gender_input,
                no_gi_level_input,
            ],
            outputs=save_output,
        )
        return name_input, save_output, save_button


def create_student_search_tab():
    """Create the Student Search tab"""
    with gr.TabItem("🔍 Student Search"):
        gr.Markdown("### Search for a Student")
        with gr.Row():
            with gr.Column():
                search_name = gr.Textbox(
                    label="Student Name",
                    placeholder="e.g., John Doe",
                    lines=1,
                )
                search_button = gr.Button("Search", variant="primary")
            with gr.Column():
                search_output = gr.Textbox(
                    label="Student Information", lines=10, interactive=False
                )
        search_button.click(
            fn=load_student_info,
            inputs=[search_name],
            outputs=search_output,
        )
        return search_name, search_output, search_button


def create_list_students_tab():
    """Create the List All Students tab"""
    with gr.TabItem("📋 List All Students"):
        gr.Markdown("### List All Students")
        with gr.Row():
            with gr.Column():
                list_button = gr.Button("List All Students", variant="primary")
            with gr.Column():
                list_output = gr.Textbox(
                    label="Student List", lines=15, interactive=False
                )
        list_button.click(
            fn=list_all_students,
            outputs=list_output,
        )
        return list_output, list_button


def create_database_viewer_tab():
    """Create the Database Viewer tab"""
    with gr.TabItem("🗄️ Database Viewer"):
        gr.Markdown("### View Database Contents")
        with gr.Row():
            with gr.Column():
                table_input = gr.Dropdown(
                    choices=["students", "game_plans", "progress_tracking"],
                    label="Select Table",
                    value="students",
                )
                db_button = gr.Button("View Data", variant="primary")
            with gr.Column():
                db_output = gr.Textbox(
                    label="Database Contents", lines=15, interactive=False
                )
        db_button.click(fn=view_database, inputs=table_input, outputs=db_output)
        return table_input, db_output, db_button


def create_training_examples_tab():
    """Create the Training Examples tab"""
    with gr.TabItem("🎲 Training Examples"):
        gr.Markdown("### Generate Training Examples")
        with gr.Row():
            with gr.Column():
                examples_count = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=5,
                    step=1,
                    label="Number of Examples",
                )
                examples_button = gr.Button("Generate Examples", variant="primary")
            with gr.Column():
                examples_output = gr.Textbox(
                    label="Generated Examples", lines=15, interactive=False
                )
        examples_button.click(
            fn=generate_training_examples,
            inputs=[examples_count],
            outputs=examples_output,
        )
        return examples_count, examples_output, examples_button


# These functions need to be imported from main.py
def route_query(message: str) -> str:
    """Placeholder - will be imported from main.py"""
    pass


def chat_with_coach(message: str, personality: str, use_tools: bool = False) -> str:
    """Placeholder - will be imported from main.py"""
    pass


def get_game_plan(tournament_info: str, use_rag: bool = False) -> str:
    """Placeholder - will be imported from main.py"""
    pass


def track_progress(technique: str, level: str, no_gi_level: str, notes: str) -> str:
    """Placeholder - will be imported from main.py"""
    pass


def save_student_info(
    name: str, age: int, weight: float, belt: str, gender: str, no_gi_level: str
) -> str:
    """Placeholder - will be imported from main.py"""
    pass


def load_student_info(name: str) -> str:
    """Placeholder - will be imported from main.py"""
    pass


def list_all_students() -> str:
    """Placeholder - will be imported from main.py"""
    pass


def view_database(table_name: str) -> str:
    """Placeholder - will be imported from main.py"""
    pass


def generate_training_examples(count: int = 5) -> str:
    """Placeholder - will be imported from main.py"""
    pass
