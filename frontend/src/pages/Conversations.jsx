import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, Play, Download, MapPin, MessageSquare, CreditCard, 
  CheckCircle, XCircle, Clock, PlayCircle, Mic, AlertCircle, ArrowLeft
} from 'lucide-react';
import './Conversations.css';

// --- Mock Data Generator ---
const mockConversations = [
  {
    id: 'ORD-2101',
    phone: '+91 98765 43210',
    lang: {c: 'hi', e: '🇮🇳', name: 'Hindi'},
    agent: 'Intent Agent',
    outcome: 'VALIDATED',
    duration: '1m 45s',
    rounds: 3,
    discount: '₹0',
    messages: [
      { type: 'system', text: 'Order Intercepted. Routing to Intent Agent.' },
      { type: 'agent', text: 'नमस्ते! हमने देखा कि आपने ₹1,299 का COD ऑर्डर किया है। क्या आप डिलीवरी के समय इस राशि का भुगतान करने के लिए उपलब्ध होंगे?', trans: 'Hello! We noticed you placed a COD order for ₹1,299. Will you be available to pay this amount at delivery?', time: '10:00 AM' },
      { type: 'user', text: 'हां, मैं घर पर ही रहूंगा।', trans: 'Yes, I will be at home.', time: '10:02 AM' },
      { type: 'agent', text: 'धन्यवाद! आपका ऑर्डर कन्फर्म हो गया है और जल्द ही डिस्पैच किया जाएगा।', trans: 'Thank you! Your order is confirmed and will be dispatched soon.', time: '10:02 AM' },
      { type: 'system', text: 'Session closed. Disposition: VALIDATED' }
    ]
  },
  {
    id: 'ORD-2102',
    phone: '+91 91234 56789',
    lang: {c: 'mr', e: '🚩', name: 'Marathi'},
    agent: 'Prepaid Agent',
    outcome: 'CONVERTED',
    duration: '4m 12s',
    rounds: 5,
    discount: '₹65',
    messages: [
      { type: 'system', text: 'High Risk COD detected. Routing to Prepaid Conversion Agent.' },
      { type: 'agent', text: 'नमस्कार! जर तुम्ही आता UPI द्वारे पेमेंट केले, तर तुम्हाला ₹65 ची झटपट सूट मिळेल. लिंक पाठवू का?', trans: 'Hello! If you pay via UPI now, you will get an instant ₹65 discount. Should I send the link?', time: '11:15 AM' },
      { type: 'user', isVoice: true, duration: '0:04', text: 'हो, लिंक पाठवा.', trans: 'Yes, send the link.', time: '11:17 AM' },
      { type: 'system', text: 'Payment link generated: rzp.io/l/mavve123' },
      { type: 'agent', text: 'ही तुमची लिंक आहे: rzp.io/l/mavve123. ही लिंक १५ मिनिटांसाठी वैध आहे.', trans: 'Here is your link. It is valid for 15 minutes.', time: '11:17 AM' },
      { type: 'system', text: 'Webhook received: Payment SUCCESS' },
      { type: 'agent', text: 'तुमचे पेमेंट यशस्वी झाले आहे! तुमचे पैसे वाचले आहेत. लवकरच ऑर्डर मिळेल.', trans: 'Your payment was successful! You saved money. Order will arrive soon.', time: '11:19 AM' },
      { type: 'system', text: 'Order updated to PREPAID. Session closed.' }
    ]
  },
  {
    id: 'ORD-2103',
    phone: '+91 88888 11111',
    lang: {c: 'bn', e: '🐅', name: 'Bengali'},
    agent: 'Address Agent',
    outcome: 'CANCELLED',
    duration: '8m 30s',
    rounds: 4,
    discount: '₹0',
    messages: [
      { type: 'system', text: 'Address Anomaly: Missing Landmarks. Routing to Address Agent.' },
      { type: 'agent', text: 'নমস্কার! আপনার ঠিকানায় কিছু তথ্য বাদ পড়েছে। আপনি কি কাছাকাছি কোনো ল্যান্ডমার্ক বলতে পারবেন?', trans: 'Hello! Your address is missing some info. Can you provide a nearby landmark?', time: '02:00 PM' },
      { type: 'user', text: 'আমি তো জানি না, আমার ছেলে অর্ডার করেছে।', trans: 'I do not know, my son ordered it.', time: '02:05 PM' },
      { type: 'system', text: 'Agent detected uncertainty. Switching strategy.' },
      { type: 'agent', text: 'কোনো সমস্যা নেই। আপনি কি অর্ডারটি বাতিল করতে চান? এতে কোনো চার্জ লাগবে না।', trans: 'No problem. Would you like to cancel the order? There are no charges.', time: '02:06 PM' },
      { type: 'user', text: 'হ্যাঁ, বাতিল করে দিন।', trans: 'Yes, cancel it.', time: '02:08 PM' },
      { type: 'system', text: 'Session closed. Disposition: CANCELLED' }
    ]
  },
  // Add 7 more mock conversations to hit the 10+ requirement
  ...Array.from({length: 8}).map((_, i) => ({
    id: `ORD-${2104 + i}`,
    phone: `+91 77777 ${10000 + i}`,
    lang: {c: 'en', e: '🇬🇧', name: 'English'},
    agent: ['Intent Agent', 'Address Agent', 'Prepaid Agent'][i%3],
    outcome: ['VALIDATED', 'CANCELLED', 'ESCALATED'][i%3],
    duration: `${Math.floor(Math.random()*5 + 1)}m ${Math.floor(Math.random()*59)}s`,
    rounds: Math.floor(Math.random()*4 + 2),
    discount: i%3===0 ? '₹50' : '₹0',
    messages: [
      { type: 'system', text: 'Session initiated.' },
      { type: 'agent', text: 'Hello, this is a MAVVE agent verification message.', trans: 'N/A', time: '12:00 PM' },
      { type: 'user', text: 'Okay.', trans: 'N/A', time: '12:01 PM' },
      { type: 'system', text: 'Session closed.' }
    ]
  }))
];

export default function Conversations() {
  const [conversations, setConversations] = useState(mockConversations);
  const [selectedConv, setSelectedConv] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [agentFilter, setAgentFilter] = useState('All');
  
  // Replay State
  const [isReplaying, setIsReplaying] = useState(false);
  const [visibleMessages, setVisibleMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  // Filter Logic
  const filteredConvs = conversations.filter(c => {
    const matchSearch = c.id.toLowerCase().includes(searchTerm.toLowerCase()) || c.phone.includes(searchTerm);
    const matchAgent = agentFilter === 'All' || c.agent.includes(agentFilter);
    return matchSearch && matchAgent;
  });

  const getAgentIcon = (agent) => {
    if(agent.includes('Address')) return <MapPin size={16} color="#3b82f6" />;
    if(agent.includes('Intent')) return <MessageSquare size={16} color="#10b981" />;
    return <CreditCard size={16} color="#f59e0b" />;
  };

  const getBadgeClass = (outcome) => {
    if(['VALIDATED', 'CONVERTED'].includes(outcome)) return 'badge-success';
    if(outcome === 'CANCELLED') return 'badge-danger';
    return 'badge-warning';
  };

  // Replay Logic
  const startReplay = () => {
    if (!selectedConv) return;
    setIsReplaying(true);
    setVisibleMessages([]);
    let currentIndex = 0;

    const showNext = () => {
      if (currentIndex >= selectedConv.messages.length) {
        setIsReplaying(false);
        setIsTyping(false);
        return;
      }

      const msg = selectedConv.messages[currentIndex];
      
      // If it's a system message, show instantly
      if (msg.type === 'system') {
        setVisibleMessages(prev => [...prev, msg]);
        currentIndex++;
        setTimeout(showNext, 500);
      } else {
        // Show typing indicator
        setIsTyping(true);
        // Simulate thinking/typing delay (1s to 2.5s)
        const delay = Math.random() * 1500 + 1000;
        
        setTimeout(() => {
          setIsTyping(false);
          setVisibleMessages(prev => [...prev, msg]);
          currentIndex++;
          // Wait before showing next message
          setTimeout(showNext, 800);
        }, delay);
      }
    };

    showNext();
  };

  // Select conversation
  useEffect(() => {
    if (selectedConv) {
      setIsReplaying(false);
      setIsTyping(false);
      setVisibleMessages(selectedConv.messages);
    }
  }, [selectedConv]);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [visibleMessages, isTyping]);

  // Export JSON
  const handleExport = () => {
    if(!selectedConv) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(selectedConv, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `${selectedConv.id}_transcript.json`;
    a.click();
  };

  return (
    <div className="conversations-page">
      
      {/* Left Panel */}
      <div className={`conv-list-panel ${selectedConv ? 'mobile-hidden' : ''}`}>
        <div className="list-header">
          <div className="search-wrap">
            <Search className="search-icon" size={16} />
            <input 
              type="text" 
              placeholder="Search ID or Phone..." 
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="filters-row">
            <select value={agentFilter} onChange={e => setAgentFilter(e.target.value)}>
              <option value="All">All Agents</option>
              <option value="Address">Address</option>
              <option value="Intent">Intent</option>
              <option value="Prepaid">Prepaid</option>
            </select>
          </div>
        </div>
        
        <div className="conv-list">
          {filteredConvs.map(conv => (
            <div 
              key={conv.id} 
              className={`conv-item ${selectedConv?.id === conv.id ? 'active' : ''}`}
              onClick={() => setSelectedConv(conv)}
            >
              <div className="item-top">
                <span className="item-order">{conv.id}</span>
                <span className="item-time">{conv.duration}</span>
              </div>
              <div className="item-mid">
                {conv.lang.e} {conv.phone.substring(0, 7)}****
              </div>
              <div className="item-bot">
                <div style={{display: 'flex', alignItems: 'center', gap: '4px'}}>
                  {getAgentIcon(conv.agent)}
                  <span style={{fontSize: '0.75rem', color: 'var(--text-secondary)'}}>{conv.agent}</span>
                </div>
                <span className={`badge ${getBadgeClass(conv.outcome)}`}>{conv.outcome}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel */}
      <div className={`conv-detail-panel ${!selectedConv ? 'mobile-hidden' : ''}`}>
        {!selectedConv ? (
          <div className="empty-state">
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem'}}>
              <MessageSquare size={48} opacity={0.2} />
              <p>Select a conversation to view the transcript</p>
            </div>
          </div>
        ) : (
          <>
            <div className="detail-header">
              <div className="header-info" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <button 
                  className="mobile-back-btn btn-icon" 
                  onClick={() => setSelectedConv(null)} 
                  title="Back to list"
                >
                  <ArrowLeft size={20} />
                </button>
                <div>
                  <h2>{selectedConv.id}</h2>
                  <div className="header-sub">
                    <span>{selectedConv.phone}</span>
                    <span>{selectedConv.lang.e} {selectedConv.lang.name}</span>
                  </div>
                </div>
              </div>
              <div className="header-actions">
                <button 
                  className="btn btn-primary" 
                  onClick={startReplay} 
                  disabled={isReplaying}
                >
                  <Play size={16} /> Replay
                </button>
                <button className="btn-icon" onClick={handleExport} title="Export JSON">
                  <Download size={20} />
                </button>
              </div>
            </div>

            <div className="chat-window">
              {visibleMessages.map((msg, i) => {
                if (msg.type === 'system') {
                  return (
                    <div key={i} className="system-chip">
                      {msg.text}
                    </div>
                  );
                }

                return (
                  <div key={i} className={`message-row ${msg.type}`}>
                    <div className="message-bubble">
                      {msg.isVoice ? (
                        <div className="voice-message">
                          <button className="play-btn"><PlayCircle size={20} fill="white" /></button>
                          <div className="waveform">
                            {Array.from({length: 20}).map((_, j) => (
                              <div key={j} className="wave-bar" style={{height: `${Math.random() * 100}%`}}></div>
                            ))}
                          </div>
                          <span style={{fontSize: '0.75rem', fontWeight: 'bold'}}>{msg.duration}</span>
                          <Mic size={14} color="var(--text-muted)" style={{marginLeft: 'auto'}} />
                        </div>
                      ) : (
                        <div className="message-original">{msg.text}</div>
                      )}
                      
                      {msg.trans && msg.trans !== 'N/A' && (
                        <div className="message-translation">"{msg.trans}"</div>
                      )}
                      <div className="message-meta">
                        {msg.time}
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {isTyping && (
                <div className="message-row agent">
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="detail-footer">
              <div className="meta-group">
                <div className="meta-item">
                  <span className="meta-label">Duration</span>
                  <span className="meta-val">{selectedConv.duration}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Turns</span>
                  <span className="meta-val">{selectedConv.rounds}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Discount Applied</span>
                  <span className="meta-val" style={{color: 'var(--accent-success)'}}>{selectedConv.discount}</span>
                </div>
              </div>
              <div>
                <span className={`badge ${getBadgeClass(selectedConv.outcome)}`} style={{fontSize: '0.875rem', padding: '0.4rem 0.8rem'}}>
                  Final: {selectedConv.outcome}
                </span>
              </div>
            </div>
          </>
        )}
      </div>
      
    </div>
  );
}
