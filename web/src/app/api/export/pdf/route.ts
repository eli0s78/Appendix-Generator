import { NextRequest, NextResponse } from 'next/server';
import puppeteer from 'puppeteer-core';
import chromium from '@sparticuz/chromium-min';

// Interface for the request body
interface PdfExportRequest {
  html: string;
  styles?: string; // Optional custom styles to inject
}

// Allow longer execution time (Vercel Pro: 300s, Hobby: 10s - asking for max possible)
export const maxDuration = 60;

export async function POST(req: NextRequest) {
  try {
    const { html, styles }: PdfExportRequest = await req.json();

    if (!html) {
      return NextResponse.json(
        { error: 'HTML content is required' },
        { status: 400 }
      );
    }

    console.log('Starting PDF generation...');
    const isDev = process.env.NODE_ENV === 'development';
    console.log(`Environment: ${process.env.NODE_ENV}, isDev: ${isDev}`);

    let browser;
    try {
      if (isDev) {
        console.log('Launching local Puppeteer...');
        const localPuppeteer = await import('puppeteer');
        browser = await localPuppeteer.launch({
          headless: true,
          args: ['--no-sandbox', '--disable-setuid-sandbox'],
        });
      } else {
        console.log('Launching Serverless Chromium (Remote)...');

        // Remote URL for the chromium binary (matching the package version 131.0.1)
        const chromiumPack = "https://github.com/Sparticuz/chromium/releases/download/v131.0.1/chromium-v131.0.1-pack.tar";

        browser = await puppeteer.launch({
          args: chromium.args,
          defaultViewport: { width: 1920, height: 1080 },
          executablePath: await chromium.executablePath(chromiumPack),
          headless: true,
        });
      }
    } catch (launchError: any) {
      console.error('Browser Launch Failed:', launchError);
      return NextResponse.json(
        {
          error: 'Failed to launch browser',
          details: launchError.message,
          stack: launchError.stack
        },
        { status: 500 }
      );
    }

    const page = await browser.newPage();

    // Set content with a shell that includes Tailwind/Globals
    const fullHtml = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appendix Export</title>
        <style>
          ${styles || ''}
        </style>
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
          /* (Styles truncated for brevity in logs, but kept in actual code) */
          table { width: 100% !important; border-collapse: collapse !important; border: 1px solid #d1d5db !important; margin-bottom: 1rem !important; font-size: 9pt !important; }
          thead { display: table-header-group !important; background-color: #4A4A8A !important; border-bottom: 2px solid #4A4A8A !important; color: white !important; }
          tfoot { display: table-footer-group !important; }
          tr { break-inside: avoid !important; page-break-inside: avoid !important; border-bottom: 1px solid #e5e7eb !important; }
          tbody tr:nth-child(even) { background-color: #f9fafb !important; }
          th, td { border: 1px solid #d1d5db !important; padding: 0.5rem 0.75rem !important; text-align: left !important; }
          th { font-weight: 700 !important; color: #FFFFFF !important; background-color: #4A4A8A !important; }
          h1, h2, h3, h4, h5, h6 { break-after: avoid; page-break-after: avoid; }
          ul, ol, p { orphans: 3; widows: 3; }
          li { break-inside: avoid; }
        </style>
      </head>
      <body>
        <div class="print-content">
          ${html}
        </div>
      </body>
      </html>
    `;

    console.log('Setting page content...');
    await page.setContent(fullHtml, {
      waitUntil: 'networkidle0',
      timeout: 30000,
    });

    console.log('Waiting for fonts...');
    await page.evaluateHandle('document.fonts.ready');

    console.log('Generating PDF buffer...');
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

    console.log('Closing browser...');
    await browser.close();

    console.log('PDF Generated successfully.');
    return new NextResponse(pdfBuffer as any, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=appendix.pdf',
      },
    });

  } catch (error: any) {
    console.error('PDF Generation Error:', error);
    return NextResponse.json(
      {
        error: 'Critical PDF Generation Failure',
        details: error.message,
        stack: error.stack
      },
      { status: 500 }
    );
  }
}
