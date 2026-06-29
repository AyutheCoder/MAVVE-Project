import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Splash from './pages/Splash';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Orders from './pages/Orders';
import Agents from './pages/Agents';
import Conversations from './pages/Conversations';
import Settings from './pages/Settings';
import Profile from './pages/Profile';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  useEffect(() => {
    // Check Auth
    const auth = localStorage.getItem('mavveAuth');
    if (auth === 'true') {
      setIsAuthenticated(true);
    }
    setIsAuthLoading(false);

    // Apply Theme globally on load
    const savedTheme = localStorage.getItem('mavveTheme') || 'default';
    if (savedTheme === 'meesho') {
      document.documentElement.setAttribute('data-theme', 'meesho');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }, []);

  if (isAuthLoading) return null;

  // Protected Route wrapper
  const ProtectedRoute = ({ children }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    return <Layout setIsAuthenticated={setIsAuthenticated}>{children}</Layout>;
  };

  return (
    <Routes>
      <Route path="/" element={<Splash />} />
      <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
      
      {/* Protected Routes */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
      <Route path="/agents" element={<ProtectedRoute><Agents /></ProtectedRoute>} />
      <Route path="/conversations" element={<ProtectedRoute><Conversations /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      
      {/* Catch-all redirect to splash */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
