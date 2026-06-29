import React, { useState, useEffect } from 'react';
import { User, Mail, Shield, Calendar, Activity, Edit3, Save, Palette } from 'lucide-react';
import './Profile.css';

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('mavveTheme') || 'default');
  const [profile, setProfile] = useState({
    name: 'Admin',
    email: 'admin@mavve.ai',
    role: 'System Administrator',
    department: 'Operations',
    joinDate: 'Jan 15, 2026',
    timezone: 'Asia/Kolkata (IST)',
    phone: '+91 98765 43210'
  });

  useEffect(() => {
    if (theme === 'meesho') {
      document.documentElement.setAttribute('data-theme', 'meesho');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('mavveTheme', theme);
  }, [theme]);

  const handleSave = () => {
    setIsEditing(false);
    // In a real app, this would be an API call
  };

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1>Admin Profile</h1>
        <p>View and manage your account details</p>
      </div>

      <div className="profile-grid">
        {/* Left Column: Avatar & Summary */}
        <div className="profile-sidebar glass-card">
          <div className="profile-avatar-large">
            <span>{profile.name.substring(0, 2).toUpperCase()}</span>
          </div>
          <h2 className="profile-name">{profile.name}</h2>
          <div className="profile-badge">{profile.role}</div>
          
          <div className="profile-stats">
            <div className="stat-box">
              <span className="stat-value">1,204</span>
              <span className="stat-label">Interventions</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">98%</span>
              <span className="stat-label">Success Rate</span>
            </div>
          </div>
        </div>

        {/* Right Column: Details Form */}
        <div className="profile-details glass-card">
          <div className="details-header">
            <h3>Personal Information</h3>
            {!isEditing ? (
              <button className="btn-icon-text" onClick={() => setIsEditing(true)}>
                <Edit3 size={16} /> Edit
              </button>
            ) : (
              <button className="btn-icon-text active" onClick={handleSave}>
                <Save size={16} /> Save
              </button>
            )}
          </div>

          <div className="details-grid">
            <div className="detail-item">
              <label>
                <User size={14} /> Full Name
              </label>
              {isEditing ? (
                <input 
                  type="text" 
                  value={profile.name} 
                  onChange={e => setProfile({...profile, name: e.target.value})}
                  className="profile-input" 
                />
              ) : (
                <div className="detail-value">{profile.name}</div>
              )}
            </div>

            <div className="detail-item">
              <label>
                <Mail size={14} /> Email Address
              </label>
              {isEditing ? (
                <input 
                  type="email" 
                  value={profile.email} 
                  onChange={e => setProfile({...profile, email: e.target.value})}
                  className="profile-input" 
                />
              ) : (
                <div className="detail-value">{profile.email}</div>
              )}
            </div>

            <div className="detail-item">
              <label>
                <Shield size={14} /> Role / Access Level
              </label>
              <div className="detail-value">{profile.role}</div>
            </div>

            <div className="detail-item">
              <label>
                <Calendar size={14} /> Joined Date
              </label>
              <div className="detail-value">{profile.joinDate}</div>
            </div>
          </div>

          <div className="details-header" style={{ marginTop: '2.5rem', paddingTop: '2rem', borderTop: '1px solid var(--border-light)' }}>
            <h3><Palette size={16} style={{marginRight: '0.5rem', verticalAlign: 'text-bottom'}} /> Dashboard Appearance</h3>
          </div>
          
          <div className="theme-switcher-grid">
            <div 
              className={`theme-card ${theme === 'default' ? 'active' : ''}`}
              onClick={() => setTheme('default')}
            >
              <div className="theme-color-preview" style={{background: '#3b82f6'}}></div>
              <div className="theme-info">
                <strong>Default Blue</strong>
                <span>Standard corporate styling</span>
              </div>
            </div>
            
            <div 
              className={`theme-card ${theme === 'meesho' ? 'active' : ''}`}
              onClick={() => setTheme('meesho')}
            >
              <div className="theme-color-preview" style={{background: 'linear-gradient(135deg, #f43397, #df2884)'}}></div>
              <div className="theme-info">
                <strong>Meesho Pink</strong>
                <span>Vibrant brand identity</span>
              </div>
            </div>
          </div>

          <div className="details-header" style={{ marginTop: '2.5rem', paddingTop: '2rem', borderTop: '1px solid var(--border-light)' }}>
            <h3>Recent Activity</h3>
          </div>
          <div className="activity-timeline">
            <div className="activity-item">
              <div className="activity-icon"><Activity size={12} /></div>
              <div className="activity-content">
                <strong>Updated agent configuration</strong>
                <span>Today at 10:42 AM</span>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-icon"><Activity size={12} /></div>
              <div className="activity-content">
                <strong>Logged into dashboard</strong>
                <span>Today at 09:15 AM</span>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-icon"><Activity size={12} /></div>
              <div className="activity-content">
                <strong>Toggled Demo Mode</strong>
                <span>Yesterday at 04:30 PM</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
