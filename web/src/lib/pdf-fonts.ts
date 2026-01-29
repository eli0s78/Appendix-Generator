/**
 * PDF Font utilities for Unicode support
 *
 * Uses Noto Sans from Google Fonts for comprehensive Unicode coverage.
 * Font is fetched from CDN and cached in localStorage for subsequent use.
 */

import { jsPDF } from 'jspdf';

// Google Fonts CDN URL for Noto Sans (v42 - latest as of 2025)
const NOTO_SANS_REGULAR_URL = 'https://fonts.gstatic.com/s/notosans/v42/o-0mIpQlx3QUlC5A4PNB6Ryti20_6n1iPHjcz6L1SoM-jCpoiyD9A-9a6Vc.ttf';
const NOTO_SANS_BOLD_URL = 'https://fonts.gstatic.com/s/notosans/v42/o-0mIpQlx3QUlC5A4PNB6Ryti20_6n1iPHjcz6L1SoM-jCpoiyAaBO9a6Vc.ttf';

// Cache keys for localStorage
const CACHE_KEY_REGULAR = 'pdf-font-noto-sans-regular';
const CACHE_KEY_BOLD = 'pdf-font-noto-sans-bold';
const CACHE_VERSION_KEY = 'pdf-font-cache-version';
const CURRENT_CACHE_VERSION = '2'; // Updated v42 fonts

// Track if fonts are registered
let fontsRegistered = false;
let fontLoadPromise: Promise<void> | null = null;

/**
 * Convert ArrayBuffer to base64 string
 */
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Fetch font from URL and return as base64
 */
async function fetchFontAsBase64(url: string): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch font: ${response.status}`);
  }
  const buffer = await response.arrayBuffer();
  return arrayBufferToBase64(buffer);
}

/**
 * Get cached font from localStorage
 */
function getCachedFont(key: string): string | null {
  try {
    // Check cache version
    const version = localStorage.getItem(CACHE_VERSION_KEY);
    if (version !== CURRENT_CACHE_VERSION) {
      // Clear old cache
      localStorage.removeItem(CACHE_KEY_REGULAR);
      localStorage.removeItem(CACHE_KEY_BOLD);
      localStorage.setItem(CACHE_VERSION_KEY, CURRENT_CACHE_VERSION);
      return null;
    }
    return localStorage.getItem(key);
  } catch {
    // localStorage not available or full
    return null;
  }
}

/**
 * Cache font in localStorage
 */
function cacheFont(key: string, base64: string): void {
  try {
    localStorage.setItem(key, base64);
    localStorage.setItem(CACHE_VERSION_KEY, CURRENT_CACHE_VERSION);
  } catch {
    // localStorage not available or full - continue without caching
    console.warn('Could not cache font in localStorage');
  }
}

/**
 * Load and register fonts with jsPDF
 * This function is idempotent - calling multiple times is safe
 */
async function loadFonts(): Promise<void> {
  // Get regular font (required)
  let regularBase64 = getCachedFont(CACHE_KEY_REGULAR);
  if (!regularBase64) {
    regularBase64 = await fetchFontAsBase64(NOTO_SANS_REGULAR_URL);
    cacheFont(CACHE_KEY_REGULAR, regularBase64);
  }

  // Get bold font (optional, fallback to regular if fails)
  let boldBase64 = getCachedFont(CACHE_KEY_BOLD);
  if (!boldBase64) {
    try {
      boldBase64 = await fetchFontAsBase64(NOTO_SANS_BOLD_URL);
      cacheFont(CACHE_KEY_BOLD, boldBase64);
    } catch {
      // Fallback to regular for bold
      boldBase64 = regularBase64;
    }
  }

  // Store fonts for registration
  (globalThis as Record<string, unknown>).__PDF_FONT_REGULAR__ = regularBase64;
  (globalThis as Record<string, unknown>).__PDF_FONT_BOLD__ = boldBase64;

  fontsRegistered = true;
}

/**
 * Ensure fonts are loaded (call this before creating PDFs)
 * Returns silently if fonts fail to load - fallback to standard fonts
 */
export async function ensureFontsLoaded(): Promise<void> {
  if (fontsRegistered) {
    return;
  }

  if (!fontLoadPromise) {
    fontLoadPromise = loadFonts().catch((error) => {
      console.warn('Failed to load PDF fonts, using fallback:', error);
      fontsRegistered = false;
      fontLoadPromise = null;
    });
  }

  await fontLoadPromise;
}

/**
 * Register fonts with a jsPDF instance
 * Must call ensureFontsLoaded() first
 */
export function registerFonts(doc: jsPDF): void {
  if (!fontsRegistered) {
    console.warn('Fonts not loaded. Call ensureFontsLoaded() first.');
    return;
  }

  const regularBase64 = (globalThis as Record<string, unknown>).__PDF_FONT_REGULAR__ as string;
  const boldBase64 = (globalThis as Record<string, unknown>).__PDF_FONT_BOLD__ as string;

  if (regularBase64) {
    doc.addFileToVFS('NotoSans-Regular.ttf', regularBase64);
    doc.addFont('NotoSans-Regular.ttf', 'NotoSans', 'normal');
  }

  if (boldBase64) {
    doc.addFileToVFS('NotoSans-Bold.ttf', boldBase64);
    doc.addFont('NotoSans-Bold.ttf', 'NotoSans', 'bold');
  }
}

/**
 * Check if Unicode fonts are available
 */
export function areFontsLoaded(): boolean {
  return fontsRegistered;
}
