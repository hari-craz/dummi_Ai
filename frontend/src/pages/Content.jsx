import { useEffect, useState } from 'react';
import { getContent, createContent, getContentByCategory } from '../services/api';

export default function Content({ toast }) {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [activeTab, setActiveTab] = useState('all');
    const [categories, setCategories] = useState([]);
    const [form, setForm] = useState({
        content_id: '', title: '', category: '', tags: '', description: '',
    });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadContent();
    }, []);

    async function loadContent() {
        setLoading(true);
        try {
            const data = await getContent();
            setItems(data);
            const cats = [...new Set(data.map((c) => c.category).filter(Boolean))];
            setCategories(cats);
        } catch {
            toast('Failed to load content', 'error');
        } finally {
            setLoading(false);
        }
    }

    async function handleTabChange(cat) {
        setActiveTab(cat);
        if (cat === 'all') {
            loadContent();
            return;
        }
        setLoading(true);
        try {
            const data = await getContentByCategory(cat);
            setItems(data);
        } catch {
            toast('Failed to filter content', 'error');
        } finally {
            setLoading(false);
        }
    }

    async function handleCreate(e) {
        e.preventDefault();
        if (!form.content_id.trim() || !form.title.trim()) return;
        setSubmitting(true);
        try {
            await createContent({
                content_id: form.content_id.trim(),
                title: form.title.trim(),
                category: form.category.trim(),
                tags: form.tags.split(',').map((s) => s.trim()).filter(Boolean),
                description: form.description.trim() || null,
            });
            toast('Content created!', 'success');
            setShowModal(false);
            setForm({ content_id: '', title: '', category: '', tags: '', description: '' });
            setActiveTab('all');
            loadContent();
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <>
            <div className="page-header">
                <h1>Content</h1>
                <p>Browse and manage content items for recommendations</p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div className="tabs">
                    <button className={`tab${activeTab === 'all' ? ' active' : ''}`} onClick={() => handleTabChange('all')}>
                        All
                    </button>
                    {categories.map((cat) => (
                        <button key={cat} className={`tab${activeTab === cat ? ' active' : ''}`} onClick={() => handleTabChange(cat)}>
                            {cat}
                        </button>
                    ))}
                </div>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Content</button>
            </div>

            {loading ? (
                <div className="loading-overlay"><div className="spinner" /></div>
            ) : items.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📚</div>
                    <p>No content found. Add your first content item!</p>
                    <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Content</button>
                </div>
            ) : (
                <div className="content-grid">
                    {items.map((item) => (
                        <div key={item.content_id} className="content-card">
                            <h3>{item.title}</h3>
                            {item.description && <div className="card-desc">{item.description}</div>}
                            <div style={{ marginBottom: '12px' }}>
                                {item.tags?.map((tag) => (
                                    <span key={tag} className="tag">{tag}</span>
                                ))}
                            </div>
                            <div className="card-footer">
                                <span className="tag green">{item.category}</span>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    {item.content_id}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Add New Content</h2>
                            <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
                        </div>
                        <form onSubmit={handleCreate}>
                            <div className="form-group">
                                <label>Content ID</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g. tut-ml-001"
                                    value={form.content_id}
                                    onChange={(e) => setForm({ ...form, content_id: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Title</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g. Introduction to Machine Learning"
                                    value={form.title}
                                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Category</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g. machine-learning"
                                    value={form.category}
                                    onChange={(e) => setForm({ ...form, category: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Tags (comma-separated)</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g. beginner, tutorial, python"
                                    value={form.tags}
                                    onChange={(e) => setForm({ ...form, tags: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    className="form-textarea"
                                    placeholder="Describe this content..."
                                    value={form.description}
                                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                                />
                            </div>
                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={submitting}>
                                    {submitting ? 'Creating...' : 'Add Content'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
