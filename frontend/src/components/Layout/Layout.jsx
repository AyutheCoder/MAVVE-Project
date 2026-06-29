import { useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

function Layout({ children }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className="app-layout">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <div className={`main-content ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Header collapsed={sidebarCollapsed} />
        <main className="page-container page-enter">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout
