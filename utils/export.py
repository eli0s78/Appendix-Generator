"""
Export utilities - Convert appendix content to downloadable formats.
"""

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re


def export_to_markdown(content: str, title: str) -> bytes:
    """
    Export content as a Markdown file.
    
    Args:
        content: Markdown content
        title: Document title
        
    Returns:
        Bytes of the markdown file
    """
    full_content = f"# {title}\n\n{content}"
    return full_content.encode('utf-8')


def export_to_docx(content: str, title: str) -> bytes:
    """
    Export Markdown content as a Word document.
    
    Args:
        content: Markdown content
        title: Document title
        
    Returns:
        Bytes of the .docx file
    """
    doc = Document()
    
    # Add title
    title_para = doc.add_heading(title, 0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Process markdown content
    lines = content.split('\n')
    current_table_data = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if not in_table:
                doc.add_paragraph()
            continue
        
        # Handle tables
        if line.startswith('|'):
            in_table = True
            # Skip separator lines
            if re.match(r'^\|[\s\-:|]+\|$', line):
                continue
            # Parse table row
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            current_table_data.append(cells)
            continue
        elif in_table:
            # End of table, create it
            if current_table_data:
                create_table(doc, current_table_data)
                current_table_data = []
            in_table = False
        
        # Handle headings
        if line.startswith('### '):
            doc.add_heading(line[4:], level=3)
        elif line.startswith('## '):
            doc.add_heading(line[3:], level=2)
        elif line.startswith('# '):
            doc.add_heading(line[2:], level=1)
        # Handle bullet points
        elif line.startswith('- ') or line.startswith('* '):
            para = doc.add_paragraph(style='List Bullet')
            add_formatted_text(para, line[2:])
        # Handle numbered lists
        elif re.match(r'^\d+\.\s', line):
            para = doc.add_paragraph(style='List Number')
            text = re.sub(r'^\d+\.\s', '', line)
            add_formatted_text(para, text)
        # Regular paragraph
        else:
            para = doc.add_paragraph()
            add_formatted_text(para, line)
    
    # Handle any remaining table
    if current_table_data:
        create_table(doc, current_table_data)
    
    # Save to bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def create_table(doc: Document, data: list):
    """Create a table in the document from parsed data."""
    if not data or not data[0]:
        return
    
    rows = len(data)
    cols = len(data[0])
    
    table = doc.add_table(rows=rows, cols=cols)
    table.style = 'Table Grid'
    
    for i, row_data in enumerate(data):
        row = table.rows[i]
        for j, cell_text in enumerate(row_data):
            if j < len(row.cells):
                cell = row.cells[j]
                cell.text = cell_text
                # Bold header row
                if i == 0:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
    
    # Add spacing after table
    doc.add_paragraph()


def add_formatted_text(paragraph, text: str):
    """Add text to paragraph with basic markdown formatting (bold, italic)."""
    # Handle bold and italic
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
    
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        else:
            paragraph.add_run(part)


def export_planning_table_to_markdown(planning_data: dict) -> bytes:
    """
    Export the planning table as a Markdown file.
    
    Args:
        planning_data: The parsed planning data from Prompt 1
        
    Returns:
        Bytes of the markdown file
    """
    content = []
    
    # Book overview
    overview = planning_data.get('book_overview', {})
    content.append(f"# Foresight Planning Table")
    content.append(f"\n## Book Overview\n")
    content.append(f"**Title:** {overview.get('title', 'N/A')}")
    content.append(f"**Scope:** {overview.get('scope', 'N/A')}")
    content.append(f"**Total Chapters:** {overview.get('total_chapters', 'N/A')}")
    content.append(f"**Disciplines:** {', '.join(overview.get('disciplines', []))}")
    
    # Chapters table
    content.append(f"\n## Planning Table\n")
    
    for chapter in planning_data.get('chapters', []):
        content.append(f"### {chapter.get('group_id', 'Unknown')}")
        content.append(f"**Chapters:** {', '.join(map(str, chapter.get('chapter_numbers', [])))}")
        content.append(f"**Titles:** {', '.join(chapter.get('chapter_titles', []))}")
        content.append(f"\n**Summary:** {chapter.get('content_summary', '')}")
        content.append(f"\n**Thematic Quadrants:** {', '.join(chapter.get('thematic_quadrants', []))}")
        content.append(f"\n**Foresight Task:**\n{chapter.get('foresight_task', '')}")
        content.append("\n---\n")
    
    # Implementation notes
    if planning_data.get('implementation_notes'):
        content.append(f"## Implementation Notes\n")
        content.append(planning_data['implementation_notes'])
    
    return '\n'.join(content).encode('utf-8')
