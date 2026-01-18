# Frequently Asked Questions (FAQ)

## Forward Thinking - Foresight Appendix Generator

---

## General Questions

### What is Forward Thinking - Foresight?

Forward Thinking - Foresight is an AI-powered tool that generates future-oriented appendices for academic books. It analyzes book content, identifies key themes, and creates forward-looking content exploring how topics will evolve 20-30 years into the future.

### Who is this tool for?

- **Academic publishers** preparing new editions or supplementary materials
- **Researchers** exploring long-term implications of their work
- **Think tanks** conducting scenario analyses
- **Educational institutions** creating forward-looking study materials
- **Authors** wanting to add futurist perspectives to their books

### How long does it take?

- **Setup**: 2 minutes (one-time API key setup)
- **Upload & Extract**: 5-30 seconds (depending on PDF size)
- **Analysis**: 30-60 seconds
- **Appendix Generation**: 1-2 minutes per appendix

**Total**: Under 5 minutes from upload to finished appendix

---

## Technical Questions

### What file formats are supported?

Currently, the tool supports **PDF files** with extractable text. Scanned PDFs or image-based documents are not supported (they require OCR processing first).

### How large can my PDF be?

- **Recommended**: Up to 50MB for smooth processing
- **Maximum**: 100MB (larger files will process but may be slower)
- **Page limit**: Works with books up to 600+ pages

Large books are intelligently truncated to preserve beginning and ending chapters while staying within AI processing limits.

### What languages are supported?

The underlying AI (Google Gemini) supports **100+ languages**. The tool works best with:
- English
- Spanish
- French
- German
- Chinese
- Japanese
- And most other major languages

### Do I need to install anything?

**Prerequisites:**
- Python 3.8 or higher
- Required Python packages (install via `pip install -r requirements.txt`)

**That's it!** The app runs entirely on your local machine using Streamlit.

---

## Cost & API Questions

### Is this free to use?

The tool itself is **completely free and open-source**. However, you need:

1. **Google AI API Key** (Free tier available)
   - Free tier: Generous limits for personal/moderate use
   - Paid tiers: Start at very affordable rates for higher volume

### How much does the API cost?

**Free Tier (Google AI Studio):**
- 60 requests per minute
- 1,500 requests per day
- Sufficient for analyzing dozens of books per month

**Paid Tier:**
- Pay-per-use pricing
- Typically a few cents per book analysis
- Enterprise pricing available for high volume

**Estimated costs:**
- Book analysis: ~$0.05-$0.20 per book
- Appendix generation: ~$0.10-$0.30 per appendix

### Where do I get an API key?

Visit [Google AI Studio](https://aistudio.google.com/apikey) and:
1. Sign in with your Google account
2. Click "Create API Key"
3. Copy the key (starts with "AIza...")
4. Paste it in the Foresight sidebar

Takes about 2 minutes.

---

## Privacy & Security Questions

### Is my data secure?

**Yes.** Here's how we protect your data:

- **Local processing**: The app runs entirely on your machine
- **No permanent storage**: PDFs are processed in memory and not saved
- **Encrypted API calls**: Communication with Google AI is encrypted (HTTPS)
- **No data retention**: Google AI doesn't use your data to train models (per their policies)

### Can I use this offline?

**Partially:**
- Upload and extraction: Works offline
- Analysis and generation: Requires internet (API calls to Google AI)

For completely air-gapped use, you'd need to set up a local AI model (advanced setup).

### What happens to my uploaded PDFs?

- PDFs are loaded into memory temporarily
- Text is extracted and processed
- **Nothing is stored permanently**
- When you close the app, all data is cleared

### Can I use this with proprietary/confidential books?

Yes, but be aware:
- Book content is sent to Google AI for processing
- Google's AI services have enterprise-grade security
- For highly sensitive content, consult your organization's data policies

---

## Usage Questions

### Can I customize the output?

**Yes! You can customize:**

1. **Time Horizon**: Default is 2040-2050, but you can adjust
2. **Word Count**: Default is 2,500-3,500 words per appendix
3. **Thematic Focus**: Request specific themes in the planning table
4. **Chapter Groupings**: Modify how chapters are grouped before generation

### Can I edit the generated appendices?

**Absolutely!** Outputs are provided in three formats:

- **Markdown (.md)**: Easy to edit in any text editor
- **Word (.docx)**: Edit directly in Microsoft Word
- **PDF (.pdf)**: Print-ready, but less editable

We recommend treating AI outputs as high-quality first drafts that benefit from expert review and refinement.

### What if the AI makes mistakes?

The AI provides strong first drafts based on patterns in academic literature, but:

- **Always review outputs** for accuracy and relevance
- **Add domain expertise** - you know your field better than any AI
- **Refine and adjust** - think of it as an AI research assistant
- **Regenerate if needed** - you can generate multiple versions

### Can I generate multiple appendices for one book?

**Yes!** After analysis:
- The planning table shows all chapter groups
- You can generate appendices for each group separately
- Download all appendices in one batch (coming soon)

---

## Troubleshooting

### The app says "No valid API key in .env file"

**Solution:**
1. Check that your API key is correctly pasted in the sidebar
2. Click "Validate Key" to test it
3. If using developer mode, verify the `.env` file contains your key

### PDF extraction fails with "No extractable text"

**This means your PDF is image-based** (scanned pages).

**Solutions:**
- Use a PDF with selectable/copyable text
- Convert your scanned PDF using OCR software (Adobe Acrobat, etc.)
- Try a different version of the book

### API calls fail with "Quota exceeded"

**You've hit your API rate limit.**

**Solutions:**
- Wait a few minutes and try again
- Check your usage at [Google AI Studio](https://aistudio.google.com/)
- Upgrade to a paid tier if you need higher limits

### The app is slow or unresponsive

**Possible causes:**
- Large PDF file (>100MB)
- Slow internet connection
- API service is busy

**Solutions:**
- Use smaller PDFs (under 50MB)
- Check your internet connection
- Try again in a few minutes

### Generated appendix is off-topic or low quality

**This can happen occasionally.**

**Solutions:**
- **Regenerate**: Click "Regenerate" to get a fresh version
- **Adjust the planning table**: Request changes to focus on specific themes
- **Provide more specific instructions**: Use the "Request Changes" field

---

## Integration & Deployment Questions

### Can I deploy this for my team?

**Yes!** Options include:

1. **Local deployment**: Each team member runs it on their machine
2. **Shared server**: Deploy on an internal server
3. **Cloud deployment**: Use Streamlit Cloud, AWS, or Azure
4. **Custom integration**: Integrate into existing workflows via API

### Can I white-label this tool?

The tool is **open-source**, so you can:
- Modify the branding and styling
- Add your organization's logo
- Customize the interface
- Extend functionality

### Does this integrate with our existing tools?

**Currently** it's a standalone tool, but it can be integrated with:
- Document management systems
- Publishing workflows
- Content management platforms
- Custom APIs

Custom integration support is available.

### Can we get support or customization help?

For enterprise needs:
- **Customization services**: Tailor the tool to your workflow
- **Training**: Onboard your team
- **Support**: Dedicated support for production use
- **Consulting**: Strategic guidance on AI-powered content generation

---

## Output Quality Questions

### How does the quality compare to human-written content?

**Strengths:**
- Comprehensive coverage of topics
- Structured and well-organized
- Consistent tone and style
- Fast iteration

**Limitations:**
- May lack deep domain expertise
- Benefits from expert review
- Should be treated as a first draft

**Best approach**: Use AI for the heavy lifting, add human expertise for refinement.

### Can I trust the forward-looking predictions?

The AI generates **plausible scenarios** based on:
- Current academic literature
- Established trends
- Logical extrapolations

However:
- These are **speculative** by nature
- Not guaranteed predictions
- Should be reviewed by domain experts
- Best used as thought-starters

### What citation style does it use?

The AI typically uses:
- **Academic style**: Formal, third-person
- **Evidence-based**: References trends and literature
- **Balanced**: Considers multiple perspectives

For specific citation formats (APA, MLA, Chicago), you may need to adjust in post-processing.

---

## Comparison Questions

### How is this different from ChatGPT?

**Foresight advantages:**
- **Specialized**: Built specifically for future-oriented academic content
- **Structured workflow**: Guides you through analysis → planning → generation
- **Book-aware**: Analyzes entire books, not just snippets
- **Export-ready**: Professional formatting in multiple formats
- **Reproducible**: Consistent quality across appendices

### How is this different from hiring a researcher?

**Time**: Minutes vs. days/weeks
**Cost**: Pennies vs. hundreds/thousands of dollars
**Scalability**: Unlimited vs. limited by staff availability
**Expertise**: Broad vs. deep domain knowledge

**Best approach**: Use Foresight for first drafts, researchers for refinement.

---

## Future Features

### What features are planned?

**Coming soon:**
- Batch export (all appendices at once)
- Custom templates for branding
- Multi-language interface
- Citation management integration
- Collaborative editing features
- Advanced analytics dashboard

### Can I request features?

**Yes!** We welcome feedback and feature requests. The tool is open-source and community-driven.

---

## Getting Help

### Where can I get support?

- **Documentation**: README.md and this FAQ
- **Demo Script**: DEMO_SCRIPT.md for detailed walkthrough
- **GitHub Issues**: Report bugs or request features
- **Community**: Join discussions with other users

### I found a bug. What should I do?

Please report it with:
- Description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Screenshots if applicable

---

## Quick Reference

### Essential Links

- **Google AI Studio**: https://aistudio.google.com/apikey
- **Setup Guide**: See README.md
- **Demo Script**: See DEMO_SCRIPT.md

### Key Metrics

- **Setup time**: ~2 minutes
- **Processing time**: <5 minutes per book
- **Output length**: 2,500-3,500 words per appendix
- **Cost per book**: ~$0.15-$0.50 (estimated)

---

**Still have questions?** Check the README.md or DEMO_SCRIPT.md for more details!
