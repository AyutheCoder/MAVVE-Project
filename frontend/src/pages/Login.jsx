import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, Mail, Lock, Zap, Shield, Globe, Bot } from 'lucide-react';
import './Login.css';

const PARTICLES = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  size: Math.random() * 4 + 2,
  x: Math.random() * 100,
  y: Math.random() * 100,
  duration: Math.random() * 6 + 4,
  delay: Math.random() * 3,
}));

const TAGLINE = 'Agentic AI for Bharat Commerce';

export default function Login({ setIsAuthenticated }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [typedText, setTypedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const navigate = useNavigate();

  // Typing animation
  useEffect(() => {
    if (!isTyping) return;
    let i = 0;
    const interval = setInterval(() => {
      setTypedText(TAGLINE.slice(0, i + 1));
      i++;
      if (i >= TAGLINE.length) {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 60);
    return () => clearInterval(interval);
  }, [isTyping]);

  const handleLogin = (e) => {
    e.preventDefault();
    setIsAuthenticated(true);
    localStorage.setItem('mavveAuth', 'true');
    navigate('/dashboard');
  };

  return (
    <div className="login-container">
      {/* Floating Particles */}
      <div className="particles-container">
        {PARTICLES.map(p => (
          <div
            key={p.id}
            className="particle"
            style={{
              width: p.size,
              height: p.size,
              left: `${p.x}%`,
              top: `${p.y}%`,
              animationDuration: `${p.duration}s`,
              animationDelay: `${p.delay}s`,
            }}
          />
        ))}
      </div>

      <div className="login-card glass-panel">
        <div className="login-header">
          <div className="logo-icon">
            <Zap size={28} />
          </div>
          <h1>MAVVE</h1>
          <p className="tagline">
            {typedText}
            <span className="cursor-blink">|</span>
          </p>
        </div>

        {/* Feature badges */}
        <div className="feature-badges">
          <span className="feature-badge"><Shield size={12} /> Secure</span>
          <span className="feature-badge"><Globe size={12} /> 22+ Languages</span>
          <span className="feature-badge"><Bot size={12} /> Multi-Agent</span>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group">
            <Mail className="input-icon" size={18} />
            <input 
              type="email" 
              placeholder="Admin Email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          
          <div className="input-group">
            <Lock className="input-icon" size={18} />
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          <button type="submit" className="login-btn">
            <LogIn size={18} />
            Sign In to Dashboard
          </button>
        </form>
        
        <div className="login-footer">
          <p>Mock Authentication — Enter any credentials</p>
        </div>
      </div>
    </div>
  );
}
