/**
 * SwiftLaTeX PDF Export
 * Uses SwiftLaTeX's PdfTeX engine (WebAssembly) to compile LaTeX to PDF in the browser
 */

import { markdownToLatex, sanitizeFilename } from './latex-template';

// Type definitions for SwiftLaTeX engine
interface CompileResult {
  pdf: Uint8Array;
  log: string;
  status: number;
}

interface PdfTeXEngineInterface {
  loadEngine(): Promise<void>;
  isReady(): boolean;
  writeMemFSFile(filename: string, content: string | Uint8Array): void;
  setEngineMainFile(filename: string): void;
  compileLaTeX(): Promise<CompileResult>;
  flushCache(): void;
}

// Global engine instance (lazy loaded)
let engineInstance: PdfTeXEngineInterface | null = null;
let engineLoading: Promise<PdfTeXEngineInterface> | null = null;
let scriptLoaded = false;

/**
 * Load the PdfTeXEngine script dynamically
 */
async function loadEngineScript(): Promise<void> {
  if (scriptLoaded) return;

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = '/swiftlatex/PdfTeXEngine.js';
    script.async = true;
    script.onload = () => {
      scriptLoaded = true;
      resolve();
    };
    script.onerror = () => {
      reject(new Error('Failed to load SwiftLaTeX engine script'));
    };
    document.head.appendChild(script);
  });
}

/**
 * Get or initialize the SwiftLaTeX engine
 */
async function getEngine(): Promise<PdfTeXEngineInterface> {
  // Return existing engine if ready
  if (engineInstance?.isReady()) {
    return engineInstance;
  }

  // Return loading promise if already loading
  if (engineLoading) {
    return engineLoading;
  }

  // Start loading
  engineLoading = (async () => {
    try {
      // Load the script first
      await loadEngineScript();

      // Create engine instance
      // The PdfTeXEngine class is available globally after script loads
      const PdfTeXEngine = (window as unknown as { PdfTeXEngine: new () => PdfTeXEngineInterface }).PdfTeXEngine;

      if (!PdfTeXEngine) {
        throw new Error('PdfTeXEngine not found after loading script');
      }

      engineInstance = new PdfTeXEngine();

      // Load the WebAssembly engine
      await engineInstance.loadEngine();

      return engineInstance;
    } catch (error) {
      engineLoading = null;
      throw error;
    }
  })();

  return engineLoading;
}

/**
 * Compile LaTeX source to PDF
 */
export async function compileLatexToPdf(latexSource: string): Promise<Blob> {
  const engine = await getEngine();

  // Clear any previous files
  engine.flushCache();

  // Write the LaTeX source
  engine.writeMemFSFile('main.tex', latexSource);
  engine.setEngineMainFile('main.tex');

  // Compile
  const result = await engine.compileLaTeX();

  if (result.status !== 0) {
    console.error('LaTeX compilation log:', result.log);
    throw new Error(`LaTeX compilation failed. Check console for details.`);
  }

  // Create a new Uint8Array copy to ensure clean ArrayBuffer for Blob
  const pdfData = new Uint8Array(result.pdf);
  return new Blob([pdfData], { type: 'application/pdf' });
}

/**
 * Export markdown content as PDF using LaTeX
 * This is the main entry point for PDF export
 */
export async function exportMarkdownAsLatexPdf(
  markdown: string,
  title: string,
  onProgress?: (stage: 'loading' | 'converting' | 'compiling' | 'done') => void
): Promise<void> {
  try {
    // Stage 1: Load engine
    onProgress?.('loading');
    await getEngine();

    // Stage 2: Convert markdown to LaTeX
    onProgress?.('converting');
    const latexSource = markdownToLatex(markdown, title);

    // Log for debugging (can be removed in production)
    console.log('Generated LaTeX source:', latexSource);

    // Stage 3: Compile to PDF
    onProgress?.('compiling');
    const pdfBlob = await compileLatexToPdf(latexSource);

    // Stage 4: Download
    onProgress?.('done');
    const url = URL.createObjectURL(pdfBlob);
    const filename = sanitizeFilename(title) + '.pdf';

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Revoke URL after a short delay
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  } catch (error) {
    console.error('PDF export failed:', error);
    throw error;
  }
}

/**
 * Check if the engine is loaded and ready
 */
export function isEngineReady(): boolean {
  return engineInstance?.isReady() ?? false;
}

/**
 * Pre-load the engine (call this early to reduce wait time later)
 */
export async function preloadEngine(): Promise<void> {
  try {
    await getEngine();
  } catch (error) {
    console.warn('Failed to preload SwiftLaTeX engine:', error);
  }
}
