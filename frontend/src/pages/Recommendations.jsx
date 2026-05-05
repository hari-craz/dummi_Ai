import { useEffect, useState } from 'react';
import { getUsers, getRecommendations, submitFeedback } from '../services/api';

export default function Recommendations({ toast }) {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState('');
    const [useCf, setUseCf] = useState(true);
    const [useEmbeddings, setUseEmbeddings] = useState(true);
    const [cfWeight, setCfWeight] = useState(0.5);
    const [nRecs, setNRecs] = useState(10);
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(false);
    const [feedbackSent, setFeedbackSent] = useState({});

    useEffect(() => {
        getUsers()
            .then(setUsers)
            .catch(() => toast('Failed to load users', 'error'));
    }, []);

    async function fetchRecs() {
        if (!selectedUser) {
            toast('Please select a user', 'error');
            return;
        }
        setLoading(true);
        setFeedbackSent({});
        try {
            const data = await getRecommendations({
                user_id: selectedUser,
                n_recommendations: nRecs,
                use_cf: useCf,
                use_embeddings: useEmbeddings,
                cf_weight: cfWeight,
            });
            setRecommendations(data);
            toast(`Got ${data.recommendations.length} recommendations`, 'success');
        } catch (err) {
            toast(err.message, 'error');
            setRecommendations(null);
        } finally {
            setLoading(false);
        }
    }

    async function handleFeedback(contentId, type) {
        try {
            await submitFeedback({
                user_id: selectedUser,
                content_id: contentId,
                feedback_type: type,
            });
            setFeedbackSent((prev) => ({ ...prev, [contentId]: type }));
            toast(`Feedback "${type}" recorded`, 'success');
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    return (
        <>
            <div className="page-header">
                <h1>Recommendations</h1>
                <p>Get personalized content recommendations for any user</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '24px' }}>
                {/* Controls Panel */}
                <div className="glass-card" style={{ height: 'fit-content' }}>
                    <h3 style={{ marginBottom: '20px', fontWeight: 600 }}>Settings</h3>

                    <div className="form-group">
                        <label>Select User</label>
                        <select
                            className="form-select"
                            value={selectedUser}
                            onChange={(e) => setSelectedUser(e.target.value)}
                        >
                            <option value="">-- Choose user --</option>
                            {users.map((u) => (
                                <option key={u.user_id} value={u.user_id}>
                                    {u.user_id} ({u.skill_level})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Number of Recommendations</label>
                        <div className="slider-group">
                            <input
                                type="range"
                                min="1"
                                max="20"
                                value={nRecs}
                                onChange={(e) => setNRecs(Number(e.target.value))}
                            />
                            <span className="slider-value">{nRecs}</span>
                        </div>
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                        <div className="toggle-row">
                            <label>Use Collaborative Filtering</label>
                            <label className="toggle">
                                <input type="checkbox" checked={useCf} onChange={(e) => setUseCf(e.target.checked)} />
                                <span className="toggle-slider" />
                            </label>
                        </div>
                        <div className="toggle-row">
                            <label>Use Embeddings</label>
                            <label className="toggle">
                                <input type="checkbox" checked={useEmbeddings} onChange={(e) => setUseEmbeddings(e.target.checked)} />
                                <span className="toggle-slider" />
                            </label>
                        </div>
                    </div>

                    {useCf && useEmbeddings && (
                        <div className="form-group">
                            <label>CF Weight ({(cfWeight * 100).toFixed(0)}% CF / {((1 - cfWeight) * 100).toFixed(0)}% Emb)</label>
                            <div className="slider-group">
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.05"
                                    value={cfWeight}
                                    onChange={(e) => setCfWeight(Number(e.target.value))}
                                />
                                <span className="slider-value">{cfWeight.toFixed(2)}</span>
                            </div>
                        </div>
                    )}

                    <button
                        className="btn btn-primary btn-lg"
                        style={{ width: '100%', justifyContent: 'center', marginTop: '8px' }}
                        onClick={fetchRecs}
                        disabled={loading || !selectedUser}
                    >
                        {loading ? (
                            <><div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Getting...</>
                        ) : (
                            '🎯 Get Recommendations'
                        )}
                    </button>
                </div>

                {/* Results Panel */}
                <div>
                    {recommendations === null ? (
                        <div className="empty-state glass-card">
                            <div className="empty-icon">🎯</div>
                            <p>Select a user and click "Get Recommendations" to see personalized content suggestions</p>
                        </div>
                    ) : recommendations.recommendations.length === 0 ? (
                        <div className="empty-state glass-card">
                            <div className="empty-icon">🤷</div>
                            <p>No recommendations found. Try training models first or add more content.</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                                <h3 style={{ fontWeight: 600 }}>
                                    Results for <span style={{ color: 'var(--accent-primary-hover)' }}>{recommendations.user_id}</span>
                                </h3>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                    {recommendations.recommendations.length} items
                                </span>
                            </div>
                            {recommendations.recommendations.map((rec, idx) => (
                                <div key={rec.content_id} className="rec-card">
                                    <div className="rec-rank">{idx + 1}</div>
                                    <div className="rec-info">
                                        <h4>{rec.title || rec.content_id}</h4>
                                        <div className="rec-meta">
                                            {rec.category && <span className="tag green">{rec.category}</span>}
                                            {rec.method && <span className="tag blue">{rec.method}</span>}
                                            <span className="rec-score" style={{ color: 'var(--accent-amber)' }}>
                                                Score: {typeof rec.score === 'number' ? rec.score.toFixed(3) : rec.score}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="rec-actions">
                                        {feedbackSent[rec.content_id] ? (
                                            <span className={`tag ${feedbackSent[rec.content_id] === 'positive' ? 'green' : 'red'}`}>
                                                {feedbackSent[rec.content_id] === 'positive' ? '👍 Liked' : '👎 Disliked'}
                                            </span>
                                        ) : (
                                            <>
                                                <button
                                                    className="feedback-btn like"
                                                    title="Like"
                                                    onClick={() => handleFeedback(rec.content_id, 'positive')}
                                                >
                                                    👍
                                                </button>
                                                <button
                                                    className="feedback-btn dislike"
                                                    title="Dislike"
                                                    onClick={() => handleFeedback(rec.content_id, 'negative')}
                                                >
                                                    👎
                                                </button>
                                            </>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}