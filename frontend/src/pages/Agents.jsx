import React, { useState, useEffect } from 'react';
import { 
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { Network, Bot, MapPin, MessageSquare, CreditCard, CheckCircle, XCircle, Play, Pause } from 'lucide-react';
import './Agents.css';

// --- Mock Data ---
const agentMetrics = {
  address: { name: 'Address Agent', sessions: 1245, success: 85, avgRounds: 2.1, avgTime: '45s', icon: <MapPin size={24} />, color: '#3b82f6' },
  intent: { name: 'Intent Agent', sessions: 890, success: 92, avgRounds: 1.4, avgTime: '20s', icon: <MessageSquare size={24} />, color: '#10b981' },
  prepaid: { name: 'Prepaid Agent', sessions: 650, success: 45, avgRounds: 3.2, avgTime: '90s', icon: <CreditCard size={24} />, color: '#f59e0b' },
};

const langData = [
  { name: 'Hindi (hi)', value: 450 },
  { name: 'Marathi (mr)', value: 210 },
  { name: 'Bengali (bn)', value: 180 },
  { name: 'Telugu (te)', value: 120 },
  { name: 'English (en)', value: 90 },
];

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const heatmapData = days.map(d => Array.from({length: 24}, () => Math.floor(Math.random() * 100)));

// Simulation steps
const SIM_STEPS = [
  { active: 'trigger', label: 'Order ORD-4192 placed (COD ₹1,299) — RTO Score: 0.78', delay: 1200 },
  { active: 'orchestrator', label: 'Risk analyzed: Address anomaly + High RTO history → Routing to Address Agent', delay: 1800 },
  { active: 'address', label: 'Address Agent: "बड़े मंदिर के पास, जिला X" — Querying landmark DB...', delay: 2000 },
  { active: 'address', label: 'Address Agent: Confidence 0.4 → 0.85. Landmark verified via Bhashini ASR.', delay: 1500 },
  { active: 'orchestrator', label: 'Address resolved. COD still risky → Routing to Prepaid Agent', delay: 1200 },
  { active: 'prepaid', label: 'Prepaid Agent: Offering ₹65 discount for UPI payment...', delay: 1800 },
  { active: 'prepaid', label: 'User agreed! UPI link generated: rzp.io/l/mavve4192', delay: 1500 },
  { active: 'dispatch', label: '✅ Payment SUCCESS. Order converted to PREPAID. Dispatching!', delay: 1200 },
];
// Neural Trace Hook
const useNeuralTrace = (agentKey) => {
  const [lines, setLines] = useState([]);
  useEffect(() => {
    const logs = {
      address: ['[GEO] Parsing lat/long...', '[DB] Querying landmarks...', '[ASR] Voice match 89%...', '[GEO] Pinpoint accurate.'],
      intent: ['[NLP] Extracting intent...', '[VEC] Cosine sim 0.94...', '[SYS] Escalation risk low.', '[NLP] Intent resolved.'],
      prepaid: ['[PG] Initializing gateway...', '[DISC] Checking eligibility...', '[SMS] Link sent.', '[PG] Payment verified.']
    }[agentKey] || ['[SYS] Initializing...'];
    
    let i = 0;
    const interval = setInterval(() => {
      const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric" });
      setLines(prev => {
        const next = [...prev, { time: now, text: logs[i % logs.length] }];
        return next.slice(-6);
      });
      i++;
    }, 1500 + Math.random() * 1000);
    return () => clearInterval(interval);
  }, [agentKey]);
  return lines;
};

const NeuralTerminal = ({ agentKey }) => {
  const traceLines = useNeuralTrace(agentKey);
  return (
    <div className="neural-terminal">
      {traceLines.map((line, i) => (
        <div key={i} className="terminal-line">
          <span className="timestamp">[{line.time}]</span>
          {line.text}
        </div>
      ))}
      <div style={{marginTop: '0.5rem', color: '#10b981'}}>
        <span className="timestamp">[{new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric" })}]</span>
        &gt; AWAITING
        <span className="terminal-cursor"></span>
      </div>
    </div>
  );
};

const AgentMetricCard = ({ agentKey, agent, renderDonut }) => {
  return (
    <div className="agent-card-container">
      {/* Front Face */}
      <div className="metric-card glass-card agent-front-face">
        <div className="metric-header">
          <div style={{color: agent.color}}>{agent.icon}</div>
          {agent.name}
        </div>
        {renderDonut(agent.success, agent.color)}
        <div className="metric-stats">
          <div className="stat-box">
            <span className="stat-label">Sessions</span>
            <span className="stat-val">{agent.sessions.toLocaleString()}</span>
          </div>
          <div className="stat-box">
            <span className="stat-label">Avg Time</span>
            <span className="stat-val">{agent.avgTime}</span>
          </div>
        </div>
        <div style={{textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-secondary)'}}>
          Avg Rounds: {agent.avgRounds}
        </div>
      </div>
      
      {/* Back Face: Neural Trace Overlay */}
      <div className="agent-trace-overlay">
        <div className="terminal-header">LIVE NEURAL TRACE</div>
        <NeuralTerminal agentKey={agentKey} />
      </div>
    </div>
  );
};

export default function Agents() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [simRunning, setSimRunning] = useState(false);
  const [simStep, setSimStep] = useState(-1);
  const [simLog, setSimLog] = useState([]);

  // Simulation engine
  useEffect(() => {
    if (!simRunning || simStep < 0) return;
    if (simStep >= SIM_STEPS.length) {
      setSimRunning(false);
      return;
    }
    const timer = setTimeout(() => {
      setSimLog(prev => [...prev, SIM_STEPS[simStep].label]);
      setSimStep(prev => prev + 1);
    }, SIM_STEPS[simStep]?.delay || 1000);
    return () => clearTimeout(timer);
  }, [simRunning, simStep]);

  const startSim = () => {
    setSimLog([]);
    setSimStep(0);
    setSimRunning(true);
  };

  const activeNode = simStep > 0 
    ? SIM_STEPS[Math.min(simStep - 1, SIM_STEPS.length - 1)].active 
    : null;

  const renderDonut = (successRate, color) => {
    const data = [{name: 'Success', value: successRate}, {name: 'Fail', value: 100-successRate}];
    return (
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} innerRadius={55} outerRadius={75} paddingAngle={5} dataKey="value" stroke="none">
              <Cell fill={color} />
              <Cell fill="rgba(255,255,255,0.08)" />
            </Pie>
            <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fill="#fff" fontSize="22px" fontWeight="bold">
              {successRate}%
            </text>
          </PieChart>
        </ResponsiveContainer>
        {/* Pulse Core Animation */}
        <svg className="pulse-core-svg">
          <circle cx="50%" cy="50%" r="38" fill="none" stroke={color} strokeWidth="1" className="pulse-ring-1" opacity="0.4" />
          <circle cx="50%" cy="50%" r="42" fill="none" stroke={color} strokeWidth="1" className="pulse-ring-2" opacity="0.2" />
          <circle cx="50%" cy="50%" r="10" fill={color} className="pulse-center" />
        </svg>
      </div>
    );
  };

  const getIntensityColor = (val) => {
    const alpha = (val / 100) * 0.8 + 0.1;
    return `rgba(var(--accent-primary-rgb), ${alpha})`;
  };

  return (
    <div className="agents-page">
      
      {/* 1. Agent Flow Visualizer with SVG Connections */}
      <div className="glass-card" style={{padding: '0'}}>
        <div style={{padding: '1.25rem', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <h2 style={{fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Network size={20} /> LangGraph Orchestrator Flow
          </h2>
          <button 
            className={`sim-btn ${simRunning ? 'active' : ''}`}
            onClick={simRunning ? () => setSimRunning(false) : startSim}
          >
            {simRunning ? <><Pause size={14} /> Stop</> : <><Play size={14} /> Live Simulation</>}
          </button>
        </div>
        
        <div className="flow-vis-container">
          {/* SVG Flow Graph */}
          <div className="flow-svg-wrapper">
            <svg viewBox="0 0 600 320" className="flow-svg">
              {/* Connection lines */}
              <line x1="300" y1="55" x2="300" y2="95" className={`flow-line ${(activeNode === 'orchestrator' || activeNode === 'trigger') ? 'active' : ''}`} />
              
              <line x1="300" y1="155" x2="150" y2="195" className={`flow-line ${activeNode === 'address' ? 'active' : ''}`} />
              <line x1="300" y1="155" x2="300" y2="195" className={`flow-line ${activeNode === 'intent' ? 'active' : ''}`} />
              <line x1="300" y1="155" x2="450" y2="195" className={`flow-line ${activeNode === 'prepaid' ? 'active' : ''}`} />
              
              <line x1="450" y1="250" x2="225" y2="285" className={`flow-line ${activeNode === 'dispatch' ? 'active' : ''}`} />
              <line x1="450" y1="250" x2="375" y2="285" className={`flow-line ${activeNode === 'cancel' ? 'active' : ''}`} />

              {/* Animated data flow dots */}
              {activeNode && (
                <>
                  <circle r="4" fill="var(--accent-primary)" opacity="0.9">
                    <animateMotion dur="0.8s" repeatCount="indefinite" 
                      path={(activeNode === 'orchestrator' || activeNode === 'trigger') ? 'M300,55 L300,95' :
                            activeNode === 'address' ? 'M300,155 L150,195' :
                            activeNode === 'intent' ? 'M300,155 L300,195' :
                            activeNode === 'prepaid' ? 'M300,155 L450,195' :
                            activeNode === 'dispatch' ? 'M450,250 L225,285' :
                            activeNode === 'cancel' ? 'M450,250 L375,285' : 'M300,55 L300,95'} />
                  </circle>
                  <circle r="4" fill="var(--accent-primary)" opacity="0.5">
                    <animateMotion dur="0.8s" repeatCount="indefinite" begin="0.4s"
                      path={(activeNode === 'orchestrator' || activeNode === 'trigger') ? 'M300,55 L300,95' :
                            activeNode === 'address' ? 'M300,155 L150,195' :
                            activeNode === 'intent' ? 'M300,155 L300,195' :
                            activeNode === 'prepaid' ? 'M300,155 L450,195' :
                            activeNode === 'dispatch' ? 'M450,250 L225,285' :
                            activeNode === 'cancel' ? 'M450,250 L375,285' : 'M300,55 L300,95'} />
                  </circle>
                </>
              )}

              {/* Nodes */}
              {/* Trigger */}
              <g className={`flow-g-node ${activeNode === 'trigger' ? 'glow' : ''}`}>
                <rect x="245" y="15" width="110" height="40" rx="8" className="node-rect" />
                <text x="300" y="39" textAnchor="middle" className="node-text">Order Trigger</text>
              </g>

              {/* Orchestrator */}
              <g className={`flow-g-node ${activeNode === 'orchestrator' ? 'glow' : ''}`}>
                <rect x="225" y="95" width="150" height="55" rx="10" className="node-rect orchestrator-rect" />
                <text x="300" y="118" textAnchor="middle" className="node-text" style={{fontWeight: 700}}>MAVVE</text>
                <text x="300" y="137" textAnchor="middle" className="node-subtext">Orchestrator</text>
              </g>

              {/* Address Agent */}
              <g className={`flow-g-node ${activeNode === 'address' ? 'glow' : ''}`}>
                <rect x="90" y="195" width="120" height="55" rx="8" className="node-rect" />
                <text x="150" y="218" textAnchor="middle" className="node-text">🏠 Address</text>
                <text x="150" y="237" textAnchor="middle" className="node-subtext">Agent</text>
              </g>

              {/* Intent Agent */}
              <g className={`flow-g-node ${activeNode === 'intent' ? 'glow' : ''}`}>
                <rect x="240" y="195" width="120" height="55" rx="8" className="node-rect" />
                <text x="300" y="218" textAnchor="middle" className="node-text">🔍 Intent</text>
                <text x="300" y="237" textAnchor="middle" className="node-subtext">Agent</text>
              </g>

              {/* Prepaid Agent */}
              <g className={`flow-g-node ${activeNode === 'prepaid' ? 'glow' : ''}`}>
                <rect x="390" y="195" width="120" height="55" rx="8" className="node-rect" />
                <text x="450" y="218" textAnchor="middle" className="node-text">💳 Prepaid</text>
                <text x="450" y="237" textAnchor="middle" className="node-subtext">Agent</text>
              </g>

              {/* Dispatch */}
              <g className={`flow-g-node ${activeNode === 'dispatch' ? 'glow' : ''}`}>
                <rect x="175" y="285" width="100" height="30" rx="6" className="node-rect dispatch-rect" />
                <text x="225" y="304" textAnchor="middle" className="node-text" fill="#10b981">DISPATCH</text>
              </g>

              {/* Cancel */}
              <g className={`flow-g-node ${activeNode === 'cancel' ? 'glow' : ''}`}>
                <rect x="325" y="285" width="100" height="30" rx="6" className="node-rect cancel-rect" />
                <text x="375" y="304" textAnchor="middle" className="node-text" fill="#ef4444">CANCEL</text>
              </g>
            </svg>
          </div>

          {/* Simulation Log */}
          {simLog.length > 0 && (
            <div className="sim-log">
              <div className="sim-log-title">Simulation Log</div>
              {simLog.map((log, i) => (
                <div key={i} className="sim-log-entry" style={{animationDelay: `${i * 0.1}s`}}>
                  <span className="sim-log-step">Step {i + 1}</span>
                  <span>{log}</span>
                </div>
              ))}
              {!simRunning && simStep >= SIM_STEPS.length && (
                <div className="sim-log-entry sim-complete">
                  🎉 Simulation Complete — Order salvaged! ₹1,299 revenue protected.
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 2. Agent Performance Metrics */}
      <div className="metrics-grid">
        {Object.entries(agentMetrics).map(([key, agent]) => (
          <AgentMetricCard key={key} agentKey={key} agent={agent} renderDonut={renderDonut} />
        ))}
      </div>

      {/* 3. Bottom Analytics Row */}
      <div className="agents-bottom-row">
        <div className="glass-card" style={{padding: '1.25rem'}}>
          <h2 style={{fontSize: '1rem', marginBottom: '1rem'}}>Language Distribution</h2>
          <div style={{height: '250px'}}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={langData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={false}>
                  {langData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={{backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc'}} itemStyle={{color: '#f8fafc'}} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card" style={{padding: '1.25rem'}}>
          <h2 style={{fontSize: '1rem', marginBottom: '1rem'}}>Intervention Heatmap (Peak Hours)</h2>
          <div className="heatmap-container">
            <div></div>
            {Array.from({length: 24}).map((_, i) => (
              <div key={i} className="heatmap-header">{i}h</div>
            ))}
            
            {days.map((day, i) => (
              <React.Fragment key={day}>
                <div className="heatmap-day">{day}</div>
                {heatmapData[i].map((val, j) => (
                  <div key={`${i}-${j}`} className="heatmap-cell" style={{backgroundColor: getIntensityColor(val)}} title={`${val} sessions at ${j}:00 on ${day}`}></div>
                ))}
              </React.Fragment>
            ))}
          </div>
          <div style={{display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '0.5rem', marginTop: '0.75rem', fontSize: '0.7rem', color: 'var(--text-secondary)'}}>
            <span>Less</span>
            <div style={{width: '60px', height: '8px', background: 'linear-gradient(to right, rgba(var(--accent-primary-rgb), 0.1), rgba(var(--accent-primary-rgb), 0.9))', borderRadius: '4px'}}></div>
            <span>More</span>
          </div>
        </div>
      </div>
      
    </div>
  );
}
