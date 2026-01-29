/**
 * Markdown to LaTeX converter for PDF export
 * Converts markdown content to LaTeX format for compilation with SwiftLaTeX
 */

/**
 * Escape special LaTeX characters
 */
function escapeLatex(text: string): string {
  return text
    .replace(/\\/g, '\\textbackslash{}')
    .replace(/&/g, '\\&')
    .replace(/%/g, '\\%')
    .replace(/\$/g, '\\$')
    .replace(/#/g, '\\#')
    .replace(/_/g, '\\_')
    .replace(/\{/g, '\\{')
    .replace(/\}/g, '\\}')
    .replace(/~/g, '\\textasciitilde{}')
    .replace(/\^/g, '\\textasciicircum{}');
}

/**
 * Convert Unicode arrows and symbols to LaTeX equivalents
 */
function convertSymbols(text: string): string {
  return text
    .replace(/→/g, '$\\rightarrow$')
    .replace(/←/g, '$\\leftarrow$')
    .replace(/↑/g, '$\\uparrow$')
    .replace(/↓/g, '$\\downarrow$')
    .replace(/↔/g, '$\\leftrightarrow$')
    .replace(/⇒/g, '$\\Rightarrow$')
    .replace(/⇐/g, '$\\Leftarrow$')
    .replace(/⇔/g, '$\\Leftrightarrow$')
    .replace(/≤/g, '$\\leq$')
    .replace(/≥/g, '$\\geq$')
    .replace(/≠/g, '$\\neq$')
    .replace(/≈/g, '$\\approx$')
    .replace(/±/g, '$\\pm$')
    .replace(/×/g, '$\\times$')
    .replace(/÷/g, '$\\div$')
    .replace(/∞/g, '$\\infty$')
    .replace(/∑/g, '$\\sum$')
    .replace(/∏/g, '$\\prod$')
    .replace(/√/g, '$\\sqrt{}$')
    .replace(/∈/g, '$\\in$')
    .replace(/∉/g, '$\\notin$')
    .replace(/⊂/g, '$\\subset$')
    .replace(/⊃/g, '$\\supset$')
    .replace(/∪/g, '$\\cup$')
    .replace(/∩/g, '$\\cap$')
    .replace(/∧/g, '$\\land$')
    .replace(/∨/g, '$\\lor$')
    .replace(/¬/g, '$\\neg$')
    .replace(/α/g, '$\\alpha$')
    .replace(/β/g, '$\\beta$')
    .replace(/γ/g, '$\\gamma$')
    .replace(/δ/g, '$\\delta$')
    .replace(/ε/g, '$\\epsilon$')
    .replace(/θ/g, '$\\theta$')
    .replace(/λ/g, '$\\lambda$')
    .replace(/μ/g, '$\\mu$')
    .replace(/π/g, '$\\pi$')
    .replace(/σ/g, '$\\sigma$')
    .replace(/τ/g, '$\\tau$')
    .replace(/φ/g, '$\\phi$')
    .replace(/ω/g, '$\\omega$')
    .replace(/•/g, '$\\bullet$')
    .replace(/◦/g, '$\\circ$')
    .replace(/★/g, '$\\star$')
    .replace(/☆/g, '$\\star$');
}

/**
 * Convert inline markdown formatting to LaTeX
 */
function convertInlineFormatting(text: string): string {
  // Preserve math delimiters - extract and restore after processing
  const mathBlocks: string[] = [];
  let processed = text;

  // Extract display math first ($$...$$)
  processed = processed.replace(/\$\$(.+?)\$\$/g, (_, math) => {
    mathBlocks.push(`\\[${math}\\]`);
    return `%%MATH${mathBlocks.length - 1}%%`;
  });

  // Extract inline math ($...$) - be careful not to match escaped $
  processed = processed.replace(/(?<!\\)\$(.+?)(?<!\\)\$/g, (_, math) => {
    mathBlocks.push(`$${math}$`);
    return `%%MATH${mathBlocks.length - 1}%%`;
  });

  // Convert bold+italic (***text***)
  processed = processed.replace(/\*\*\*(.+?)\*\*\*/g, '\\textbf{\\textit{$1}}');

  // Convert bold (**text**)
  processed = processed.replace(/\*\*(.+?)\*\*/g, '\\textbf{$1}');

  // Convert italic (*text* or _text_)
  processed = processed.replace(/\*(.+?)\*/g, '\\textit{$1}');
  processed = processed.replace(/_(.+?)_/g, '\\textit{$1}');

  // Convert inline code (`code`)
  processed = processed.replace(/`([^`]+)`/g, '\\texttt{$1}');

  // Convert links [text](url)
  processed = processed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '\\href{$2}{$1}');

  // Convert strikethrough (~~text~~)
  processed = processed.replace(/~~(.+?)~~/g, '\\sout{$1}');

  // Convert superscript (^text^)
  processed = processed.replace(/\^([^^]+)\^/g, '\\textsuperscript{$1}');

  // Convert subscript (~text~) - only if not strikethrough
  processed = processed.replace(/(?<!~)~([^~]+)~(?!~)/g, '\\textsubscript{$1}');

  // Convert Unicode symbols
  processed = convertSymbols(processed);

  // Restore math blocks
  mathBlocks.forEach((math, i) => {
    processed = processed.replace(`%%MATH${i}%%`, math);
  });

  return processed;
}

/**
 * Convert a markdown table to LaTeX
 */
function convertTable(lines: string[]): string {
  if (lines.length < 2) return '';

  // Parse header
  const headerCells = lines[0]
    .split('|')
    .filter(cell => cell.trim())
    .map(cell => convertInlineFormatting(cell.trim()));

  const numCols = headerCells.length;
  const colSpec = 'l'.repeat(numCols).split('').join('|');

  let latex = '\\begin{table}[htbp]\n\\centering\n';
  latex += `\\begin{tabular}{|${colSpec}|}\n\\hline\n`;

  // Header row
  latex += headerCells.map(cell => `\\textbf{${cell}}`).join(' & ') + ' \\\\\n\\hline\n';

  // Skip separator row (index 1), process data rows
  for (let i = 2; i < lines.length; i++) {
    const cells = lines[i]
      .split('|')
      .filter(cell => cell.trim())
      .map(cell => convertInlineFormatting(cell.trim()));

    if (cells.length > 0) {
      latex += cells.join(' & ') + ' \\\\\n';
    }
  }

  latex += '\\hline\n\\end{tabular}\n\\end{table}\n';
  return latex;
}

/**
 * Convert markdown list to LaTeX
 */
function convertList(lines: string[], startIndex: number): { latex: string; endIndex: number } {
  const result: string[] = [];
  let i = startIndex;
  let currentIndent = 0;
  let listStack: ('itemize' | 'enumerate')[] = [];

  const getIndentLevel = (line: string): number => {
    const match = line.match(/^(\s*)/);
    return match ? Math.floor(match[1].length / 2) : 0;
  };

  const isOrderedItem = (line: string): boolean => /^\s*\d+\.\s/.test(line);
  const isUnorderedItem = (line: string): boolean => /^\s*[-*+]\s/.test(line);
  const isListItem = (line: string): boolean => isOrderedItem(line) || isUnorderedItem(line);

  while (i < lines.length && isListItem(lines[i])) {
    const line = lines[i];
    const indent = getIndentLevel(line);
    const ordered = isOrderedItem(line);
    const listType = ordered ? 'enumerate' : 'itemize';

    // Handle indent changes
    while (indent > listStack.length) {
      result.push(`\\begin{${listType}}`);
      listStack.push(listType);
    }
    while (indent < listStack.length) {
      const closingType = listStack.pop();
      result.push(`\\end{${closingType}}`);
    }

    // If we're at same level but different list type, close and open
    if (listStack.length > 0 && listStack[listStack.length - 1] !== listType) {
      const closingType = listStack.pop();
      result.push(`\\end{${closingType}}`);
      result.push(`\\begin{${listType}}`);
      listStack.push(listType);
    }

    // If no list started yet, start one
    if (listStack.length === 0) {
      result.push(`\\begin{${listType}}`);
      listStack.push(listType);
    }

    // Extract item content
    const content = line.replace(/^\s*(?:\d+\.|-|\*|\+)\s*/, '').trim();
    result.push(`\\item ${convertInlineFormatting(content)}`);

    i++;
  }

  // Close all remaining lists
  while (listStack.length > 0) {
    const closingType = listStack.pop();
    result.push(`\\end{${closingType}}`);
  }

  return { latex: result.join('\n'), endIndex: i };
}

/**
 * Convert markdown code block to LaTeX
 */
function convertCodeBlock(code: string, language?: string): string {
  // Simple verbatim environment for code
  return `\\begin{verbatim}\n${code}\n\\end{verbatim}`;
}

/**
 * Main function to convert markdown to LaTeX
 */
export function markdownToLatex(markdown: string, title: string): string {
  const lines = markdown.split('\n');
  const latexLines: string[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // Empty line
    if (trimmed === '') {
      latexLines.push('');
      i++;
      continue;
    }

    // Code block
    if (trimmed.startsWith('```')) {
      const language = trimmed.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      latexLines.push(convertCodeBlock(codeLines.join('\n'), language));
      i++; // Skip closing ```
      continue;
    }

    // Headings
    if (trimmed.startsWith('######')) {
      latexLines.push(`\\paragraph{${convertInlineFormatting(trimmed.slice(6).trim())}}`);
      i++;
      continue;
    }
    if (trimmed.startsWith('#####')) {
      latexLines.push(`\\paragraph{${convertInlineFormatting(trimmed.slice(5).trim())}}`);
      i++;
      continue;
    }
    if (trimmed.startsWith('####')) {
      latexLines.push(`\\paragraph{${convertInlineFormatting(trimmed.slice(4).trim())}}`);
      i++;
      continue;
    }
    if (trimmed.startsWith('###')) {
      latexLines.push(`\\subsubsection{${convertInlineFormatting(trimmed.slice(3).trim())}}`);
      i++;
      continue;
    }
    if (trimmed.startsWith('##')) {
      latexLines.push(`\\subsection{${convertInlineFormatting(trimmed.slice(2).trim())}}`);
      i++;
      continue;
    }
    if (trimmed.startsWith('#')) {
      latexLines.push(`\\section{${convertInlineFormatting(trimmed.slice(1).trim())}}`);
      i++;
      continue;
    }

    // Horizontal rule
    if (/^[-*_]{3,}$/.test(trimmed)) {
      latexLines.push('\\hrulefill');
      i++;
      continue;
    }

    // Blockquote
    if (trimmed.startsWith('>')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].trim().slice(1).trim());
        i++;
      }
      latexLines.push('\\begin{quote}');
      latexLines.push(convertInlineFormatting(quoteLines.join(' ')));
      latexLines.push('\\end{quote}');
      continue;
    }

    // Table
    if (trimmed.includes('|') && i + 1 < lines.length && lines[i + 1].includes('---')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].includes('|')) {
        tableLines.push(lines[i]);
        i++;
      }
      latexLines.push(convertTable(tableLines));
      continue;
    }

    // List
    if (/^\s*(?:\d+\.|-|\*|\+)\s/.test(line)) {
      const { latex, endIndex } = convertList(lines, i);
      latexLines.push(latex);
      i = endIndex;
      continue;
    }

    // Regular paragraph
    latexLines.push(convertInlineFormatting(trimmed));
    i++;
  }

  return wrapInDocument(latexLines.join('\n'), title);
}

/**
 * Wrap content in a complete LaTeX document
 */
function wrapInDocument(content: string, title: string): string {
  // Escape title for LaTeX (but preserve for display)
  const safeTitle = title.replace(/[\\%$#&{}_^~]/g, '');

  return `\\documentclass[11pt,a4paper]{article}

% Encoding and fonts
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage{lmodern}

% Math packages
\\usepackage{amsmath,amssymb,amsfonts}

% Graphics and colors
\\usepackage{graphicx}
\\usepackage{xcolor}

% Links
\\usepackage{hyperref}
\\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=blue,
    citecolor=blue
}

% Lists
\\usepackage{enumitem}
\\setlist[itemize]{topsep=2pt,itemsep=1pt,partopsep=0pt,parsep=0pt}
\\setlist[enumerate]{topsep=2pt,itemsep=1pt,partopsep=0pt,parsep=0pt}

% Tables
\\usepackage{booktabs}
\\usepackage{array}

% Strikethrough
\\usepackage[normalem]{ulem}

% Page layout
\\usepackage{geometry}
\\geometry{margin=1in}

% Paragraph spacing
\\setlength{\\parindent}{0pt}
\\setlength{\\parskip}{6pt}

\\title{${safeTitle}}
\\date{}

\\begin{document}

\\maketitle

${content}

\\end{document}
`;
}

/**
 * Sanitize filename for PDF export
 */
export function sanitizeFilename(name: string): string {
  return name
    .replace(/[<>:"/\\|?*]/g, '_')
    .replace(/\s+/g, '_')
    .slice(0, 50) || 'appendix';
}
