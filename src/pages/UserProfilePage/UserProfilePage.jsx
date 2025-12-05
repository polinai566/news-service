import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { userAPI, authAPI } from '../../api/index';
import './UserProfilePage.css';

function UserProfilePage() {
    const { userId } = useParams();
    const navigate = useNavigate();
    
    const [profileUser, setProfileUser] = useState(null);
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [editForm, setEditForm] = useState({
        user_name: '',
        email: '',
        user_role: 'user',
        avatar: '',
        password: ''
    });
    const [sessions, setSessions] = useState([]);
    const [showSessions, setShowSessions] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                
                // загрузка текущего пользователя
                const userStr = localStorage.getItem('user');
                const token = localStorage.getItem('token');
                
                if (!userStr || !token) {
                    navigate('/login');
                    return;
                }
                
                const currentUserData = JSON.parse(userStr);
                setCurrentUser(currentUserData);
                
                // определение профиля для загрузки
                let targetUserId;
                if (userId) {
                    // проверка прав: админ может смотреть любой профиль
                    if (currentUserData.user_role !== 'admin' && currentUserData.user_id !== parseInt(userId)) {
                        setError('У вас нет прав для просмотра этого профиля');
                        setLoading(false);
                        return;
                    }
                    targetUserId = parseInt(userId);
                } else {
                    // если userId не указан, показываем профиль текущего пользователя
                    targetUserId = currentUserData.user_id;
                }
                
                // загрзка данных профиля
                const response = await userAPI.getUserById(targetUserId);
                setProfileUser(response.data);
                
                // заполнение формы редактирования
                setEditForm({
                    user_name: response.data.user_name || '',
                    email: response.data.email || '',
                    user_role: response.data.user_role || 'user',
                    avatar: response.data.avatar || '',
                    password: ''
                });
                
                // загрузка сессии пользователя (только для админа или самого пользователя)
                if (currentUserData.user_role === 'admin' || currentUserData.user_id === targetUserId) {
                    try {
                        const sessionsResponse = await authAPI.getUserSessions(targetUserId);
                        setSessions(sessionsResponse.data || []);
                    } catch (sessionsErr) {
                        console.warn('Не удалось загрузить сессии:', sessionsErr);
                    }
                }
                
                setLoading(false);
            } catch (err) {
                console.error('Ошибка загрузки профиля:', err);
                
                if (err.response?.status === 401) {
                    setError('Сессия истекла. Пожалуйста, войдите снова.');
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    setTimeout(() => navigate('/login'), 2000);
                } else if (err.response?.status === 403) {
                    setError('У вас нет прав для просмотра этого профиля');
                } else if (err.response?.status === 404) {
                    setError('Пользователь не найден');
                } else {
                    setError('Не удалось загрузить профиль');
                }
                
                setLoading(false);
            }
        };
        
        loadData();
    }, [userId, navigate]);

    const handleEditChange = (e) => {
        const { name, value } = e.target;
        setEditForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSaveProfile = async () => {
        if (!editForm.user_name.trim() || !editForm.email.trim()) {
            setError('Имя и email обязательны для заполнения');
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            const targetUserId = userId ? parseInt(userId) : currentUser.user_id;
            
            // подготовка данных для отправки
            const updateData = {
                user_name: editForm.user_name.trim(),
                email: editForm.email.trim(),
                avatar: editForm.avatar.trim() || null
            };
            
            // только админ может менять роль
            if (currentUser.user_role === 'admin') {
                updateData.user_role = editForm.user_role;
            }
            
            // если указан пароль, добавляем его
            if (editForm.password.trim()) {
                updateData.password = editForm.password.trim();
            }
            
            const response = await userAPI.updateUser(targetUserId, updateData);
            
            // обновляем данные профиля
            setProfileUser(response.data);
            
            // если это профиль текущего пользователя, обновляем данные в localStorage
            if (!userId || targetUserId === currentUser.user_id) {
                const updatedUser = {
                    ...currentUser,
                    user_name: response.data.user_name,
                    email: response.data.email,
                    user_role: response.data.user_role,
                    avatar: response.data.avatar
                };
                localStorage.setItem('user', JSON.stringify(updatedUser));
                setCurrentUser(updatedUser);
            }
            
            setIsEditing(false);
            setEditForm(prev => ({ ...prev, password: '' })); // очистка поля пароля
            
            alert('Профиль успешно обновлен!');
        } catch (err) {
            console.error('Ошибка обновления профиля:', err);
            
            if (err.response?.status === 401) {
                setError('Сессия истекла. Пожалуйста, войдите снова.');
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                setTimeout(() => navigate('/login'), 2000);
            } else if (err.response?.status === 400) {
                setError('Некорректные данные: ' + (err.response.data?.detail || ''));
            } else if (err.response?.status === 403) {
                setError('У вас нет прав для редактирования этого профиля');
            } else {
                setError('Не удалось обновить профиль');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteUser = async () => {
        if (!window.confirm('Вы уверены, что хотите удалить этого пользователя? Это действие нельзя отменить.')) {
            return;
        }

        try {
            const targetUserId = userId ? parseInt(userId) : currentUser.user_id;
            await userAPI.deleteUser(targetUserId);
            
            alert('Пользователь успешно удален');
            
            // если удаляем себя, выходим из системы
            if (!userId || targetUserId === currentUser.user_id) {
                handleLogout();
            } else {
                // если удаляем другого пользователя, возвращаемся на главную
                navigate('/');
            }
        } catch (err) {
            console.error('Ошибка удаления пользователя:', err);
            
            if (err.response?.status === 401) {
                setError('Сессия истекла. Пожалуйста, войдите снова.');
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                setTimeout(() => navigate('/login'), 2000);
            } else if (err.response?.status === 403) {
                setError('У вас нет прав для удаления этого пользователя');
            } else if (err.response?.status === 404) {
                setError('Пользователь не найден');
            } else {
                setError('Не удалось удалить пользователя');
            }
        }
    };

    const handleLogout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Ошибка при выходе:', error);
        } finally {
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('session');
            localStorage.removeItem('user');
            localStorage.removeItem('userId');
            navigate('/login');
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const formatSessionDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="user-profile-container">
                <div className="loading">Загрузка профиля...</div>
            </div>
        );
    }

    if (error && !profileUser) {
        return (
            <div className="user-profile-container">
                <div className="error-message">
                    {error}
                    <Link to="/" className="back-link">← На главную</Link>
                </div>
            </div>
        );
    }

    const isOwnProfile = !userId || parseInt(userId) === currentUser?.user_id;
    const canEdit = isOwnProfile || currentUser?.user_role === 'admin';
    const canDelete = currentUser?.user_role === 'admin' || isOwnProfile;
    const canViewSessions = isOwnProfile || currentUser?.user_role === 'admin';

    return (
        <div className="user-profile-container">
            <div className="profile-header">
                <Link to="/" className="back-link">← На главную</Link>
                <h1>Профиль пользователя</h1>
                {!isOwnProfile && (
                    <p className="profile-subtitle">
                        Просмотр профиля другого пользователя
                    </p>
                )}
            </div>

            {error && (
                <div className="error-message">{error}</div>
            )}

            <div className="profile-content">
                <div className="profile-avatar-section">
                    <div className="avatar-container">
                        {profileUser?.avatar ? (
                            <img 
                                src={profileUser.avatar} 
                                alt={profileUser.user_name} 
                                className="user-avatar"
                            />
                        ) : (
                            <div className="avatar-placeholder">
                                {profileUser?.user_name?.charAt(0)?.toUpperCase() || 'U'}
                            </div>
                        )}
                    </div>
                    
                    {!isEditing && canEdit && (
                        <div className="avatar-section-actions">
                            <button 
                                onClick={() => setIsEditing(true)}
                                className="edit-profile-btn"
                            >
                                ✏️ Редактировать профиль
                            </button>

                            {canDelete && (
                                <button
                                    onClick={() => setShowDeleteConfirm(true)}
                                    className="delete-user-btn"
                                >
                                    🗑️ Удалить профиль
                                </button>
                            )}
                        </div>
                    )}
                </div>

                <div className="profile-info-section">
                    {isEditing ? (
                        <div className="edit-form">
                            <h2>Редактирование профиля</h2>
                            
                            <div className="form-group">
                                <label htmlFor="user_name">Имя пользователя:</label>
                                <input
                                    type="text"
                                    id="user_name"
                                    name="user_name"
                                    value={editForm.user_name}
                                    onChange={handleEditChange}
                                    disabled={isSubmitting}
                                    required
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="email">Email:</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={editForm.email}
                                    onChange={handleEditChange}
                                    disabled={isSubmitting}
                                    required
                                />
                            </div>
                            
                            {currentUser?.user_role === 'admin' && (
                                <div className="form-group">
                                    <label htmlFor="user_role">Роль:</label>
                                    <select
                                        id="user_role"
                                        name="user_role"
                                        value={editForm.user_role}
                                        onChange={handleEditChange}
                                        disabled={isSubmitting}
                                    >
                                        <option value="user">Пользователь</option>
                                        <option value="author">Автор</option>
                                        <option value="admin">Администратор</option>
                                    </select>
                                </div>
                            )}
                            
                            <div className="form-group">
                                <label htmlFor="avatar">URL аватара:</label>
                                <input
                                    type="text"
                                    id="avatar"
                                    name="avatar"
                                    value={editForm.avatar}
                                    onChange={handleEditChange}
                                    disabled={isSubmitting}
                                    placeholder="https://example.com/avatar.jpg"
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="password">Новый пароль:</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={editForm.password}
                                    onChange={handleEditChange}
                                    disabled={isSubmitting}
                                    placeholder="Введите новый пароль"
                                />
                            </div>
                            
                            <div className="form-actions">
                                <button
                                    onClick={() => {
                                        setIsEditing(false);
                                        setEditForm({
                                            user_name: profileUser.user_name,
                                            email: profileUser.email,
                                            user_role: profileUser.user_role,
                                            avatar: profileUser.avatar || '',
                                            password: ''
                                        });
                                    }}
                                    disabled={isSubmitting}
                                    className="cancel-btn"
                                >
                                    Отмена
                                </button>
                                <button
                                    onClick={handleSaveProfile}
                                    disabled={isSubmitting}
                                    className="save-btn"
                                >
                                    {isSubmitting ? 'Сохранение...' : 'Сохранить'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="view-form">
                            <h2>Информация о пользователе</h2>
                            
                            <div className="info-grid">
                                <div className="info-item">
                                    <span className="info-label">Имя:</span>
                                    <span className="info-value">{profileUser?.user_name}</span>
                                </div>
                                
                                <div className="info-item">
                                    <span className="info-label">Email:</span>
                                    <span className="info-value">{profileUser?.email}</span>
                                </div>
                                
                                <div className="info-item">
                                    <span className="info-label">Роль:</span>
                                    <span className={`info-value role-badge role-${profileUser?.user_role}`}>
                                        {profileUser?.user_role === 'admin' ? 'Администратор' : 
                                         profileUser?.user_role === 'author' ? 'Автор' : 'Пользователь'}
                                    </span>
                                </div>
                                
                                <div className="info-item">
                                    <span className="info-label">Дата регистрации:</span>
                                    <span className="info-value">
                                        {profileUser?.registration_date ? formatDate(profileUser.registration_date) : 'Неизвестно'}
                                    </span>
                                </div>
                                
                                {profileUser?.avatar && (
                                    <div className="info-item">
                                        <span className="info-label">Аватар:</span>
                                        <span className="info-value">
                                            <a href={profileUser.avatar} target="_blank" rel="noopener noreferrer">
                                                Ссылка
                                            </a>
                                        </span>
                                    </div>
                                )}
                            </div>
                            
                            {canViewSessions && (
                                <div className="sessions-section">
                                    <button
                                        onClick={() => setShowSessions(!showSessions)}
                                        className="toggle-sessions-btn"
                                    >
                                        {showSessions ? 'Скрыть' : 'Показать'} активные сессии ({sessions.length})
                                    </button>
                                    
                                    {showSessions && (
                                        <div className="sessions-list">
                                            {sessions.length === 0 ? (
                                                <p className="no-sessions">Нет активных сессий</p>
                                            ) : (
                                                sessions.map((session, index) => (
                                                    <div key={index} className="session-item">
                                                        <div className="session-info">
                                                            <span className="session-device">
                                                                {session.user_agent || 'Неизвестное устройство'}
                                                            </span>
                                                            <span className="session-expire">
                                                                Истекает: {formatSessionDate(session.refresh_token_expiretime)}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {showDeleteConfirm && (
                <div className="delete-confirm-modal">
                    <div className="modal-content">
                        <h3>Подтверждение удаления</h3>
                        <p>
                            Вы уверены, что хотите удалить пользователя <strong>{profileUser?.user_name}</strong>?
                            Это действие нельзя отменить. Все новости и комментарии пользователя также будут удалены.
                        </p>
                        <div className="modal-actions">
                            <button
                                onClick={() => setShowDeleteConfirm(false)}
                                className="modal-cancel-btn"
                            >
                                Отмена
                            </button>
                            <button
                                onClick={handleDeleteUser}
                                className="modal-confirm-btn"
                            >
                                Удалить
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default UserProfilePage;