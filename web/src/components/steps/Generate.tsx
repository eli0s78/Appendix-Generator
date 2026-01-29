'use client';

import { useState, useRef, useEffect } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { useAppState, ChapterGroup } from '@/hooks/useAppState';
import { callGemini, getWorkingModel } from '@/lib/gemini-client';
import { getGenerationPrompt } from '@/lib/prompts';
import { exportToMarkdown, exportToDocx, exportAllAsZip } from '@/lib/export';
import { MarkdownPreview } from '@/components/MarkdownPreview';
import { LoadingOverlay } from '@/components/LoadingOverlay';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Loader2,
  Wand2,
  Download,
  FileText,
  FileType,
  Printer,
  Archive,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';

export function Generate() {
  const {
    apiKey,
    detectedTier,
    bookContent,
    planningData,
    generatedAppendices,
    addGeneratedAppendix,
    wordCountOption,
    forecastYears,
  } = useAppState();

  const [activeTab, setActiveTab] = useState<string>(
    planningData?.chapters?.[0]?.group_id || ''
  );
  const [isGenerating, setIsGenerating] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pdfExportStatus, setPdfExportStatus] = useState<{
    isExporting: boolean;
    stage: string;
  }>({ isExporting: false, stage: '' });
  const [pdfGroupId, setPdfGroupId] = useState<string | null>(null);
  const printRef = useRef<HTMLDivElement>(null);

  // AbortController ref for cancellation
  const generateAbortRef = useRef<AbortController | null>(null);

  // Warmup the PDF generator on mount (unpack chromium)
  useEffect(() => {
    fetch('/api/export/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ warmup: true }),
    }).catch(err => console.debug('PDF warmup skipped:', err));
  }, []);

  const handleGenerate = async (group: ChapterGroup) => {
    if (!apiKey || !bookContent || !planningData) return;

    // Create new AbortController for this request
    generateAbortRef.current = new AbortController();

    setIsGenerating(group.group_id);
    setError(null);

    try {
      const model = getWorkingModel(detectedTier);

      // Build chapter info from the group's data
      const chapterInfo = `Group ID: ${group.group_id}
Type: ${group.group_type}
Chapters: ${group.chapter_numbers?.join(', ')}
Titles: ${group.chapter_titles?.join(', ')}

Summary:
${group.content_summary}

Thematic Quadrants:
${group.thematic_quadrants?.join('\n- ') || 'Not specified'}

Foresight Task:
${group.foresight_task}`;

      // Build a title from the group data
      const groupTitle = group.chapter_titles?.length === 1
        ? group.chapter_titles[0]
        : `Chapters ${group.chapter_numbers?.join(', ')}`;

      const prompt = getGenerationPrompt(
        `${group.group_id}: ${groupTitle}`,
        chapterInfo,
        bookContent,
        wordCountOption,
        forecastYears
      );

      const response = await callGemini(apiKey, prompt, model, generateAbortRef.current.signal);
      addGeneratedAppendix(group.group_id, response);
    } catch (err) {
      // Don't show error if it was cancelled
      if (err instanceof Error && err.name === 'AbortError') {
        // Cancelled by user - do nothing, keep existing data
      } else {
        setError(err instanceof Error ? err.message : 'Generation failed');
      }
    } finally {
      setIsGenerating(null);
      generateAbortRef.current = null;
    }
  };

  const handleCancelGenerate = () => {
    if (generateAbortRef.current) {
      generateAbortRef.current.abort();
    }
  };

  const handleDownloadMarkdown = (groupId: string) => {
    const content = generatedAppendices[groupId];
    if (content) {
      const group = planningData?.chapters?.find((g) => g.group_id === groupId);
      const title = group?.chapter_titles?.join('_') || groupId;
      exportToMarkdown(content, `Appendix_${groupId}_${title}`);
    }
  };

  const handleDownloadDocx = async (groupId: string) => {
    const content = generatedAppendices[groupId];
    if (content) {
      const group = planningData?.chapters?.find((g) => g.group_id === groupId);
      const title = group?.chapter_titles?.join('_') || groupId;
      await exportToDocx(content, `Appendix_${groupId}_${title}`);
    }
  };

  const handleDownloadPdf = (groupId: string) => {
    setPdfGroupId(groupId);
  };

  // Effect to handle PDF generation when content is ready in the hidden div
  useEffect(() => {
    if (pdfGroupId && printRef.current && generatedAppendices[pdfGroupId]) {
      const doExport = async () => {
        const group = planningData?.chapters?.find(g => g.group_id === pdfGroupId);
        const title = group?.chapter_titles?.join('_') || pdfGroupId;

        setPdfExportStatus({ isExporting: true, stage: 'Preparing layout...' });

        try {
          if (!printRef.current?.innerHTML) {
            throw new Error('Print content not ready');
          }

          // Force a small delay to ensure MathJax/images are rendered
          await new Promise(resolve => setTimeout(resolve, 1000));

          // Convert Markdown to HTML for the PDF generator
          console.log('Converting Markdown to HTML...');
          const htmlContent = printRef.current.innerHTML;

          // Add Tailwind typography classes to the HTML wrapper
          const styledHtml = `
            <div class="prose prose-sm max-w-none">
              <h1 class="text-2xl font-bold mb-4" style="color: #4A4A8A;">${title}</h1>
              ${htmlContent}
            </div>
          `;

          setPdfExportStatus(prev => ({ ...prev, stage: 'Generating PDF on server...' }));

          console.log('Sending request to PDF API...');
          const response = await fetch('/api/export/pdf', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              html: styledHtml,
              // We can inject custom CSS here if needed
              styles: `
                h1, h2, h3 { color: #4A4A8A; }
                blockquote { border-left: 4px solid #e5e7eb; padding-left: 1rem; font-style: italic; }
              `
            }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.details || errorData.error || 'Failed to generate PDF on server');
          }

          const blob = await response.blob();

          // Dynamically import file-saver to avoid SSR issues
          const { saveAs } = await import('file-saver');
          saveAs(blob, `Appendix_${pdfGroupId}_${title}.pdf`);

        } catch (err) {
          console.error('PDF export error:', err);
          setError(err instanceof Error ? `PDF Error: ${err.message}` : 'Failed to export PDF.');
        } finally {
          setPdfExportStatus({ isExporting: false, stage: '' });
          setPdfGroupId(null);
        }
      };

      doExport();
    }
  }, [pdfGroupId, generatedAppendices, planningData]);

  const handleDownloadAll = async () => {
    if (Object.keys(generatedAppendices).length > 0 && planningData) {
      // Define the PDF generator callback
      const pdfGenerator = async (content: string, title: string): Promise<Blob> => {
        // 1. Render Markdown to HTML using the same component as preview for consistency
        const rawHtml = renderToStaticMarkup(<MarkdownPreview content={content} />);

        // 2. Wrap effectively like the single export
        const titleLine = planningData?.chapters?.find(g => g.group_id === title)?.chapter_titles?.join('_') || title;

        const styledHtml = `
            <div class="prose prose-sm max-w-none">
              <h1 class="text-2xl font-bold mb-4" style="color: #4A4A8A;">${titleLine}</h1>
              ${rawHtml}
            </div>
          `;

        // 3. Call API with consistent styles
        const response = await fetch('/api/export/pdf', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            html: styledHtml,
            styles: `
                h1, h2, h3 { color: #4A4A8A; }
                blockquote { border-left: 4px solid #e5e7eb; padding-left: 1rem; font-style: italic; }
              `
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to generate PDF');
        }

        return await response.blob();
      };

      setPdfExportStatus({ isExporting: true, stage: 'Generating ZIP with PDFs...' });

      try {
        await exportAllAsZip(
          generatedAppendices,
          planningData.book_overview.title,
          pdfGenerator
        );
      } catch (error) {
        console.error("ZIP export failed:", error);
        setError("Failed to generate ZIP file.");
      } finally {
        setPdfExportStatus({ isExporting: false, stage: '' });
      }
    }
  };

  const generatedCount = Object.keys(generatedAppendices).length;
  const totalCount = planningData?.chapters?.length || 0;

  if (!planningData) {
    return (
      <Alert>
        <AlertDescription>
          Please complete the analysis step first.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Loading Overlay for AI Generation */}
      <LoadingOverlay
        isOpen={isGenerating !== null}
        message="Generating Appendix"
        subMessage={`Creating foresight analysis for ${isGenerating}...`}
        onCancel={handleCancelGenerate}
      />

      {/* Loading Overlay for PDF Export */}
      <LoadingOverlay
        isOpen={pdfExportStatus.isExporting}
        message="Exporting PDF"
        subMessage={pdfExportStatus.stage}
      />

      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Wand2 className="w-5 h-5" />
              Generate Appendices
            </span>
            <Badge variant={generatedCount === totalCount ? 'default' : 'secondary'}>
              {generatedCount} / {totalCount} Generated
            </Badge>
          </CardTitle>
          <CardDescription>
            Generate future-oriented appendices based on your planning table (targeting {new Date().getFullYear() + forecastYears})
          </CardDescription>
        </CardHeader>
        {generatedCount > 0 && (
          <CardContent>
            <Button onClick={handleDownloadAll} variant="outline" className="w-full">
              <Archive className="w-4 h-4 mr-2" />
              Download All ({generatedCount} appendices) as ZIP
            </Button>
          </CardContent>
        )}
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Tabs for each appendix */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="flex flex-wrap w-full !h-auto justify-start gap-2 p-2 bg-muted">
          {planningData.chapters?.map((group: ChapterGroup) => (
            <TabsTrigger
              key={group.group_id}
              value={group.group_id}
              className="relative data-[state=active]:bg-background h-auto py-2 px-3 text-left whitespace-normal h-auto min-h-[2rem]"
            >
              <div className="flex items-center gap-2">
                <span>{group.group_id}</span>
                {generatedAppendices[group.group_id] && (
                  <CheckCircle2 className="w-3 h-3 text-green-500 flex-shrink-0" />
                )}
              </div>
            </TabsTrigger>
          ))}
        </TabsList>

        {planningData.chapters?.map((group: ChapterGroup) => (
          <TabsContent key={group.group_id} value={group.group_id} className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  {group.chapter_titles?.join(' & ') || `Chapters ${group.chapter_numbers?.join(', ')}`}
                </CardTitle>
                <CardDescription>{group.content_summary}</CardDescription>
                <div className="flex gap-1 flex-wrap mt-2">
                  {group.chapter_numbers?.map((ch: number) => (
                    <Badge key={ch} variant="outline" className="text-xs">
                      Chapter {ch}
                    </Badge>
                  ))}
                  <Badge variant={group.group_type === 'GROUP' ? 'default' : 'secondary'} className="text-xs">
                    {group.group_type}
                  </Badge>
                </div>
                {group.thematic_quadrants && group.thematic_quadrants.length > 0 && (
                  <div className="flex gap-1 flex-wrap mt-2">
                    {group.thematic_quadrants.map((q: string, i: number) => (
                      <Badge key={i} variant="outline" className="text-xs bg-purple-50">
                        {q}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                {!generatedAppendices[group.group_id] ? (
                  <Button
                    onClick={() => handleGenerate(group)}
                    disabled={isGenerating !== null}
                    className="w-full"
                    size="lg"
                  >
                    {isGenerating === group.group_id ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating appendix...
                      </>
                    ) : (
                      <>
                        <Wand2 className="w-4 h-4 mr-2" />
                        Generate This Appendix
                      </>
                    )}
                  </Button>
                ) : (
                  <>
                    {/* Generated Content Preview - Rich Text */}
                    <div className="bg-background border border-border rounded-lg p-6 max-h-[600px] overflow-y-auto">
                      <MarkdownPreview content={generatedAppendices[group.group_id]} />
                    </div>

                    <Separator />

                    {/* Download Options */}
                    <div className="flex flex-wrap gap-2">
                      <Button
                        onClick={() => handleDownloadMarkdown(group.group_id)}
                        variant="outline"
                        size="sm"
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        Download Markdown
                      </Button>
                      <Button
                        onClick={() => handleDownloadDocx(group.group_id)}
                        variant="outline"
                        size="sm"
                      >
                        <FileType className="w-4 h-4 mr-2" />
                        Download Word
                      </Button>
                      <Button
                        onClick={() => handleDownloadPdf(group.group_id)}
                        variant="outline"
                        size="sm"
                      >
                        <Printer className="w-4 h-4 mr-2" />
                        Download PDF
                      </Button>
                      <Button
                        onClick={() => handleGenerate(group)}
                        variant="ghost"
                        size="sm"
                        disabled={isGenerating !== null}
                      >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Regenerate
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Hidden Print Container */}
      <div style={{ position: 'absolute', left: '-10000px', top: 0, width: '800px' }}>
        <div ref={printRef} className="p-8 bg-white text-black prose prose-sm max-w-none">
          {pdfGroupId && generatedAppendices[pdfGroupId] ? (
            <>
              <h1 className="text-2xl font-bold mb-6 border-b pb-2">
                {planningData?.chapters?.find(g => g.group_id === pdfGroupId)?.chapter_titles?.join(' & ') || pdfGroupId}
              </h1>
              <MarkdownPreview content={generatedAppendices[pdfGroupId]} />
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
