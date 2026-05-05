import { useEffect, useState } from 'react';
import { getUsers, createUser } from '../services/api';

export default function Users({ toast }) {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [search, setSearch] = useState('');
    const [form, setForm] = useState({ user_id: '', interests: '', skill_level: 'beginner' });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadUsers();
    }, []);

    async function loadUsers() {
        setLoading(true);
        try {
            const data = await getUsers();
            setUsers(data);
        } catch {
            toast('Failed to load users', 'error');
        } finally {
            setLoading(false);
        }
    }

    async function handleCreate(e) {
        e.preventDefault();
        if (!form.user_id.trim()) return;
        setSubmitting(true);
        try {
            await createUser({
                user_id: form.user_id.trim(),
                interests: form.interests.split(',').map((s) => s.trim()).filter(Boolean),
                skill_level: form.skill_level,
            });
            toast('User created successfully!', 'success');
            setShowModal(false);
            setForm({ user_id: '', interests: '', skill_level: 'beginner' });
            loadUsers();
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            setSubmitting(false);
        }
    }

    const filtered = users.filter(
        (u) =>
            u.user_id.toLowerCase().includes(search.toLowerCase()) ||
            u.interests.some((i) => i.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <>
            <div className="page-header">
                <h1>Users</h1>
                <p>Manage users and their preferences</p>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
                <input
                    className="form-input"
                    placeholder="Search users by ID or interest..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    style={{ maxWidth: '400px' }}
                />
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    + Create User
                </button>
            </div>

            {loading ? (
                <div className="loading-overlay"><div className="spinner" /></div>
            ) : filtered.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">👥</div>
                    <p>{users.length === 0 ? 'No users yet. Create your first user!' : 'No matching users found.'}</p>
                    {users.length === 0 && (
                        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                            + Create User
                        </button>
                    )}
                </div>
            ) : (
                <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>User ID</th>
                                <th>Interests</th>
                                <th>Skill Level</th>
                                <th>History</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map((user) => (
                                <tr key={user.user_id}>
                                    <td style={{ fontWeight: 600 }}>{user.user_id}</td>
                                    <td>
                                        {user.interests.map((interest) => (
                                            <span key={interest} className="tag">{interest}</span>
                                        ))}
                                    </td>
                                    <td>
                                        <span className={`tag ${user.skill_level === 'beginner' ? 'green' : user.skill_level === 'intermediate' ? 'amber' : 'blue'}`}>
                                            {user.skill_level}
                                        </span>
                                    </td>
                                    <td>{user.history?.length || 0} items</td>
                                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Create New User</h2>
                            <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
                        </div>
                        <form onSubmit={handleCreate}>
                            <div className="form-group">
                                <label>User ID</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g. alice"
                                    value={form.user_id}
                                    onChange={(e) => setForm({ ...form, user_id: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Interests (comma-separated)</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g. machine-learning, python, data-science"
                                    value={form.interests}
                                    onChange={(e) => setForm({ ...form, interests: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Skill Level</label>
                                <select
                                    className="form-select"
                                    value={form.skill_level}
                                    onChange={(e) => setForm({ ...form, skill_level: e.target.value })}
                                >
                                    <option value="beginner">Beginner</option>
                                    <option value="intermediate">Intermediate</option>
                                    <option value="advanced">Advanced</option>
                                </select>
                            </div>
                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={submitting}>
                                    {submitting ? 'Creating...' : 'Create User'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
