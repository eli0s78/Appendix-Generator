'use client';

import { useState, useRef } from 'react';
import { useAppState } from '@/hooks/useAppState';
import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  FilePlus,
  Save,
  FolderOpen,
  HelpCircle,
  Info,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

type PendingAction = 'new' | 'load' | null;

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const {
    hasProjectData,
    hasUnsavedChanges,
    resetAll,
    getProjectData,
    loadProjectData,
    markAsSaved,
    planningData,
    detectedTier,
    apiKeyValid,
  } = useAppState();

  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle New Project
  const handleNewProject = () => {
    if (hasUnsavedChanges()) {
      setPendingAction('new');
      setShowConfirmDialog(true);
    } else if (hasProjectData()) {
      setPendingAction('new');
      setShowConfirmDialog(true);
    } else {
      resetAll();
    }
  };

  // Handle Save Project
  const handleSaveProject = () => {
    const data = getProjectData();
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const bookTitle = planningData?.book_overview?.title || 'project';
    const safeName = bookTitle.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50);
    const filename = `appendix_${safeName}_${new Date().toISOString().split('T')[0]}.json`;

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);

    markAsSaved();
  };

  // Handle Load Project click
  const handleLoadClick = () => {
    if (hasUnsavedChanges()) {
      setPendingAction('load');
      setShowConfirmDialog(true);
    } else {
      fileInputRef.current?.click();
    }
  };

  // Handle file selection
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    e.target.value = '';

    if (hasUnsavedChanges() && pendingAction !== 'load') {
      setPendingFile(file);
      setPendingAction('load');
      setShowConfirmDialog(true);
      return;
    }

    await loadFile(file);
  };

  // Load the file
  const loadFile = async (file: File) => {
    try {
      let data;

      // Check for legacy .appendix-session file (Gzip compressed JSON)
      if (file.name.endsWith('.appendix-session')) {
        try {
          const stream = file.stream().pipeThrough(new DecompressionStream('gzip'));
          const response = await new Response(stream).json();
          const legacyData = response as any;

          // Map legacy data to new schema
          data = {
            version: '1.0',
            savedAt: legacyData.saved_at || new Date().toISOString(),
            // Decode API key from base64 if present
            apiKey: legacyData.api_key_encoded ? atob(legacyData.api_key_encoded) : null,
            fileName: null,
            bookContent: legacyData.book_content,
            // Map legacy extraction info keys
            extractionInfo: legacyData.extraction_info ? {
              pages: legacyData.extraction_info.pages || 0,
              estimatedWords: Math.round((legacyData.extraction_info.final_chars || 0) / 5),
              estimatedChars: legacyData.extraction_info.final_chars || 0,
              bibliographyRemoved: false, // Default
              indexRemoved: false, // Default
              wasTruncated: false, // Default
              keptPercentage: 100
            } : null,
            planningData: legacyData.planning_data,
            generatedAppendices: legacyData.generated_appendices || {},
            forecastYears: 15, // Default
            wordCountOption: '2500-3500', // Default
            currentStep: legacyData.generated_appendices && Object.keys(legacyData.generated_appendices).length > 0 ? 4 : (legacyData.planning_data ? 3 : 2)
          };

          console.log("Legacy session imported successfully", data);
        } catch (err) {
          console.error("Failed to decompress legacy session:", err);
          alert('Failed to load legacy session. The file might be corrupted.');
          return;
        }
      } else {
        // Standard JSON load
        const text = await file.text();
        data = JSON.parse(text);
      }

      // Only require version field - other fields can be null/empty
      if (!data.version) {
        alert('Invalid project file format: missing version');
        return;
      }

      loadProjectData(data);
    } catch (e) {
      console.error(e);
      alert('Failed to load project file. Please check the file format.');
    }
  };

  // Handle confirm dialog actions
  const handleConfirmSaveAndProceed = () => {
    handleSaveProject();
    proceedWithAction();
  };

  const handleConfirmDiscard = () => {
    proceedWithAction();
  };

  const handleConfirmCancel = () => {
    setShowConfirmDialog(false);
    setPendingAction(null);
    setPendingFile(null);
  };

  const proceedWithAction = () => {
    setShowConfirmDialog(false);

    if (pendingAction === 'new') {
      resetAll();
    } else if (pendingAction === 'load') {
      if (pendingFile) {
        loadFile(pendingFile);
        setPendingFile(null);
      } else {
        fileInputRef.current?.click();
      }
    }

    setPendingAction(null);
  };

  return (
    <>
      {/* Sidebar Panel - Fixed position, no overlay */}
      <aside
        className={`fixed top-0 left-0 h-full bg-gray-50 border-r shadow-sm z-30 transition-all duration-200 flex flex-col ${isOpen ? 'w-64' : 'w-0'
          }`}
        style={{ overflow: 'hidden' }}
      >
        <div className="flex flex-col h-full w-64">
          {/* Header */}
          <div className="flex items-center p-4 border-b bg-white">
            <span className="font-semibold text-gray-700">File</span>
          </div>

          {/* File Actions */}
          <div className="p-3 space-y-1">
            <Button
              variant="ghost"
              className="w-full justify-start h-9 px-3"
              onClick={handleNewProject}
            >
              <FilePlus className="w-4 h-4 mr-2" />
              New Project
            </Button>

            <Button
              variant="ghost"
              className="w-full justify-start h-9 px-3"
              onClick={handleSaveProject}
              disabled={!hasProjectData()}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Project
            </Button>

            <Button
              variant="ghost"
              className="w-full justify-start h-9 px-3"
              onClick={handleLoadClick}
            >
              <FolderOpen className="w-4 h-4 mr-2" />
              Load Project
            </Button>

            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.appendix-session"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          <div className="border-t mx-3" />

          {/* Help & About */}
          <div className="p-3 flex-1 overflow-y-auto">
            <Accordion type="single" collapsible className="space-y-1">
              <AccordionItem value="help" className="border-none">
                <AccordionTrigger className="text-sm py-2 px-3 hover:bg-gray-100 rounded hover:no-underline">
                  <span className="flex items-center gap-2">
                    <HelpCircle className="w-4 h-4" />
                    Quick Help
                  </span>
                </AccordionTrigger>
                <AccordionContent className="px-3 pb-2">
                  <div className="text-xs text-muted-foreground space-y-2">
                    <p className="font-medium">Workflow:</p>
                    <ol className="list-decimal list-inside space-y-1 ml-1">
                      <li>
                        <strong>API Setup</strong> - Get key from{' '}
                        <a
                          href="https://aistudio.google.com/apikey"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline inline-flex items-center gap-0.5"
                        >
                          Google AI Studio
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </li>
                      <li>
                        <strong>Upload Book</strong> - PDF extraction
                      </li>
                      <li>
                        <strong>Analyze</strong> - AI planning table
                      </li>
                      <li>
                        <strong>Generate</strong> - Create appendices
                      </li>
                    </ol>
                  </div>
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="about" className="border-none">
                <AccordionTrigger className="text-sm py-2 px-3 hover:bg-gray-100 rounded hover:no-underline">
                  <span className="flex items-center gap-2">
                    <Info className="w-4 h-4" />
                    About
                  </span>
                </AccordionTrigger>
                <AccordionContent className="px-3 pb-2">
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p className="font-medium">Appendix Generator v2.0</p>
                    <hr className="my-2" />
                    <p><strong>Creator:</strong> Elias Pierrakos</p>
                    <p><strong>Organization:</strong> eLearning EKPA</p>
                    <p><strong>Supervisor:</strong> Panagiotis Petrakis</p>
                    <hr className="my-2" />
                    <p className="italic text-[10px]">Made with Google Antigravity</p>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>

          {/* Model Info */}
          {apiKeyValid && (
            <div className="p-3 border-t text-xs text-muted-foreground bg-white">
              Tier: {detectedTier === 'paid' ? 'Paid' : 'Free'}
            </div>
          )}
        </div>
      </aside>

      {/* Toggle Button - Always visible */}
      <button
        onClick={onToggle}
        className={`fixed top-4 z-40 p-2 bg-white rounded-r-lg shadow-md border border-l-0 hover:bg-gray-50 transition-all duration-200 ${isOpen ? 'left-64' : 'left-0 rounded-lg border-l'
          }`}
        aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        {isOpen ? (
          <ChevronLeft className="w-4 h-4" />
        ) : (
          <ChevronRight className="w-4 h-4" />
        )}
      </button>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {hasUnsavedChanges() ? 'Unsaved Changes' : 'Confirm Action'}
            </DialogTitle>
            <DialogDescription>
              {hasUnsavedChanges()
                ? `You have unsaved changes. Do you want to save before you ${pendingAction === 'new' ? 'create a new project' : 'load another project'
                }?`
                : `Are you sure you want to ${pendingAction === 'new' ? 'create a new project' : 'load another project'
                }? Your current project will be closed.`}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex gap-2 sm:gap-0">
            {hasUnsavedChanges() ? (
              <>
                <Button variant="outline" onClick={handleConfirmCancel}>
                  Cancel
                </Button>
                <Button variant="destructive" onClick={handleConfirmDiscard}>
                  Discard Changes
                </Button>
                <Button onClick={handleConfirmSaveAndProceed}>
                  Save & Continue
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" onClick={handleConfirmCancel}>
                  Cancel
                </Button>
                <Button onClick={handleConfirmDiscard}>
                  Continue
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
