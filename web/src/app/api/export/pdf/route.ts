import { NextRequest, NextResponse } from 'next/server';
import puppeteer from 'puppeteer-core';
import chromium from '@sparticuz/chromium';

// Interface for the request body
interface PdfExportRequest {
  html: string;
  styles?: string; // Optional custom styles to inject
}

export async function POST(req: NextRequest) {
  try {
    const { html, styles }: PdfExportRequest = await req.json();

    if (!html) {
      return NextResponse.json(
        { error: 'HTML content is required' },
        { status: 400 }
      );
    }

    let browser;
    if (process.env.NODE_ENV === 'development') {
      const localPuppeteer = await import('puppeteer');
      browser = await localPuppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'], // Standard args for stability
      });
    } else {
      browser = await puppeteer.launch({
        args: chromium.args,
        defaultViewport: { width: 1920, height: 1080 },
        executablePath: await chromium.executablePath(),
        headless: true,
      });
    }

    const page = await browser.newPage();

    // Set content with a shell that includes Tailwind/Globals
    // We assume the passed HTML is just the body content or a fragment.
    // We'll wrap it in a proper HTML structure.
    const fullHtml = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appendix Export</title>
        <!-- Inject styles passed from frontend (which should include the tailwind collected CSS) -->
        <style>
          ${styles || ''}
        </style>
        <!-- Add base print styles to ensure defaults if not passed -->
        <style>
          @page {
            size: A4;
            margin: 20mm;
          }
          body {
            font-family: ui-sans-serif, system-ui, sans-serif;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
          /* Table fidelity - High Specificity Configuration */
          table {
            width: 100% !important;
            border-collapse: collapse !important;
            page-break-inside: auto;
            border: 1px solid #d1d5db !important; /* gray-300 */
            margin-bottom: 1rem !important;
            font-size: 9pt !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          
          thead {
            display: table-header-group !important;
            background-color: #4A4A8A !important; /* Primary Color */
            border-bottom: 2px solid #4A4A8A !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          
          tfoot {
            display: table-footer-group !important;
          }

          tr {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
            border-bottom: 1px solid #e5e7eb !important; /* gray-200 */
          }

          /* Zebra striping for readability */
          tbody tr:nth-child(even) {
            background-color: #f9fafb !important; /* gray-50 */
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          
          th, td {
            border: 1px solid #d1d5db !important; /* gray-300 */
            padding: 0.5rem 0.75rem !important;
            text-align: left !important;
          }

          th {
            font-weight: 700 !important;
            color: #FFFFFF !important; /* White text */
            background-color: #4A4A8A !important; /* Ensure header bg */
          }

          /* Typography flow control */
          h1, h2, h3, h4, h5, h6 {
            break-after: avoid;
            page-break-after: avoid;
          }
          ul, ol, p {
            orphans: 3; 
            widows: 3;
          }
          li {
            break-inside: avoid;
          }
        </style>
      </head>
      <body>
        <div class="print-content">
          ${html}
        </div>
      </body>
      </html>
    `;

    // Set content and wait for network idle to ensure images/fonts load
    await page.setContent(fullHtml, {
      waitUntil: 'networkidle0',
      timeout: 30000,
    });

    // Wait for fonts to be ready
    await page.evaluateHandle('document.fonts.ready');

    // Generate PDF
    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20mm',
        right: '20mm',
        bottom: '20mm',
        left: '20mm',
      },
      displayHeaderFooter: false,
    });

    await browser.close();

    // Return the PDF
    return new NextResponse(pdfBuffer as any, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=appendix.pdf',
      },
    });

  } catch (error) {
    console.error('PDF Generation Error:', error);
    return NextResponse.json(
      { error: 'Failed to generate PDF' },
      { status: 500 }
    );
  }
}
