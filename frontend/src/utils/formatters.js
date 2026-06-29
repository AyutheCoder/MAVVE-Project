/**
 * Format currency in Indian Rupee notation.
 * @param {number} amount
 * @returns {string}
 */
export function formatINR(amount) {
  if (amount >= 10_000_000) {
    return `₹${(amount / 10_000_000).toFixed(1)} Cr`
  }
  if (amount >= 100_000) {
    return `₹${(amount / 100_000).toFixed(1)} L`
  }
  return `₹${amount.toLocaleString('en-IN')}`
}

/**
 * Format large numbers with K/M suffix.
 * @param {number} num
 * @returns {string}
 */
export function formatNumber(num) {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`
  return num.toLocaleString()
}

/**
 * Get risk level label from score.
 * @param {number} score 0.0 - 1.0
 * @returns {'low' | 'medium' | 'high'}
 */
export function getRiskLevel(score) {
  if (score < 0.4) return 'low'
  if (score < 0.65) return 'medium'
  return 'high'
}

/**
 * Get language name from ISO 639-1 code.
 * @param {string} code
 * @returns {string}
 */
export function getLanguageName(code) {
  const map = {
    hi: 'Hindi', mr: 'Marathi', bn: 'Bengali', ta: 'Tamil',
    te: 'Telugu', kn: 'Kannada', gu: 'Gujarati', ml: 'Malayalam',
    pa: 'Punjabi', or: 'Odia', en: 'English',
  }
  return map[code] || code
}

/**
 * Format relative time (e.g., "2 min ago").
 * @param {string} isoDate
 * @returns {string}
 */
export function timeAgo(isoDate) {
  const diff = (Date.now() - new Date(isoDate).getTime()) / 1000
  if (diff < 60) return `${Math.floor(diff)}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}
