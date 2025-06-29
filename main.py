# (The full content of app.py, but with imports updated to use app and app.agents)

import gradio as gr
from app.config import Config
from app.database import init_database, view_all_rows
from app.agents.coach_agent import run_coach_agent, run_coach_agent_with_tools
from app.agents.game_plan_agent import run_game_plan_agent, run_game_plan_agent_rag
from app.agents.router_agent import run_router
from app.evaluation import generate_examples

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


def route_query(message: str) -> str:
    try:
        return run_router(message)
    except Exception as e:
        return f"Error: {str(e)}"


def track_progress(
    technique: str, level: str, notes: str, gender: str, no_gi_level: str
) -> str:
    try:
        from app.agents.coach_agent import track_student_progress

        # Include gender and no-gi level in the tracking
        progress_info = f"Gender: {gender}, No-Gi Level: {no_gi_level}\n"
        return progress_info + track_student_progress(technique, level, notes)
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


with gr.Blocks(title="BJJ AI Agents", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🥋 BJJ AI Agents System")
    gr.Markdown("Welcome to the Brazilian Jiu-Jitsu AI coaching system!")

    with gr.Tabs():
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
                    game_plan_button = gr.Button(
                        "Generate Game Plan", variant="primary"
                    )
                with gr.Column():
                    game_plan_output = gr.Textbox(
                        label="Generated Game Plan", lines=15, interactive=False
                    )
            game_plan_button.click(
                fn=get_game_plan,
                inputs=[game_plan_input, use_rag_checkbox],
                outputs=game_plan_output,
            )

        with gr.TabItem("🎯 Smart Router"):
            gr.Markdown(
                "### AI Router - Automatically routes your query to the best agent"
            )
            with gr.Row():
                with gr.Column():
                    router_input = gr.Textbox(
                        label="Ask anything about BJJ",
                        placeholder="e.g., I need help with my tournament strategy...",
                        lines=3,
                    )
                    router_button = gr.Button("Route Query", variant="primary")
                with gr.Column():
                    router_output = gr.Textbox(
                        label="Response", lines=10, interactive=False
                    )
            router_button.click(
                fn=route_query, inputs=router_input, outputs=router_output
            )

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
                    gender_input = gr.Dropdown(
                        choices=["Male", "Female", "Other"],
                        label="Gender",
                        value="Male",
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
                inputs=[
                    technique_input,
                    level_input,
                    notes_input,
                    gender_input,
                    no_gi_level_input,
                ],
                outputs=track_output,
            )

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

if __name__ == "__main__":
    demo.launch(
        server_name=Config.GRADIO_SERVER_NAME,
        server_port=Config.GRADIO_SERVER_PORT,
        share=True,
    )
