import sqlite3
import pandas as pd
from src.llm_utils import use_llm_clean


def generate_examples(n=5):
    """Generate training examples for the BJJ AI agents"""
    try:
        examples_prompt = f"""
        Generate {n} diverse training examples for BJJ AI agents. 
        Each example should include:
        1. A realistic user query about BJJ
        2. The expected agent response
        3. The type of agent that should handle it (coach, game_plan, injury)
        
        Format each example as:
        Query: [user question]
        Expected Response: [detailed response]
        Agent Type: [coach/game_plan/injury]
        ---
        """
        response = use_llm_clean(examples_prompt)
        return response
    except Exception as e:
        return f"Error generating examples: {str(e)}"


def compute_section_coverage_score(
    df: pd.DataFrame, required_sections: list[str]
) -> float:
    """Compute coverage score for required sections"""
    try:
        if df.empty:
            return 0.0

        present_sections = 0
        for section in required_sections:
            if df["output_text"].str.contains(section, case=False, na=False).any():
                present_sections += 1

        return present_sections / len(required_sections)
    except Exception as e:
        print(f"Error computing coverage score: {e}")
        return 0.0


def evaluate_section_coverage(
    agent_type: str, input_text: str, output_text: str, required_sections: list[str]
) -> dict:
    """Evaluate section coverage for a specific agent response"""
    try:
        df = pd.DataFrame(
            {
                "agent_type": [agent_type],
                "input_text": [input_text],
                "output_text": [output_text],
            }
        )

        coverage_score = compute_section_coverage_score(df, required_sections)

        missing_sections = []
        for section in required_sections:
            if not df["output_text"].str.contains(section, case=False, na=False).any():
                missing_sections.append(section)

        return {
            "coverage_score": coverage_score,
            "missing_sections": missing_sections,
            "total_sections": len(required_sections),
            "covered_sections": len(required_sections) - len(missing_sections),
        }
    except Exception as e:
        return {
            "coverage_score": 0.0,
            "missing_sections": required_sections,
            "total_sections": len(required_sections),
            "covered_sections": 0,
            "error": str(e),
        }


def evaluate_agent_response(
    agent_type: str, input_text: str, output_text: str, evaluation_criteria: dict
) -> dict:
    """Evaluate an agent response based on multiple criteria"""
    try:
        results = {}

        if "required_sections" in evaluation_criteria:
            coverage_results = evaluate_section_coverage(
                agent_type,
                input_text,
                output_text,
                evaluation_criteria["required_sections"],
            )
            results["coverage"] = coverage_results

        if "min_length" in evaluation_criteria:
            min_length = evaluation_criteria["min_length"]
            actual_length = len(output_text.split())
            results["length"] = {
                "actual_length": actual_length,
                "min_required": min_length,
                "meets_requirement": actual_length >= min_length,
            }

        if "required_keywords" in evaluation_criteria:
            required_keywords = evaluation_criteria["required_keywords"]
            found_keywords = []
            for keyword in required_keywords:
                if keyword.lower() in output_text.lower():
                    found_keywords.append(keyword)

            results["relevance"] = {
                "found_keywords": found_keywords,
                "total_keywords": len(required_keywords),
                "keyword_coverage": len(found_keywords) / len(required_keywords),
            }

        return results
    except Exception as e:
        return {"error": str(e)}


def save_evaluation_results(
    agent_type: str, input_text: str, output_text: str, evaluation_results: dict
):
    """Save evaluation results to database"""
    try:
        from src.database import save_data_to_sqlite

        overall_score = 0.0
        if "coverage" in evaluation_results:
            overall_score += evaluation_results["coverage"]["coverage_score"]
        if "relevance" in evaluation_results:
            overall_score += evaluation_results["relevance"]["keyword_coverage"]

        overall_score = overall_score / 2.0

        data = {
            "agent_type": agent_type,
            "input_text": input_text,
            "output_text": output_text,
            "score": overall_score,
            "feedback": str(evaluation_results),
        }

        return save_data_to_sqlite("evaluation_results", data)
    except Exception as e:
        print(f"Error saving evaluation results: {e}")
        return False


def get_evaluation_summary(agent_type: str = None, limit: int = 10) -> str:
    """Get a summary of evaluation results"""
    try:
        conn = sqlite3.connect("bjj_app.db")

        if agent_type:
            query = """
                SELECT AVG(score) as avg_score, COUNT(*) as total_evaluations
                FROM evaluation_results 
                WHERE agent_type = ?
            """
            cursor = conn.execute(query, (agent_type,))
        else:
            query = """
                SELECT agent_type, AVG(score) as avg_score, COUNT(*) as total_evaluations
                FROM evaluation_results 
                GROUP BY agent_type
            """
            cursor = conn.execute(query)

        results = cursor.fetchall()
        conn.close()

        if not results:
            return "No evaluation results found."

        summary = "Evaluation Summary:\n"
        for row in results:
            if agent_type:
                summary += f"Average Score: {row[0]:.3f}\n"
                summary += f"Total Evaluations: {row[1]}\n"
            else:
                summary += f"{row[0]}: Avg Score {row[1]:.3f} ({row[2]} evaluations)\n"

        return summary
    except Exception as e:
        return f"Error getting evaluation summary: {str(e)}"
