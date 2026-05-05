import { useEffect, useState } from 'react';
import { trainModels, getTrainingStatus } from '../services/api';

export default function Training({ toast }) {
    const [retrainCf, setRetrainCf] = useState(true);
    const [regenEmbeddings, setRegenEmbeddings] = useState(false);
    const [training, setTraining] = useState(false);
    const [status, setStatus] = useState(null);
    const [result, setResult] = useState(null);
    const [loadingStatus, setLoadingStatus] = useState(true);

    useEffect(() => {
        loadStatus();
    }, []);

    async function loadStatus() {
        setLoadingStatus(true);
        try {
            const data = await getTrainingStatus();
            setStatus(data);
        } catch {
            toast('Failed to load training status', 'error');
        } finally {
            setLoadingStatus(false);
        }
    }

    async function handleTrain() {
        if (!retrainCf && !regenEmbeddings) {
            toast('Select at least one training option', 'error');
            return;
        }
        setTraining(true);
        setResult(null);
        try {
            const res = await trainModels({
                retrain_cf: retrainCf,
                regenerate_embeddings: regenEmbeddings,
            });
            setResult(res);
            toast('Training completed!', 'success');
            loadStatus();
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            setTraining(false);
        }
    }

    return (
        <>
            <div className="page-header">
                <h1>Training</h1>
                <p>Train ML models and monitor system status</p>
            </div>

            <div className="training-panel">
                {/* Controls */}
                <div className="training-controls">
                    <h3 style={{ marginBottom: '24px', fontWeight: 600 }}>Train Models</h3>

                    <div className="toggle-row" style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '16px' }}>
                        <div>
                            <label style={{ fontWeight: 500 }}>Retrain Collaborative Filtering</label>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '4px' }}>
                                Update user-item matrix factorization model
                            </p>
                        </div>
                        <label className="toggle">
                            <input type="checkbox" checked={retrainCf} onChange={(e) => setRetrainCf(e.target.checked)} />
                            <span className="toggle-slider" />
                        </label>
                    </div>

                    <div className="toggle-row" style={{ paddingTop: '16px' }}>
                        <div>
                            <label style={{ fontWeight: 500 }}>Regenerate Embeddings</label>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '4px' }}>
                                Re-encode all content with Sentence Transformers
                            </p>
                        </div>
                        <label className="toggle">
                            <input type="checkbox" checked={regenEmbeddings} onChange={(e) => setRegenEmbeddings(e.target.checked)} />
                            <span className="toggle-slider" />
                        </label>
                    </div>

                    <button
                        className="btn btn-primary btn-lg"
                        style={{ width: '100%', justifyContent: 'center', marginTop: '32px' }}
                        onClick={handleTrain}
                        disabled={training}
                    >
                        {training ? (
                            <><div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Training...</>
                        ) : (
                            '⚡ Start Training'
                        )}
                    </button>

                    {result && (
                        <div style={{ marginTop: '24px', padding: '20px', background: 'var(--accent-green-bg)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(52, 211, 153, 0.2)' }}>
                            <h4 style={{ color: 'var(--accent-green)', marginBottom: '12px' }}>✓ Training Complete</h4>
                            <div className="status-item">
                                <span className="status-label">Status</span>
                                <span className="status-value" style={{ color: 'var(--accent-green)' }}>{result.status}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Embeddings Generated</span>
                                <span className="status-value">{result.embeddings_generated}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">CF Model Trained</span>
                                <span className="status-value">{result.cf_model_trained ? 'Yes' : 'No'}</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Status */}
                <div className="training-status">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                        <h3 style={{ fontWeight: 600 }}>Current Status</h3>
                        <button className="btn btn-ghost btn-sm" onClick={loadStatus} disabled={loadingStatus}>
                            ↻ Refresh
                        </button>
                    </div>

                    {loadingStatus ? (
                        <div className="loading-overlay" style={{ padding: '40px' }}><div className="spinner" /></div>
                    ) : status ? (
                        <>
                            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '12px' }}>
                                Vector Database
                            </h4>
                            <div className="status-item">
                                <span className="status-label">Total Vectors</span>
                                <span className="status-value">{status.vector_db?.total_vectors ?? 0}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Dimension</span>
                                <span className="status-value">{status.vector_db?.dimension ?? 384}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Index Trained</span>
                                <span className="status-value">
                                    <span className={`badge badge-${status.vector_db?.is_trained ? 'success' : 'warning'}`}>
                                        {status.vector_db?.is_trained ? '● Trained' : '○ Not Trained'}
                                    </span>
                                </span>
                            </div>

                            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '12px', marginTop: '24px' }}>
                                Collaborative Filtering
                            </h4>
                            <div className="status-item">
                                <span className="status-label">Model Trained</span>
                                <span className="status-value">
                                    <span className={`badge badge-${status.cf_model?.trained ? 'success' : 'warning'}`}>
                                        {status.cf_model?.trained ? '● Yes' : '○ No'}
                                    </span>
                                </span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Users in Model</span>
                                <span className="status-value">{status.cf_model?.n_users ?? 0}</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">Items in Model</span>
                                <span className="status-value">{status.cf_model?.n_items ?? 0}</span>
                            </div>
                            {status.cf_model?.trained_at && (
                                <div className="status-item">
                                    <span className="status-label">Last Trained</span>
                                    <span className="status-value" style={{ fontSize: '0.85rem' }}>
                                        {new Date(status.cf_model.trained_at).toLocaleString()}
                                    </span>
                                </div>
                            )}
                            {status.cf_model?.rmse && (
                                <div className="status-item">
                                    <span className="status-label">RMSE</span>
                                    <span className="status-value">{status.cf_model.rmse.toFixed(4)}</span>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="empty-state">
                            <p>Could not load training status</p>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
