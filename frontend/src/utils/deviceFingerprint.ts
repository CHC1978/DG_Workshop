/**
 * Generate device fingerprint for trusted device功能
 * 使用多種設備屬性和 Web Crypto API SHA-256 hash
 */

export async function generateDeviceFingerprint(): Promise<string> {
  const components = [
    // 基本資訊
    navigator.userAgent,
    navigator.language,
    navigator.languages?.join(',') || '',
    new Date().getTimezoneOffset().toString(),

    // 螢幕資訊
    screen.width + 'x' + screen.height,
    screen.availWidth + 'x' + screen.availHeight,
    screen.colorDepth.toString(),
    screen.pixelDepth.toString(),

    // 硬體資訊
    navigator.hardwareConcurrency?.toString() || '',
    navigator.deviceMemory?.toString() || '',
    navigator.maxTouchPoints?.toString() || '',

    // 平台資訊
    navigator.platform,
    navigator.vendor,

    // 其他屬性
    Intl.DateTimeFormat().resolvedOptions().timeZone,
    navigator.doNotTrack || '',
  ]

  // Canvas fingerprinting (提高唯一性)
  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.textBaseline = 'top'
      ctx.font = '14px Arial'
      ctx.fillStyle = '#f60'
      ctx.fillRect(125, 1, 62, 20)
      ctx.fillStyle = '#069'
      ctx.fillText('Device Fingerprint', 2, 15)
      components.push(canvas.toDataURL())
    }
  } catch (e) {
    // Canvas fingerprinting 失敗，繼續
  }

  const fingerprint = components.join('|')

  // 使用 Web Crypto API 的 SHA-256 hash
  try {
    const encoder = new TextEncoder()
    const data = encoder.encode(fingerprint)
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')
    return hashHex
  } catch (e) {
    // Fallback: 使用簡單 hash (不應該發生，因為 Web Crypto API 廣泛支援)
    console.warn('Web Crypto API not available, using fallback hash')
    let hash = 0
    for (let i = 0; i < fingerprint.length; i++) {
      const char = fingerprint.charCodeAt(i)
      hash = (hash << 5) - hash + char
      hash = hash & hash
    }
    return Math.abs(hash).toString(36)
  }
}

export function getDeviceName(): string {
  const ua = navigator.userAgent
  let browser = 'Unknown Browser'
  let os = 'Unknown OS'

  // Detect browser
  if (ua.includes('Chrome') && !ua.includes('Edg')) browser = 'Chrome'
  else if (ua.includes('Firefox')) browser = 'Firefox'
  else if (ua.includes('Safari') && !ua.includes('Chrome')) browser = 'Safari'
  else if (ua.includes('Edg')) browser = 'Edge'

  // Detect OS
  if (ua.includes('Windows')) os = 'Windows'
  else if (ua.includes('Mac')) os = 'macOS'
  else if (ua.includes('Linux')) os = 'Linux'
  else if (ua.includes('Android')) os = 'Android'
  else if (ua.includes('iOS')) os = 'iOS'

  return `${browser} on ${os}`
}
