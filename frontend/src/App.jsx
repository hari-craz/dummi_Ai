import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Content from './pages/Content';
import Recommendations from './pages/Recommendations';
import Training from './pages/Training';
import { useState, useCallback } from 'react';

function ToastContainer({ toasts, onRemove }) {
  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.type}`} onClick={() => onRemove(t.id)}>
          <span>{t.type === 'success' ? '✓' : t.type === 'error' ? '✕' : 'ℹ'}</span>
          <span>{t.message}</span>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard toast={addToast} />} />
            <Route path="/users" element={<Users toast={addToast} />} />
            <Route path="/content" element={<Content toast={addToast} />} />
            <Route path="/recommendations" element={<Recommendations toast={addToast} />} />
            <Route path="/training" element={<Training toast={addToast} />} />
          </Routes>
        </main>
        <ToastContainer toasts={toasts} onRemove={removeToast} />
      </div>
    </BrowserRouter>
  );
}
