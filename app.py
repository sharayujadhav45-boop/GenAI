"""Gradio UI for the AI Quiz & MCQ Generator with Beautiful Peach Light Theme."""
import time
import gradio as gr
from fastapi import FastAPI
from prompts import user_prompt
from llm import MODEL, generate_quiz
from rag import extract_pdf_text, retrieve
from export import to_csv, to_pdf

# ------------------------------------------------------------------------------
# THEME CONFIGURATION (Light Theme with Curated Peach Palette)
# ------------------------------------------------------------------------------
peach_hue = gr.themes.colors.Color(
    name="peach",
    c50="#fff8f5",
    c100="#ffede5",
    c200="#fed9cc",
    c300="#fdbba6",
    c400="#fb9475",
    c500="#f77348",
    c600="#e5552b",
    c700="#c23e18",
    c800="#9f3316",
    c900="#812c16",
    c950="#461408",
)

warm_neutral = gr.themes.colors.Color(
    name="warm_neutral",
    c50="#faf7f5",
    c100="#f5eee9",
    c200="#eadece",
    c300="#d7c5ba",
    c400="#bca89d",
    c500="#9d887d",
    c600="#7e6b61",
    c700="#635249",
    c800="#493b34",
    c900="#312621",
    c950="#1c1512",
)

PEACH_THEME = gr.themes.Soft(
    primary_hue=peach_hue,
    secondary_hue=peach_hue,
    neutral_hue=warm_neutral,
    font=[
        gr.themes.GoogleFont("Plus Jakarta Sans"),
        gr.themes.GoogleFont("Inter"),
        "Segoe UI",
        "sans-serif",
    ],
    font_mono=[
        gr.themes.GoogleFont("JetBrains Mono"),
        "Consolas",
        "monospace",
    ],
).set(
    body_text_color="#1a0f0a",
    body_text_color_dark="#1a0f0a",
    body_text_color_subdued="#59463e",
    body_text_color_subdued_dark="#59463e",
    block_label_text_color="#1a0f0a",
    block_label_text_color_dark="#1a0f0a",
    block_title_text_color="#1a0f0a",
    block_title_text_color_dark="#1a0f0a",
    body_background_fill="#fffaf7",
    body_background_fill_dark="#fffaf7",
    block_background_fill="#ffffff",
    block_background_fill_dark="#ffffff",
    block_border_width="1px",
    block_border_color="#fce3d6",
    block_border_color_dark="#fce3d6",
    block_shadow="0 8px 24px -4px rgba(245, 115, 72, 0.07)",
    block_radius="18px",
    button_primary_background_fill="linear-gradient(135deg, #ff8a65 0%, #f4511e 100%)",
    button_primary_background_fill_hover="linear-gradient(135deg, #ff784f 0%, #e64a19 100%)",
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
    button_primary_border_color="transparent",
    button_primary_shadow="0 4px 16px rgba(244, 81, 30, 0.28)",
    button_secondary_background_fill="#fff4ed",
    button_secondary_background_fill_hover="#ffede2",
    button_secondary_text_color="#c23e18",
    button_secondary_text_color_dark="#c23e18",
    button_secondary_border_color="#fed7c5",
    input_background_fill="#ffffff",
    input_background_fill_dark="#ffffff",
    input_border_color="#fedbc9",
    input_border_color_dark="#fedbc9",
    input_border_color_focus="#f77348",
    checkbox_label_text_color="#1a0f0a",
    checkbox_label_text_color_dark="#1a0f0a",
    checkbox_label_text_color_selected="#c23e18",
    checkbox_label_text_color_selected_dark="#c23e18",
    checkbox_label_background_fill_selected="#fff1e8",
    checkbox_border_color_selected="#f77348",
)

# ------------------------------------------------------------------------------
# ADVANCED CUSTOM CSS FOR PEACH LIGHT AESTHETICS
# ------------------------------------------------------------------------------
APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root, .dark {
    color-scheme: light !important;
    --peach-50: #fff9f6;
    --peach-100: #ffede3;
    --peach-200: #fedbc9;
    --peach-300: #fdbba2;
    --peach-400: #fa9575;
    --peach-500: #f56d47;
    --peach-600: #e24f26;
    --peach-700: #be3c18;
    --peach-grad: linear-gradient(135deg, #ff8a65 0%, #f4511e 100%);
    --peach-grad-hover: linear-gradient(135deg, #ff784f 0%, #e64a19 100%);
    --peach-subtle-grad: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 245, 238, 0.94) 100%);
    --ink-dark: #1a0f0a;
    --ink-body: #241812;
    --ink-muted: #59463e;
    --card-border: #fce3d6;
    --card-shadow: 0 10px 32px -4px rgba(245, 109, 71, 0.08), 0 3px 10px -2px rgba(245, 109, 71, 0.04);
    --body-text-color: #1a0f0a !important;
    --body-text-color-subdued: #59463e !important;
    --tw-prose-body: #241812 !important;
    --tw-prose-headings: #1a0f0a !important;
    --tw-prose-bold: #1a0f0a !important;
}

html, body, .gradio-container, .dark, .dark body, .dark .gradio-container {
    background: radial-gradient(circle at 5% 5%, #fff7f2 0%, #fffbf8 45%, #fff3ec 100%) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: #241812 !important;
    min-height: 100vh;
}

.gradio-container {
    max-width: 1140px !important;
    margin: 0 auto !important;
    padding: 2.5rem 1.5rem 4rem !important;
}

/* ==========================================================================
   HERO BANNER
   ========================================================================== */
#hero-banner {
    background: var(--peach-subtle-grad) !important;
    border: 1.5px solid var(--peach-200) !important;
    border-radius: 24px !important;
    padding: 2.4rem 2.6rem !important;
    margin-bottom: 2rem !important;
    box-shadow: 0 16px 40px -8px rgba(245, 109, 71, 0.14), 0 4px 14px -2px rgba(245, 109, 71, 0.05) !important;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}

#hero-banner::after {
    content: "";
    position: absolute;
    top: -60px;
    right: -60px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, rgba(254, 219, 201, 0.6) 0%, rgba(255, 255, 255, 0) 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 14px;
    background: #fff0e7;
    border: 1px solid #fed2be;
    border-radius: 999px;
    color: #c23e18;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.pulsing-gem {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #f56d47;
    box-shadow: 0 0 0 0 rgba(245, 109, 71, 0.7);
    animation: pulse-dot 1.8s infinite;
}

@keyframes pulse-dot {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 109, 71, 0.6); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(245, 109, 71, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 109, 71, 0); }
}

.hero-version-tag {
    font-size: 0.8rem;
    font-weight: 600;
    color: #a4533a;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid #ffd8c7;
    padding: 4px 10px;
    border-radius: 8px;
}

.hero-title-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.5rem;
}

.hero-main-title {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    letter-spacing: -0.03em !important;
    background: linear-gradient(135deg, #2b1810 0%, #c23e18 55%, #f56d47 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-peach-sparkle {
    font-size: 2rem;
    animation: gentle-bounce 2.6s infinite ease-in-out;
}

@keyframes gentle-bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
}

.hero-desc {
    font-size: 1.05rem !important;
    color: var(--ink-secondary) !important;
    line-height: 1.65 !important;
    max-width: 780px !important;
    margin: 0 0 1.4rem 0 !important;
}

.hero-features-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.feature-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 13px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #fedccb;
    border-radius: 999px;
    color: #923418;
    font-size: 0.83rem;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(245, 109, 71, 0.05);
    transition: all 0.2s ease;
}

.feature-chip:hover {
    background: #fff5ee;
    border-color: #fdbba2;
    transform: translateY(-1px);
}

.chip-icon {
    font-size: 0.95rem;
}

/* ==========================================================================
   CARDS & SECTIONS
   ========================================================================== */
.section-card {
    background: #ffffff !important;
    border: 1.5px solid var(--card-border) !important;
    border-radius: 20px !important;
    padding: 1.6rem !important;
    box-shadow: var(--card-shadow) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.section-card:hover {
    border-color: var(--peach-300) !important;
    box-shadow: 0 14px 38px -4px rgba(245, 109, 71, 0.11), 0 4px 12px -2px rgba(245, 109, 71, 0.04) !important;
}

.section-card h3 {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: var(--ink-dark) !important;
    letter-spacing: -0.015em !important;
    margin-top: 0 !important;
    margin-bottom: 1rem !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ==========================================================================
   TABS STYLING
   ========================================================================== */
.gradio-container [role="tablist"] {
    border-bottom: 2px solid var(--peach-200) !important;
    gap: 10px !important;
    margin-bottom: 1.75rem !important;
    background: transparent !important;
}

.gradio-container [role="tab"] {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: var(--ink-muted) !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 0.75rem 1.6rem !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.2s ease !important;
}

.gradio-container [role="tab"]:hover {
    color: var(--peach-600) !important;
    background: rgba(255, 240, 231, 0.6) !important;
}

.gradio-container [role="tab"][aria-selected="true"] {
    color: #c23e18 !important;
    background: #fff0e7 !important;
    border-bottom: 3.5px solid var(--peach-500) !important;
    font-weight: 700 !important;
}

/* ==========================================================================
   BUTTONS
   ========================================================================== */
.gradio-container button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    border-radius: 13px !important;
    font-weight: 600 !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    letter-spacing: 0.01em !important;
}

.gradio-container button.primary,
#generate-button button,
#start-quiz-btn button {
    background: var(--peach-grad) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 0.85rem 1.8rem !important;
    min-height: 3.2rem !important;
    box-shadow: 0 6px 20px rgba(244, 81, 30, 0.32) !important;
}

.gradio-container button.primary:hover,
#generate-button button:hover,
#start-quiz-btn button:hover {
    background: var(--peach-grad-hover) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(244, 81, 30, 0.44) !important;
}

.gradio-container button.primary:active,
#generate-button button:active,
#start-quiz-btn button:active {
    transform: translateY(0) !important;
    box-shadow: 0 3px 10px rgba(244, 81, 30, 0.25) !important;
}

.gradio-container button.secondary,
#next-btn button {
    background: #fff4ed !important;
    color: #c23e18 !important;
    border: 1.5px solid #fed7c5 !important;
    border-radius: 13px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.5rem !important;
    min-height: 3.2rem !important;
}

.gradio-container button.secondary:hover,
#next-btn button:hover {
    background: #ffede0 !important;
    border-color: #fdbca2 !important;
    color: #a62f0f !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(245, 109, 71, 0.12) !important;
}

/* ==========================================================================
   INPUTS, SLIDERS & CONTROLS
   ========================================================================== */
.gradio-container input,
.gradio-container textarea,
.gradio-container [role="listbox"] {
    background: #ffffff !important;
    border: 1.5px solid var(--peach-200) !important;
    border-radius: 12px !important;
    color: var(--ink-dark) !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 0.95rem !important;
    transition: all 0.2s ease !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus {
    border-color: var(--peach-500) !important;
    box-shadow: 0 0 0 3.5px rgba(245, 109, 71, 0.18) !important;
    outline: none !important;
}

.gradio-container label {
    font-weight: 600 !important;
    color: var(--ink-dark) !important;
    font-size: 0.92rem !important;
    margin-bottom: 0.35rem !important;
}

.gradio-container .input-info {
    color: var(--ink-muted) !important;
    font-size: 0.82rem !important;
}

/* Radio button styling */
.gradio-container [data-testid="radio-group"] {
    gap: 8px !important;
}

.gradio-container [data-testid="radio-group"] label,
.dark .gradio-container [data-testid="radio-group"] label {
    border: 1.5px solid var(--peach-200) !important;
    border-radius: 11px !important;
    padding: 0.65rem 1rem !important;
    background: #ffffff !important;
    color: #1a0f0a !important;
    font-size: 0.98rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

.gradio-container [data-testid="radio-group"] label span,
.dark .gradio-container [data-testid="radio-group"] label span {
    color: #1a0f0a !important;
    font-weight: 600 !important;
}

.gradio-container [data-testid="radio-group"] label:hover,
.dark .gradio-container [data-testid="radio-group"] label:hover {
    border-color: var(--peach-400) !important;
    background: #fff8f4 !important;
}

.gradio-container [data-testid="radio-group"] label[data-checked="true"],
.gradio-container [data-testid="radio-group"] label.selected,
.dark .gradio-container [data-testid="radio-group"] label[data-checked="true"],
.dark .gradio-container [data-testid="radio-group"] label.selected {
    border-color: var(--peach-500) !important;
    background: #fff0e7 !important;
    color: #c23e18 !important;
    font-weight: 700 !important;
}

.gradio-container [data-testid="radio-group"] label[data-checked="true"] span,
.gradio-container [data-testid="radio-group"] label.selected span,
.dark .gradio-container [data-testid="radio-group"] label[data-checked="true"] span,
.dark .gradio-container [data-testid="radio-group"] label.selected span {
    color: #c23e18 !important;
    font-weight: 700 !important;
}

/* File Upload Component */
.gradio-container .file-preview,
.gradio-container [data-testid="file-preview"],
.gradio-container .file-upload {
    border: 2px dashed var(--peach-300) !important;
    border-radius: 16px !important;
    background: #fffaf7 !important;
    transition: all 0.2s ease !important;
}

.gradio-container .file-preview:hover,
.gradio-container [data-testid="file-preview"]:hover {
    border-color: var(--peach-500) !important;
    background: #fff5ee !important;
}

/* Slider */
.gradio-container input[type="range"] {
    accent-color: var(--peach-500) !important;
}

/* ==========================================================================
   STATUS & BANNER CALLOUTS
   ========================================================================== */
.status-pill {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.85rem 1.25rem;
    border-radius: 14px;
    margin: 1.2rem 0;
    font-size: 0.95rem;
    font-weight: 500;
}

.status-success {
    background: #f0fdf4;
    border: 1.5px solid #bbf7d0;
    color: #166534;
}

.status-error {
    background: #fff1f2;
    border: 1.5px solid #fecdd3;
    color: #9f1239;
}

.status-info {
    background: #fff6ee;
    border: 1.5px solid #fecdb3;
    color: #9c3c1b;
}

/* ==========================================================================
   QUIZ PREVIEW STYLING (HIGH CONTRAST & PERFECT VISIBILITY)
   ========================================================================== */
.preview-container {
    padding: 0.5rem 0;
}

.preview-header-bar {
    border-bottom: 1.5px solid var(--peach-200);
    padding-bottom: 0.9rem;
    margin-bottom: 1.2rem;
}

.preview-title-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 0.35rem;
}

.preview-title-wrap h3,
.dark .preview-title-wrap h3 {
    margin: 0 !important;
    color: #1a0f0a !important;
    font-size: 1.3rem !important;
    font-weight: 800 !important;
}

.preview-count-pill {
    background: #fff0e7 !important;
    color: #c23e18 !important;
    border: 1.5px solid #ffd4bf !important;
    padding: 4px 14px !important;
    border-radius: 999px !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
}

.preview-hint,
.dark .preview-hint {
    color: #493b34 !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
    line-height: 1.5 !important;
}

.preview-hint strong,
.dark .preview-hint strong {
    color: #c23e18 !important;
}

.preview-card,
.dark .preview-card {
    background: #ffffff !important;
    border: 1.5px solid #fce3d6 !important;
    border-radius: 16px !important;
    padding: 1.25rem 1.45rem !important;
    margin-bottom: 1.15rem !important;
    box-shadow: 0 4px 14px rgba(245, 109, 71, 0.06) !important;
    transition: all 0.2s ease !important;
}

.preview-card:hover,
.dark .preview-card:hover {
    border-color: #fdbba2 !important;
    box-shadow: 0 8px 22px rgba(245, 109, 71, 0.12) !important;
}

.preview-q-title,
.dark .preview-q-title {
    display: flex !important;
    align-items: flex-start !important;
    gap: 12px !important;
    margin-bottom: 1rem !important;
    line-height: 1.55 !important;
}

.preview-q-num,
.dark .preview-q-num {
    background: linear-gradient(135deg, #ff8a65 0%, #f4511e 100%) !important;
    color: #ffffff !important;
    padding: 3px 11px !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    flex-shrink: 0 !important;
    box-shadow: 0 2px 6px rgba(244, 81, 30, 0.28) !important;
    margin-top: 2px !important;
}

/* Crystal-clear question text with solid high-contrast ink color */
.preview-q-text,
.preview-q-title span,
.preview-card .preview-q-title span,
.dark .preview-q-text,
.dark .preview-q-title span,
.dark .preview-card .preview-q-title span {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #1a0f0a !important;
    line-height: 1.55 !important;
}

.preview-opts-container,
.dark .preview-opts-container {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)) !important;
    gap: 10px !important;
}

.preview-opt-item,
.dark .preview-opt-item {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    background: #fff8f5 !important;
    border: 1.5px solid #fedecf !important;
    border-radius: 11px !important;
    padding: 0.65rem 0.95rem !important;
    transition: all 0.2s ease !important;
}

.preview-opt-item:hover,
.dark .preview-opt-item:hover {
    background: #fff0e7 !important;
    border-color: #fdbba2 !important;
}

.preview-opt-letter,
.dark .preview-opt-letter {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 26px !important;
    height: 26px !important;
    background: #ffede3 !important;
    color: #c23e18 !important;
    border: 1px solid #fed2be !important;
    border-radius: 7px !important;
    font-weight: 800 !important;
    font-size: 0.82rem !important;
    flex-shrink: 0 !important;
}

/* Crystal-clear option text with high contrast and sharp weight */
.preview-opt-text,
.preview-opt-item span.preview-opt-text,
.preview-opt-item span:last-child,
.dark .preview-opt-text,
.dark .preview-opt-item span.preview-opt-text,
.dark .preview-opt-item span:last-child {
    font-size: 0.96rem !important;
    font-weight: 600 !important;
    color: #241812 !important;
    line-height: 1.4 !important;
}

/* ==========================================================================
   INTERACTIVE QUIZ ARENA ("TAKE QUIZ")
   ========================================================================== */
.quiz-empty-box {
    text-align: center;
    padding: 3rem 1.5rem;
    background: #ffffff;
    border: 2px dashed var(--peach-200);
    border-radius: 20px;
    margin: 1.5rem 0;
}

.empty-icon {
    font-size: 2.8rem;
    margin-bottom: 0.75rem;
}

.quiz-empty-box h3 {
    font-size: 1.35rem;
    color: var(--ink-dark);
    margin: 0 0 0.5rem 0;
    justify-content: center;
}

.quiz-empty-box p {
    color: var(--ink-muted);
    font-size: 0.95rem;
    max-width: 480px;
    margin: 0 auto;
}

.active-q-box {
    background: #ffffff;
    border: 1.5px solid var(--peach-200);
    border-radius: 20px;
    padding: 1.8rem;
    box-shadow: var(--card-shadow);
    margin-bottom: 1.5rem;
}

.q-progress-bar-wrap {
    margin-bottom: 1.5rem;
}

.q-progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.q-badge-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: #fff0e7;
    border: 1px solid #ffd4bf;
    border-radius: 999px;
    color: #c23e18;
    font-weight: 700;
    font-size: 0.85rem;
}

.q-pct-text {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--ink-muted);
}

.progress-track {
    width: 100%;
    height: 9px;
    background: #ffede3;
    border-radius: 999px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--peach-grad);
    border-radius: 999px;
    transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.q-question-text,
.dark .q-question-text,
.active-q-box h3,
.dark .active-q-box h3 {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 800 !important;
    color: #1a0f0a !important;
    line-height: 1.5 !important;
    margin: 0 !important;
}

/* Feedback Cards */
.feedback-card {
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    margin: 1.2rem 0;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.feedback-correct,
.dark .feedback-correct {
    background: #f0fdf4 !important;
    border: 1.5px solid #86efac !important;
    color: #14532d !important;
}

.feedback-correct .fb-headline,
.dark .feedback-correct .fb-headline {
    color: #14532d !important;
}

.feedback-correct .fb-detail,
.dark .feedback-correct .fb-detail {
    color: #166534 !important;
}

.feedback-incorrect,
.dark .feedback-incorrect {
    background: #fff1f0 !important;
    border: 1.5px solid #fecdd3 !important;
    color: #881337 !important;
}

.feedback-incorrect .fb-headline,
.dark .feedback-incorrect .fb-headline {
    color: #881337 !important;
}

.feedback-incorrect .fb-correct-callout,
.dark .feedback-incorrect .fb-correct-callout {
    background: #ffffff !important;
    border: 1.5px solid #fca5a5 !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
    display: inline-block !important;
    margin-bottom: 0.6rem !important;
    font-size: 0.95rem !important;
    color: #9f1239 !important;
    font-weight: 700 !important;
}

.feedback-incorrect .fb-detail,
.dark .feedback-incorrect .fb-detail {
    color: #3b0714 !important;
}

.fb-headline {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.fb-correct-callout {
    background: #ffffff;
    border: 1px solid #fecdd3;
    padding: 6px 12px;
    border-radius: 8px;
    display: inline-block;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
    color: #9f1239;
}

.fb-detail {
    font-size: 0.95rem;
    line-height: 1.55;
    opacity: 0.92;
}

.alert-box {
    padding: 0.9rem 1.2rem;
    border-radius: 12px;
    font-weight: 500;
    font-size: 0.92rem;
    margin: 1rem 0;
}

.alert-warning {
    background: #fffbeb;
    border: 1.5px solid #fde68a;
    color: #92400e;
}

.alert-info {
    background: #fff7ed;
    border: 1.5px solid #fed7aa;
    color: #9a3412;
}

/* Quiz Completion Screen */
.quiz-completion-card {
    text-align: center;
    background: #ffffff;
    border: 2px solid var(--peach-200);
    border-radius: 24px;
    padding: 2.8rem 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 16px 45px -8px rgba(245, 109, 71, 0.14);
}

.complete-header-badge {
    display: inline-block;
    padding: 5px 16px;
    background: #fff0e7;
    border: 1px solid #fed2be;
    border-radius: 999px;
    color: #c23e18;
    font-weight: 800;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}

.complete-heading {
    font-family: 'Outfit', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: var(--ink-dark) !important;
    margin: 0 0 1.2rem 0 !important;
}

.score-pill-row {
    display: inline-flex;
    align-items: baseline;
    gap: 8px;
    background: #fff7f2;
    border: 2px solid var(--peach-300);
    border-radius: 20px;
    padding: 0.9rem 2.2rem;
    margin-bottom: 1.2rem;
}

.score-main {
    font-family: 'Outfit', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #c23e18;
    line-height: 1;
}

.score-divider {
    font-size: 2rem;
    color: #fdbba2;
    font-weight: 600;
}

.score-total {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--ink-dark);
    line-height: 1;
}

.score-pct-badge {
    margin-left: 8px;
    background: var(--peach-500);
    color: #ffffff;
    padding: 4px 10px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.9rem;
}

.score-remark {
    font-size: 1.1rem;
    color: var(--ink-body);
    max-width: 540px;
    margin: 0 auto 1.4rem auto;
    line-height: 1.6;
}

.restart-prompt {
    font-size: 0.92rem;
    color: var(--ink-muted);
}

/* ==========================================================================
   DOWNLOADS CARD
   ========================================================================== */
.downloads-panel {
    background: #fffbf8 !important;
    border: 1.5px solid var(--peach-200) !important;
    border-radius: 18px !important;
    padding: 1.4rem !important;
    margin-top: 1.5rem !important;
}

.downloads-panel h3 {
    margin-top: 0 !important;
    color: var(--ink-dark) !important;
    font-size: 1.15rem !important;
}

.downloads-desc {
    color: var(--ink-muted) !important;
    font-size: 0.88rem !important;
    margin-bottom: 1rem !important;
}

/* ==========================================================================
   RESPONSIVE
   ========================================================================== */
@media (max-width: 768px) {
    .gradio-container { padding: 1.2rem 0.8rem 2.5rem !important; }
    #hero-banner { padding: 1.5rem 1.3rem !important; }
    .hero-main-title { font-size: 1.85rem !important; }
    .section-card { padding: 1.1rem !important; }
    .score-main { font-size: 2.4rem; }
    .score-total { font-size: 1.8rem; }
}
"""

# ------------------------------------------------------------------------------
# HERO BANNER HTML TEMPLATE
# ------------------------------------------------------------------------------
HERO_HTML = """
<div id="hero-banner">
    <div class="hero-top-row">
        <div class="hero-pill">
            <span class="pulsing-gem"></span>
            <span>AI-POWERED QUIZ STUDIO</span>
        </div>
        <div class="hero-version-tag">🍑 Light Peach Edition</div>
    </div>
    <div class="hero-title-row">
        <h1 class="hero-main-title">AI Quiz Studio</h1>
        <span class="hero-peach-sparkle">🍑</span>
    </div>
    <p class="hero-desc">
        Craft high-impact quizzes, multiple-choice questions, and personalized practice exams in seconds.
        Generate from topics, raw study notes, or uploaded PDFs — then practice interactively or export clean PDF & CSV files.
    </p>
    <div class="hero-features-chips">
        <div class="feature-chip"><span class="chip-icon">⚡</span> Instant AI Generation</div>
        <div class="feature-chip"><span class="chip-icon">🎯</span> Bloom's Taxonomy Alignment</div>
        <div class="feature-chip"><span class="chip-icon">📄</span> PDF & Notes RAG</div>
        <div class="feature-chip"><span class="chip-icon">🏆</span> Interactive Test Arena</div>
        <div class="feature-chip"><span class="chip-icon">📥</span> Print-Ready PDF & CSV</div>
    </div>
</div>
<script>
    (function() {
        function enforceLight() {
            if (document.documentElement.classList.contains('dark')) document.documentElement.classList.remove('dark');
            if (document.body && document.body.classList.contains('dark')) document.body.classList.remove('dark');
        }
        enforceLight();
        window.addEventListener('DOMContentLoaded', enforceLight);
        setTimeout(enforceLight, 300);
        setTimeout(enforceLight, 1000);
    })();
</script>
"""


# ------------------------------------------------------------------------------
# BACKEND LOGIC
# ------------------------------------------------------------------------------
def generate(source, topic, text, pdf, n, difficulty, qtype, language, bloom):
    started = time.perf_counter()
    try:
        context = ""
        if source == "Topic":
            if not topic.strip():
                raise ValueError("Please enter a topic.")
        elif source == "Paste Text":
            if len(text.split()) < 30:
                raise ValueError("Please paste at least ~30 words of text.")
            context = retrieve(text, topic)
        else:
            if pdf is None:
                raise ValueError("Please upload a PDF document.")
            context = retrieve(extract_pdf_text(pdf), topic)

        quiz = generate_quiz(
            user_prompt(topic, context, int(n), difficulty, qtype, language, bloom),
            int(n),
            qtype=qtype,
        )
        qs = [q.model_dump() for q in quiz.questions]
        csv_path = to_csv(qs)
        pdf_path = to_pdf(qs)
    except Exception as e:
        elapsed = time.perf_counter() - started
        error_html = (
            f'<div class="status-pill status-error">'
            f'<span>⚠️ <strong>Quiz generation failed:</strong> {e}</span>'
            f'</div>'
        )
        return (
            {},
            error_html,
            None,
            None,
            f'<div class="status-pill status-error">⚠️ Generation interrupted after {elapsed:.1f}s. Check input details or model quota, then try again.</div>',
        )

    # Format Quiz Preview with Clean Cards
    preview_cards = []
    for i, q in enumerate(qs, 1):
        opts_html = "".join(
            f'<div class="preview-opt-item"><span class="preview-opt-letter">{chr(65 + j)}</span><span class="preview-opt-text">{opt}</span></div>'
            for j, opt in enumerate(q["options"])
        )
        preview_cards.append(
            f'<div class="preview-card">'
            f'<div class="preview-q-title"><span class="preview-q-num">Q{i}</span><span class="preview-q-text">{q["question"]}</span></div>'
            f'<div class="preview-opts-container">{opts_html}</div>'
            f'</div>'
        )

    preview_html = (
        f'<div class="preview-container">'
        f'<div class="preview-header-bar">'
        f'<div class="preview-title-wrap"><h3>✨ Generated Questions Preview</h3><span class="preview-count-pill">{len(qs)} Questions Ready</span></div>'
        f'<p class="preview-hint">Review your questions below, download your files, or switch to the <strong>"Take Quiz"</strong> tab to test your mastery interactively!</p>'
        f'</div>'
        + "".join(preview_cards)
        + '</div>'
    )

    elapsed = time.perf_counter() - started
    status_html = (
        f'<div class="status-pill status-success">'
        f'<span>✨ Successfully generated <strong>{len(qs)} questions</strong> in <strong>{elapsed:.1f}s</strong> using <code>{MODEL}</code>.</span>'
        f'</div>'
    )

    return (
        {"qs": qs, "i": 0, "score": 0, "done": False},
        preview_html,
        csv_path,
        pdf_path,
        status_html,
    )


def show_source_inputs(source):
    return gr.update(visible=source == "Paste Text"), gr.update(visible=source == "Upload PDF")


def render(st):
    if not st or not st.get("qs"):
        placeholder = """
        <div class="quiz-empty-box">
            <div class="empty-icon">💡</div>
            <h3>Ready to test your knowledge?</h3>
            <p>Generate a quiz in the <strong>Generate</strong> tab first, then click <strong>Start / Restart Quiz</strong> below to begin your practice session!</p>
        </div>
        """
        return (
            st,
            placeholder,
            gr.update(choices=[], value=None, interactive=False),
            "",
            gr.update(interactive=False),
            gr.update(interactive=False),
        )

    i, qs = st["i"], st["qs"]
    if i >= len(qs):
        st["done"] = True
        pct = round((st["score"] / len(qs)) * 100) if len(qs) else 0
        if pct >= 80:
            badge = "🌟 Mastered"
            remark = "Outstanding performance! You have thoroughly mastered this material."
        elif pct >= 60:
            badge = "👏 Good Job"
            remark = "Great effort! A quick review of missed points will get you to 100%."
        else:
            badge = "📚 Needs Practice"
            remark = "Keep practicing! Review the explanations and try another attempt."

        score_card = f"""
        <div class="quiz-completion-card">
            <div class="complete-header-badge">🎉 QUIZ COMPLETED</div>
            <h2 class="complete-heading">{badge}</h2>
            <div class="score-pill-row">
                <span class="score-main">{st["score"]}</span>
                <span class="score-divider">/</span>
                <span class="score-total">{len(qs)}</span>
                <span class="score-pct-badge">{pct}% Score</span>
            </div>
            <p class="score-remark">{remark}</p>
            <div class="restart-prompt">Click <strong>Start / Restart Quiz</strong> below if you want to attempt this quiz again!</div>
        </div>
        """
        return (
            st,
            score_card,
            gr.update(choices=[], value=None, interactive=False),
            "",
            gr.update(interactive=False),
            gr.update(interactive=False),
        )

    q = qs[i]
    choices = [(f"{chr(65 + j)}.  {option}", j) for j, option in enumerate(q["options"])]
    pct = int(((i + 1) / len(qs)) * 100)
    q_card = f"""
    <div class="active-q-box">
        <div class="q-progress-bar-wrap">
            <div class="q-progress-header">
                <span class="q-badge-chip">Question {i + 1} of {len(qs)}</span>
                <span class="q-pct-text">{pct}% Completed</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width: {pct}%;"></div></div>
        </div>
        <div class="q-body-content">
            <h3 class="q-question-text">{q["question"]}</h3>
        </div>
    </div>
    """
    return (
        st,
        q_card,
        gr.update(choices=choices, value=None, interactive=True),
        "",
        gr.update(interactive=True),
        gr.update(interactive=False),
    )


def start_quiz(st):
    if st and st.get("qs"):
        st = {**st, "i": 0, "score": 0, "done": False}
    return render(st)


def check(st, choice):
    if not st or not st.get("qs") or st["i"] >= len(st["qs"]):
        return (
            st,
            gr.update(),
            gr.update(),
            '<div class="alert-box alert-info">ℹ️ Generate and start a quiz first.</div>',
            gr.update(interactive=False),
            gr.update(interactive=False),
        )
    if st["done"]:
        return (
            st,
            gr.update(),
            gr.update(interactive=False),
            '<div class="alert-box alert-info">ℹ️ You have already answered this question. Click <strong>Next question</strong> to continue.</div>',
            gr.update(interactive=False),
            gr.update(interactive=True),
        )
    if choice is None:
        return (
            st,
            gr.update(),
            gr.update(),
            '<div class="alert-box alert-warning">⚠️ Please select an answer before submitting.</div>',
            gr.update(interactive=True),
            gr.update(interactive=False),
        )

    q = st["qs"][st["i"]]
    st["done"] = True
    if choice == q["answer_index"]:
        st["score"] += 1
        feedback = f"""
        <div class="feedback-card feedback-correct">
            <div class="fb-headline"><span class="fb-icon">✅</span> <strong>Correct! Outstanding work.</strong></div>
            <div class="fb-detail">{q["explanation"]}</div>
        </div>
        """
    else:
        answer = q["options"][q["answer_index"]]
        feedback = f"""
        <div class="feedback-card feedback-incorrect">
            <div class="fb-headline"><span class="fb-icon">❌</span> <strong>Not quite right.</strong></div>
            <div class="fb-correct-callout">Correct Answer: <strong>{chr(65 + q["answer_index"])}. {answer}</strong></div>
            <div class="fb-detail">{q["explanation"]}</div>
        </div>
        """

    return (
        st,
        gr.update(),
        gr.update(interactive=False),
        feedback,
        gr.update(interactive=False),
        gr.update(interactive=True),
    )


def nxt(st):
    if not st or not st.get("qs"):
        return render(st)
    if not st.get("done"):
        return (
            st,
            gr.update(),
            gr.update(),
            '<div class="alert-box alert-warning">⚠️ Submit your answer before moving to the next question.</div>',
            gr.update(interactive=True),
            gr.update(interactive=False),
        )
    st = {**st, "i": st["i"] + 1, "done": False}
    return render(st)


# ------------------------------------------------------------------------------
# GRADIO BLOCKS APPLICATION
# ------------------------------------------------------------------------------
with gr.Blocks(
    title="AI Quiz Studio • Peach Edition",
    js="() => { document.documentElement.classList.remove('dark'); document.body.classList.remove('dark'); }",
) as demo:
    gr.HTML(HERO_HTML)

    state = gr.State({})

    with gr.Tab("✨ Generate Quiz"):
        with gr.Row():
            with gr.Column(scale=3, elem_classes="section-card"):
                gr.Markdown("### 📝 1. Choose Your Source")
                source = gr.Radio(
                    ["Topic", "Paste Text", "Upload PDF"],
                    value="Topic",
                    label="Input Source",
                    info="Select where the AI should extract facts and questions from.",
                )
                topic = gr.Textbox(
                    label="Topic or Focus Keyword",
                    placeholder="e.g. Cellular Respiration, Quantum Computing, Indian History...",
                    info="Required for Topic; acts as high-priority focus when using text or PDF.",
                )
                text = gr.Textbox(
                    label="Paste Study Text or Notes",
                    placeholder="Paste article, notes, or chapter excerpt here (minimum ~30 words)...",
                    lines=8,
                    visible=False,
                )
                pdf = gr.File(
                    label="Upload PDF Document (max 10 MB)",
                    file_types=[".pdf"],
                    type="filepath",
                    visible=False,
                )

            with gr.Column(scale=2, elem_classes="section-card"):
                gr.Markdown("### ⚙️ 2. Quiz Configuration")
                n = gr.Slider(1, 20, value=5, step=1, label="Number of Questions")
                difficulty = gr.Dropdown(
                    ["Easy", "Medium", "Hard"],
                    value="Medium",
                    label="Difficulty Level",
                )
                qtype = gr.Dropdown(
                    ["MCQ", "True/False", "Fill-in-the-blank"],
                    value="MCQ",
                    label="Question Format",
                )
                language = gr.Dropdown(
                    ["English", "Hindi"],
                    value="English",
                    label="Language",
                )
                bloom = gr.Dropdown(
                    ["Any", "Remember", "Understand", "Apply", "Analyze", "Evaluate"],
                    value="Any",
                    label="Bloom's Taxonomy Level",
                )

        btn = gr.Button("✨ Generate Quiz Now", variant="primary", elem_id="generate-button")

        generation_status = gr.HTML()
        out = gr.HTML(elem_classes="section-card")

        with gr.Column(elem_classes="downloads-panel"):
            gr.Markdown("### 📥 Download & Export Options")
            gr.Markdown("Export your generated quiz instantly. The PDF includes an answer key; the CSV contains options and detailed explanations.")
            with gr.Row():
                csv_f = gr.File(label="📄 Download CSV", interactive=False)
                pdf_f = gr.File(label="📑 Download PDF", interactive=False)

        source.change(show_source_inputs, source, [text, pdf])

    with gr.Tab("🎯 Take Quiz"):
        gr.Markdown("### 🚀 Interactive Practice Arena\nTake your generated quiz question by question. Select your choice, submit for immediate feedback with explanations, and track your score in real-time.")
        start = gr.Button("🚀 Start / Restart Quiz", variant="primary", elem_id="start-quiz-btn")

        qmd = gr.HTML(elem_classes="section-card")
        radio = gr.Radio(choices=[], label="Choose your answer:", interactive=False)
        fb = gr.HTML()

        with gr.Row():
            sub = gr.Button("✅ Submit Answer", variant="primary")
            nb = gr.Button("➡️ Next Question", variant="secondary", elem_id="next-btn", interactive=False)

    btn.click(
        generate,
        [source, topic, text, pdf, n, difficulty, qtype, language, bloom],
        [state, out, csv_f, pdf_f, generation_status],
    )

    quiz_outputs = [state, qmd, radio, fb, sub, nb]
    start.click(start_quiz, state, quiz_outputs)
    sub.click(check, [state, radio], quiz_outputs)
    nb.click(nxt, state, quiz_outputs)

# Vercel's Python runtime serves the exported ASGI application.
app = gr.mount_gradio_app(
    FastAPI(),
    demo,
    path="/",
    theme=PEACH_THEME,
    css=APP_CSS,
)

if __name__ == "__main__":
    demo.launch(
        theme=PEACH_THEME,
        css=APP_CSS,
    )
