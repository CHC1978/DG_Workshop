/**
 * HTML Sanitizer Utility
 *
 * Provides XSS protection for any user-generated HTML content.
 * Uses DOMPurify for safe HTML rendering.
 *
 * Usage:
 *   import { sanitizeHtml, sanitizeUrl } from '@/utils/sanitizer'
 *
 *   const safeHtml = sanitizeHtml(userInput)
 *   const safeUrl = sanitizeUrl(userProvidedUrl)
 */

import DOMPurify, { type Config } from 'dompurify'

/**
 * Default DOMPurify configuration
 * Restrictive by default - only allow safe elements
 */
const DEFAULT_CONFIG: Config = {
  // Allow only basic formatting tags
  ALLOWED_TAGS: [
    'p', 'br', 'b', 'i', 'u', 'strong', 'em',
    'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre',
    'a', 'span', 'div'
  ],
  // Allow only safe attributes
  ALLOWED_ATTR: [
    'href', 'title', 'class', 'id',
    'target', 'rel'
  ],
  // Force all links to open in new tab with noopener
  ADD_ATTR: ['target', 'rel'],
  // Disallow data: and javascript: URLs
  ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel):|[^a-z]|[a-z+.-]+(?:[^a-z+.\-:]|$))/i,
  // Remove dangerous elements completely
  FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input'],
  FORBID_ATTR: ['onerror', 'onclick', 'onload', 'onmouseover', 'onfocus', 'onblur'],
}

/**
 * Minimal configuration for plain text only
 */
const PLAIN_TEXT_CONFIG: Config = {
  ALLOWED_TAGS: [],
  ALLOWED_ATTR: [],
}

/**
 * Sanitize HTML content for safe rendering
 *
 * @param dirty - Potentially unsafe HTML string
 * @param config - Optional DOMPurify configuration override
 * @returns Sanitized HTML string
 */
export function sanitizeHtml(
  dirty: string | null | undefined,
  config: Config = DEFAULT_CONFIG
): string {
  if (!dirty) return ''

  // Sanitize and return (RETURN_TRUSTED_TYPE: false ensures string return)
  return DOMPurify.sanitize(dirty, { ...config, RETURN_TRUSTED_TYPE: false }) as string
}

/**
 * Strip all HTML tags and return plain text
 *
 * @param dirty - Potentially unsafe HTML string
 * @returns Plain text with all HTML removed
 */
export function stripHtml(dirty: string | null | undefined): string {
  if (!dirty) return ''

  return DOMPurify.sanitize(dirty, { ...PLAIN_TEXT_CONFIG, RETURN_TRUSTED_TYPE: false }) as string
}

/**
 * Sanitize a URL to prevent javascript: and data: attacks
 *
 * @param url - Potentially unsafe URL
 * @returns Sanitized URL or empty string if unsafe
 */
export function sanitizeUrl(url: string | null | undefined): string {
  if (!url) return ''

  const trimmed = url.trim().toLowerCase()

  // Block dangerous protocols
  const dangerousProtocols = [
    'javascript:',
    'data:',
    'vbscript:',
    'file:',
  ]

  for (const protocol of dangerousProtocols) {
    if (trimmed.startsWith(protocol)) {
      console.warn('[Security] Blocked dangerous URL:', url)
      return ''
    }
  }

  // Allow relative URLs and safe protocols
  const safeProtocols = ['http:', 'https:', 'mailto:', 'tel:']
  const hasProtocol = /^[a-z][a-z0-9+.-]*:/i.test(url)

  if (hasProtocol) {
    const isSafe = safeProtocols.some(p => trimmed.startsWith(p))
    if (!isSafe) {
      console.warn('[Security] Blocked unknown protocol URL:', url)
      return ''
    }
  }

  return url
}

/**
 * Escape HTML special characters for safe text display
 * Use this when you need to display user input as text (not HTML)
 *
 * @param text - Text to escape
 * @returns Escaped text safe for HTML display
 */
export function escapeHtml(text: string | null | undefined): string {
  if (!text) return ''

  const escapeMap: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  }

  return text.replace(/[&<>"'/]/g, char => escapeMap[char] || char)
}

/**
 * Validate and sanitize file name
 * Removes path traversal attempts and dangerous characters
 *
 * @param filename - User-provided filename
 * @returns Sanitized filename
 */
export function sanitizeFilename(filename: string | null | undefined): string {
  if (!filename) return ''

  // Remove path separators and null bytes
  let safe = filename
    .replace(/\\/g, '')
    .replace(/\//g, '')
    .replace(/\0/g, '')

  // Remove leading dots (hidden files)
  safe = safe.replace(/^\.+/, '')

  // Remove dangerous extensions by double-checking
  const dangerousExtensions = ['.exe', '.bat', '.cmd', '.sh', '.ps1', '.php', '.jsp']
  const lowerSafe = safe.toLowerCase()

  for (const ext of dangerousExtensions) {
    if (lowerSafe.endsWith(ext)) {
      console.warn('[Security] Blocked dangerous file extension:', filename)
      safe = safe.slice(0, -ext.length) + '.blocked'
    }
  }

  // Limit length
  if (safe.length > 255) {
    safe = safe.slice(0, 255)
  }

  return safe || 'unnamed'
}

/**
 * Create a safe HTML element from user content
 * Use this in Vue templates with v-html when absolutely necessary
 *
 * @param content - User content to render
 * @returns Sanitized HTML ready for v-html
 */
export function createSafeHtml(content: string | null | undefined): string {
  return sanitizeHtml(content)
}

// Export DOMPurify for advanced usage
export { DOMPurify }
