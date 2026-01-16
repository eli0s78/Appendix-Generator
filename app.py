"""
Forward Thinking - Foresight Appendix Generator

A Streamlit application that helps generate future-oriented appendices for academic books.
Uses Google Gemini for AI analysis and generation.
"""

import streamlit as st
import json
from prompts import get_analysis_prompt, get_generation_prompt
from utils import (
    extract_text_from_pdf,
    get_pdf_info,
    truncate_content,
    configure_gemini,
    call_gemini,
    parse_json_response,
    test_api_key,
    get_working_model,
    export_to_markdown,
    export_to_docx,
    export_planning_table_to_markdown
)

# Page configuration
st.set_page_config(
    page_title="Foresight Appendix Generator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E5A7C;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E8F4F8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D4EDDA;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3CD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'book_content' not in st.session_state:
    st.session_state.book_content = None
if 'planning_data' not in st.session_state:
    st.session_state.planning_data = None
if 'generated_appendices' not in st.session_state:
    st.session_state.generated_appendices = {}
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'working_model' not in st.session_state:
    st.session_state.working_model = "gemini-2.5-pro-preview-05-06"


def main():
    # Header
    st.markdown('<p class="main-header">🔮 Forward Thinking - Foresight</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate Future-Oriented Appendices for Academic Books</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        st.subheader("1. API Key")
        api_key = st.text_input(
            "Google AI Studio API Key",
            type="password",
            help="Get your free API key from https://aistudio.google.com/apikey"
        )
        
        if api_key:
            if st.button("Validate Key"):
                with st.spinner("Validating..."):
                    success, message = test_api_key(api_key)
                    if success:
                        st.session_state.api_key_valid = True
                        st.session_state.api_key = api_key
                        st.session_state.working_model = get_working_model(api_key)
                        configure_gemini(api_key)
                        st.success(f"✅ {message}")
                    else:
                        st.session_state.api_key_valid = False
                        st.error(f"❌ {message}")
        
        if st.session_state.api_key_valid:
            st.success("✅ API Connected")
        
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
        st.warning("👈 Please enter and validate your Google AI Studio API key in the sidebar to begin.")
        
        with st.expander("How to get a free API key"):
            st.markdown("""
            1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
            2. Sign in with your Google account
            3. Click "Create API Key"
            4. Copy the key and paste it in the sidebar
            
            **Note:** The free tier has generous limits for personal use.
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
        # Get PDF info
        pdf_info = get_pdf_info(uploaded_file)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages", pdf_info.get('pages', 'N/A'))
        with col2:
            st.metric("Est. Words", f"{int(pdf_info.get('estimated_words', 0)):,}")
        with col3:
            st.metric("Has Text", "✅ Yes" if pdf_info.get('has_text') else "❌ No")
        
        if not pdf_info.get('has_text'):
            st.error("This PDF doesn't appear to have extractable text. It may be scanned/image-based.")
            return
        
        # Extract text button
        if st.button("📖 Extract Book Content", type="primary"):
            with st.spinner("Extracting text from PDF..."):
                try:
                    uploaded_file.seek(0)
                    content = extract_text_from_pdf(uploaded_file)
                    content = truncate_content(content)
                    st.session_state.book_content = content
                    st.success(f"✅ Extracted {len(content):,} characters from the book")
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
            with st.spinner("Analyzing book with Gemini 3 Pro... This may take a minute."):
                try:
                    configure_gemini(st.session_state.api_key)
                    prompt = get_analysis_prompt(st.session_state.book_content)
                    response = call_gemini(prompt, st.session_state.working_model)
                    planning_data = parse_json_response(response)
                    st.session_state.planning_data = planning_data
                    st.success("✅ Analysis complete!")
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
        col1, col2 = st.columns(2)
        with col1:
            planning_md = export_planning_table_to_markdown(planning_data)
            st.download_button(
                "📥 Download Planning Table (.md)",
                planning_md,
                file_name="planning_table.md",
                mime="text/markdown"
            )
        
        # Request changes
        st.divider()
        st.subheader("Request Changes")
        change_request = st.text_area(
            "Describe any changes you'd like to make to the planning table:",
            placeholder="E.g., 'Combine chapters 4 and 5 into one group' or 'Add climate change as a quadrant for Group A'",
            height=100
        )
        
        if change_request and st.button("🔄 Apply Changes"):
            with st.spinner("Applying changes..."):
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
                    st.success("✅ Changes applied! Please review the updated table.")
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
            with st.spinner("Generating appendix with Gemini 3 Pro... This may take 1-2 minutes."):
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
                    st.success("✅ Appendix generated!")
                    
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
            col1, col2, col3 = st.columns(3)
            
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
