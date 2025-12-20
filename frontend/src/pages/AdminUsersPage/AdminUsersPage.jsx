import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { userAPI, newsAPI, commentAPI } from '../../api/index.js';
import './AdminUsersPage.css';

function AdminUsersPage() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [stats, setStats] = useState({ users: 0, news: 0, comments: 0 });

    useEffect(() => {
        async function fetchAll() {
            try {
                setLoading(true);
                setError('');
                const usersRes = await userAPI.getAllUsers();
                setUsers(usersRes.data);
                const newsRes = await newsAPI.getNewsList();
                const commentsArr = await Promise.all(
                  newsRes.data.map(news => commentAPI.getCommentsByNews(news.news_id))
                );
                setStats({
                    users: usersRes.data.length,
                    news: newsRes.data.length,
                    comments: commentsArr.reduce((acc, res) => acc + res.data.length, 0)
                });
            } catch (e) {
                setError('Не удалось загрузить пользователей или статистику');
            } finally {
                setLoading(false);
            }
        }
        fetchAll();
    }, []);

    const handleDelete = async (userId) => {
        if (!window.confirm('Удалить пользователя?')) return;
        try {
            await userAPI.deleteUser(userId);
            setUsers(users => users.filter(u => u.user_id !== userId));
            setStats(s => ({ ...s, users: s.users - 1 }));
        } catch (e) {
            alert('Ошибка удаления пользователя');
        }
    };

    const renderRole = (role) => {
        switch (role) {
            case 'admin': return '👑 Администратор';
            case 'author': return '✍️ Автор';
            case 'user': return '👤 Пользователь';
            default: return role;
        }
    };

    return (
        <div className="admin-users-container">
            <h1 className="admin-users-title">Управление пользователями</h1>
            
            <div className="admin-users-stats">
                <strong>Статистика:</strong>
                <ul>
                    <li>Пользователей: {stats.users}</li>
                    <li>Новостей: {stats.news}</li>
                    <li>Комментариев: {stats.comments}</li>
                </ul>
            </div>
            
            {loading ? (
                <div className="admin-loading">Загрузка...</div>
            ) : error ? (
                <div className="admin-error" style={{ color: 'red' }}>{error}</div>
            ) : (
                <table className="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Имя</th>
                            <th>Роль</th>
                            <th>Дата регистрации</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(u => (
                            <tr key={u.user_id}>
                                <td>{u.user_id}</td>
                                <td>{u.user_name}</td>
                                <td>
                                    <span className="admin-user-role">
                                        {renderRole(u.user_role)}
                                    </span>
                                </td>
                                <td>
                                    {new Date(u.registration_date).toLocaleDateString('ru-RU')}
                                </td>
                                <td>
                                    <div className="admin-actions">
                                        <Link 
                                            to={`/profile/${u.user_id}`}
                                            className="admin-profile-btn"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            👤 Профиль
                                        </Link>
                                        <button 
                                            className="admin-delete-btn" 
                                            onClick={() => handleDelete(u.user_id)}
                                        >
                                            🗑️ Удалить
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default AdminUsersPage;