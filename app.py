"""
Appendix Generator

A Streamlit application that helps generate future-oriented appendices for academic books.
Uses Google Gemini for AI analysis and generation.
"""

import streamlit as st
import json
import os
import re
import zipfile
from io import BytesIO
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
    get_detected_tier,
    export_to_markdown,
    export_to_docx,
    export_to_pdf,
    export_planning_table_to_markdown,
    export_planning_table_to_docx,
    export_planning_table_to_pdf,
    save_session,
    load_session,
    get_session_filename,
    decode_api_key
)

# Load environment variables for developer mode
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Appendix Generator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load external CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


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
    st.session_state.working_model = "gemini-2.5-flash"  # Use free tier model
# Track saved state for unsaved changes detection
if 'last_saved_state' not in st.session_state:
    st.session_state.last_saved_state = None
# Generation settings (exposed in Step 3)
if 'forecast_years' not in st.session_state:
    st.session_state.forecast_years = 15  # Default: 15 years ahead
if 'word_count_option' not in st.session_state:
    st.session_state.word_count_option = "Standard (2500-3500 words)"
if 'word_count_value' not in st.session_state:
    st.session_state.word_count_value = "2500-3500"
# Pending action when confirmation is needed (e.g., 'new_project', 'load_project')
if 'pending_action' not in st.session_state:
    st.session_state.pending_action = None
# Pending file data for load action
if 'pending_load_data' not in st.session_state:
    st.session_state.pending_load_data = None
# Flag to track if user saved in modal and should proceed
if 'modal_saved_and_proceed' not in st.session_state:
    st.session_state.modal_saved_and_proceed = False

# Developer Mode: Auto-load API key from .env
DEVELOPER_MODE = os.getenv('DEVELOPER_MODE', 'false').lower() == 'true'
if DEVELOPER_MODE and 'developer_mode_initialized' not in st.session_state:
    env_api_key = os.getenv('GOOGLE_API_KEY', '')
    if env_api_key and env_api_key != 'your-api-key-here':
        st.session_state.api_key = env_api_key
        st.session_state.api_key_valid = True
        st.session_state.working_model = get_working_model(env_api_key)
        st.session_state.detected_tier = get_detected_tier()  # Store tier in session
        configure_gemini(env_api_key)
        st.session_state.developer_mode_initialized = True

# Step 4 Dev Mode: Skip directly to Step 4 with mock data
# Set STEP4_DEV_MODE=true in .env to enable
STEP4_DEV_MODE = os.getenv('STEP4_DEV_MODE', 'false').lower() == 'true'
if STEP4_DEV_MODE and 'step4_dev_initialized' not in st.session_state:
    # Mock all prerequisites as complete
    st.session_state.api_key_valid = True
    st.session_state.api_key = "mock-api-key-for-dev"
    st.session_state.book_content = "Mock book content for Step 4 development testing."
    st.session_state.extraction_info = {'final_chars': 50000, 'pages': 200}
    st.session_state.ready_to_generate = True
    st.session_state.working_model = "gemini-2.5-flash"  # Use free tier model

    # Mock planning data with realistic chapter groups (11 groups for tab testing)
    st.session_state.planning_data = {
        "book_title": "Mock Book: Future of Technology",
        "chapters": [
            {
                "group_id": "GROUP_A",
                "chapters": ["Chapter 1: Introduction to AI", "Chapter 2: Machine Learning Basics"],
                "foresight_task": "Analyze how artificial intelligence and machine learning technologies will evolve over the next decade."
            },
            {
                "group_id": "GROUP_B",
                "chapters": ["Chapter 3: Cloud Computing", "Chapter 4: Edge Computing"],
                "foresight_task": "Examine the convergence of cloud and edge computing paradigms."
            },
            {
                "group_id": "GROUP_C",
                "chapters": ["Chapter 5: Cybersecurity", "Chapter 6: Privacy"],
                "foresight_task": "Investigate emerging cybersecurity threats and privacy concerns."
            },
            {
                "group_id": "GROUP_D",
                "chapters": ["Chapter 7: Sustainable Tech", "Chapter 8: Green Computing"],
                "foresight_task": "Assess how technology can address environmental challenges."
            },
            {
                "group_id": "GROUP_E",
                "chapters": ["Chapter 9: Quantum Computing", "Chapter 10: Quantum Algorithms"],
                "foresight_task": "Explore the emerging field of quantum computing."
            },
            {
                "group_id": "GROUP_F",
                "chapters": ["Chapter 11: Biotechnology", "Chapter 12: Bioinformatics"],
                "foresight_task": "Examine the intersection of biology and technology."
            },
            {
                "group_id": "GROUP_G",
                "chapters": ["Chapter 13: Space Tech", "Chapter 14: Satellites"],
                "foresight_task": "Analyze the future of space technology."
            },
            {
                "group_id": "GROUP_H",
                "chapters": ["Chapter 15: Robotics", "Chapter 16: Automation"],
                "foresight_task": "Explore advances in robotics and industrial automation."
            },
            {
                "group_id": "GROUP_I",
                "chapters": ["Chapter 17: AR/VR", "Chapter 18: Metaverse"],
                "foresight_task": "Analyze immersive technologies and virtual worlds."
            },
            {
                "group_id": "GROUP_J",
                "chapters": ["Chapter 19: Blockchain", "Chapter 20: Web3"],
                "foresight_task": "Examine decentralized technologies and their applications."
            },
            {
                "group_id": "GROUP_K",
                "chapters": ["Chapter 21: Ethics", "Chapter 22: Governance"],
                "foresight_task": "Consider ethical frameworks for emerging technologies."
            }
        ]
    }

    # Pre-generate ALL appendices for complete UI testing
    mock_appendix_content = """# Appendix: Future-Oriented Analysis

## Executive Summary

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## 1. Current State Analysis

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

### 1.1 Key Trends

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.

## 2. Future Projections

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.

### 2.1 Short-term (2025-2028)

- **Trend 1**: Ut enim ad minima veniam
- **Trend 2**: Nisi ut aliquid ex ea commodi consequatur
- **Trend 3**: Quis autem vel eum iure reprehenderit

### 2.2 Long-term (2028-2035)

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium.

## 3. Recommendations

1. **Policy Framework**: Establish comprehensive governance structures
2. **Education Investment**: Develop literacy programs
3. **Research Collaboration**: Foster international cooperation

## Conclusion

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

---
*This appendix was generated for development testing purposes.*
"""

    st.session_state.generated_appendices = {
        "GROUP_A": mock_appendix_content,
        "GROUP_B": mock_appendix_content,
        "GROUP_C": mock_appendix_content,
        "GROUP_D": mock_appendix_content,
        "GROUP_E": mock_appendix_content,
        "GROUP_F": mock_appendix_content,
        "GROUP_G": mock_appendix_content,
        "GROUP_H": mock_appendix_content,
        "GROUP_I": mock_appendix_content,
        "GROUP_J": mock_appendix_content,
        "GROUP_K": mock_appendix_content,
    }

    st.session_state.step4_dev_initialized = True

# Step 3 Dev Mode: Skip directly to Step 3 with mock planning data for layout testing
# Set STEP3_DEV_MODE=true in .env to enable
STEP3_DEV_MODE = os.getenv('STEP3_DEV_MODE', 'false').lower() == 'true'
if STEP3_DEV_MODE and 'step3_dev_initialized' not in st.session_state:
    # Mock prerequisites as complete (API key and book extraction)
    st.session_state.api_key_valid = True
    st.session_state.api_key = "mock-api-key-for-dev"
    st.session_state.book_content = "Mock book content for Step 3 layout development testing."
    st.session_state.extraction_info = {'final_chars': 850000, 'pages': 350, 'was_truncated': False}
    st.session_state.working_model = "gemini-2.5-flash"  # Use free tier model

    # Add mock extraction messages to test layout consistency
    st.session_state.extraction_messages = [
        "📚 Bibliography/References section removed (77,420 chars saved)",
        "📖 Index section removed (5,100 chars saved)"
    ]

    st.session_state.current_step = 3
    st.session_state.step3_dev_initialized = True
    # Mock planning data with realistic structure for layout testing
    st.session_state.planning_data = {
        "book_overview": {
            "title": "Trends and Facts in the Greek Economy: Resources, Infrastructures and Defence",
            "total_chapters": 15,
            "scope": "This book provides a comprehensive analysis of key economic, social, environmental, and geopolitical trends affecting Greece. It delves into the country's natural resources, energy systems, climate change impacts, demographics, and strategic infrastructure.",
            "disciplines": ["Economics", "Political Science", "Environmental Studies", "Demography", "Strategic Studies"],
            "languages": ["Greek", "English"]
        },
        "chapters": [
            {
                "group_id": "GROUP_A",
                "group_type": "Thematic",
                "chapter_numbers": [1, 2, 3],
                "chapter_titles": ["Oil & Gas Reserves", "Critical Minerals", "Water Resources"],
                "content_summary": "This group explores Greece's significant natural resource endowment, focusing on both hydrocarbon reserves in the Aegean Sea and critical minerals essential for the green energy transition.",
                "thematic_quadrants": ["Resource Economics", "Environmental Sustainability", "Geopolitical Strategy", "Technology & Extraction"],
                "foresight_task": "Analyze future resource extraction scenarios considering technological advances, environmental constraints, geopolitical tensions in the Eastern Mediterranean, and the global shift toward sustainable energy sources."
            },
            {
                "group_id": "GROUP_B",
                "group_type": "Methodological",
                "chapter_numbers": [4, 5, 6],
                "chapter_titles": ["Energy Transition", "Renewable Energy", "Grid Infrastructure"],
                "content_summary": "This group comprehensively analyzes Greece's energy system transformation, examining the historical shift from fossil fuels to renewables and the modernization of electrical grid infrastructure.",
                "thematic_quadrants": ["Energy Policy", "Technological Innovation", "Economic Impact", "Infrastructure Development"],
                "foresight_task": "Project energy mix evolution and grid modernization requirements through 2050, considering EU decarbonization targets, regional energy security concerns, and investment requirements for smart grid deployment."
            },
            {
                "group_id": "GROUP_C",
                "group_type": "Empirical",
                "chapter_numbers": [7, 8, 9],
                "chapter_titles": ["Climate Impacts", "Adaptation Strategies", "Coastal Vulnerability"],
                "content_summary": "This group addresses the multifaceted challenge of climate change in Greece, analyzing observed impacts on ecosystems, agriculture, and coastal areas while evaluating adaptation policy frameworks.",
                "thematic_quadrants": ["Environmental Science", "Policy Response", "Economic Adaptation", "Social Resilience"],
                "foresight_task": "Model climate scenarios and assess adaptation investment priorities, including coastal protection infrastructure, agricultural adaptation measures, and urban heat mitigation strategies for major cities."
            },
            {
                "group_id": "GROUP_D",
                "group_type": "Theoretical",
                "chapter_numbers": [10, 11, 12],
                "chapter_titles": ["Population Trends", "Migration Patterns", "Labor Force"],
                "content_summary": "This group explores Greece's demographic landscape and its profound socio-economic implications, examining aging population trends, migration dynamics, and labor market transformations over the coming decades.",
                "thematic_quadrants": ["Demographic Analysis", "Labor Economics", "Social Policy", "Migration Studies"],
                "foresight_task": "Forecast demographic shifts and their economic consequences, including pension system sustainability, healthcare demand projections, labor force composition changes, and integration policy requirements."
            },
            {
                "group_id": "GROUP_E",
                "group_type": "Thematic",
                "chapter_numbers": [13, 14, 15],
                "chapter_titles": ["Transport Networks", "Digital Infrastructure", "Urban Planning"],
                "content_summary": "This group examines Greece's physical and digital infrastructure requirements, analyzing transport connectivity improvements, broadband expansion needs, and sustainable urban development planning challenges.",
                "thematic_quadrants": ["Transport Policy", "Digital Transformation", "Urban Development", "Investment Planning"],
                "foresight_task": "Evaluate infrastructure investment priorities and modernization pathways, considering EU funding opportunities, public-private partnership models, and integration with pan-European transport and digital networks."
            }
        ]
    }
    
    st.session_state.step3_dev_initialized = True


def get_project_state_snapshot() -> dict:
    """Get a snapshot of current project state for comparison."""
    return {
        'book_content': st.session_state.get('book_content'),
        'extraction_info': st.session_state.get('extraction_info'),
        'planning_data': st.session_state.get('planning_data'),
        'generated_appendices': dict(st.session_state.get('generated_appendices', {})),
        'ready_to_generate': st.session_state.get('ready_to_generate', False),
    }


def has_project_data() -> bool:
    """Check if there's any project data (beyond just API key)."""
    return (
        st.session_state.get('book_content') is not None or
        st.session_state.get('planning_data') is not None or
        bool(st.session_state.get('generated_appendices'))
    )


def has_unsaved_changes() -> bool:
    """Check if current state differs from last saved state."""
    if not has_project_data():
        return False

    last_saved = st.session_state.get('last_saved_state')
    if last_saved is None:
        # Never saved - any project data means unsaved changes
        return True

    current = get_project_state_snapshot()
    return current != last_saved


def mark_as_saved():
    """Mark current state as saved."""
    st.session_state.last_saved_state = get_project_state_snapshot()


def clear_project_state():
    """Clear all project-related session state."""
    keys_to_clear = [
        'book_content', 'extraction_info', 'planning_data',
        'generated_appendices', 'ready_to_generate', 'last_saved_state',
        'pending_action', 'pending_load_data', 'truncation_warning',
        'step4_dev_initialized', 'developer_mode_initialized',
        'modal_saved_and_proceed', 'last_processed_file_id',
        'active_generation_tab'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    # Reset to defaults
    st.session_state.generated_appendices = {}
    st.session_state.ready_to_generate = False
    st.session_state.last_saved_state = None


def clear_pending_state():
    """Clear all modal/pending state flags. Call on Cancel or after action completes."""
    keys_to_clear = [
        'pending_action',
        'pending_load_data',
        'modal_saved_and_proceed',
        'last_processed_file_id',
        'api_key_invalid_on_load',
        'awaiting_load_dialog'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def execute_project_load(loaded_data: dict) -> bool:
    """
    Apply loaded project data to session state.

    Args:
        loaded_data: Deserialized session data dict

    Returns:
        True if load succeeded, False if API key is invalid (modal will show)
    """
    # Restore project data
    st.session_state.book_content = loaded_data.get("book_content")
    st.session_state.extraction_info = loaded_data.get("extraction_info")
    st.session_state.planning_data = loaded_data.get("planning_data")
    st.session_state.generated_appendices = loaded_data.get("generated_appendices", {})
    st.session_state.ready_to_generate = loaded_data.get("ready_to_generate", False)
    st.session_state.working_model = loaded_data.get("working_model")

    # Clear file tracking to allow future uploads
    st.session_state.last_processed_file_id = None

    # Restore and validate API key
    api_key = decode_api_key(loaded_data.get("api_key_encoded"))
    if api_key:
        success, _ = test_api_key(api_key)
        if success:
            st.session_state.api_key = api_key
            st.session_state.api_key_valid = True
            st.session_state.working_model = get_working_model(api_key)
            st.session_state.detected_tier = get_detected_tier()  # Store tier in session
            configure_gemini(api_key)
        else:
            st.session_state.api_key_invalid_on_load = True
            st.session_state.api_key_valid = False
    else:
        st.session_state.api_key_valid = False

    # Mark as saved (this is a freshly loaded project)
    mark_as_saved()
    return not st.session_state.get('api_key_invalid_on_load', False)


def create_all_appendices_zip(generated_appendices: dict) -> bytes:
    """Create a ZIP file containing all generated appendices in multiple formats."""
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for group_id, content in generated_appendices.items():
            clean_name = re.sub(r'[^\w\-]', '_', group_id)

            # Add markdown version
            md_bytes = export_to_markdown(content, f"Appendix - {group_id}")
            zf.writestr(f"{clean_name}/appendix_{clean_name}.md", md_bytes)

            # Add docx version
            docx_bytes = export_to_docx(content, f"Appendix - {group_id}")
            zf.writestr(f"{clean_name}/appendix_{clean_name}.docx", docx_bytes)

            # Add pdf version
            pdf_bytes = export_to_pdf(content, f"Appendix - {group_id}")
            zf.writestr(f"{clean_name}/appendix_{clean_name}.pdf", pdf_bytes)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def render_header_and_wizard():
    """Render the header (title, subtitle) and wizard step indicator in a single container"""
    # Check if ALL appendices are generated (Step 4 complete only when all done)
    total_groups = len(st.session_state.planning_data.get('chapters', [])) if st.session_state.planning_data else 0
    generated_count = len(st.session_state.generated_appendices)
    all_generated = total_groups > 0 and generated_count >= total_groups

    steps = [
        ("API Setup", st.session_state.api_key_valid),
        ("Upload Book", st.session_state.book_content is not None),
        ("Analyze & Review", st.session_state.ready_to_generate),  # Complete when user clicks "Proceed"
        ("Generate", all_generated)  # Complete only when ALL appendices are generated
    ]

    # Determine current step (the first incomplete step)
    current = 1
    if st.session_state.api_key_valid:
        current = 2
    if st.session_state.book_content:
        current = 3
    if st.session_state.ready_to_generate:  # Only advance when user explicitly proceeds
        current = 4

    # Build HTML - all in one container for consistent centering
    header_html = '<div class="app-header-container">'
    header_html += '<p class="main-header">Appendix Generator</p>'
    header_html += '<p class="sub-header">Generate Future-Oriented Appendices for Academic Books</p>'
    
    # Accessible Wizard Container
    header_html += '<div class="wizard-container" role="progressbar" aria-label="Completion Progress" aria-valuemin="1" aria-valuemax="4" aria-valuenow="' + str(current) + '">'
    header_html += '<div class="wizard-steps">'

    for i, (label, completed) in enumerate(steps, 1):
        # Connector (before step, except first)
        if i > 1:
            conn_class = "completed" if steps[i-2][1] else ""
            header_html += f'<div class="step-connector {conn_class}" aria-hidden="true"></div>'

        # Step circle
        if completed:
            circle_class = "completed"
            circle_content = "✓"
            aria_current = ""
            step_status = "completed"
        elif i == current:
            circle_class = "current"
            circle_content = str(i)
            aria_current = ' aria-current="step"'
            step_status = "current"
        else:
            circle_class = "upcoming"
            circle_content = str(i)
            aria_current = ""
            step_status = "upcoming"

        label_class = "active" if i == current else ""
        underline_class = "active" if i == current else ""

        header_html += f'''
        <div class="wizard-step" aria-label="Step {i}: {label} ({step_status})">
            <div class="step-circle {circle_class}">{circle_content}</div>
            <div class="step-label {label_class}">{label}</div>
            <div class="step-underline {underline_class}"></div>
        </div>
        '''

    header_html += '</div></div></div>'

    st.markdown(header_html, unsafe_allow_html=True)

    return current


def main():
    # Header and Wizard - rendered in single container for consistent centering
    current_step = render_header_and_wizard()

    # Sidebar
    with st.sidebar:
        # === FILE MENU (Top) - Stacked buttons ===
        st.markdown("**File**")

        # New button - check for unsaved changes or confirm close
        if st.button("New Project", key="new_session", use_container_width=True):
            if has_unsaved_changes():
                st.session_state.pending_action = 'new_project'
            elif st.session_state.book_content is not None:
                # Project exists but is saved - ask for confirmation
                st.session_state.confirm_new_project = True
            else:
                # No project open, just reset
                clear_project_state()
            st.rerun()

        # Save button - mark as saved when clicked
        session_data = save_session(dict(st.session_state))
        filename = get_session_filename(dict(st.session_state))
        if st.download_button(
            "Save Project",
            session_data,
            filename,
            "application/gzip",
            key="save_session",
            use_container_width=True,
            on_click=mark_as_saved
        ):
            pass  # on_click handles marking as saved

        # Load Project button - check unsaved changes first, then open dialog
        if st.button("Load Project", key="load_project_btn", use_container_width=True):
            if has_unsaved_changes():
                # Show unsaved changes warning first
                st.session_state.pending_action = 'load_project'
                st.session_state.awaiting_load_dialog = True  # Flag to show load dialog after
            else:
                st.session_state.show_load_dialog = True
            st.rerun()

        st.markdown("---")

        # === QUICK HELP ===
        with st.expander("Quick Help", expanded=False):
            st.markdown("""
            **Workflow:**
            1. **API Setup** - Get free key from [Google AI Studio](https://aistudio.google.com/apikey)
            2. **Upload Book** - Upload PDF and extract content
            3. **Analyze** - AI creates planning table
            4. **Generate** - Create appendices for chapters
            """, unsafe_allow_html=True)

        with st.expander("About", expanded=False):
            st.markdown("""**Appendix Generator** v1.0
<hr style="margin: 0.5rem 0;">

**Creator:** Elias Pierrakos<br>
**Organization:** eLearning EKPA<br>
**Scientific Supervisor:** Panagiotis Petrakis
<hr style="margin: 0.5rem 0;">

*Made with Google Antigravity* © 2026""", unsafe_allow_html=True)

        # === DEV MODE (if enabled) ===
        if STEP4_DEV_MODE:
            st.markdown("---")
            st.warning("⚠️ **DEV MODE**\nUsing mock data.")
            if st.button("Reset Dev Mode", key="reset_dev"):
                for key in ['step4_dev_initialized', 'generated_appendices']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        # === MODEL INFO (bottom) ===
        if st.session_state.api_key_valid and st.session_state.working_model:
            st.markdown("---")
            # Read tier from session state (persists across steps)
            tier_label = st.session_state.get('detected_tier') or "unknown"
            st.caption(f"Model: {st.session_state.working_model} | Tier: {tier_label}")

    # API Key Modal - shown when loaded session has invalid API key
    if st.session_state.get('api_key_invalid_on_load'):
        @st.dialog("API Key Required")
        def api_key_modal():
            st.markdown("Your saved API key is no longer valid. Please enter a new one to continue.")
            new_key = st.text_input("Google AI Studio API Key", type="password", key="modal_api_key")
            if st.button("Validate & Continue", type="primary", key="modal_validate"):
                if new_key:
                    success, msg = test_api_key(new_key)
                    if success:
                        st.session_state.api_key = new_key
                        st.session_state.api_key_valid = True
                        st.session_state.working_model = get_working_model(new_key)
                        st.session_state.detected_tier = get_detected_tier()  # Store tier in session
                        configure_gemini(new_key)
                        del st.session_state['api_key_invalid_on_load']
                        st.rerun()
                    else:
                        st.error(f"Invalid key: {msg}")

        api_key_modal()

    # Unsaved Changes Confirmation Modal
    if st.session_state.get('pending_action') in ['new_project', 'load_project']:
        action = st.session_state.pending_action
        action_label = "create a new project" if action == 'new_project' else "load another project"

        @st.dialog("Unsaved Changes")
        def unsaved_changes_modal():
            st.markdown(f"You have unsaved changes. Do you want to save before you {action_label}?")

            # Check if user already saved (via the download button)
            if st.session_state.get('modal_saved_and_proceed'):
                # User clicked save, now proceed with action
                pending = st.session_state.pending_action
                pending_data = st.session_state.get('pending_load_data')
                awaiting_load = st.session_state.get('awaiting_load_dialog')

                # Clear pending state FIRST
                clear_pending_state()

                if pending == 'new_project':
                    clear_project_state()
                elif pending == 'load_project':
                    if pending_data:
                        # We have data from sidebar uploader (old flow)
                        execute_project_load(pending_data)
                    elif awaiting_load:
                        # Show load dialog (new flow)
                        st.session_state.show_load_dialog = True

                st.rerun()

            col1, col2, col3 = st.columns(3)

            with col1:
                # Save button - downloads the file
                modal_session_data = save_session(dict(st.session_state))
                modal_filename = get_session_filename(dict(st.session_state))

                def on_save_click():
                    mark_as_saved()
                    st.session_state.modal_saved_and_proceed = True

                st.download_button(
                    "Save Project",
                    modal_session_data,
                    modal_filename,
                    "application/gzip",
                    key="modal_save_download",
                    use_container_width=True,
                    type="primary",
                    on_click=on_save_click
                )

            with col2:
                if st.button("Discard", key="modal_discard", use_container_width=True):
                    # Discard changes and proceed with action
                    pending = st.session_state.pending_action
                    pending_data = st.session_state.get('pending_load_data')
                    awaiting_load = st.session_state.get('awaiting_load_dialog')

                    # Clear pending state FIRST
                    clear_pending_state()

                    if pending == 'new_project':
                        clear_project_state()
                    elif pending == 'load_project':
                        if pending_data:
                            # We have data from sidebar uploader (old flow)
                            execute_project_load(pending_data)
                        elif awaiting_load:
                            # Show load dialog (new flow)
                            st.session_state.show_load_dialog = True

                    st.rerun()

            with col3:
                if st.button("Cancel", key="modal_cancel", use_container_width=True):
                    clear_pending_state()  # Clears ALL flags properly
                    st.rerun()

        unsaved_changes_modal()

    # Load Project Dialog - shown when user clicks Load Project button
    if st.session_state.get('show_load_dialog'):
        @st.dialog("Load Project")
        def load_project_dialog():
            st.markdown("Select a saved project file (.appendix-session) to load:")

            # Use None for type to accept custom extensions, then validate manually
            uploaded_file = st.file_uploader(
                "Choose file",
                type=None,  # Accept all files, validate extension manually
                key="load_dialog_file"
            )

            # Validate file extension
            file_valid = False
            if uploaded_file is not None:
                if uploaded_file.name.endswith('.appendix-session'):
                    file_valid = True
                else:
                    st.error("Please select a .appendix-session file")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Load", key="dialog_load_btn", use_container_width=True, type="primary", disabled=not file_valid):
                    if uploaded_file is not None and file_valid:
                        try:
                            file_data = uploaded_file.read()
                            loaded = load_session(file_data)

                            # Close dialog
                            del st.session_state['show_load_dialog']

                            # Load directly (unsaved changes already handled before dialog)
                            execute_project_load(loaded)
                            st.session_state.load_success = True

                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to load: {str(e)}")

            with col2:
                if st.button("Cancel", key="dialog_cancel_btn", use_container_width=True):
                    del st.session_state['show_load_dialog']
                    st.rerun()

        load_project_dialog()

    # Show load success message in main area
    if st.session_state.get('load_success'):
        st.success("Project loaded successfully!")
        del st.session_state['load_success']

    # Confirm New Project Dialog - shown when closing a saved project
    if st.session_state.get('confirm_new_project'):
        @st.dialog("Close Project")
        def confirm_new_project_dialog():
            st.markdown("Are you sure you want to close this project and start a new one?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Yes", key="confirm_new_yes", use_container_width=True, type="primary"):
                    del st.session_state['confirm_new_project']
                    clear_project_state()
                    st.rerun()

            with col2:
                if st.button("Cancel", key="confirm_new_cancel", use_container_width=True):
                    del st.session_state['confirm_new_project']
                    st.rerun()

        confirm_new_project_dialog()

    # Step 1: API Setup
    if current_step == 1:


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
                st.session_state.detected_tier = get_detected_tier()  # Store tier in session
                configure_gemini(api_key)
                st.rerun()
            else:
                st.session_state.api_key_valid = False
                status_placeholder.empty()
                st.markdown(f'<div class="error-box"><strong>Connection Failed</strong> – {message}<br><br><strong>Need help?</strong> Get your free API key at <a href="https://aistudio.google.com/apikey" target="_blank" style="color: inherit; text-decoration: underline;">Google AI Studio</a></div>', unsafe_allow_html=True)

        # Setup Guide (expanded by default)
        with st.expander("How to get an API key", expanded=True):
            st.markdown("""
            ### Quick Setup Guide:

            1. **Visit** [Google AI Studio](https://aistudio.google.com/apikey)
            2. **Sign in** with your Google account
            3. **Click** "Create API Key" or "Get API Key"
            4. **Copy** the key (starts with "AIza...")
            5. **Paste** it above and click "Validate Key"

            ---

            *Already have a key?* Paste it above to get started!

            **Note:** Gemini 3 Pro (recommended model) needs a **paid tier API Key**. You need to have a Billing Linked Account with Google for the paid tier. The free credits in the paid plan are more than enough - you won't be charged.

            *Want to use a free tier?* The application will use Gemini 2.5 Flash model.
            """)

    # Step 2: Upload Book
    elif current_step == 2:


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

                    # Store extraction messages to show on Step 3
                    messages = []
                    
                    # Bibliography removal info
                    if extraction_info.get('bibliography_removed', False):
                        bib_saved = extraction_info.get('bibliography_chars_saved', 0)
                        messages.append(f"📚 Bibliography/References section removed ({bib_saved:,} chars saved)")
                    
                    # Index removal info
                    if extraction_info.get('index_removed', False):
                        idx_saved = extraction_info.get('index_chars_saved', 0)
                        messages.append(f"📖 Index section removed ({idx_saved:,} chars saved)")
                    
                    # Truncation warning
                    if extraction_info.get('was_truncated', False):
                        messages.append(f"⚠️ Book was large ({extraction_info['original_chars']:,} chars). Kept {extraction_info['kept_percentage']}% (beginning + end). Some middle content was omitted.")
                    
                    if messages:
                        st.session_state.extraction_messages = messages

                    # Auto-advance to Step 3
                    st.rerun()

                except Exception as e:
                    status_placeholder.error(f"Error extracting text: {str(e)}")

    # Step 3: Analyze & Review
    elif current_step == 3:

        # Generation Settings - show BEFORE analysis so user can configure first
        # Only show if analysis hasn't been done yet
        if not st.session_state.planning_data:
            with st.expander("Generation Settings (Optional)", expanded=False):
                st.caption("Customize how appendices are generated:")

                col_years, col_words = st.columns(2)

                with col_years:
                    st.markdown("**Forecast Horizon**")
                    years_ahead = st.slider(
                        "Years ahead",
                        min_value=5,
                        max_value=30,
                        value=st.session_state.forecast_years,
                        step=5,
                        label_visibility="collapsed",
                        help="How many years into the future should the appendix analyze?",
                        key="forecast_years_slider_top"
                    )
                    st.session_state.forecast_years = years_ahead
                    from datetime import datetime
                    current_year = datetime.now().year
                    target_year = current_year + years_ahead
                    st.caption(f"Appendices will analyze trends up to {target_year}")

                with col_words:
                    st.markdown("**Target Word Count**")
                    word_options = {
                        "Short (1500-2000 words)": "1500-2000",
                        "Standard (2500-3500 words)": "2500-3500",
                        "Detailed (4000-5000 words)": "4000-5000"
                    }
                    current_options = list(word_options.keys())
                    current_idx = current_options.index(st.session_state.word_count_option) if st.session_state.word_count_option in current_options else 1

                    selected = st.radio(
                        "Word count",
                        options=current_options,
                        index=current_idx,
                        label_visibility="collapsed",
                        key="word_count_radio_top"
                    )
                    st.session_state.word_count_option = selected
                    st.session_state.word_count_value = word_options[selected]

        # Initialize analyzing state
        if 'analyzing' not in st.session_state:
            st.session_state.analyzing = False

        # Determine button state
        button_disabled = st.session_state.planning_data is not None or st.session_state.analyzing

        col_btn, col_status = st.columns([1, 3])

        with col_btn:
            analyze_clicked = st.button(
                "Analyze Book & Create Planning Table",
                type="primary",
                disabled=button_disabled,
                key="analyze_book_btn"
            )

        with col_status:
            # Determine what status to show
            if st.session_state.analyzing:
                st.markdown('''<div class="progress-timer" style="margin: 0; padding: 0.5rem 1rem;">
                    <div class="spinner"></div>
                    <span>Analyzing book with AI — this may take 30-60 seconds...</span>
                </div>''', unsafe_allow_html=True)
            elif st.session_state.planning_data:
                st.markdown('<div class="success-box" style="margin: 0; padding: 0.5rem 1rem;">✓ <strong>Analysis Complete!</strong> Review below, then go to <strong>Generate</strong></div>', unsafe_allow_html=True)
            
            # Show extraction messages from Step 2 inline here
            elif st.session_state.get('extraction_messages'):
                msg_html = ""
                for msg in st.session_state.extraction_messages:
                    if msg.startswith("⚠️"):
                        msg_html += f'<div class="warning-box" style="margin: 0; margin-bottom: 0.5rem; padding: 0.5rem 1rem;">{msg}</div>'
                    else:
                        msg_html += f'<div class="info-box" style="margin: 0; margin-bottom: 0.5rem; padding: 0.5rem 1rem;">{msg}</div>'
                st.markdown(msg_html, unsafe_allow_html=True)
                
                # Clear after showing once? 
                # User wants persistent alignment, but previously it cleared. 
                # Let's keep the clear logic but AFTER rendering this frame? 
                # Actually, standard Streamlit pattern is to clear on next rerun.
                # If we delete it here, it might disappear on interaction. 
                # For now, let's NOT delete it immediately to see if it stabilizes the layout.
                # del st.session_state.extraction_messages 

        if analyze_clicked:
            # Clear messages when user actually proceeds to analyze
            if 'extraction_messages' in st.session_state:
                del st.session_state.extraction_messages
            st.session_state.analyzing = True
            st.rerun()

        # Perform analysis if in analyzing state (after rerun)
        if st.session_state.analyzing and not st.session_state.planning_data:
            try:
                configure_gemini(st.session_state.api_key)
                prompt = get_analysis_prompt(st.session_state.book_content)
                response = call_gemini(prompt, st.session_state.working_model)
                planning_data = parse_json_response(response)
                st.session_state.planning_data = planning_data
                st.session_state.analyzing = False
                st.rerun()
            except Exception as e:
                st.session_state.analyzing = False
                st.error(f"Error during analysis: {str(e)}")
                with st.expander("Debug info"):
                    st.text(str(e))

        # Step 2b: Review Planning Table
        if st.session_state.planning_data:
            st.divider()
            st.subheader("Review Planning Table")

            planning_data = st.session_state.planning_data

            # Book Overview - two columns for metadata, full width for scope
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

            def get_type_badge_class(group_type):
                """Map group type to CSS badge class."""
                type_lower = (group_type or '').lower()
                if 'thematic' in type_lower or 'theme' in type_lower:
                    return 'thematic'
                elif 'method' in type_lower:
                    return 'methodological'
                elif 'theor' in type_lower:
                    return 'theoretical'
                elif 'empir' in type_lower or 'data' in type_lower:
                    return 'empirical'
                return 'default'

            for i, chapter in enumerate(chapters):
                group_id = chapter.get('group_id', f'Group {i+1}')
                group_type = chapter.get('group_type', 'General')
                chapter_count = len(chapter.get('chapter_numbers', []))
                content_summary = chapter.get('content_summary', 'N/A')
                badge_class = get_type_badge_class(group_type)

                # Use full summary in expander label (no truncation)
                with st.expander(f"{group_id} — {content_summary}", expanded=False):
                    # Header with badges
                    st.markdown(f'''
                    <div class="chapter-card-header">
                        <span class="type-badge {badge_class}">{group_type}</span>
                        <span class="chapter-count-badge">{chapter_count} chapter{"s" if chapter_count != 1 else ""}</span>
                    </div>
                    ''', unsafe_allow_html=True)

                    # Two-column layout
                    col_left, col_right = st.columns([1, 1])

                    # Left Column: Chapters, Titles, Summary, Thematic Quadrants
                    with col_left:
                        chapter_nums = chapter.get('chapter_numbers', [])
                        chapter_titles = chapter.get('chapter_titles', [])

                        st.markdown("**Chapters:**")
                        for num, title in zip(chapter_nums, chapter_titles):
                            st.write(f"  Ch. {num}: {title}")

                        st.markdown("**Summary:**")
                        st.info(content_summary)

                        quadrants = chapter.get('thematic_quadrants', [])
                        if quadrants:
                            st.markdown("**Thematic Quadrants:**")
                            for q in quadrants:
                                st.write(f"  • {q}")

                    # Right Column: Foresight Task
                    with col_right:
                        st.markdown("**Foresight Task (Assignment Brief):**")
                        foresight_text = chapter.get('foresight_task', 'N/A')

                        # Use consistent height with scrolling
                        st.markdown(f'''
                        <div class="info-box" style="max-height: 300px; overflow-y: auto; font-size: 0.9rem; margin-top: 0.5rem;">
                            {foresight_text}
                        </div>
                        ''', unsafe_allow_html=True)

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

            # Bottom section: Settings (can be adjusted), Changes (optional), then Proceed button
            st.divider()

            # Generation Settings (collapsible) - allows adjustment before proceeding
            with st.expander("Generation Settings (Adjust before proceeding)", expanded=False):
                st.caption("You can still adjust these settings before generating appendices:")

                col_years, col_words = st.columns(2)

                with col_years:
                    st.markdown("**Forecast Horizon**")
                    years_ahead = st.slider(
                        "Years ahead",
                        min_value=5,
                        max_value=30,
                        value=st.session_state.forecast_years,
                        step=5,
                        label_visibility="collapsed",
                        help="How many years into the future should the appendix analyze?",
                        key="forecast_years_slider_bottom"
                    )
                    st.session_state.forecast_years = years_ahead
                    from datetime import datetime
                    current_year = datetime.now().year
                    target_year = current_year + years_ahead
                    st.caption(f"Appendices will analyze trends up to {target_year}")

                with col_words:
                    st.markdown("**Target Word Count**")
                    word_options = {
                        "Short (1500-2000 words)": "1500-2000",
                        "Standard (2500-3500 words)": "2500-3500",
                        "Detailed (4000-5000 words)": "4000-5000"
                    }
                    current_options = list(word_options.keys())
                    current_idx = current_options.index(st.session_state.word_count_option) if st.session_state.word_count_option in current_options else 1

                    selected = st.radio(
                        "Word count",
                        options=current_options,
                        index=current_idx,
                        label_visibility="collapsed",
                        key="word_count_radio_bottom"
                    )
                    st.session_state.word_count_option = selected
                    st.session_state.word_count_value = word_options[selected]

            # Collapsible Request Changes section (above proceed button)
            with st.expander("Need to make changes? (Optional)", expanded=False):
                st.caption("Describe any changes you'd like to make to the planning table:")
                change_request = st.text_area(
                    "Change request",
                    placeholder="E.g., 'Combine chapters 4 and 5' or 'Add climate change as a quadrant' or 'Remove chapter 3 from the analysis'",
                    height=100,
                    label_visibility="collapsed"
                )

                if change_request and st.button("Apply Changes", type="secondary"):
                    progress_placeholder = st.empty()
                    progress_placeholder.markdown('''<div class="progress-timer" style="margin: 0; padding: 0.5rem 1rem;">
                        <div class="spinner"></div>
                        <span>Applying changes...</span>
                    </div>''', unsafe_allow_html=True)

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
                        st.success("Changes applied successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error applying changes: {str(e)}")

            # Proceed button - prominent, centered
            st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
            col_spacer1, col_proceed_btn, col_spacer2 = st.columns([1, 2, 1])
            with col_proceed_btn:
                if st.button("Proceed to Generate Appendices", type="primary", use_container_width=True, key="proceed_to_generate"):
                    st.session_state.ready_to_generate = True
                    st.rerun()

            # Add padding at the bottom
            st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

    # Step 4: Generate
    elif current_step == 4:

        chapters = st.session_state.planning_data.get('chapters', [])
        total_groups = len(chapters)
        generated_count = len(st.session_state.generated_appendices)

        # Build tab group data
        tab_group_ids = [ch.get('group_id', f'Group_{i}') for i, ch in enumerate(chapters)]

        # Initialize active tab in session state if not present
        if 'active_generation_tab' not in st.session_state:
            st.session_state.active_generation_tab = tab_group_ids[0] if tab_group_ids else None

        # Ensure active tab is valid (in case chapters changed)
        if st.session_state.active_generation_tab not in tab_group_ids and tab_group_ids:
            st.session_state.active_generation_tab = tab_group_ids[0]

        # Tab Bar Row: Tabs + Download All button
        # Calculate column widths based on number of tabs
        num_tabs = len(tab_group_ids)
        tab_col_widths = [1] * num_tabs + [1]  # Equal width for tabs + download button

        tab_row_cols = st.columns(tab_col_widths)

        # Render tab buttons
        for idx, group_id in enumerate(tab_group_ids):
            with tab_row_cols[idx]:
                is_generated = group_id in st.session_state.generated_appendices
                is_active = group_id == st.session_state.active_generation_tab
                checkmark = " ✓" if is_generated else ""

                # Use different button types: active (disabled primary), completed (primary), incomplete (secondary)
                if is_active:
                    # Active tab - disabled primary, styled orange via CSS
                    st.button(
                        f"{group_id}{checkmark}",
                        key=f"tab_active_{group_id}",
                        type="primary",
                        use_container_width=True,
                        disabled=True  # Can't click already-active tab
                    )
                elif is_generated:
                    # Completed tab (not active) - primary button, styled green via CSS
                    if st.button(
                        f"{group_id}{checkmark}",
                        key=f"tab_complete_{group_id}",
                        type="primary",
                        use_container_width=True
                    ):
                        st.session_state.active_generation_tab = group_id
                        st.rerun()
                else:
                    # Incomplete tab - secondary style (gray)
                    if st.button(
                        f"{group_id}",
                        key=f"tab_btn_{group_id}",
                        type="secondary",
                        use_container_width=True
                    ):
                        st.session_state.active_generation_tab = group_id
                        st.rerun()

        # Download All button in last column (styled blue via CSS)
        with tab_row_cols[-1]:
            if generated_count > 0:
                zip_data = create_all_appendices_zip(st.session_state.generated_appendices)
                st.download_button(
                    f"Download All ({generated_count}/{total_groups})",
                    zip_data,
                    "all_appendices.zip",
                    "application/zip",
                    key="download_all_zip",
                    use_container_width=True
                )
            else:
                # Show disabled-looking button placeholder
                st.button(
                    f"Download All (0/{total_groups})",
                    key="download_all_disabled",
                    use_container_width=True,
                    disabled=True
                )

        # Get selected tab index
        selected_idx = tab_group_ids.index(st.session_state.active_generation_tab)

        # Render only the selected tab content
        chapter = chapters[selected_idx]
        group_id = chapter.get('group_id', 'Unknown')
        brief_text = chapter.get('foresight_task', 'N/A')
        is_generated = group_id in st.session_state.generated_appendices

        # Two-column layout: Content (65%) | Brief (35%)

        col_main, col_brief = st.columns([65, 35], vertical_alignment="top")

        with col_brief:
            # Use a container with position:sticky to keep brief at top
            st.markdown(f"""
            <div style="position: sticky; top: 1rem;">
                <p style="font-weight: 600; margin-bottom: 0.5rem;">📋 Assignment Brief</p>
                <div style="background: #E3F2FD; border-left: 4px solid #2196F3; padding: 1rem; border-radius: 4px; color: #0D47A1;">
                    {brief_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_main:
            if is_generated:
                # GENERATED STATE: Show downloads + preview
                appendix_content = st.session_state.generated_appendices[group_id]

                # Download buttons row
                st.markdown("**Download Appendix**")
                c1, c2, c3, c4 = st.columns(4)
                clean_name = re.sub(r'[^\w\-]', '_', group_id)

                with c1:
                    md_bytes = export_to_markdown(appendix_content, f"Appendix - {group_id}")
                    st.download_button("📥 Markdown", md_bytes, f"appendix_{clean_name}.md", "text/markdown", key=f"md_{group_id}")
                with c2:
                    docx_bytes = export_to_docx(appendix_content, f"Appendix - {group_id}")
                    st.download_button("📥 Word", docx_bytes, f"appendix_{clean_name}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"docx_{group_id}")
                with c3:
                    pdf_bytes = export_to_pdf(appendix_content, f"Appendix - {group_id}")
                    st.download_button("📥 PDF", pdf_bytes, f"appendix_{clean_name}.pdf", "application/pdf", key=f"pdf_{group_id}")
                with c4:
                    if st.button("Regenerate", key=f"regen_{group_id}", type="primary"):
                        st.session_state.confirm_regenerate = group_id
                        st.rerun()

                # Content preview - minimal divider
                st.markdown('<hr style="margin: 0.25rem 0 0 0; border: none; border-top: 1px solid #E2E8F0;">', unsafe_allow_html=True)
                st.markdown(appendix_content)

            else:
                # NOT GENERATED STATE: Show generate button + aligned status
                gen_col, status_col = st.columns([1, 3])

                with gen_col:
                    generate_clicked = st.button("Generate Appendix", type="primary", key=f"gen_{group_id}")

                with status_col:
                    status_placeholder = st.empty()

                if generate_clicked:
                    # Show animated progress indicator
                    status_placeholder.markdown(
                        '''<div class="progress-timer" style="margin: 0; padding: 0.5rem 1rem;">
                            <div class="spinner"></div>
                            <span>Generating appendix with AI...</span>
                        </div>''',
                        unsafe_allow_html=True
                    )

                    try:
                        configure_gemini(st.session_state.api_key)
                        chapter_info = json.dumps(chapter, indent=2)

                        prompt = get_generation_prompt(
                            target_assignment=group_id,
                            chapter_info=chapter_info,
                            book_content=st.session_state.book_content,
                            word_count=st.session_state.get('word_count_value', "2500-3500")
                        )

                        response = call_gemini(prompt, st.session_state.working_model)
                        st.session_state.generated_appendices[group_id] = response
                        st.rerun()

                    except Exception as e:
                        status_placeholder.error(f"Error: {str(e)}")

        # Regenerate Confirmation Dialog (placed after Step 4 content)
        if st.session_state.get('confirm_regenerate'):
            regen_group_id = st.session_state.confirm_regenerate

            @st.dialog("Confirm Regeneration")
            def confirm_regenerate_dialog():
                st.markdown(f"""
                <div class="confirm-dialog-content">
                    <div class="confirm-dialog-warning">
                        This will delete the current appendix for <strong>{regen_group_id}</strong> and generate a new one. This action cannot be undone.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Regenerate", key="confirm_regen_yes", type="primary", use_container_width=True):
                        del st.session_state.generated_appendices[regen_group_id]
                        del st.session_state['confirm_regenerate']
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="confirm_regen_cancel", use_container_width=True):
                        del st.session_state['confirm_regenerate']
                        st.rerun()

            confirm_regenerate_dialog()


if __name__ == "__main__":
    main()
