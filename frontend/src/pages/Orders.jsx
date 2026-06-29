import React, { useState, useMemo } from 'react';
import { 
  Search, Filter, X, ChevronLeft, ChevronRight, Eye, RefreshCw, Send, 
  MapPin, Clock, MessageSquare, AlertTriangle 
} from 'lucide-react';
import './Orders.css';

// --- Mock Data Generator (100+ orders) ---
const generateMockOrders = () => {
  const statuses = ['PLACED', 'INTERCEPTED', 'VALIDATED', 'DISPATCHED', 'RTO', 'CANCELLED'];
  const agents = ['Address Agent', 'Intent Agent', 'Prepaid Agent', 'None'];
  const langs = [{c: 'hi', e: '🇮🇳'}, {c: 'mr', e: '🚩'}, {c: 'bn', e: '🐅'}, {c: 'en', e: '🇬🇧'}];
  
  const orders = [];
  for(let i=1; i<=125; i++) {
    const risk = Math.random();
    const isHighRisk = risk > 0.65;
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const lang = langs[Math.floor(Math.random() * langs.length)];
    
    orders.push({
      id: `ORD-${1000 + i}`,
      customer: `User ${i}`,
      phone: `+91 98765${Math.floor(10000 + Math.random()*90000)}`,
      language: lang,
      amount: Math.floor(200 + Math.random() * 2000),
      paymentMode: Math.random() > 0.3 ? 'COD' : 'PREPAID',
      riskScore: risk,
      status: status,
      agent: isHighRisk ? agents[Math.floor(Math.random() * 3)] : 'None',
      date: new Date(Date.now() - Math.floor(Math.random() * 10 * 86400000)).toISOString().split('T')[0],
      transcript: isHighRisk ? [
        { sender: 'agent', text: 'Hi! We received your COD order. Please confirm if you will be available to pay cash.' },
        { sender: 'user', text: 'Yes I am ready.' },
        { sender: 'agent', text: 'Great! Your order is confirmed and will be dispatched soon.' }
      ] : []
    });
  }
  return orders.sort((a, b) => new Date(b.date) - new Date(a.date));
};

const ALL_ORDERS = generateMockOrders();

export default function Orders() {
  const [orders, setOrders] = useState(ALL_ORDERS);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [paymentFilter, setPaymentFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState(0); // minimum risk
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Modal State
  const [selectedOrder, setSelectedOrder] = useState(null);

  const handleForceDispatch = (orderId) => {
    setOrders(prevOrders => 
      prevOrders.map(order => 
        order.id === orderId 
          ? { ...order, status: 'DISPATCHED' } 
          : order
      )
    );
  };

  // Filter Logic
  const filteredOrders = useMemo(() => {
    return orders.filter(o => {
      const matchSearch = o.id.toLowerCase().includes(searchTerm.toLowerCase()) || o.phone.includes(searchTerm);
      const matchStatus = statusFilter === 'All' || o.status === statusFilter;
      const matchPayment = paymentFilter === 'All' || o.paymentMode === paymentFilter;
      const matchRisk = o.riskScore >= riskFilter;
      return matchSearch && matchStatus && matchPayment && matchRisk;
    });
  }, [orders, searchTerm, statusFilter, paymentFilter, riskFilter]);

  // Pagination Logic
  const totalPages = Math.ceil(filteredOrders.length / itemsPerPage);
  const currentData = filteredOrders.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const getRiskColor = (score) => {
    if(score < 0.4) return '#10b981'; // Green
    if(score < 0.65) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  return (
    <div className="orders-page">
      
      {/* Filter Bar */}
      <div className="filter-bar glass-card">
        <div className="filter-group" style={{flex: 1, minWidth: '250px'}}>
          <Search size={18} className="search-icon" style={{position: 'absolute', marginLeft: '10px', color: 'var(--text-muted)'}} />
          <input 
            type="text" 
            className="filter-input" 
            placeholder="Search Order ID or Phone..." 
            style={{paddingLeft: '35px', width: '100%'}}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="filter-group">
          <span className="filter-label">Status:</span>
          <select className="filter-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option>All</option>
            <option>PLACED</option>
            <option>INTERCEPTED</option>
            <option>VALIDATED</option>
            <option>DISPATCHED</option>
            <option>RTO</option>
            <option>CANCELLED</option>
          </select>
        </div>

        <div className="filter-group">
          <span className="filter-label">Payment:</span>
          <select className="filter-select" value={paymentFilter} onChange={(e) => setPaymentFilter(e.target.value)}>
            <option>All</option>
            <option>COD</option>
            <option>PREPAID</option>
          </select>
        </div>

        <div className="filter-group">
          <span className="filter-label">Min Risk: {(riskFilter * 100).toFixed(0)}%</span>
          <input 
            type="range" 
            min="0" max="1" step="0.05" 
            value={riskFilter}
            onChange={(e) => setRiskFilter(parseFloat(e.target.value))}
            style={{width: '100px'}}
          />
        </div>
      </div>

      {/* Orders Table */}
      <div className="glass-card table-container">
        <table className="orders-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Payment</th>
              <th>Risk Score</th>
              <th>Status</th>
              <th>Agent</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentData.map((order) => (
              <tr key={order.id}>
                <td style={{fontWeight: '500', color: 'var(--accent-primary)', cursor: 'pointer'}} onClick={() => setSelectedOrder(order)}>
                  {order.id}
                </td>
                <td>
                  <div>{order.customer} {order.language.e}</div>
                  <div style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>{order.phone}</div>
                </td>
                <td>₹{order.amount}</td>
                <td>
                  <span className={`badge ${order.paymentMode === 'COD' ? 'badge-warning' : 'badge-success'}`}>
                    {order.paymentMode}
                  </span>
                </td>
                <td>
                  <div className="risk-val-text" style={{color: getRiskColor(order.riskScore)}}>
                    {(order.riskScore * 100).toFixed(1)}%
                  </div>
                  <div className="risk-bar-container">
                    <div 
                      className="risk-bar-fill" 
                      style={{width: `${order.riskScore * 100}%`, backgroundColor: getRiskColor(order.riskScore)}}
                    ></div>
                  </div>
                </td>
                <td>
                  <span className={`badge ${
                    ['VALIDATED', 'DISPATCHED'].includes(order.status) ? 'badge-success' :
                    order.status === 'RTO' || order.status === 'CANCELLED' ? 'badge-danger' :
                    order.status === 'INTERCEPTED' ? 'badge-warning' : 'badge-info'
                  }`}>
                    {order.status}
                  </span>
                </td>
                <td>{order.agent}</td>
                <td>
                  <div className="action-btns">
                    <button className="btn-icon" onClick={() => setSelectedOrder(order)} title="View Details">
                      <Eye size={18} />
                    </button>
                    {order.status === 'INTERCEPTED' && (
                      <button 
                        className="btn-icon" 
                        title="Force Dispatch"
                        onClick={() => handleForceDispatch(order.id)}
                      >
                        <Send size={18} color="#10b981" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {currentData.length === 0 && (
              <tr><td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>No orders found matching filters.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination">
        <span style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
          Showing {(currentPage-1)*itemsPerPage + 1} to {Math.min(currentPage*itemsPerPage, filteredOrders.length)} of {filteredOrders.length} orders
        </span>
        <div className="page-controls">
          <button 
            className="page-btn" 
            disabled={currentPage === 1} 
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
          >
            <ChevronLeft size={16} />
          </button>
          <span style={{padding: '0.5rem 1rem', fontSize: '0.875rem'}}>{currentPage} / {totalPages || 1}</span>
          <button 
            className="page-btn" 
            disabled={currentPage === totalPages || totalPages === 0} 
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Slide-over Modal */}
      {selectedOrder && (
        <div className="modal-overlay" onClick={() => setSelectedOrder(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 style={{fontSize: '1.25rem'}}>Order {selectedOrder.id}</h2>
              <button className="btn-icon" onClick={() => setSelectedOrder(null)}><X size={20}/></button>
            </div>
            
            <div className="modal-body">
              {/* Summary */}
              <div>
                <div className="section-title">Customer Summary</div>
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem'}}>
                  <div><span style={{color: 'var(--text-muted)'}}>Name:</span> {selectedOrder.customer}</div>
                  <div><span style={{color: 'var(--text-muted)'}}>Phone:</span> {selectedOrder.phone}</div>
                  <div><span style={{color: 'var(--text-muted)'}}>Language:</span> {selectedOrder.language.e} {selectedOrder.language.c.toUpperCase()}</div>
                  <div><span style={{color: 'var(--text-muted)'}}>Payment:</span> {selectedOrder.paymentMode}</div>
                </div>
              </div>

              {/* Risk Breakdown */}
              <div>
                <div className="section-title">Risk Analysis</div>
                <div style={{display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem'}}>
                  <AlertTriangle color={getRiskColor(selectedOrder.riskScore)} size={24} />
                  <span style={{fontSize: '1.5rem', fontWeight: 'bold', color: getRiskColor(selectedOrder.riskScore)}}>
                    {(selectedOrder.riskScore * 100).toFixed(1)}% RTO Risk
                  </span>
                </div>
                {selectedOrder.riskScore > 0.65 && (
                  <ul style={{fontSize: '0.875rem', color: 'var(--text-secondary)', paddingLeft: '1.5rem'}}>
                    <li>High historical RTO rate in pincode</li>
                    <li>Address formatting anomaly detected</li>
                  </ul>
                )}
              </div>

              {/* Address Comparison */}
              {selectedOrder.agent === 'Address Agent' && (
                <div>
                  <div className="section-title">Address Verification</div>
                  <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem'}}>
                    <div style={{background: 'rgba(239, 68, 68, 0.1)', padding: '0.75rem', borderRadius: '4px'}}>
                      <span style={{color: '#ef4444', fontWeight: 'bold'}}>Original:</span> Demo Address Missing details, near tree
                    </div>
                    <div style={{background: 'rgba(16, 185, 129, 0.1)', padding: '0.75rem', borderRadius: '4px'}}>
                      <span style={{color: '#10b981', fontWeight: 'bold'}}>Resolved:</span> House No 42, Green Tree Lane, Behind Main Temple, Pune 411001
                    </div>
                  </div>
                </div>
              )}

              {/* Chat Transcript */}
              <div style={{flex: 1, display: 'flex', flexDirection: 'column'}}>
                <div className="section-title">MAVVE Agent Transcript</div>
                {selectedOrder.transcript.length > 0 ? (
                  <div className="chat-container" style={{flex: 1}}>
                    {selectedOrder.transcript.map((msg, i) => (
                      <div key={i} className={`chat-bubble ${msg.sender}`}>
                        {msg.text}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>
                    No agent interaction recorded.
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>
      )}
      
    </div>
  );
}
