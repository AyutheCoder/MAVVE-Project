import { useLocation } from 'react-router-dom'
import { Search, Bell, Activity } from 'lucide-react'

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/orders': 'Order Management',
  '/agents': 'Agent Performance',
  '/conversations': 'Conversations',
  '/settings': 'Settings',
}

function Header({ collapsed }) {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'MAVVE'

  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        left: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
        right: 0,
        height: 'var(--header-height)',
        background: 'rgba(10, 15, 30, 0.85)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        zIndex: 90,
        transition: 'left var(--transition-base)',
      }}
    >
      {/* Page Title */}
      <h1
        style={{
          fontSize: '1.25rem',
          fontWeight: 700,
          letterSpacing: '-0.02em',
        }}
      >
        {title}
      </h1>

      {/* Right Section */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Search */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            background: 'var(--bg-glass)',
            color: 'var(--text-tertiary)',
            fontSize: '0.85rem',
            minWidth: 200,
          }}
        >
          <Search size={16} />
          <span>Search orders...</span>
          <span
            style={{
              marginLeft: 'auto',
              fontSize: '0.7rem',
              padding: '2px 6px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-muted)',
            }}
          >
            ⌘K
          </span>
        </div>

        {/* System Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            borderRadius: 'var(--radius-full)',
            background: 'var(--color-success-bg)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
          }}
        >
          <Activity size={14} color="var(--color-success)" />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-success)' }}>
            System Online
          </span>
        </div>

        {/* Notifications */}
        <button
          id="notifications-bell"
          style={{
            position: 'relative',
            padding: 8,
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            background: 'transparent',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            transition: 'all var(--transition-fast)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--bg-glass-hover)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
          }}
        >
          <Bell size={18} />
          <span
            style={{
              position: 'absolute',
              top: 4,
              right: 4,
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: 'var(--color-danger)',
              border: '2px solid var(--bg-primary)',
            }}
          />
        </button>

        {/* User Avatar */}
        <div
          id="user-avatar"
          style={{
            width: 36,
            height: 36,
            borderRadius: 'var(--radius-full)',
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.85rem',
            fontWeight: 700,
            color: 'white',
            cursor: 'pointer',
          }}
        >
          M
        </div>
      </div>
    </header>
  )
}

export default Header
