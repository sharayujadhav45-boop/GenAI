---
title: AI Quiz and MCQ Generator
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# AI Quiz & MCQ Generator Using Generative AI

Generates MCQ / True-False / Fill-in-the-blank quizzes from a topic, pasted text or PDF.

**Pipeline:** input → (PDF or pasted text → chunks → lightweight keyword-ranked top-k) → prompt → Qwen2.5-1.5B-Instruct by default (override with `MODEL_ID`; local Qwen2.5-1.5B fallback) → JSON parse + Pydantic validation + one repair retry → question preview / interactive quiz / CSV / PDF.

The quiz validates the requested question count, unique non-empty questions and options, valid answer indexes, and question-type-specific option formats. Correct answers are hidden in the preview and shown in quiz feedback only after submission. Generation defaults to a smaller, faster model, uses a tighter question-count-based response limit and concise explanations, retries once to repair invalid model output, and times out stalled Hugging Face API requests after 60 seconds before trying the local fallback. Note/PDF retrieval uses lightweight keyword ranking instead of loading a separate embedding model. Generation time and any generation errors are shown in the app. CSV and PDF downloads become available when generation succeeds.

## Run locally
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:HF_TOKEN = "hf_xxx"   # Recommended: Hugging Face Inference API
python app.py
```

Without `HF_TOKEN`, the app loads the local Qwen fallback model the first time it is used; this downloads the model and requires sufficient memory. Install all dependencies first with `python -m pip install -r requirements.txt`. Run that command in the same activated environment used to start the app. If generation fails, the app reports whether the API request or local fallback failed.

## Deploy on Hugging Face Spaces
1. Create a Space (SDK: Gradio). 2. Settings → Secrets → add `HF_TOKEN`.
3. Push these files: `git add . && git commit -m init && git push`.

## Limitations
PDF export uses latin-1 fonts (Hindi displays in the app and CSV, but may not render correctly in the PDF); scanned PDFs need OCR; free API has rate limits. PDF uploads are limited to 10 MB, and pasted text must contain at least 30 words.
# GenAI
