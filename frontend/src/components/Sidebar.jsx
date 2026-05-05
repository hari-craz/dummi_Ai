import { NavLink, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { healthCheck } from '../services/api';

export default function Sidebar() {
    const [healthy, setHealthy] = useState(null);
    const location = useLocation();

    useEffect(() => {
        healthCheck()
            .then(() => setHealthy(true))
            .catch(() => setHealthy(false));

        const iv = setInterval(() => {
            healthCheck()
                .then(() => setHealthy(true))
                .catch(() => setHealthy(false));
        }, 15000);
        return () => clearInterval(iv);
    }, []);

    const links = [
        { to: '/', icon: '📊', label: 'Dashboard' },
        { to: '/users', icon: '👥', label: 'Users' },
        { to: '/content', icon: '📚', label: 'Content' },
        { to: '/recommendations', icon: '🎯', label: 'Recommendations' },
        { to: '/training', icon: '⚡', label: 'Training' },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="logo-icon">D</div>
                <span className="logo-text">Dummi AI</span>
            </div>

            <nav className="sidebar-nav">
                {links.map((link) => (
                    <NavLink
                        key={link.to}
                        to={link.to}
                        end={link.to === '/'}
                        className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                    >
                        <span className="nav-icon">{link.icon}</span>
                        <span>{link.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="health-badge">
                    <span className={`health-dot${healthy === false ? ' offline' : ''}`} />
                    <span>
                        {healthy === null ? 'Checking...' : healthy ? 'API Online' : 'API Offline'}
                    </span>
                </div>
            </div>
        </aside>
    );
}
