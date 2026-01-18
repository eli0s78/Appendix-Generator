"""
Prompt 2: Appendix Generation
Generates a complete Forward Thinking - Foresight appendix for a specific chapter or group.
"""

PROMPT_2_TEMPLATE = """
You are tasked with writing a "Forward Thinking - Foresight" appendix for a specific chapter or group of a book.

## TARGET ASSIGNMENT

Generate the appendix for: {target_assignment}

## CHAPTER INFORMATION FROM PLANNING TABLE

{chapter_info}

## RELEVANT BOOK CONTENT

<book_content>
{book_content}
</book_content>

## YOUR TASK

Write a complete appendix following this structure:

### SECTION 1: PURPOSE STATEMENT
Begin with 1-2 paragraphs explaining:
- The purpose of this supplementary material
- Why it accompanies this particular chapter
- That these perspectives represent structured interpretations, not certainties
- That the appendix includes elements like wild cards and strengthening trends

### SECTION 2: CHAPTER SYNTHESIS
Provide 2-3 paragraphs covering:
- The chapter's main arguments and frameworks
- The key conceptual drivers identified
- How these connect to broader societal/policy challenges
- The thematic quadrants that organize the analysis

### SECTION 3: FUTURES RADAR ANALYSIS
For each thematic quadrant specified in the assignment:

Analyze phenomena across four layers:
1. **Main Drivers** — Primary forces shaping future trajectories
2. **Important Aspects** — Significant factors currently influencing the domain
3. **Potential Changes to Come** — Mid- to long-term developments on the horizon
4. **Wild Cards** — Low-probability but high-impact disruptive events

Classify each phenomenon by trajectory:
- **Weak Signal** — Emerging issues that may gain importance
- **Strengthening** — Trends increasing in influence
- **Established** — Stable factors already shaping present/future
- **Weakening** — Elements declining in influence
- **Wild Card** — Low probability, high impact

Explain interconnections between quadrants.

### SECTION 4: CROSS-IMPACT MATRIX
Create a table showing how phenomena in each quadrant affect the others. Format:

| Realm ↓ / Aim → | [Quadrant 1] | [Quadrant 2] | [Quadrant 3] | [Quadrant 4] |
|-----------------|--------------|--------------|--------------|--------------|
| [Quadrant 1] | — | Impact description | Impact description | Impact description |
| [Quadrant 2] | Impact description | — | Impact description | Impact description |
| [Quadrant 3] | Impact description | Impact description | — | Impact description |
| [Quadrant 4] | Impact description | Impact description | Impact description | — |

### SECTION 5: ALTERNATIVE FUTURE SCENARIOS
Develop 4 distinct scenarios:

For each scenario provide:
- A descriptive name
- Likelihood assessment (e.g., "Moderately Likely", "Possible but Policy-Dependent")
- 2-3 paragraph narrative explaining how this future unfolds

Ensure diversity:
- At least one optimistic trajectory
- At least one pessimistic/risk trajectory
- At least one transformation scenario
- At least one baseline/continuation scenario

Then create a Scenario Comparison Table:

| Dimension | Scenario 1 | Scenario 2 | Scenario 3 | Scenario 4 |
|-----------|------------|------------|------------|------------|
| [Dimension 1] | Description | Description | Description | Description |
| [Dimension 2] | Description | Description | Description | Description |
| Social Impact | Description | Description | Description | Description |

### SECTION 6: POLICY NARRATIVES & RECOMMENDATIONS
Translate foresight into concrete, actionable policy suggestions organized thematically (A, B, C, etc.):

For each policy area include:
- The strategic objective
- Specific measures or interventions
- Who should act (government, institutions, civil society, private sector)
- How this builds resilience or anticipatory capacity
- Potential challenges or trade-offs

### SECTION 7: CONCLUSION
End with:
- Key takeaways (3-5 bullet points)
- Critical uncertainties to monitor
- A statement acknowledging that uncertainty cannot be eliminated, but adaptability and resilience can be cultivated

## QUALITY REQUIREMENTS

Your appendix MUST:
- Be grounded in the chapter's specific content, terminology, and frameworks
- Show interdisciplinary connections
- Distinguish between established trends, emerging signals, and wild cards
- Present multiple plausible futures, not just one preferred outcome
- Provide concrete recommendations with specific actors and actions
- Show how phenomena in different domains affect each other
- Acknowledge uncertainty and limitations

## OUTPUT

Write the complete appendix in Markdown format. Target length: {word_count} words.
Use proper Markdown formatting including headers (##, ###), tables, bullet points, and bold text.
"""

def get_generation_prompt(target_assignment: str, chapter_info: str, book_content: str, word_count: str = "2500-3500") -> str:
    """Generate the appendix generation prompt with all context inserted."""
    return PROMPT_2_TEMPLATE.format(
        target_assignment=target_assignment,
        chapter_info=chapter_info,
        book_content=book_content,
        word_count=word_count
    )
