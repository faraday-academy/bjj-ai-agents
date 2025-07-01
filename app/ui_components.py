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


def _create_agent_badge(label, color, text_color):
    """Create a styled agent badge."""
    return (
        f'<div style="background-color:{color}; color:{text_color}; '
        "padding:5px 10px; border-radius:15px; font-weight:bold; "
        f'font-size:14px; display:inline-block;">{label}</div>'
    )


def _routing_badge():
    """Badge shown during routing."""
    return _create_agent_badge("⏳ Routing...", "#ffc107", "#212529")


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
    with gr.Tab("🤖 Enhanced AI Chat"):
        gr.Markdown("## 💬 Enhanced AI Chat with Agent Routing")
        gr.Markdown(
            "The AI will automatically route your query to the best agent "
            "(Coach, Game Plan, or Injury)."
        )
        with gr.Row():
            agent_badge = gr.Markdown(
                "**Agent:** 🤖 AI Assistant", elem_id="agent_badge"
            )

        chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            bubble_full_width=False,
            avatar_images=(
                ("images/user_avatar.png"),
                ("images/bjj_bot_avatar.png"),
            ),
            height=500,
        )
        chat_history = gr.State([])

        with gr.Row():
            txt = gr.Textbox(
                scale=4,
                show_label=False,
                placeholder="Enter text and press enter, or upload an image",
                container=False,
            )
        txt.submit(
            add_message, [chatbot, chat_history, txt], [chatbot, chat_history]
        ).then(bot, [chatbot, chat_history], [chatbot, chat_history, agent_badge])
        txt.submit(lambda: gr.update(value=""), None, txt, queue=False)


def create_coach_chat_tab():
    with gr.Tab("👨‍🏫 Coach Chat"):
        gr.Markdown("## 💬 Chat with a Virtual BJJ Coach")
        with gr.Row():
            personality = gr.Dropdown(
                label="Choose a personality",
                choices=["james", "ryan", "lacey", "mat"],
                value="james",
            )
            use_tools = gr.Checkbox(label="Enable Tools", value=True)
        gr.Interface(
            fn=chat_with_coach,
            inputs=[
                gr.Textbox(lines=5, placeholder="Ask your coach anything..."),
                personality,
                use_tools,
            ],
            outputs=gr.Textbox(label="Coach's Response"),
            title="BJJ Coach",
            description="Get advice from a virtual BJJ coach with a "
            "selectable personality.",
        )


def create_game_plan_tab():
    with gr.Tab("📋 Game Plan Generator"):
        gr.Markdown("## 🏆 Generate a Competition Game Plan")
        gr.Interface(
            fn=get_game_plan,
            inputs=[
                gr.Textbox(
                    lines=5,
                    placeholder=(
                        "Enter tournament details, your style, "
                        "opponent's style, etc."
                    ),
                ),
                gr.Checkbox(label="Use RAG for Enhanced Strategy", value=False),
            ],
            outputs=gr.Textbox(label="Generated Game Plan"),
            title="Game Plan Generator",
            description="Create a strategic game plan for your next competition.",
        )


def create_progress_tracking_tab(demo, user_profile_state):
    with gr.Tab("📈 Progress Tracking"):
        gr.Markdown("## 📊 Track Your BJJ Progress")
        gr.Markdown("Log the techniques you're learning and track your proficiency.")
        with gr.Row():
            with gr.Column():
                technique_name = gr.Textbox(
                    label="Technique", placeholder="e.g., Armbar from guard"
                )
                proficiency_level = gr.Dropdown(
                    label="Proficiency Level",
                    choices=["Learning", "Practicing", "Mastered"],
                )
                no_gi_level_progress = gr.Dropdown(
                    label="No-Gi Level",
                    choices=["Beginner", "Intermediate", "Advanced"],
                    interactive=False,  # Pre-filled from profile
                )
                notes = gr.Textbox(
                    label="Notes",
                    placeholder="e.g., Struggling with posture control",
                )
                track_button = gr.Button("Track Progress", variant="primary")
            with gr.Column():
                tracking_output = gr.Textbox(
                    label="Confirmation",
                    interactive=False,
                    placeholder="Tracking status will appear here",
                )

        # Pre-fill from profile state
        demo.load(
            lambda profile: profile.get("no_gi_level", "Beginner"),
            [user_profile_state],
            [no_gi_level_progress],
        )

        track_button.click(
            fn=track_progress,
            inputs=[
                technique_name,
                proficiency_level,
                no_gi_level_progress,
                notes,
            ],
            outputs=tracking_output,
        )


def create_student_profile_tab(user_profile_state):
    with gr.Tab("👤 Student Profile Management"):
        gr.Markdown("## 📝 Manage Your Profile")
        gr.Markdown(
            "Keep your profile up-to-date for personalized advice. "
            "This profile will be used by all agents."
        )
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🥋 Gi Information")
                student_name = gr.Textbox(label="Name", placeholder="Enter your name")
                belt_color = gr.Dropdown(
                    label="Belt Color",
                    choices=["White", "Blue", "Purple", "Brown", "Black"],
                )
            with gr.Column():
                gr.Markdown("### 🤼 No-Gi Information")
                no_gi_level = gr.Dropdown(
                    label="No-Gi Level",
                    choices=["Beginner", "Intermediate", "Advanced"],
                )
                student_weight = gr.Number(label="Weight (lbs)", precision=0)
        student_age = gr.Slider(minimum=5, maximum=100, label="Age", step=1)
        student_gender = gr.Radio(label="Gender", choices=["Male", "Female"])
        save_button = gr.Button("Save Profile", variant="primary")
        output_status = gr.Textbox(
            label="Status",
            interactive=False,
            placeholder="Save status will appear here",
        )

        save_button.click(
            fn=save_student_info,
            inputs=[
                student_name,
                student_age,
                student_weight,
                belt_color,
                student_gender,
                no_gi_level,
            ],
            outputs=output_status,
        )

        # Update state on save
        save_button.click(
            fn=lambda name, age, weight, belt, gender, nogi: {
                "name": name,
                "age": age,
                "weight": weight,
                "belt": belt,
                "gender": gender,
                "no_gi_level": nogi,
            },
            inputs=[
                student_name,
                student_age,
                student_weight,
                belt_color,
                student_gender,
                no_gi_level,
            ],
            outputs=user_profile_state,
        )


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
    with gr.Tab("🗃️ Database Viewer"):
        gr.Markdown("## 🔍 View Database Tables")
        gr.Markdown("Inspect the raw data stored in the application's database.")
        with gr.Row():
            table_name = gr.Dropdown(
                label="Select Table",
                choices=[
                    "students",
                    "progress_tracking",
                    "game_plans",
                ],
            )
            view_button = gr.Button("View Table", variant="primary")
        with gr.Row():
            db_output = gr.Textbox(label="Table Data", lines=20, interactive=False)
        view_button.click(fn=view_database, inputs=[table_name], outputs=db_output)


def create_training_examples_tab():
    with gr.Tab("🥋 Training Examples"):
        gr.Markdown("## 💡 Generate Training Scenarios")
        gr.Markdown(
            "Create random training scenarios to test your knowledge "
            "and decision-making."
        )
        with gr.Row():
            gen_examples_btn = gr.Button("🧠 Generate Examples", variant="primary")
        with gr.Row():
            examples_output = gr.Textbox(
                label="Generated Scenarios", lines=10, interactive=False
            )
        gen_examples_btn.click(
            fn=generate_training_examples, inputs=None, outputs=examples_output
        )


def create_resources_tab():
    with gr.Tab("📚 Resources"):
        gr.Markdown("## 📚 External Resources")
        gr.Markdown(
            "A collection of blogs, videos, and other resources "
            "to be used by the AI agents."
        )
        # Placeholder for resource management UI
        gr.Textbox(
            label="YouTube Channels",
            placeholder="Enter YouTube channel URLs, one per line",
        )
        gr.Textbox(
            label="Blog Articles", placeholder="Enter blog article URLs, one per line"
        )
        gr.Button("Save Resources")
        gr.Markdown(
            "### Future functionality: Web scraping and JSON management "
            "will be implemented here."
        )


# Placeholder functions for Gradio callbacks
route_query = lambda x: "Routing..."
chat_with_coach = lambda x, y, z: "Coach says hi"
get_game_plan = lambda x, y: "Here's your game plan"
track_progress = lambda w, x, y, z: "Progress tracked"
save_student_info = lambda a, b, c, d, e, f: "Profile saved"
load_student_info = lambda x: "Student loaded"
list_all_students = lambda: "All students listed"
view_database = lambda x: "Database view"
generate_training_examples = lambda: "Here are some examples"
add_message = lambda a, b, c: (a, b)
bot = lambda a, b: (a, b, "Agent: AI Assistant")
