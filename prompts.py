"""Prompt templates."""

SYSTEM = """You are an expert exam setter. Output ONLY valid JSON, no markdown, no commentary.
Schema: {"questions":[{"question":str,"options":[str,...],"answer_index":int,"explanation":str}]}
Rules:
- Exactly one correct option; answer_index is its 0-based position.
- Every question, option, and explanation must be non-empty; options and questions must be unique.
- Distractors must be plausible. Never use "all of the above" / "none of the above".
- No duplicate questions. Vary the position of the correct answer.
- If CONTEXT is given, every question must be answerable from the context only.
- Keep questions and options concise. Explanation: one concise sentence justifying the answer."""

TYPE_RULES = {
    "MCQ": "4 options each.",
    "True/False": 'options must be exactly ["True","False"].',
    "Fill-in-the-blank": "question contains a blank '_____'; 4 options for the missing word.",
}


def user_prompt(topic, context, n, difficulty, qtype, language, bloom):
    parts = [f"Create {n} {qtype} questions. Difficulty: {difficulty}. Language: {language}.",
             TYPE_RULES[qtype]]
    if bloom and bloom != "Any":
        parts.append(f"Target Bloom's taxonomy level: {bloom}.")
    if topic:
        parts.append(f"Topic: {topic}")
    if context:
        parts.append(f"CONTEXT:\n{context}")
    return "\n".join(parts)


REPAIR = ("Your previous output was invalid ({error}). Return ONLY corrected JSON "
          "matching the schema, with exactly {n} questions. Preserve the requested question type.")
