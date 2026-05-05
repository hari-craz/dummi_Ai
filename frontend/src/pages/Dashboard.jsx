import { useEffect, useState } from 'react';
import { getUsers, getContent, getTrainingStatus, healthCheck } from '../services/api';

export default function Dashboard({ toast }) {
    const [stats, setStats] = useState({ users: 0, content: 0, health: null, training: null });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
    }, []);

    async function loadStats() {
        setLoading(true);
        try {
            const [users, content, health] = await Promise.all([
                getUsers().catch(() => []),
                getContent().catch(() => []),
                healthCheck().catch(() => null),
            ]);

            let training = null;
            try {
                training = await getTrainingStatus();
            } catch { }

            setStats({
                users: users.length,
                content: content.length,
                health: health ? 'healthy' : 'offline',
                training,
            });
        } catch (err) {
            toast('Failed to load dashboard stats', 'error');
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="spinner" />
            </div>
        );
    }

    const cfTrained = stats.training?.cf_model?.trained;
    const vectorCount = stats.training?.vector_db?.total_vectors || 0;

    return (
        <>
            <div className="page-header">
                <h1>Dashboard</h1>
                <p>Overview of your Dummi AI recommendation system</p>
            </div>

            <div className="stats-grid">
                <div className="stat-card purple">
                    <div className="stat-icon">👥</div>
                    <div className="stat-value">{stats.users}</div>
                    <div className="stat-label">Total Users</div>
                </div>

                <div className="stat-card green">
                    <div className="stat-icon">📚</div>
                    <div className="stat-value">{stats.content}</div>
                    <div className="stat-label">Content Items</div>
                </div>

                <div className="stat-card amber">
                    <div className="stat-icon">🧠</div>
                    <div className="stat-value">{vectorCount}</div>
                    <div className="stat-label">Embeddings</div>
                </div>

                <div className="stat-card blue">
                    <div className="stat-icon">⚡</div>
                    <div className="stat-value">{cfTrained ? 'Yes' : 'No'}</div>
                    <div className="stat-label">CF Model Trained</div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                <div className="glass-card">
                    <h3 style={{ marginBottom: '16px', fontWeight: 600 }}>System Health</h3>
                    <div className="status-item">
                        <span className="status-label">API Server</span>
                        <span className={`badge badge-${stats.health === 'healthy' ? 'success' : 'error'}`}>
                            {stats.health === 'healthy' ? '● Online' : '● Offline'}
                        </span>
                    </div>
                    <div className="status-item">
                        <span className="status-label">Database</span>
                        <span className={`badge badge-${stats.users >= 0 ? 'success' : 'error'}`}>
                            ● Connected
                        </span>
                    </div>
                    <div className="status-item">
                        <span className="status-label">Vector DB</span>
                        <span className={`badge badge-${vectorCount > 0 ? 'success' : 'warning'}`}>
                            {vectorCount > 0 ? '● Active' : '○ Empty'}
                        </span>
                    </div>
                </div>

                <div className="glass-card">
                    <h3 style={{ marginBottom: '16px', fontWeight: 600 }}>Quick Actions</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <a href="/users" className="btn btn-secondary" style={{ justifyContent: 'center' }}>
                            👥 Manage Users
                        </a>
                        <a href="/content" className="btn btn-secondary" style={{ justifyContent: 'center' }}>
                            📚 Manage Content
                        </a>
                        <a href="/recommendations" className="btn btn-primary" style={{ justifyContent: 'center' }}>
                            🎯 Get Recommendations
                        </a>
                        <a href="/training" className="btn btn-secondary" style={{ justifyContent: 'center' }}>
                            ⚡ Train Models
                        </a>
                    </div>
                </div>
            </div>

            {stats.training?.cf_model && (
                <div className="glass-card" style={{ marginTop: '24px' }}>
                    <h3 style={{ marginBottom: '16px', fontWeight: 600 }}>Model Info</h3>
                    <div className="status-item">
                        <span className="status-label">Last Trained</span>
                        <span className="status-value">
                            {stats.training.cf_model.trained_at
                                ? new Date(stats.training.cf_model.trained_at).toLocaleString()
                                : 'Never'}
                        </span>
                    </div>
                    <div className="status-item">
                        <span className="status-label">Users in model</span>
                        <span className="status-value">{stats.training.cf_model.n_users}</span>
                    </div>
                    <div className="status-item">
                        <span className="status-label">Items in model</span>
                        <span className="status-value">{stats.training.cf_model.n_items}</span>
                    </div>
                    {stats.training.cf_model.rmse && (
                        <div className="status-item">
                            <span className="status-label">RMSE</span>
                            <span className="status-value">{stats.training.cf_model.rmse.toFixed(4)}</span>
                        </div>
                    )}
                </div>
            )}
        </>
    );
}
