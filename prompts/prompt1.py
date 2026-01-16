"""
Prompt 1: Book Analysis & Foresight Planning
Analyzes a book and produces a structured planning table for appendix generation.
"""

PROMPT_1_TEMPLATE = """
You are tasked with analyzing a book to prepare a "Forward Thinking - Foresight" framework. Your goal is to create a structured planning document that will guide the subsequent generation of future-oriented appendices for each chapter (or chapter group).

## THE BOOK CONTENT

The following is the extracted text from the book:

<book_content>
{book_content}
</book_content>

## YOUR TASK

### STEP 1: READ AND MAP THE BOOK
- Identify all chapters, their titles, and approximate page locations
- Note the book's overall theme and disciplinary scope
- Identify any existing Part/Section divisions
- Note the language of each chapter (if multilingual)

### STEP 2: ANALYZE EACH CHAPTER
For each chapter, determine:
- Core subject matter and key arguments
- Main concepts, theories, or frameworks introduced
- The chapter's role within the book's overall narrative
- Key conceptual drivers that would anchor a foresight analysis

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
  "implementation_notes": "Any observations for the person generating appendices"
}}
```

IMPORTANT: 
- The foresight_task must be detailed and specific to the chapter content
- Include specific phenomena, trends, and wild cards relevant to each chapter
- Specify time horizon (typically 2040-2050) and word count (typically 2000-4000 words)
- Respond ONLY with the JSON object, no additional text
"""

def get_analysis_prompt(book_content: str) -> str:
    """Generate the analysis prompt with book content inserted."""
    return PROMPT_1_TEMPLATE.format(book_content=book_content)
