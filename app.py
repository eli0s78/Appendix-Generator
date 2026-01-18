"""
Forward Thinking - Foresight Appendix Generator

A Streamlit application that helps generate future-oriented appendices for academic books.
Uses Google Gemini for AI analysis and generation.
"""

import streamlit as st
import json
import os
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
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced with UI/UX Pro Max Design System
# Design System: B2B Professional Academic Research Tool
# Color Palette: Professional Blue + Neutral Grey (Trust & Authority)
# Typography: Editorial Classic (Cormorant Garamond + Libre Baskerville)
st.markdown("""
<style>
    /* Import Professional Typography */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Styles */
    * {
        cursor: default;
    }

    button, a, [role="button"] {
        cursor: pointer !important;
    }

    /* Main Headers - Editorial Typography */
    .main-header {
        font-size: 2.8rem;
        font-weight: 600;
        color: #0F172A;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Cormorant Garamond', serif;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #334155;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
        font-family: 'Libre Baskerville', serif;
        line-height: 1.6;
    }

    /* Step Headers - Professional Academic Style */
    .step-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0F172A;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #E2E8F0;
        font-family: 'Cormorant Garamond', serif;
    }

    /* Workflow Progress Indicator - Professional Blue Gradient */
    .workflow-tracker {
        background: linear-gradient(135deg, #0F172A 0%, #0369A1 100%);
        color: white;
        padding: 1.75rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .step-indicator {
        display: inline-block;
        margin: 0.5rem;
        padding: 0.65rem 1.25rem;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.15);
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 200ms ease;
        font-size: 0.95rem;
    }
    .step-completed {
        background: rgba(5, 150, 105, 0.3);
        border: 1px solid rgba(5, 150, 105, 0.4);
    }
    .step-current {
        background: rgba(3, 105, 161, 0.4);
        border: 2px solid white;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);
    }
    .step-pending {
        background: rgba(255, 255, 255, 0.08);
        opacity: 0.7;
    }

    /* Info Boxes - Professional Academic Style */
    .info-box {
        background-color: #F1F5F9;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #0369A1;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
        font-family: 'Libre Baskerville', serif;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #0F172A;
    }
    .success-box {
        background-color: #ECFDF5;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #059669;
        box-shadow: 0 2px 6px rgba(5, 150, 105, 0.08);
        font-family: 'Libre Baskerville', serif;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #064E3B;
    }
    .warning-box {
        background-color: #FFFBEB;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #D97706;
        box-shadow: 0 2px 6px rgba(217, 119, 6, 0.08);
        font-family: 'Libre Baskerville', serif;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #78350F;
    }
    .error-box {
        background-color: #FEF2F2;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #DC2626;
        box-shadow: 0 2px 6px rgba(220, 38, 38, 0.08);
        font-family: 'Libre Baskerville', serif;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #7F1D1D;
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

    /* Progress Messages - Professional Blue */
    .progress-message {
        background: linear-gradient(135deg, #0F172A 0%, #0369A1 100%);
        color: white;
        padding: 1.25rem 1.75rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        animation: pulse 2s ease-in-out infinite;
        box-shadow: 0 4px 12px rgba(3, 105, 161, 0.15);
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #F8FAFC;
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
        font-family: 'Libre Baskerville', serif;
        line-height: 1.7;
        color: #0F172A;
    }

    p {
        max-width: 75ch;
        line-height: 1.7;
    }

    /* Streamlit Element Overrides */
    .stTextInput > label, .stSelectbox > label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #0F172A;
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
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'working_model' not in st.session_state:
    st.session_state.working_model = "gemini-2.5-pro-preview-05-06"
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

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


def render_workflow_tracker():
    """Render the visual workflow progress tracker."""
    # Determine current step based on session state
    current_step = 1
    if st.session_state.api_key_valid:
        current_step = 2
    if st.session_state.book_content:
        current_step = 3
    if st.session_state.planning_data:
        current_step = 4

    steps = [
        {"num": 1, "name": "API Setup", "icon": "🔑"},
        {"num": 2, "name": "Upload Book", "icon": "📚"},
        {"num": 3, "name": "Analyze", "icon": "🔍"},
        {"num": 4, "name": "Generate", "icon": "✨"}
    ]

    workflow_html = '<div class="workflow-tracker"><div style="text-align: center;">'

    for step in steps:
        if step["num"] < current_step:
            status_class = "step-completed"
            icon = "✓"
        elif step["num"] == current_step:
            status_class = "step-current"
            icon = step["icon"]
        else:
            status_class = "step-pending"
            icon = "○"

        workflow_html += f'<span class="step-indicator {status_class}">{icon} Step {step["num"]}: {step["name"]}</span>'

    workflow_html += '</div></div>'
    st.markdown(workflow_html, unsafe_allow_html=True)


def load_demo_data():
    """Load sample demo data for demonstration purposes."""
    st.session_state.demo_mode = True
    st.session_state.book_content = """
    Chapter 1: Introduction to Digital Transformation

    The rapid evolution of digital technologies has fundamentally altered the landscape of modern business and society. Organizations across all sectors are grappling with the implications of artificial intelligence, cloud computing, and data analytics. This transformation extends beyond mere technological adoption; it represents a fundamental shift in how we conceptualize value creation, customer engagement, and organizational structure.

    Chapter 2: Artificial Intelligence and Machine Learning

    Artificial intelligence has emerged as one of the most transformative technologies of the 21st century. Machine learning algorithms now power everything from recommendation systems to autonomous vehicles. Deep learning techniques have revolutionized computer vision, natural language processing, and predictive analytics. As these technologies mature, questions arise about their long-term implications for employment, privacy, and social equity.

    Chapter 3: The Future of Work

    The workplace of tomorrow will bear little resemblance to its current form. Remote collaboration tools, augmented reality interfaces, and AI-powered assistance will reshape how we perform tasks and interact with colleagues. The gig economy continues to expand, challenging traditional employment models and social safety nets. Organizations must adapt to increasingly distributed workforces while maintaining culture and productivity.
    """

    st.session_state.extraction_info = {
        'pages': 3,
        'final_chars': 1247,
        'original_chars': 1247,
        'was_truncated': False
    }

    st.session_state.planning_data = {
        'book_overview': {
            'title': 'Digital Transformation: A Guide to the Future',
            'total_chapters': 3,
            'disciplines': ['Technology', 'Business', 'Sociology'],
            'languages': ['English'],
            'scope': 'Exploration of digital transformation across business and society'
        },
        'chapters': [
            {
                'group_id': 'Group A',
                'group_type': 'Thematic',
                'chapter_numbers': [1, 2],
                'chapter_titles': ['Introduction to Digital Transformation', 'Artificial Intelligence and Machine Learning'],
                'content_summary': 'Covers the fundamentals of digital transformation and AI technologies',
                'thematic_quadrants': ['Technology Adoption', 'AI Ethics', 'Innovation Management'],
                'foresight_task': 'Explore how AI and digital transformation will evolve by 2040-2050, considering ethical implications, societal impact, and technological breakthroughs.'
            }
        ]
    }


def main():
    # Header
    st.markdown('<p class="main-header">Forward Thinking - Foresight</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate Future-Oriented Appendices for Academic Books</p>', unsafe_allow_html=True)

    # Demo Mode Toggle
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🎯 Try Demo Mode" if not st.session_state.demo_mode else "🔄 Exit Demo", use_container_width=True):
            if not st.session_state.demo_mode:
                load_demo_data()
                st.rerun()
            else:
                # Reset demo mode
                st.session_state.demo_mode = False
                st.session_state.book_content = None
                st.session_state.extraction_info = None
                st.session_state.planning_data = None
                st.session_state.generated_appendices = {}
                st.rerun()

    if st.session_state.demo_mode:
        st.markdown('<div class="info-box">ℹ️ <strong>Demo Mode Active</strong> - Using sample book data. Try the full workflow without uploading a PDF!</div>', unsafe_allow_html=True)

    # Workflow Tracker
    render_workflow_tracker()

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # Developer Mode Indicator
        if DEVELOPER_MODE:
            st.markdown('<div class="success-box">🔧 <strong>Developer Mode Active</strong></div>', unsafe_allow_html=True)
            if st.session_state.api_key_valid:
                st.markdown(f'<div class="info-box">✓ API Key Auto-Loaded<br><small>Model: {st.session_state.working_model}</small></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-box">⚠ No valid API key in .env file</div>', unsafe_allow_html=True)

        # API Key input
        st.subheader("1. API Key")

        # Show API key input field (pre-filled in dev mode, but still editable)
        default_key = st.session_state.get('api_key', '') if DEVELOPER_MODE else ''
        api_key = st.text_input(
            "Google AI Studio API Key",
            value=default_key,
            type="password",
            help="Get your free API key from https://aistudio.google.com/apikey",
            disabled=DEVELOPER_MODE and st.session_state.api_key_valid
        )
        
        if api_key:
            if st.button("Validate Key"):
                progress_placeholder = st.empty()
                progress_placeholder.markdown('<div class="progress-message">🔑 Validating your API key...</div>', unsafe_allow_html=True)

                success, message = test_api_key(api_key)
                progress_placeholder.empty()

                if success:
                    st.session_state.api_key_valid = True
                    st.session_state.api_key = api_key
                    st.session_state.working_model = get_working_model(api_key)
                    configure_gemini(api_key)
                    st.markdown(f'<div class="success-box success-animation">✓ {message}</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.session_state.api_key_valid = False
                    st.markdown(f'<div class="error-box">✗ {message}<br><br>💡 <strong>Need help?</strong> Get your free API key at <a href="https://aistudio.google.com/apikey" target="_blank">Google AI Studio</a></div>', unsafe_allow_html=True)

        if st.session_state.api_key_valid:
            st.markdown('<div class="success-box">✓ API Connected</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Settings
        st.subheader("2. Settings")
        time_horizon = st.text_input("Time Horizon", value="2040-2050")
        word_count = st.text_input("Target Word Count", value="2500-3500")
        
        st.divider()
        
        # Help
        st.subheader("ℹ️ Help")
        st.markdown("""
        **Workflow:**
        1. Enter your Gemini API key
        2. Upload a PDF book
        3. Analyze to create planning table
        4. Review and adjust if needed
        5. Generate appendices
        
        **Get API Key:**
        Visit [Google AI Studio](https://aistudio.google.com/apikey)
        """)
    
    # Main content area
    if not st.session_state.api_key_valid:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 2rem;">
            <h3 style="margin-top: 0;">🔑 API Key Required</h3>
            <p>Please enter and validate your Google AI Studio API key in the sidebar to begin.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📖 How to get a free API key (takes 2 minutes)", expanded=True):
            st.markdown("""
            ### Quick Setup Guide:

            1. **Visit** [Google AI Studio](https://aistudio.google.com/apikey)
            2. **Sign in** with your Google account
            3. **Click** "Create API Key" or "Get API Key"
            4. **Copy** the key (starts with "AIza...")
            5. **Paste** it in the sidebar ← and click "Validate Key"

            **Note:** The free tier includes generous limits - perfect for testing and moderate use.

            **Already have a key?** Paste it in the sidebar to get started!
            """)
        return
    
    # Step 1: Upload Book
    st.markdown('<p class="step-header">📚 Step 1: Upload Book</p>', unsafe_allow_html=True)
    
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
            st.markdown('<div class="error-box">⚠️ This PDF doesn\'t appear to have extractable text. It may be a scanned/image-based document.<br><br>💡 <strong>What to do:</strong> Use a PDF with selectable text, or convert your scanned PDF using OCR software.</div>', unsafe_allow_html=True)
            return
        
        # Extract text button
        if st.button("📖 Extract Book Content", type="primary"):
            progress_placeholder = st.empty()
            progress_placeholder.markdown('<div class="progress-message">📖 Extracting text from your PDF...</div>', unsafe_allow_html=True)

            try:
                uploaded_file.seek(0)
                content, extraction_info = extract_with_info(uploaded_file)
                st.session_state.book_content = content
                st.session_state.extraction_info = extraction_info

                progress_placeholder.empty()
                st.markdown(f'<div class="success-box success-animation">✓ Successfully extracted {extraction_info["final_chars"]:,} characters from {extraction_info["pages"]} pages</div>', unsafe_allow_html=True)

                # Show warning if content was truncated
                if extraction_info.get('was_truncated', False):
                    st.warning(f"⚠️ Book was large ({extraction_info['original_chars']:,} chars). Kept {extraction_info['kept_percentage']}% (beginning + end). Some middle content was omitted. If chapters are missing, use 'Request Changes' to add them manually.")

            except Exception as e:
                st.error(f"Error extracting text: {str(e)}")
    
    # Step 2: Analyze Book
    if st.session_state.book_content:
        st.markdown('<p class="step-header">🔍 Step 2: Analyze Book</p>', unsafe_allow_html=True)
        
        with st.expander("Preview extracted content", expanded=False):
            st.text_area(
                "Book Content (Preview)",
                st.session_state.book_content[:5000] + "...",
                height=200,
                disabled=True
            )
        
        if st.button("🔬 Analyze Book & Create Planning Table", type="primary"):
            progress_placeholder = st.empty()
            progress_placeholder.markdown('<div class="progress-message">🔬 Analyzing your book with AI... This may take 30-60 seconds</div>', unsafe_allow_html=True)

            try:
                configure_gemini(st.session_state.api_key)
                prompt = get_analysis_prompt(st.session_state.book_content)
                response = call_gemini(prompt, st.session_state.working_model)
                planning_data = parse_json_response(response)
                st.session_state.planning_data = planning_data

                progress_placeholder.empty()
                st.markdown('<div class="success-box success-animation">✓ Analysis complete! Planning table is ready for review.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                with st.expander("Debug info"):
                    st.text(str(e))
    
    # Step 3: Review Planning Table
    if st.session_state.planning_data:
        st.markdown('<p class="step-header">📋 Step 3: Review Planning Table</p>', unsafe_allow_html=True)
        
        planning_data = st.session_state.planning_data
        
        # Book Overview
        overview = planning_data.get('book_overview', {})
        st.subheader("Book Overview")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Title:** {overview.get('title', 'N/A')}")
            st.write(f"**Total Chapters:** {overview.get('total_chapters', 'N/A')}")
        with col2:
            st.write(f"**Disciplines:** {', '.join(overview.get('disciplines', []))}")
            st.write(f"**Languages:** {', '.join(overview.get('languages', []))}")
        
        st.write(f"**Scope:** {overview.get('scope', 'N/A')}")
        
        st.divider()
        
        # Chapters/Groups
        st.subheader("Chapter Groups & Assignments")
        
        chapters = planning_data.get('chapters', [])
        
        for i, chapter in enumerate(chapters):
            with st.expander(f"**{chapter.get('group_id', f'Chapter {i+1}')}** - {', '.join(chapter.get('chapter_titles', [])[:2])}{'...' if len(chapter.get('chapter_titles', [])) > 2 else ''}", expanded=False):
                
                st.write(f"**Type:** {chapter.get('group_type', 'N/A')}")
                st.write(f"**Chapters:** {', '.join(map(str, chapter.get('chapter_numbers', [])))}")
                st.write(f"**Titles:** {', '.join(chapter.get('chapter_titles', []))}")
                
                st.write("**Summary:**")
                st.info(chapter.get('content_summary', 'N/A'))
                
                st.write("**Thematic Quadrants:**")
                for q in chapter.get('thematic_quadrants', []):
                    st.write(f"  • {q}")
                
                st.write("**Foresight Task:**")
                st.text_area(
                    "Assignment Brief",
                    chapter.get('foresight_task', 'N/A'),
                    height=150,
                    key=f"task_{i}",
                    disabled=True
                )
        
        # Download planning table
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            planning_md = export_planning_table_to_markdown(planning_data)
            st.download_button(
                "📥 Planning Table (.md)",
                planning_md,
                file_name="planning_table.md",
                mime="text/markdown"
            )
        with col2:
            try:
                planning_docx = export_planning_table_to_docx(planning_data)
                st.download_button(
                    "📥 Planning Table (.docx)",
                    planning_docx,
                    file_name="planning_table.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.warning(f"DOCX error: {str(e)}")
        with col3:
            try:
                planning_pdf = export_planning_table_to_pdf(planning_data)
                st.download_button(
                    "📥 Planning Table (.pdf)",
                    planning_pdf,
                    file_name="planning_table.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.warning(f"PDF error: {str(e)}")
        
        # Request changes
        st.divider()
        st.subheader("Request Changes")
        change_request = st.text_area(
            "Describe any changes you'd like to make to the planning table:",
            placeholder="E.g., 'Combine chapters 4 and 5 into one group' or 'Add climate change as a quadrant for Group A'",
            height=100
        )
        
        if change_request and st.button("🔄 Apply Changes"):
            progress_placeholder = st.empty()
            progress_placeholder.markdown('<div class="progress-message">🔄 Applying your changes to the planning table...</div>', unsafe_allow_html=True)

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
                st.markdown('<div class="success-box success-animation">✓ Changes applied successfully! Please review the updated table below.</div>', unsafe_allow_html=True)
                st.rerun()
            except Exception as e:
                st.error(f"Error applying changes: {str(e)}")
    
    # Step 4: Generate Appendices
    if st.session_state.planning_data:
        st.markdown('<p class="step-header">✨ Step 4: Generate Appendices</p>', unsafe_allow_html=True)
        
        chapters = st.session_state.planning_data.get('chapters', [])
        
        # Dropdown to select which appendix to generate
        chapter_options = {
            f"{ch.get('group_id', f'Item {i}')} - {', '.join(ch.get('chapter_titles', [])[:2])}": i 
            for i, ch in enumerate(chapters)
        }
        
        selected = st.selectbox(
            "Select chapter/group to generate appendix for:",
            options=list(chapter_options.keys())
        )
        
        selected_idx = chapter_options[selected]
        selected_chapter = chapters[selected_idx]
        
        # Show current assignment
        with st.expander("View assignment brief", expanded=False):
            st.write(selected_chapter.get('foresight_task', 'N/A'))
        
        # Generate button
        if st.button("🚀 Generate Appendix", type="primary"):
            progress_placeholder = st.empty()
            progress_placeholder.markdown('<div class="progress-message">✨ Generating your appendix with AI... This may take 1-2 minutes</div>', unsafe_allow_html=True)

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

                progress_placeholder.empty()
                st.markdown(f'<div class="success-box success-animation">✓ Appendix generated successfully! Ready to download.</div>', unsafe_allow_html=True)

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
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                md_bytes = export_to_markdown(appendix_content, f"Appendix - {selected_target}")
                st.download_button(
                    "📥 Download .md",
                    md_bytes,
                    file_name=f"appendix_{selected_target.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            
            with col2:
                try:
                    docx_bytes = export_to_docx(appendix_content, f"Appendix - {selected_target}")
                    st.download_button(
                        "📥 Download .docx",
                        docx_bytes,
                        file_name=f"appendix_{selected_target.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.warning(f"DOCX export error: {str(e)}")
            
            with col3:
                try:
                    pdf_bytes = export_to_pdf(appendix_content, f"Appendix - {selected_target}")
                    st.download_button(
                        "📥 Download .pdf",
                        pdf_bytes,
                        file_name=f"appendix_{selected_target.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.warning(f"PDF export error: {str(e)}")
            
            with col4:
                if st.button("🔄 Regenerate"):
                    del st.session_state.generated_appendices[selected_target]
                    st.rerun()
        
        # Show all generated appendices
        if st.session_state.generated_appendices:
            st.divider()
            st.subheader("📁 All Generated Appendices")
            
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
