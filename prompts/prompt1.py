"""
Prompt 1: Book Analysis & Foresight Planning
Analyzes a book and produces a structured planning table for appendix generation.
"""

PROMPT_1_TEMPLATE = """
You are tasked with analyzing a book to prepare a "Forward Thinking - Foresight" framework. Your goal is to create a structured planning document that will guide the subsequent generation of future-oriented appendices for each chapter (or chapter group).

## THE BOOK CONTENT

The following is the extracted text from the book. 
NOTE: For very long books, some middle content may have been truncated (marked with "[... CONTENT TRUNCATED ...]"). However, the beginning (including Table of Contents) and end of the book are preserved.

<book_content>
{book_content}
</book_content>

## YOUR TASK

### STEP 1: READ AND MAP THE BOOK - FIND ALL CHAPTERS
CRITICAL: You must identify ALL chapters in the book, not just the ones with full content.

To find all chapters:
1. FIRST look for a Table of Contents (usually near the beginning) - this lists ALL chapters
2. Look for chapter headings throughout the text (e.g., "Chapter 1:", "CHAPTER ONE", "1.", etc.)
3. Look for Part/Section divisions that may contain multiple chapters
4. Check BOTH the beginning AND end of the text for chapter markers
5. If content was truncated, infer missing chapters from the Table of Contents or chapter numbering patterns

For each chapter, note:
- Chapter number and title
- Approximate page location (if visible)
- Whether full content is available or only referenced in TOC

### STEP 2: ANALYZE EACH CHAPTER
For each chapter (even if content was truncated), determine:
- Core subject matter and key arguments (from available content or TOC entry)
- Main concepts, theories, or frameworks introduced
- The chapter's role within the book's overall narrative
- Key conceptual drivers that would anchor a foresight analysis

For chapters with truncated content, base your analysis on:
- The chapter title
- Any partial content available
- Context from surrounding chapters
- The Table of Contents description (if any)

### STEP 3: IDENTIFY THEMATIC QUADRANTS
For each chapter (or group), identify 3-5 thematic quadrants that organize the chapter's subject matter. These quadrants will structure the Futures Radar analysis in the appendix.

Examples of quadrant themes:
- Economic & Technological Transformation
- National Power & Security
- Social Cohesion & Governance
- Well-Being & Life Satisfaction
- Environmental Resilience
- Institutional Evolution
- Labor & Demographics
- Knowledge & Innovation Systems

### STEP 4: IDENTIFY POTENTIAL CHAPTER GROUPINGS
Group chapters ONLY if:
- They address the same core phenomenon from different angles
- A combined appendix would be more coherent than separate ones
- Separate appendices would result in significant redundancy

Keep chapters STANDALONE if:
- They have a distinct, self-contained focus
- Their foresight implications are unique

### STEP 5: CREATE THE FORESIGHT PLANNING TABLE

## OUTPUT FORMAT

Respond with a JSON object in this exact structure:

```json
{{
  "book_overview": {{
    "title": "Book title",
    "scope": "Brief description of the book's scope",
    "total_chapters": 0,
    "disciplines": ["List", "of", "disciplines"],
    "languages": ["Languages used"]
  }},
  "chapters": [
    {{
      "group_id": "GROUP_A or STANDALONE_1",
      "group_type": "GROUP or STANDALONE",
      "chapter_numbers": [1, 2, 3],
      "chapter_titles": ["Title 1", "Title 2", "Title 3"],
      "content_summary": "3-5 sentence summary of the chapter(s) content",
      "thematic_quadrants": ["Quadrant 1", "Quadrant 2", "Quadrant 3", "Quadrant 4"],
      "foresight_task": "Detailed 200-350 word assignment brief specifying: (A) Futures Radar Analysis instructions with phenomena to examine across 4 layers, (B) Cross-Impact Matrix requirements, (C) 4 scenario specifications (optimistic, pessimistic, transformative, baseline), (D) Policy narrative areas to address, (E) Parameters including time horizon and word count target"
    }}
  ],
  "implementation_notes": "Any observations for the person generating appendices, including notes about chapters with limited content"
}}
```

IMPORTANT: 
- Include ALL chapters from the book, even if some content was truncated
- The total_chapters count must match the actual number of chapters in the book
- The foresight_task must be detailed and specific to the chapter content
- Include specific phenomena, trends, and wild cards relevant to each chapter
- Specify time horizon (typically 2040-2050) and word count (typically 2000-4000 words)
- In implementation_notes, mention any chapters that had limited content due to truncation
- Respond ONLY with the JSON object, no additional text
"""

def get_analysis_prompt(book_content: str) -> str:
    """Generate the analysis prompt with book content inserted."""
    return PROMPT_1_TEMPLATE.format(book_content=book_content)
