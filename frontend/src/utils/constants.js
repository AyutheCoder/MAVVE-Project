/**
 * Application-wide constants for the MAVVE frontend.
 */

export const ORDER_STATUSES = [
  { value: 'PLACED', label: 'Placed', color: 'var(--text-secondary)' },
  { value: 'INTERCEPTED', label: 'Intercepted', color: 'var(--color-warning)' },
  { value: 'VALIDATED', label: 'Validated', color: 'var(--color-info)' },
  { value: 'DISPATCHED', label: 'Dispatched', color: 'var(--color-success)' },
  { value: 'DELIVERED', label: 'Delivered', color: 'var(--color-success)' },
  { value: 'RTO', label: 'RTO', color: 'var(--color-danger)' },
  { value: 'CANCELLED', label: 'Cancelled', color: 'var(--text-tertiary)' },
]

export const PAYMENT_MODES = [
  { value: 'COD', label: 'Cash on Delivery', color: 'var(--color-warning)' },
  { value: 'PREPAID', label: 'Prepaid', color: 'var(--color-success)' },
  { value: 'PREPAID_PENDING', label: 'Prepaid Pending', color: 'var(--color-info)' },
]

export const AGENT_TYPES = [
  { value: 'address_resolution', label: 'Address Agent', emoji: '🏠' },
  { value: 'intent_verification', label: 'Intent Agent', emoji: '🧠' },
  { value: 'prepaid_conversion', label: 'Prepaid Agent', emoji: '💳' },
]

export const SUPPORTED_LANGUAGES = [
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'mr', name: 'Marathi', flag: '🇮🇳' },
  { code: 'bn', name: 'Bengali', flag: '🇮🇳' },
  { code: 'ta', name: 'Tamil', flag: '🇮🇳' },
  { code: 'te', name: 'Telugu', flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada', flag: '🇮🇳' },
  { code: 'gu', name: 'Gujarati', flag: '🇮🇳' },
]
