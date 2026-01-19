"""
Forward Thinking - Foresight Appendix Generator

A Streamlit application that helps generate future-oriented appendices for academic books.
Uses Google Gemini for AI analysis and generation.
"""

import streamlit as st
import json
import os
import re
from dotenv import load_dotenv
from prompts import get_analysis_prompt, get_generation_prompt
from utils import (
    get_pdf_info,
    extract_with_info,
    validate_pdf_file,
    configure_gemini,
    call_gemini,
    parse_json_response,
    test_api_key,
    get_working_model,
    export_to_markdown,
    export_to_docx,
    export_to_pdf,
    export_planning_table_to_markdown,
    export_planning_table_to_docx,
    export_planning_table_to_pdf
)

# Load environment variables for developer mode
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Foresight Appendix Generator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Modern Professional Design System
# Design System: Clean, Modern Academic Research Tool
# Color Palette: Refined Blue-Grey (Professional & Trustworthy)
# Typography: Inter (Clean Sans-Serif) + System Fonts
st.markdown("""
<style>
    /* Import Modern Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Professional Icon System using Unicode and SVG */
    .icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.25em;
        height: 1.25em;
        margin-right: 0.5em;
    }

    .icon-check::before { content: "✓"; font-weight: 600; }
    .icon-circle::before { content: "○"; }
    .icon-key::before { content: "🔑"; }
    .icon-book::before { content: "📖"; }
    .icon-search::before { content: "🔍"; }
    .icon-sparkles::before { content: "✨"; }
    .icon-info::before { content: "ⓘ"; font-weight: 600; }
    .icon-warning::before { content: "⚠"; }
    .icon-error::before { content: "✕"; font-weight: 600; }
    .icon-download::before { content: "↓"; font-weight: 600; }

    /* Global Styles */
    * {
        cursor: default;
    }

    button, a, [role="button"] {
        cursor: pointer !important;
    }

    /* AGGRESSIVE: Remove ALL top spacing */
    .main {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 1rem !important;
        margin-top: 0 !important;
        max-width: 100% !important;
    }

    /* Remove default spacing from first element */
    .main .block-container > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove default paragraph margins */
    .main .block-container p {
        margin-top: 0 !important;
    }

    /* Streamlit Header - Keep visible but minimal */
    .stAppHeader {
        background-color: rgba(255, 255, 255, 0.0) !important;
        visibility: visible !important;
        height: auto !important;
    }

    /* Main Block Container - Reduced padding for better space utilization */
    .stMainBlockContainer {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0.25rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }

    /* Legacy support for older block-container class */
    .main .block-container {
        padding-top: 0.25rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* Ensure content is centered in wide mode */
    .block-container {
        max-width: 100% !important;
    }

    /* Main Headers - Compact for better space utilization */
    .main-header {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        text-align: center !important;
        margin-bottom: 0.25rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }
    .sub-header {
        font-size: 1.1rem !important;
        color: #475569 !important;
        text-align: center !important;
        margin-bottom: 0.75rem !important;
        margin-top: 0 !important;
        margin-left: auto !important;
        margin-right: auto !important;
        font-weight: 400 !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.4 !important;
        width: 100% !important;
    }

    /* Step Headers - Clean Modern Style */
    .step-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1E293B;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
        padding-bottom: 0;
        border-bottom: none;
        font-family: 'Inter', sans-serif;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Wizard Step Indicator */
    .wizard-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1.5rem 0 0.5rem;
        margin-bottom: 0;
    }

    .wizard-steps {
        display: flex;
        align-items: flex-start;
        position: relative;
    }

    .wizard-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 1;
    }

    .step-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.1rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }

    .step-circle.completed {
        background: #3B5998;
        color: white;
    }

    .step-circle.current {
        background: white;
        border: 3px solid #3B5998;
        color: #3B5998;
    }

    .step-circle.upcoming {
        background: white;
        border: 2px solid #E2E8F0;
        color: #94A3B8;
    }

    .step-connector {
        width: 100px;
        height: 2px;
        background: #E2E8F0;
        margin: 0 0.5rem;
        margin-top: 24px; /* Center vertically with circles */
    }

    .step-connector.completed {
        background: #3B5998;
    }

    .step-label {
        margin-top: 0.75rem;
        font-size: 0.875rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        color: #64748B;
        white-space: nowrap;
    }

    .step-label.active {
        color: #1E293B;
        font-weight: 600;
    }

    /* Step Underline Indicator - highlights current step */
    .step-underline {
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #3B5998, #5B7EC2);
        border-radius: 2px;
        margin-top: 0.5rem;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .step-underline.active {
        opacity: 1;
    }

    /* Remove any white box styling from markdown containers */
    [data-testid="stMarkdown"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Info Boxes - Modern Clean Style */
    .info-box {
        background-color: #F0F9FF;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #0EA5E9;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #0C4A6E;
    }
    .success-box {
        background-color: #F0FDF4;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #10B981;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #065F46;
    }
    .warning-box {
        background-color: #FFFBEB;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #F59E0B;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #92400E;
    }
    .error-box {
        background-color: #FEF2F2;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #EF4444;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #991B1B;
    }

    /* Cards and Containers */
    .metric-card {
        background: #FFFFFF;
        padding: 1.25rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
        border: 1px solid #E2E8F0;
        font-family: 'Inter', sans-serif;
    }

    /* Progress Messages - Modern Animated */
    .progress-message {
        background: #EFF6FF;
        color: #1E40AF;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        border: 2px solid #BFDBFE;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% {
            border-color: #BFDBFE;
            box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
        }
        50% {
            border-color: #60A5FA;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        }
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #F8FAFC;
    }

    /* Sidebar Header - Minimal height */
    [data-testid="stSidebarHeader"] {
        height: 2rem !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Remove top padding from sidebar */
    [data-testid="stSidebar"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    [data-testid="stSidebar"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Text Area Styling - Better Contrast */
    .stTextArea textarea {
        color: #1E293B !important;
        font-family: 'Inter', monospace !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
    }

    .stTextArea textarea:disabled {
        color: #334155 !important;
        opacity: 1 !important;
        background-color: #F8FAFC !important;
    }

    /* Button Enhancements - Improved Touch Targets */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 200ms ease;
        cursor: pointer !important;
        font-family: 'Inter', sans-serif;
        min-height: 44px;
        padding: 0.65rem 1.5rem;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(15, 23, 42, 0.15);
    }
    .stButton>button:focus {
        outline: 2px solid #0369A1;
        outline-offset: 2px;
    }

    /* Success Animation */
    .success-animation {
        animation: slideInFromTop 0.5s ease-out;
    }
    @keyframes slideInFromTop {
        0% {
            transform: translateY(-20px);
            opacity: 0;
        }
        100% {
            transform: translateY(0);
            opacity: 1;
        }
    }

    /* Accessibility - Focus States */
    :focus-visible {
        outline: 2px solid #0369A1;
        outline-offset: 2px;
    }

    /* Reduced Motion Support */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* Typography Improvements */
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.6;
        color: #1E293B;
    }

    p {
        max-width: 75ch;
        line-height: 1.6;
    }

    /* Streamlit Element Overrides */
    .stTextInput > label, .stSelectbox > label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #1E293B;
        font-size: 0.875rem;
    }

    /* Fix column vertical alignment - align items to bottom */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }

    /* Ensure buttons align with inputs */
    [data-testid="column"] .stButton {
        margin-bottom: 0;
    }

    /* Fix header centering */
    .main-header, .sub-header {
        display: block;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'book_content' not in st.session_state:
    st.session_state.book_content = None
if 'extraction_info' not in st.session_state:
    st.session_state.extraction_info = None
if 'planning_data' not in st.session_state:
    st.session_state.planning_data = None
if 'generated_appendices' not in st.session_state:
    st.session_state.generated_appendices = {}
if 'ready_to_generate' not in st.session_state:
    st.session_state.ready_to_generate = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'working_model' not in st.session_state:
    st.session_state.working_model = "gemini-2.5-pro-preview-05-06"

# Developer Mode: Auto-load API key from .env
DEVELOPER_MODE = os.getenv('DEVELOPER_MODE', 'false').lower() == 'true'
if DEVELOPER_MODE and 'developer_mode_initialized' not in st.session_state:
    env_api_key = os.getenv('GOOGLE_API_KEY', '')
    if env_api_key and env_api_key != 'your-api-key-here':
        st.session_state.api_key = env_api_key
        st.session_state.api_key_valid = True
        st.session_state.working_model = get_working_model(env_api_key)
        configure_gemini(env_api_key)
        st.session_state.developer_mode_initialized = True


def render_wizard_steps():
    """Render the wizard step indicator with progress bar"""
    steps = [
        ("API Setup", st.session_state.api_key_valid),
        ("Upload Book", st.session_state.book_content is not None),
        ("Analyze & Review", st.session_state.ready_to_generate),  # Complete when user clicks "Proceed"
        ("Generate", bool(st.session_state.generated_appendices))
    ]

    # Determine current step (the first incomplete step)
    current = 1
    if st.session_state.api_key_valid:
        current = 2
    if st.session_state.book_content:
        current = 3
    if st.session_state.ready_to_generate:  # Only advance when user explicitly proceeds
        current = 4

    # Build HTML for steps
    steps_html = '<div class="wizard-container"><div class="wizard-steps">'

    for i, (label, completed) in enumerate(steps, 1):
        # Connector (before step, except first)
        if i > 1:
            conn_class = "completed" if steps[i-2][1] else ""
            steps_html += f'<div class="step-connector {conn_class}"></div>'

        # Step circle
        if completed:
            circle_class = "completed"
            circle_content = "✓"
        elif i == current:
            circle_class = "current"
            circle_content = str(i)
        else:
            circle_class = "upcoming"
            circle_content = str(i)

        label_class = "active" if i == current else ""
        underline_class = "active" if i == current else ""

        steps_html += f'''
        <div class="wizard-step">
            <div class="step-circle {circle_class}">{circle_content}</div>
            <div class="step-label {label_class}">{label}</div>
            <div class="step-underline {underline_class}"></div>
        </div>
        '''

    steps_html += '</div></div>'

    st.markdown(steps_html, unsafe_allow_html=True)

    return current


def main():
    # Header
    st.markdown('<p class="main-header">Appendix Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate Future-Oriented Appendices for Academic Books</p>', unsafe_allow_html=True)

    # Simplified Sidebar
    with st.sidebar:
        # Working Model Display (compact)
        if st.session_state.api_key_valid and st.session_state.working_model:
            st.caption(f"Model: {st.session_state.working_model}")

        # Quick Help - Collapsed by default
        with st.expander("Quick Help", expanded=False):
            st.markdown("""
            **Workflow:**
            1. **API Setup** - Get free key from [Google AI Studio](https://aistudio.google.com/apikey)
            2. **Upload Book** - Upload PDF and extract content
            3. **Analyze** - AI creates planning table
            4. **Generate** - Create appendices for chapters
            """, unsafe_allow_html=True)

    # Wizard Step Indicator
    current_step = render_wizard_steps()


    # Step 1: API Setup
    if current_step == 1:
        st.markdown('<p class="step-header">API Setup</p>', unsafe_allow_html=True)

        # Developer Mode Indicator
        if DEVELOPER_MODE:
            if st.session_state.api_key_valid:
                st.success("✓ Developer Mode: API Auto-Loaded")
            else:
                st.warning("Developer Mode: No API key")
            st.divider()

        # API Key input - horizontal layout
        st.markdown("**Google AI Studio API Key**")

        # Horizontal layout: Input (60%) | Button (15%) | Status (25%)
        col_input, col_btn, col_status = st.columns([3, 1, 2])

        with col_input:
            default_key = st.session_state.get('api_key', '') if DEVELOPER_MODE else ''
            api_key = st.text_input(
                "Google AI Studio API Key",
                value=default_key,
                type="password",
                help="Get your free API key from https://aistudio.google.com/apikey",
                disabled=DEVELOPER_MODE and st.session_state.api_key_valid,
                label_visibility="collapsed"
            )

        with col_btn:
            validate_clicked = st.button("Validate Key", type="primary", disabled=not api_key or st.session_state.api_key_valid)

        with col_status:
            status_placeholder = st.empty()
            if st.session_state.api_key_valid:
                status_placeholder.markdown('<div class="success-box" style="margin: 0; padding: 0.5rem 1rem;">✓ <strong>Setup Complete!</strong> Go to <strong>Upload Book</strong></div>', unsafe_allow_html=True)

        if validate_clicked:
            status_placeholder.markdown('<div class="progress-message" style="margin: 0; padding: 0.5rem;">Validating...</div>', unsafe_allow_html=True)

            success, message = test_api_key(api_key)

            if success:
                st.session_state.api_key_valid = True
                st.session_state.api_key = api_key
                st.session_state.working_model = get_working_model(api_key)
                configure_gemini(api_key)
                st.rerun()
            else:
                st.session_state.api_key_valid = False
                status_placeholder.empty()
                st.markdown(f'<div class="error-box"><strong>Connection Failed</strong> – {message}<br><br><strong>Need help?</strong> Get your free API key at <a href="https://aistudio.google.com/apikey" target="_blank" style="color: inherit; text-decoration: underline;">Google AI Studio</a></div>', unsafe_allow_html=True)

        # Setup Guide (collapsed)
        with st.expander("How to get a free API key", expanded=False):
            st.markdown("""
            ### Quick Setup Guide:

            1. **Visit** [Google AI Studio](https://aistudio.google.com/apikey)
            2. **Sign in** with your Google account
            3. **Click** "Create API Key" or "Get API Key"
            4. **Copy** the key (starts with "AIza...")
            5. **Paste** it above and click "Validate Key"

            **Note:** The free tier includes generous limits - perfect for testing and moderate use.

            **Already have a key?** Paste it above to get started!
            """)

    # Step 2: Upload Book
    elif current_step == 2:
        st.markdown('<p class="step-header">Upload Book</p>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload your book (PDF)",
            type=['pdf'],
            help="Upload the PDF book you want to analyze"
        )

        if uploaded_file:
            # Validate PDF file first
            is_valid, validation_msg = validate_pdf_file(uploaded_file)

            if "⚠️" in validation_msg or "ℹ️" in validation_msg:
                if "⚠️" in validation_msg:
                    st.warning(validation_msg)
                else:
                    st.info(validation_msg)

            # Get PDF info
            pdf_info = get_pdf_info(uploaded_file)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pages", pdf_info.get('pages', 'N/A'))
            with col2:
                st.metric("Est. Words", f"{int(pdf_info.get('estimated_words', 0)):,}")
            with col3:
                st.metric("Has Text", "✓ Yes" if pdf_info.get('has_text') else "✗ No")

            if not pdf_info.get('has_text'):
                st.markdown('<div class="error-box"><strong>Unable to Extract Text</strong><br>This PDF doesn\'t appear to have selectable text. It may be a scanned or image-based document.<br><br><strong>Solution:</strong> Use a PDF with selectable text, or convert your scanned PDF using OCR software.</div>', unsafe_allow_html=True)
                st.stop()

            # Extract text button with inline progress/success
            col_btn, col_status = st.columns([1, 3])

            with col_btn:
                extract_clicked = st.button(
                    "Extract Book Content",
                    type="primary",
                    disabled=st.session_state.book_content is not None
                )

            with col_status:
                status_placeholder = st.empty()
                # Show status inline if already extracted
                if st.session_state.book_content and not extract_clicked:
                    chars = st.session_state.extraction_info['final_chars'] if st.session_state.extraction_info else 0
                    pages = st.session_state.extraction_info['pages'] if st.session_state.extraction_info else 0
                    status_placeholder.markdown(f'<div class="success-box" style="margin: 0; padding: 0.5rem 1rem;">✓ <strong>Extraction Complete!</strong> {chars:,} chars from {pages} pages. Go to <strong>Analyze & Review</strong></div>', unsafe_allow_html=True)

            if extract_clicked:
                try:
                    uploaded_file.seek(0)

                    # Show animated spinner with message
                    with status_placeholder:
                        with st.spinner("Extracting text from your PDF..."):
                            content, extraction_info = extract_with_info(uploaded_file)

                    st.session_state.book_content = content
                    st.session_state.extraction_info = extraction_info

                    # Store truncation warning to show on Step 3 if needed
                    if extraction_info.get('was_truncated', False):
                        st.session_state.truncation_warning = f"⚠️ Book was large ({extraction_info['original_chars']:,} chars). Kept {extraction_info['kept_percentage']}% (beginning + end). Some middle content was omitted. If chapters are missing, use 'Request Changes' to add them manually."

                    # Auto-advance to Step 3
                    st.rerun()

                except Exception as e:
                    status_placeholder.error(f"Error extracting text: {str(e)}")

    # Step 3: Analyze & Review
    elif current_step == 3:
        st.markdown('<p class="step-header">Analyze & Review</p>', unsafe_allow_html=True)

        # Show truncation warning from Step 2 if applicable
        if st.session_state.get('truncation_warning'):
            st.warning(st.session_state.truncation_warning)
            # Clear after showing once
            del st.session_state.truncation_warning

        # Step 3a: Analyze Book - horizontal layout
        st.subheader("Analyze Book")

        col_btn, col_status = st.columns([1, 3])

        with col_btn:
            analyze_clicked = st.button(
                "Analyze Book & Create Planning Table",
                type="primary",
                disabled=st.session_state.planning_data is not None
            )

        with col_status:
            analysis_status = st.empty()
            # Show status if already analyzed
            if st.session_state.planning_data and not analyze_clicked:
                analysis_status.markdown('<div class="success-box" style="margin: 0; padding: 0.5rem 1rem;">✓ <strong>Analysis Complete!</strong> Review below, then go to <strong>Generate</strong></div>', unsafe_allow_html=True)

        if analyze_clicked:
            analysis_status.markdown('<div class="progress-message" style="margin: 0; padding: 0.5rem;">Analyzing with AI — 30-60 seconds...</div>', unsafe_allow_html=True)

            try:
                configure_gemini(st.session_state.api_key)
                prompt = get_analysis_prompt(st.session_state.book_content)
                response = call_gemini(prompt, st.session_state.working_model)
                planning_data = parse_json_response(response)
                st.session_state.planning_data = planning_data

                analysis_status.markdown('<div class="success-box" style="margin: 0; padding: 0.5rem 1rem;">✓ <strong>Analysis Complete!</strong> Review below, then go to <strong>Generate</strong></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                with st.expander("Debug info"):
                    st.text(str(e))

        # Step 2b: Review Planning Table
        if st.session_state.planning_data:
            st.divider()
            st.subheader("Review Planning Table")

            planning_data = st.session_state.planning_data

            # Book Overview
            overview = planning_data.get('book_overview', {})
            st.markdown("#### Book Overview")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {overview.get('title', 'N/A')}")
                st.write(f"**Total Chapters:** {overview.get('total_chapters', 'N/A')}")
            with col2:
                st.write(f"**Disciplines:** {', '.join(overview.get('disciplines', []))}")
                st.write(f"**Languages:** {', '.join(overview.get('languages', []))}")

            st.write(f"**Scope:** {overview.get('scope', 'N/A')}")

            # Chapters/Groups
            st.markdown("#### Chapter Groups & Assignments")

            chapters = planning_data.get('chapters', [])

            for i, chapter in enumerate(chapters):
                # Full-width expander header with group_id and full description
                expander_label = f"{chapter.get('group_id', f'Chapter {i+1}')} - {chapter.get('content_summary', 'N/A')[:100]}{'...' if len(chapter.get('content_summary', '')) > 100 else ''}"

                with st.expander(expander_label, expanded=False):
                    # Two-column layout
                    col_left, col_right = st.columns([1, 1])

                    # Left Column: Type, Chapters, Titles, Summary, Thematic Quadrants
                    with col_left:
                        st.write(f"**Type:** {chapter.get('group_type', 'N/A')}")
                        st.write(f"**Chapters:** {', '.join(map(str, chapter.get('chapter_numbers', [])))}")
                        st.write(f"**Titles:** {', '.join(chapter.get('chapter_titles', []))}")

                        st.write("**Summary:**")
                        st.info(chapter.get('content_summary', 'N/A'))

                        st.write("**Thematic Quadrants:**")
                        for q in chapter.get('thematic_quadrants', []):
                            st.write(f"  • {q}")

                    # Right Column: Foresight Task & Assignment Brief
                    with col_right:
                        st.write("**Foresight Task:**")
                        st.markdown("*Assignment Brief*")

                        # Calculate dynamic height based on content
                        foresight_text = chapter.get('foresight_task', 'N/A')
                        # Estimate lines: count newlines + estimate line wrapping (assume ~80 chars per line)
                        line_count = foresight_text.count('\n') + (len(foresight_text) // 80) + 1
                        # Set height: ~25px per line, min 150px, max 800px
                        dynamic_height = max(150, min(800, line_count * 25))

                        st.text_area(
                            "Assignment Brief",
                            foresight_text,
                            height=dynamic_height,
                            key=f"task_{i}",
                            disabled=True,
                            label_visibility="collapsed"
                        )

            # Download planning table options
            # Validate planning data before offering downloads
            if planning_data and planning_data.get('chapters'):
                col1, col2, col3 = st.columns(3)

                with col1:
                    try:
                        planning_md = export_planning_table_to_markdown(planning_data)
                        if planning_md and len(planning_md) > 0:
                            st.download_button(
                                label="📥 Planning Table (.md)",
                                data=planning_md,
                                file_name="planning_table.md",
                                mime="text/markdown",
                                key="download_md"
                            )
                        else:
                            st.error("Markdown export returned empty file")
                    except Exception as e:
                        st.error(f"Markdown export failed: {str(e)}")

                with col2:
                    try:
                        planning_docx = export_planning_table_to_docx(planning_data)
                        if planning_docx and len(planning_docx) > 0:
                            st.download_button(
                                label="📥 Planning Table (.docx)",
                                data=planning_docx,
                                file_name="planning_table.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="download_docx"
                            )
                        else:
                            st.error("DOCX export returned empty file")
                    except Exception as e:
                        st.error(f"DOCX export failed: {str(e)}")

                with col3:
                    try:
                        planning_pdf = export_planning_table_to_pdf(planning_data)
                        if planning_pdf and len(planning_pdf) > 0:
                            st.download_button(
                                label="📥 Planning Table (.pdf)",
                                data=planning_pdf,
                                file_name="planning_table.pdf",
                                mime="application/pdf",
                                key="download_pdf"
                            )
                        else:
                            st.error("PDF export returned empty file")
                    except Exception as e:
                        st.error(f"PDF export failed: {str(e)}")
            else:
                st.warning("⚠️ Planning data is incomplete. Cannot generate export files.")

            # Request changes (expanded by default for review)
            st.subheader("Request Changes")
            change_request = st.text_area(
                "Describe any changes you'd like to make to the planning table:",
                placeholder="E.g., 'Combine chapters 4 and 5' or 'Add climate change as a quadrant' or 'Remove chapter 3 from the analysis'",
                height=100
            )

            if change_request and st.button("Apply Changes", type="secondary"):
                progress_placeholder = st.empty()
                progress_placeholder.markdown('<div class="progress-message">Applying changes...</div>', unsafe_allow_html=True)

                try:
                    configure_gemini(st.session_state.api_key)

                    change_prompt = f"""
                    Here is the current planning table:

                    {json.dumps(planning_data, indent=2)}

                    The user requests the following changes:

                    {change_request}

                    Please return the UPDATED planning table as a JSON object with the same structure.
                    Apply the requested changes while maintaining the overall format.
                    Return ONLY the JSON object.
                    """

                    response = call_gemini(change_prompt, st.session_state.working_model)
                    updated_data = parse_json_response(response)
                    st.session_state.planning_data = updated_data

                    progress_placeholder.empty()
                    st.success("✓ Changes applied!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error applying changes: {str(e)}")

            # Proceed to Generate button
            st.divider()
            st.markdown("**Ready to generate appendices?** Review the planning table above and request any changes before proceeding.")

            if st.button("Proceed to Generate Appendices →", type="primary"):
                st.session_state.ready_to_generate = True
                st.rerun()

    # Step 4: Generate
    elif current_step == 4:
        st.markdown('<p class="step-header">Generate Appendices</p>', unsafe_allow_html=True)

        chapters = st.session_state.planning_data.get('chapters', [])

        # Dropdown to select which appendix to generate - horizontal layout
        chapter_options = {
            f"{ch.get('group_id', f'Item {i}')} - {', '.join(ch.get('chapter_titles', [])[:2])}": i
            for i, ch in enumerate(chapters)
        }

        # Selector (70%) + View brief (30%) - horizontal
        col_select, col_brief = st.columns([7, 3])

        with col_select:
            selected = st.selectbox(
                "Select chapter/group to generate appendix for:",
                options=list(chapter_options.keys())
            )

        selected_idx = chapter_options[selected]
        selected_chapter = chapters[selected_idx]

        with col_brief:
            with st.expander("View assignment brief", expanded=False):
                st.write(selected_chapter.get('foresight_task', 'N/A'))

        # Generate button (25%) + status (75%) - horizontal
        col_gen_btn, col_gen_status = st.columns([1, 3])

        with col_gen_btn:
            generate_clicked = st.button("Generate Appendix", type="primary")

        with col_gen_status:
            gen_status = st.empty()

        if generate_clicked:
            gen_status.markdown('<div class="progress-message" style="margin: 0; padding: 0.5rem;">Generating with AI — 1-2 minutes...</div>', unsafe_allow_html=True)

            try:
                configure_gemini(st.session_state.api_key)

                chapter_info = json.dumps(selected_chapter, indent=2)
                target = selected_chapter.get('group_id', 'Unknown')

                prompt = get_generation_prompt(
                    target_assignment=target,
                    chapter_info=chapter_info,
                    book_content=st.session_state.book_content,
                    word_count=st.sidebar.text_input if hasattr(st.sidebar, 'text_input') else "2500-3500"
                )

                response = call_gemini(prompt, st.session_state.working_model)

                # Store generated appendix
                st.session_state.generated_appendices[target] = response

                gen_status.markdown('<div class="success-box" style="margin: 0; padding: 0.5rem 1rem;">✓ <strong>Generated!</strong> Download below.</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error generating appendix: {str(e)}")

        # Display generated appendix
        selected_target = selected_chapter.get('group_id', 'Unknown')
        if selected_target in st.session_state.generated_appendices:
            st.divider()
            st.subheader(f"Generated Appendix: {selected_target}")

            appendix_content = st.session_state.generated_appendices[selected_target]

            # Preview
            st.markdown(appendix_content)

            # Download buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                try:
                    md_bytes = export_to_markdown(appendix_content, f"Appendix - {selected_target}")
                    # Clean filename: remove special chars, keep alphanumeric and underscores
                    clean_filename = re.sub(r'[^\w\-]', '_', selected_target)
                    st.download_button(
                        "📥 Download .md",
                        md_bytes,
                        file_name=f"appendix_{clean_filename}.md",
                        mime="text/markdown",
                        key=f"dl_md_{selected_target}"
                    )
                except Exception as e:
                    st.warning(f"MD export error: {str(e)}")

            with col2:
                try:
                    docx_bytes = export_to_docx(appendix_content, f"Appendix - {selected_target}")
                    clean_filename = re.sub(r'[^\w\-]', '_', selected_target)
                    st.download_button(
                        "📥 Download .docx",
                        docx_bytes,
                        file_name=f"appendix_{clean_filename}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_docx_{selected_target}"
                    )
                except Exception as e:
                    st.warning(f"DOCX export error: {str(e)}")

            with col3:
                try:
                    pdf_bytes = export_to_pdf(appendix_content, f"Appendix - {selected_target}")
                    clean_filename = re.sub(r'[^\w\-]', '_', selected_target)
                    st.download_button(
                        "📥 Download .pdf",
                        pdf_bytes,
                        file_name=f"appendix_{clean_filename}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{selected_target}"
                    )
                except Exception as e:
                    st.warning(f"PDF export error: {str(e)}")

            with col4:
                if st.button("Regenerate Appendix"):
                    del st.session_state.generated_appendices[selected_target]
                    st.rerun()

        # Show all generated appendices (collapsible)
        if st.session_state.generated_appendices:
            with st.expander("All Generated Appendices", expanded=False):
                for target, content in st.session_state.generated_appendices.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"✅ {target}")
                    with col2:
                        md_bytes = export_to_markdown(content, f"Appendix - {target}")
                        st.download_button(
                            "Download",
                            md_bytes,
                            file_name=f"appendix_{target.replace(' ', '_')}.md",
                            mime="text/markdown",
                            key=f"dl_{target}"
                        )



if __name__ == "__main__":
    main()
