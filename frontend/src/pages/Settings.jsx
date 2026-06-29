import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, Bot, Globe, Bell, Key, Save, Edit3, Link, CheckCircle, AlertCircle
} from 'lucide-react';
import './Settings.css';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('general');

  // Form State
  const [rtoThreshold, setRtoThreshold] = useState(() => {
    const saved = localStorage.getItem('mavve_rtoThreshold');
    return saved ? parseFloat(saved) : 0.65;
  });
  
  const [agentConfig, setAgentConfig] = useState(() => {
    const saved = localStorage.getItem('mavve_agentConfig');
    return saved ? JSON.parse(saved) : {
      address: true,
      intent: true,
      prepaid: true,
      maxRounds: 3,
      maxDiscount: 15,
      tone: 'friendly'
    };
  });

  const [langConfig, setLangConfig] = useState(() => {
    const saved = localStorage.getItem('mavve_langConfig');
    return saved ? JSON.parse(saved) : {
      hi: true, mr: true, bn: true, te: true, ta: false, gu: false,
      fallback: 'hi',
      voice: 'female'
    };
  });

  const [notifyConfig, setNotifyConfig] = useState(() => {
    const saved = localStorage.getItem('mavve_notifyConfig');
    return saved ? JSON.parse(saved) : {
      escalations: true,
      dailyDigest: true,
      webhookUrl: 'https://api.yourstore.com/mavve/webhook'
    };
  });

  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem('mavve_profile');
    return saved ? JSON.parse(saved) : { name: 'Admin', email: 'admin@mavve.ai' };
  });

  // Save to localStorage whenever they change
  React.useEffect(() => localStorage.setItem('mavve_rtoThreshold', rtoThreshold), [rtoThreshold]);
  React.useEffect(() => localStorage.setItem('mavve_agentConfig', JSON.stringify(agentConfig)), [agentConfig]);
  React.useEffect(() => localStorage.setItem('mavve_langConfig', JSON.stringify(langConfig)), [langConfig]);
  React.useEffect(() => localStorage.setItem('mavve_notifyConfig', JSON.stringify(notifyConfig)), [notifyConfig]);
  React.useEffect(() => localStorage.setItem('mavve_profile', JSON.stringify(profile)), [profile]);
  const [theme, setTheme] = useState(localStorage.getItem('mavveTheme') || 'default');

  React.useEffect(() => {
    if (theme === 'meesho') {
      document.documentElement.setAttribute('data-theme', 'meesho');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('mavveTheme', theme);
  }, [theme]);

  const handleSave = () => {
    // Mock save
    alert('Settings saved successfully!');
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>System Settings</h1>
        <p>Configure MAVVE orchestration, agent parameters, and integrations.</p>
      </div>

      <div className="settings-grid">
        {/* Navigation Sidebar */}
        <div className="settings-nav">
          <div className={`settings-nav-item ${activeTab === 'general' ? 'active' : ''}`} onClick={() => setActiveTab('general')}>
            <SettingsIcon size={18} /> General Setup
          </div>
          <div className={`settings-nav-item ${activeTab === 'agents' ? 'active' : ''}`} onClick={() => setActiveTab('agents')}>
            <Bot size={18} /> Agent Configuration
          </div>
          <div className={`settings-nav-item ${activeTab === 'language' ? 'active' : ''}`} onClick={() => setActiveTab('language')}>
            <Globe size={18} /> Language & Voice
          </div>
          <div className={`settings-nav-item ${activeTab === 'notifications' ? 'active' : ''}`} onClick={() => setActiveTab('notifications')}>
            <Bell size={18} /> Notifications
          </div>
          <div className={`settings-nav-item ${activeTab === 'api' ? 'active' : ''}`} onClick={() => setActiveTab('api')}>
            <Key size={18} /> API & Integrations
          </div>
        </div>

        {/* Content Area */}
        <div className="settings-content">
          
          {activeTab === 'general' && (
            <div className="settings-section glass-card">
              <div className="section-header">
                <h2>RTO Interception Threshold</h2>
                <p>Determine the minimum P(RTO) risk score required to trigger a MAVVE intervention.</p>
              </div>
              
              <div className="form-group">
                <label className="form-label">Risk Threshold: {(rtoThreshold * 100).toFixed(0)}%</label>
                <div className="range-container">
                  <input 
                    type="range" 
                    min="0" max="1" step="0.05" 
                    value={rtoThreshold} 
                    onChange={e => setRtoThreshold(parseFloat(e.target.value))} 
                  />
                  <span className="range-value">{rtoThreshold.toFixed(2)}</span>
                </div>
                <div style={{marginTop: '1rem', padding: '1rem', background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.3)', borderRadius: '4px', fontSize: '0.875rem'}}>
                  <span style={{color: '#3b82f6', fontWeight: 'bold'}}>Preview: </span> 
                  At a {rtoThreshold} threshold, approximately <strong>{Math.floor((1 - rtoThreshold)*30 + 5)}%</strong> of all COD orders will be intercepted by MAVVE.
                </div>
              </div>
            </div>
          )}

          {activeTab === 'agents' && (
            <div className="settings-section glass-card">
              <div className="section-header">
                <h2>Agent Configuration</h2>
                <p>Enable/disable specific agents and tune their operational parameters.</p>
              </div>

              <div className="form-group">
                <label className="form-label">Active Agents</label>
                <div className="toggle-wrapper">
                  <div className="toggle-info">
                    <h4>Address Resolution Agent</h4>
                    <p>Fixes invalid addresses and collects missing landmarks.</p>
                  </div>
                  <label className="toggle-switch">
                    <input type="checkbox" checked={agentConfig.address} onChange={e => setAgentConfig({...agentConfig, address: e.target.checked})} />
                    <span className="slider"></span>
                  </label>
                </div>
                <div className="toggle-wrapper">
                  <div className="toggle-info">
                    <h4>Intent Verification Agent</h4>
                    <p>Confirms COD intent and physical availability.</p>
                  </div>
                  <label className="toggle-switch">
                    <input type="checkbox" checked={agentConfig.intent} onChange={e => setAgentConfig({...agentConfig, intent: e.target.checked})} />
                    <span className="slider"></span>
                  </label>
                </div>
                <div className="toggle-wrapper">
                  <div className="toggle-info">
                    <h4>Prepaid Conversion Agent</h4>
                    <p>Negotiates COD to Prepaid conversions using discounts.</p>
                  </div>
                  <label className="toggle-switch">
                    <input type="checkbox" checked={agentConfig.prepaid} onChange={e => setAgentConfig({...agentConfig, prepaid: e.target.checked})} />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>

              <div className="form-group" style={{marginTop: '2rem'}}>
                <label className="form-label">Max Conversation Rounds</label>
                <div className="form-desc">Maximum number of back-and-forth messages before forcing a fallback (Escalation).</div>
                <div className="range-container">
                  <input 
                    type="range" min="1" max="5" step="1" 
                    value={agentConfig.maxRounds} 
                    onChange={e => setAgentConfig({...agentConfig, maxRounds: parseInt(e.target.value)})} 
                  />
                  <span className="range-value">{agentConfig.maxRounds}</span>
                </div>
              </div>

              {agentConfig.prepaid && (
                <div className="form-group" style={{marginTop: '2rem'}}>
                  <label className="form-label">Max Prepaid Discount (%)</label>
                  <div className="form-desc">Maximum discount percentage the agent is authorized to offer for prepaid conversion.</div>
                  <div className="range-container">
                    <input 
                      type="range" min="5" max="25" step="1" 
                      value={agentConfig.maxDiscount} 
                      onChange={e => setAgentConfig({...agentConfig, maxDiscount: parseInt(e.target.value)})} 
                    />
                    <span className="range-value">{agentConfig.maxDiscount}%</span>
                  </div>
                </div>
              )}

              <div className="form-group" style={{marginTop: '2rem'}}>
                <label className="form-label">Agent Tone</label>
                <select 
                  className="settings-select" 
                  value={agentConfig.tone} 
                  onChange={e => setAgentConfig({...agentConfig, tone: e.target.value})}
                >
                  <option value="formal">Formal & Professional</option>
                  <option value="friendly">Friendly & Empathetic</option>
                  <option value="casual">Ultra-casual (Slang allowed)</option>
                </select>
              </div>
            </div>
          )}

          {activeTab === 'language' && (
            <div className="settings-section glass-card">
              <div className="section-header">
                <h2>Language & Voice Settings (Bhashini)</h2>
                <p>Configure supported vernacular languages and TTS preferences.</p>
              </div>

              <div className="form-group">
                <label className="form-label">Supported Languages</label>
                <div className="checkbox-grid">
                  {['hi:Hindi', 'mr:Marathi', 'bn:Bengali', 'te:Telugu', 'ta:Tamil', 'gu:Gujarati'].map(l => {
                    const [code, name] = l.split(':');
                    return (
                      <label key={code} className="checkbox-label">
                        <input 
                          type="checkbox" 
                          checked={langConfig[code] || false} 
                          onChange={e => setLangConfig({...langConfig, [code]: e.target.checked})} 
                        />
                        {name}
                      </label>
                    );
                  })}
                </div>
              </div>

              <div className="form-group" style={{marginTop: '2rem'}}>
                <label className="form-label">Default Fallback Language</label>
                <select className="settings-select" value={langConfig.fallback} onChange={e => setLangConfig({...langConfig, fallback: e.target.value})}>
                  <option value="hi">Hindi</option>
                  <option value="en">English</option>
                </select>
              </div>

              <div className="form-group" style={{marginTop: '2rem'}}>
                <label className="form-label">TTS Voice Gender</label>
                <select className="settings-select" value={langConfig.voice} onChange={e => setLangConfig({...langConfig, voice: e.target.value})}>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                </select>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="settings-section glass-card">
              <div className="section-header">
                <h2>Alerts & Webhooks</h2>
              </div>

              <div className="form-group">
                <div className="toggle-wrapper">
                  <div className="toggle-info">
                    <h4>Email Alerts on Escalation</h4>
                    <p>Send an email to admin when an agent escalates a conversation.</p>
                  </div>
                  <label className="toggle-switch">
                    <input type="checkbox" checked={notifyConfig.escalations} onChange={e => setNotifyConfig({...notifyConfig, escalations: e.target.checked})} />
                    <span className="slider"></span>
                  </label>
                </div>
                <div className="toggle-wrapper">
                  <div className="toggle-info">
                    <h4>Daily Digest</h4>
                    <p>Receive a daily summary of MAVVE savings and metrics.</p>
                  </div>
                  <label className="toggle-switch">
                    <input type="checkbox" checked={notifyConfig.dailyDigest} onChange={e => setNotifyConfig({...notifyConfig, dailyDigest: e.target.checked})} />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>

              <div className="form-group" style={{marginTop: '2rem'}}>
                <label className="form-label">External Order Webhook URL</label>
                <div className="form-desc">MAVVE will POST to this URL when a final outcome (DISPATCH, CANCEL, CONVERT) is reached.</div>
                <input 
                  type="text" 
                  className="settings-input" 
                  value={notifyConfig.webhookUrl} 
                  onChange={e => setNotifyConfig({...notifyConfig, webhookUrl: e.target.value})} 
                />
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="settings-section glass-card">
              <div className="section-header">
                <h2>API Integrations</h2>
                <p>Manage connection keys for third-party services.</p>
              </div>

              <div className="api-key-row">
                <div className="api-key-info">
                  <h4>Google Gemini (LLM)</h4>
                  <div className="api-key-mask">AIzaSyB**********************</div>
                </div>
                <div className="api-status connected"><CheckCircle size={14}/> Connected</div>
                <button className="btn-icon"><Edit3 size={16}/></button>
              </div>

              <div className="api-key-row">
                <div className="api-key-info">
                  <h4>WhatsApp Cloud API</h4>
                  <div className="api-key-mask">EAAO*************************</div>
                </div>
                <div className="api-status connected"><CheckCircle size={14}/> Connected</div>
                <button className="btn-icon"><Edit3 size={16}/></button>
              </div>

              <div className="api-key-row">
                <div className="api-key-info">
                  <h4>Bhashini API (Voice)</h4>
                  <div className="api-key-mask">bhashini_**********************</div>
                </div>
                <div className="api-status connected"><CheckCircle size={14}/> Connected</div>
                <button className="btn-icon"><Edit3 size={16}/></button>
              </div>

              <div className="api-key-row">
                <div className="api-key-info">
                  <h4>Payment Gateway (Razorpay/Stripe)</h4>
                  <div className="api-key-mask" style={{color: 'var(--accent-warning)'}}>Not configured</div>
                </div>
                <div className="api-status disconnected"><AlertCircle size={14}/> Disconnected</div>
                <button className="btn-icon"><Link size={16}/></button>
              </div>
            </div>
          )}



          <div className="save-bar">
            <button className="btn btn-primary" onClick={handleSave}>
              <Save size={16} /> Save Changes
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
