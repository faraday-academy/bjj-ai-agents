import os
from pathlib import Path

from langchain_openai import ChatOpenAI

openai_api_key = os.getenv("OPENAI_API_KEY")


def load_prompt(name: str) -> str:
    """Load a prompt from the prompts directory"""
    prompt_path = Path("prompts") / f"{name}.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    else:
        raise FileNotFoundError(f"Prompt file {name}.txt not found")


def list_prompts() -> list[str]:
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


def load_all_prompts() -> dict[str, str]:
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
    model_name: str = "gpt-4o",
    temperature: float = 0.0,
    model_kwargs: dict | None = None,
) -> str:
    """Send a prompt to the specified OpenAI model and return the response content."""
    if not openai_api_key:
        raise ValueError(
            "OpenAI API key must be provided or defined as `openai_api_key` in the global scope."
        )

    try:
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            model_kwargs=model_kwargs or {},
            openai_api_key=openai_api_key,
        )
        return llm.invoke(prompt).content
    except Exception as e:
        return f"Error calling LLM: {str(e)}"


def use_llm_clean(prompt: str, **kwargs) -> str:
    return use_llm_raw(prompt, **kwargs).strip()


def get_llm_instance(
    model_name: str = "gpt-4o", temperature: float = 0.7, max_tokens: int = 1000
) -> ChatOpenAI:
    """Get a configured LLM instance"""
    return ChatOpenAI(model=model_name, temperature=temperature, max_tokens=max_tokens)


def format_prompt_with_context(base_prompt: str, context: dict[str, str]) -> str:
    """Format a prompt with context variables"""
    formatted_prompt = base_prompt
    for key, value in context.items():
        placeholder = f"{{{key}}}"
        formatted_prompt = formatted_prompt.replace(placeholder, str(value))
    return formatted_prompt
