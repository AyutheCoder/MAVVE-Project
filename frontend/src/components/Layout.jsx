import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ShoppingCart, 
  Bot, 
  MessageSquare, 
  Settings,
  Bell,
  Search,
  CheckCircle,
  AlertCircle,
  Menu,
  X
} from 'lucide-react';
import confetti from 'canvas-confetti';
import './Layout.css';

export default function Layout({ children, setIsAuthenticated }) {
  const navigate = useNavigate();
  const [demoMode, setDemoMode] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [notifications, setNotifications] = useState([
    { id: 1, msg: 'Address Updated via Agent', type: 'info', time: '15 mins ago' },
    { id: 2, msg: 'Daily Summary Report', type: 'info', time: '1 hour ago' }
  ]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Toast Manager
  const addToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    
    // Also push to persistent notifications dropdown (keep last 10)
    setNotifications(prev => [{ id, msg: message, type, time: 'Just now' }, ...prev].slice(0, 10));

    setTimeout(() => removeToast(id), 5000);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, fading: true } : t));
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 300);
  };

  const handleLogout = () => {
    setShowProfile(false);
    setDemoMode(false);
    localStorage.removeItem('mavveAuth');
    if (setIsAuthenticated) setIsAuthenticated(false);
    navigate('/login');
  };

  // Demo Mode Effect
  useEffect(() => {
    let interval;
    if (demoMode) {
      addToast('Demo Mode Activated! Simulating live orders...', 'success');
      
      interval = setInterval(() => {
        const events = [
          { msg: 'New high-risk order intercepted (ORD-4192)', type: 'warning' },
          { msg: 'Address Agent successfully verified landmark for ORD-3810', type: 'success', confetti: true },
          { msg: 'Intent Agent escalated ORD-2911 (User Hostile)', type: 'error' },
          { msg: 'Prepaid Agent converted COD -> UPI for ORD-9912. Saved ₹420!', type: 'success', confetti: true }
        ];
        
        const evt = events[Math.floor(Math.random() * events.length)];
        addToast(evt.msg, evt.type);
        
        if (evt.confetti) {
          triggerConfetti();
        }
      }, 8000);
    } else {
      if(toasts.length > 0 && toasts[toasts.length-1].message.includes('Activated')) {
        addToast('Demo Mode Deactivated.', 'info');
      }
    }
    return () => clearInterval(interval);
  }, [demoMode]);

  const triggerConfetti = () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#3b82f6', '#10b981', '#ffffff']
    });
  };

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [navigate]);

  return (
    <div className="layout-container">
      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div className="mobile-overlay" onClick={() => setMobileMenuOpen(false)}></div>
      )}

      {/* Sidebar Navigation */}
      <nav className={`sidebar glass-panel ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-header">
          <Bot className="logo-icon" size={28} />
          <h2 className="logo-text">MAVVE</h2>
          <button className="btn-icon mobile-close-btn" onClick={() => setMobileMenuOpen(false)}>
            <X size={20} />
          </button>
        </div>
        
        <div className="nav-links">
          <NavLink to="/dashboard" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </NavLink>
          
          <NavLink to="/orders" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
            <ShoppingCart size={20} />
            <span>Orders</span>
          </NavLink>
          
          <NavLink to="/agents" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
            <Bot size={20} />
            <span>Agents Analytics</span>
          </NavLink>
          
          <NavLink to="/conversations" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
            <MessageSquare size={20} />
            <span>Conversations</span>
          </NavLink>
          
          <NavLink to="/settings" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
            <Settings size={20} />
            <span>Settings</span>
          </NavLink>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Top Header */}
        <header className="top-header glass-card">
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <button className="btn-icon mobile-menu-btn" onClick={() => setMobileMenuOpen(true)}>
              <Menu size={20} />
            </button>
            <div className="search-bar" style={{ position: 'relative' }}>
              <Search className="search-icon" size={18} style={{ opacity: isSearching ? 0.5 : 1 }} />
              <input 
                type="text" 
                placeholder="Search orders..." 

              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchQuery.trim()) {
                  setIsSearching(true);
                  setTimeout(() => {
                    setIsSearching(false);
                    addToast(`No results found for "${searchQuery}" in current environment.`, 'warning');
                  }, 1200);
                }
              }}
              disabled={isSearching}
            />
            {isSearching && (
              <div style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)' }}>
                <div className="pulsing-dot"></div>
              </div>
            )}
          </div>
          </div>
          
          <div className="header-actions">
            {/* Demo Mode Toggle */}
            <div className="demo-toggle-wrap" style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginRight: '1rem', background: 'rgba(255,255,255,0.05)', padding: '0.25rem 0.75rem', borderRadius: '99px'}}>
              <span style={{fontSize: '0.75rem', fontWeight: 600, color: demoMode ? 'var(--accent-success)' : 'var(--text-secondary)'}}>
                {demoMode ? 'LIVE DEMO' : 'DEMO MODE'}
              </span>
              <label className="toggle-switch" style={{margin: 0, transform: 'scale(0.8)'}}>
                <input type="checkbox" checked={demoMode} onChange={(e) => setDemoMode(e.target.checked)} />
                <span className="slider"></span>
              </label>
            </div>

            <div style={{position: 'relative'}}>
              <button className="btn-icon" onClick={() => { setShowNotifs(!showNotifs); setShowProfile(false); }} style={{position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none', cursor: 'pointer'}}>
                <Bell size={20} />
                {notifications.length > 0 && <span className="badge-dot"></span>}
              </button>
              {showNotifs && (
                <div className="dropdown-menu" style={{width: '320px', padding: '0'}}>
                  <div style={{padding: '1rem', borderBottom: '1px solid var(--border-light)', fontWeight: '600', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <span>Notifications ({notifications.length})</span>
                    {notifications.length > 0 && (
                      <span 
                        style={{fontSize: '0.75rem', color: 'var(--accent-primary)', cursor: 'pointer'}}
                        onClick={(e) => { e.stopPropagation(); setNotifications([]); }}
                      >
                        Clear All
                      </span>
                    )}
                  </div>
                  <div style={{maxHeight: '300px', overflowY: 'auto'}}>
                    {notifications.length === 0 ? (
                      <div style={{padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-muted)'}}>No new notifications</div>
                    ) : (
                      notifications.map((notif, index) => (
                        <div key={notif.id} style={{padding: '0.75rem 1rem', borderBottom: index < notifications.length - 1 ? '1px solid var(--border-light)' : 'none', background: notif.time === 'Just now' ? 'rgba(255,255,255,0.05)' : 'transparent', transition: 'background 0.3s'}}>
                          <div style={{fontSize: '0.85rem', fontWeight: '500', color: 'var(--text-primary)'}}>{notif.msg}</div>
                          <div style={{fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem'}}>{notif.time}</div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            <div style={{position: 'relative'}}>
              <div 
                className="user-profile" 
                onClick={() => { setShowProfile(!showProfile); setShowNotifs(false); }} 
                style={{cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.25rem 0.75rem 0.25rem 0.25rem', borderRadius: '99px'}}
              >
                <div className="avatar" style={{width: '32px', height: '32px', fontSize: '0.875rem'}}>AD</div>
                <span style={{fontSize: '0.875rem', fontWeight: '500'}}>Admin</span>
              </div>
              {showProfile && (
                <div className="dropdown-menu profile-menu" style={{minWidth: '220px', padding: 0}}>
                  <div 
                    onClick={() => { setShowProfile(false); navigate('/profile'); }}
                    style={{padding: '1rem', borderBottom: '1px solid var(--border-light)', background: 'rgba(0,0,0,0.2)', cursor: 'pointer', transition: 'background 0.2s'}}
                    onMouseOver={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                    onMouseOut={e => e.currentTarget.style.background = 'rgba(0,0,0,0.2)'}
                  >
                    <div style={{fontWeight: '600', fontSize: '0.95rem'}}>System Admin</div>
                    <div style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>admin@mavve.ai</div>
                  </div>
                  <div style={{padding: '0.5rem 0'}}>
                    <button className="dropdown-item text-danger" onClick={handleLogout}>Logout</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="page-container">
          {children}
        </div>
      </main>

      {/* Global Toasts */}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type} ${t.fading ? 'fade-out' : ''}`}>
            {t.type === 'success' ? <CheckCircle size={18} color="var(--accent-success)"/> : 
             t.type === 'warning' ? <AlertCircle size={18} color="var(--accent-warning)"/> :
             t.type === 'error' ? <AlertCircle size={18} color="var(--accent-danger)"/> :
             <Bot size={18} color="var(--accent-primary)"/>}
            {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}
