from pathlib import Path
from typing import Dict, List
from langchain_openai import ChatOpenAI


def load_prompt(name: str) -> str:
    """Load a prompt from the prompts directory"""
    prompt_path = Path("prompts") / f"{name}.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    else:
        raise FileNotFoundError(f"Prompt file {name}.txt not found")


def list_prompts() -> List[str]:
    """List all available prompts"""
    prompt_dir = Path("prompts")
    if not prompt_dir.exists():
        return []

    prompts = []
    for file_path in prompt_dir.rglob("*.txt"):
        relative_path = file_path.relative_to(prompt_dir)
        prompt_name = str(relative_path).replace(".txt", "")
        prompts.append(prompt_name)

    return sorted(prompts)


def load_all_prompts() -> Dict[str, str]:
    """Load all prompts into a dictionary"""
    prompts = {}
    for prompt_name in list_prompts():
        try:
            prompts[prompt_name] = load_prompt(prompt_name)
        except Exception as e:
            print(f"Error loading prompt {prompt_name}: {e}")
    return prompts


def use_llm_raw(
    prompt: str,
    model_name: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    **kwargs,
) -> str:
    """Use LLM with raw prompt"""
    try:
        llm = ChatOpenAI(
            model=model_name, temperature=temperature, max_tokens=max_tokens, **kwargs
        )
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error calling LLM: {str(e)}"


def use_llm_clean(prompt: str, **kwargs) -> str:
    """Use LLM with cleaned prompt (removes markdown formatting)"""
    try:
        cleaned_prompt = prompt.replace("```", "").strip()
        return use_llm_raw(cleaned_prompt, **kwargs)
    except Exception as e:
        return f"Error processing prompt: {str(e)}"


def get_llm_instance(
    model_name: str = "gpt-4", temperature: float = 0.7, max_tokens: int = 1000
) -> ChatOpenAI:
    """Get a configured LLM instance"""
    return ChatOpenAI(model=model_name, temperature=temperature, max_tokens=max_tokens)


def format_prompt_with_context(base_prompt: str, context: Dict[str, str]) -> str:
    """Format a prompt with context variables"""
    formatted_prompt = base_prompt
    for key, value in context.items():
        placeholder = f"{{{key}}}"
        formatted_prompt = formatted_prompt.replace(placeholder, str(value))
    return formatted_prompt
