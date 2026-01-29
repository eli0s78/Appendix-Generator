import { NextRequest, NextResponse } from 'next/server';
import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';


// Interface for the request body
interface PdfExportRequest {
  html?: string;
  styles?: string; // Optional custom styles to inject
  warmup?: boolean;
}

// Allow longer execution time (Vercel Pro: 300s, Hobby: 10s - asking for max possible)
export const maxDuration = 60;

export async function POST(req: NextRequest) {
  let browser: any;
  try {
    const { html, styles, warmup }: PdfExportRequest = await req.json();
    const isDev = process.env.NODE_ENV === 'development';

    // Warmup handling: Unpack Chromium without generating PDF
    if (warmup) {
      console.log('Warming up PDF generator environment...');
      if (process.env.NODE_ENV !== 'development') {
        process.env.AWS_LAMBDA_JS_RUNTIME = "nodejs20.x";
        const chromium = (await import('@sparticuz/chromium-min')).default;
        const chromiumPack = "https://github.com/Sparticuz/chromium/releases/download/v131.0.1/chromium-v131.0.1-pack.tar";
        await chromium.executablePath(chromiumPack);
        console.log('Chromium binary unpacked and ready.');
      }
      return NextResponse.json({ status: 'warmed' });
    }

    if (!html) {
      return NextResponse.json(
        { error: 'HTML content is required' },
        { status: 400 }
      );
    }

    console.log('Starting PDF generation...');
    console.log('Starting PDF generation...');
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

        // Explicitly set the runtime environment variable for Vercel/AWS Lambda
        process.env.AWS_LAMBDA_JS_RUNTIME = "nodejs20.x";

        // Dynamically import chromium for serverless context
        const chromium = (await import('@sparticuz/chromium-min')).default;

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

    // Read KaTeX CSS
    const katexCssPath = path.join(process.cwd(), 'node_modules', 'katex', 'dist', 'katex.min.css');
    let katexCss = '';
    try {
      katexCss = fs.readFileSync(katexCssPath, 'utf-8');
    } catch (err) {
      console.warn('Could not read KaTeX CSS:', err);
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
          @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&family=Noto+Color+Emoji&family=Noto+Sans+Math&family=Noto+Sans+Symbols&display=swap');
          /* Inject KaTeX CSS */
          ${katexCss}
          
          @page {
            size: A4;
            margin: 20mm;
          }
          body {
            font-family: 'Noto Sans', 'Noto Color Emoji', 'Open Sans', ui-sans-serif, system-ui, sans-serif;
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
    // @ts-ignore
    await page.evaluate(async () => {
      await document.fonts.ready;
    });
    // Fonts are handled by networkidle0 above

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
  } finally {
    if (browser) {
      console.log('Closing browser...');
      await browser.close();
    }
  }
}
