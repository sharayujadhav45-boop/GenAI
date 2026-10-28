"""LLM client (HF Inference API) with local fallback, JSON parsing and retries."""
import json, os, re
from pydantic import ValidationError
from prompts import SYSTEM, REPAIR, TYPE_RULES
from schemas import Quiz

MODEL = os.getenv("MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
FALLBACK = os.getenv("FALLBACK_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
API_TIMEOUT = 60
_local = None


def _call_api(messages, max_tokens):
    from huggingface_hub import InferenceClient
    client = InferenceClient(
        model=MODEL,
        token=os.getenv("HF_TOKEN"),
        timeout=API_TIMEOUT,
    )
    out = client.chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.4,
    )
    if not out.choices:
        raise RuntimeError("The model API returned no choices.")
    content = out.choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("The model API returned an empty response.")
    return content


def _call_local(messages, max_tokens):
    global _local
    if _local is None:
        try:
            import torch  # noqa: F401
            from transformers import pipeline
        except ImportError as e:
            raise RuntimeError(
                "The local model needs PyTorch and Transformers. From the project folder, "
                "run `python -m pip install -r requirements.txt` using the same Python "
                "environment that starts this app, then restart it. Alternatively, set "
                "HF_TOKEN to use the Hugging Face Inference API."
            ) from e
        _local = pipeline("text-generation", model=FALLBACK)
    out = _local(
        messages,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.4,
    )
    generated = out[0]["generated_text"]
    if isinstance(generated, list):
        generated = generated[-1].get("content", "")
    if not isinstance(generated, str) or not generated.strip():
        raise RuntimeError("The local model returned an empty response.")
    return generated


def chat(messages, max_tokens):
    """Use the API when configured; report API and local fallback errors clearly."""
    if os.getenv("HF_TOKEN"):
        try:
            return _call_api(messages, max_tokens)
        except Exception as api_error:
            try:
                return _call_local(messages, max_tokens)
            except Exception as local_error:
                raise RuntimeError(
                    f"Hugging Face API request failed ({type(api_error).__name__}: "
                    f"{str(api_error)[:250]}). The local fallback also failed: {local_error}"
                ) from local_error
    try:
        return _call_local(messages, max_tokens)
    except Exception as local_error:
        raise RuntimeError(
            f"No HF_TOKEN is configured and the local model could not start: {local_error}"
        ) from local_error


def parse_quiz(text: str) -> Quiz:
    """Strip markdown fences, extract the JSON object, validate with Pydantic."""
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise ValueError("no JSON object found")
        data = json.loads(m.group(0))
    return Quiz(**data)


def generate_quiz(user_msg: str, n: int, retries: int = 2, qtype: str = "MCQ") -> Quiz:
    if qtype not in TYPE_RULES:
        raise ValueError(f"Unsupported question type: {qtype}")
    if n < 1:
        raise ValueError("The number of questions must be at least 1.")

    max_tokens = min(3400, max(400, 160 * n + 200))
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_msg}]
    last_err = "unknown"
    for _ in range(retries):
        raw = chat(messages, max_tokens)
        try:
            quiz = parse_quiz(raw)
            if len(quiz.questions) != n:
                raise ValueError(f"expected exactly {n} questions, got {len(quiz.questions)}")
            for question in quiz.questions:
                if qtype in ("MCQ", "Fill-in-the-blank") and len(question.options) != 4:
                    raise ValueError(f"{qtype} questions must have exactly 4 options")
                if qtype == "True/False" and {
                    option.casefold() for option in question.options
                } != {"true", "false"}:
                    raise ValueError('True/False questions must use the options "True" and "False"')
                if qtype == "Fill-in-the-blank" and "_____" not in question.question:
                    raise ValueError("Fill-in-the-blank questions must contain _____")
            return quiz
        except (ValueError, ValidationError, json.JSONDecodeError) as e:
            last_err = str(e)[:200]
            messages += [{"role": "assistant", "content": raw},
                         {"role": "user", "content": REPAIR.format(error=last_err, n=n)}]
    raise RuntimeError(f"Could not get valid quiz after {retries} tries: {last_err}")
