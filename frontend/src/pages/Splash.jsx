import React from 'react';
import { Bot, Zap, Globe, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import './Splash.css';

export default function Splash() {
  return (
    <div className="splash-container">
      <div className="splash-bg-glow"></div>
      
      <div className="splash-content">
        <div className="splash-logo-wrap">
          <Bot size={48} strokeWidth={1.5} />
        </div>
        
        <h1 className="splash-title">MAVVE</h1>
        <p className="splash-subtitle">
          Intelligent Voice Agents for Bharat Commerce.<br/>
          Automatically intercept high-risk COD orders, verify intent in vernacular languages, 
          and negotiate instant prepaid conversions.
        </p>
        
        <div className="splash-features">
          <div className="feature-pill">
            <Zap size={16} /> Real-time RTO Prediction
          </div>
          <div className="feature-pill">
            <Bot size={16} /> Autonomous LangGraph Agents
          </div>
          <div className="feature-pill">
            <Globe size={16} /> Bhashini Multimodal Voice
          </div>
        </div>
        
        <Link to="/dashboard" className="cta-button">
          Enter Dashboard <ArrowRight size={20} />
        </Link>
      </div>
    </div>
  );
}
