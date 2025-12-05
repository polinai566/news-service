import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { userAPI } from '../../api/index';
import './AdminUsersPage.css';

function AdminUsersPage() {
    const [users, setUsers] = useState([]);
    const [filteredUsers, setFilteredUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [currentUser, setCurrentUser] = useState(null);
    const [hasPermission, setHasPermission] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const userStr = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        
        if (!userStr || !token) {
            navigate('/login');
            return;
        }

        try {
            const user = JSON.parse(userStr);
            setCurrentUser(user);
            
            // проверка, что пользователь админ
            const tokenParts = token.split('.');
            if (tokenParts.length === 3) {
                const payload = JSON.parse(atob(tokenParts[1]));
                const userRole = payload.user_role;

                if (userRole === 'admin') {
                    setHasPermission(true);
                    fetchUsers();
                } else {
                    setHasPermission(false);
                    setLoading(false);
                }
            }
        } catch (e) {
            console.error('Ошибка при проверке прав:', e);
            setHasPermission(false);
            setLoading(false);
        }
    }, [navigate]);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await userAPI.getAllUsers();
            setUsers(response.data);
            setFilteredUsers(response.data);
            setLoading(false);
        } catch (err) {
            console.error('Ошибка загрузки пользователей:', err);
            setError('Не удалось загрузить пользователей');
            setLoading(false);
            
            if (err.response?.status === 401) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                navigate('/login');
            } else if (err.response?.status === 403) {
                setError('У вас нет прав для просмотра этой страницы');
            }
        }
    };

    const handleSearch = (e) => {
        const query = e.target.value.toLowerCase();
        setSearchQuery(query);
        
        if (!query.trim()) {
            setFilteredUsers(users);
            return;
        }
        
        const filtered = users.filter(user => 
            user.user_name.toLowerCase().includes(query) ||
            user.email.toLowerCase().includes(query) ||
            user.user_role.toLowerCase().includes(query)
        );
        
        setFilteredUsers(filtered);
    };

    const handleClearSearch = () => {
        setSearchQuery('');
        setFilteredUsers(users);
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="admin-users-container">
                <h1>Загрузка пользователей...</h1>
            </div>
        );
    }

    if (!hasPermission) {
        return (
            <div className="admin-users-container">
                <div className="permission-error">
                    <h2>Доступ запрещен</h2>
                    <p>Только администраторы могут управлять пользователями.</p>
                    <p>
                        <Link to="/">Вернуться на главную</Link>
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="admin-users-container">
            <div className="admin-header">
                <Link to="/" className="back-link">← На главную</Link>
                <h1>Управление пользователями</h1>
                <p className="admin-subtitle">
                    Всего пользователей: {users.length} | Отфильтровано: {filteredUsers.length}
                </p>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={fetchUsers} className="retry-btn">
                        Попробовать снова
                    </button>
                </div>
            )}

            <div className="search-section">
                <div className="search-box">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={handleSearch}
                        placeholder="Поиск по имени, email или роли..."
                        className="search-input"
                    />
                    {searchQuery && (
                        <button onClick={handleClearSearch} className="clear-search-btn">
                            ✕
                        </button>
                    )}
                </div>
                <button onClick={fetchUsers} className="refresh-all-btn">
                    🔄 Обновить список
                </button>
            </div>

            <div className="users-table">
                <div className="table-header">
                    <div className="table-col-id">ID</div>
                    <div className="table-col-name">Имя</div>
                    <div className="table-col-email">Email</div>
                    <div className="table-col-role">Роль</div>
                    <div className="table-col-date">Регистрация</div>
                    <div className="table-col-actions">Действия</div>
                </div>

                <div className="table-body">
                    {filteredUsers.map((user) => (
                        <div key={user.user_id} className="table-row">
                            <div className="table-col-id">#{user.user_id}</div>
                            <div className="table-col-name">
                                <div className="user-name">
                                    {user.user_name}
                                    {user.user_id === currentUser?.user_id && (
                                        <span className="current-user-badge"> (Вы)</span>
                                    )}
                                </div>
                            </div>
                            <div className="table-col-email">{user.email}</div>
                            <div className="table-col-role">
                                <span className={`role-badge role-${user.user_role}`}>
                                    {user.user_role === 'admin' ? 'Админ' : 
                                     user.user_role === 'author' ? 'Автор' : 'Пользователь'}
                                </span>
                            </div>
                            <div className="table-col-date">
                                {formatDate(user.registration_date)}
                            </div>
                            <div className="table-col-actions">
                                <Link 
                                    to={`/profile/${user.user_id}`}
                                    className="view-profile-link"
                                >
                                    Профиль
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="admin-stats">
                <div className="stat-card">
                    <div className="stat-value">{users.length}</div>
                    <div className="stat-label">Всего пользователей</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">
                        {users.filter(u => u.user_role === 'admin').length}
                    </div>
                    <div className="stat-label">Администраторов</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">
                        {users.filter(u => u.user_role === 'author').length}
                    </div>
                    <div className="stat-label">Авторов</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">
                        {users.filter(u => u.user_role === 'user').length}
                    </div>
                    <div className="stat-label">Пользователей</div>
                </div>
            </div>
        </div>
    );
}

export default AdminUsersPage;