import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { userAPI } from '../../api/index';
import { useAuth } from '../../context/AuthContext';
import Avatar from '../../components/Avatar/Avatar';
import './UserProfilePage.css';

function UserProfilePage() {
    const { userId } = useParams();
    const navigate = useNavigate();
    const { user: currentUser, isAuthenticated, logout, refreshUser } = useAuth();
    
    const [user, setUser] = useState(null);          // профиль, который смотрим (может быть чужим)
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [loadingSave, setLoadingSave] = useState(false);
    const [deletingAccount, setDeletingAccount] = useState(false);
    
    // форма редактирования
    const [formData, setFormData] = useState({
        user_name: '',
        email: '',
        user_role: '',
        avatar: '',
        password: ''
    });

    // загрузка данных пользователя (своего или чужого)
    useEffect(() => {
        const fetchUser = async () => {
            try {
                setLoading(true);
                setError('');
                
                let targetUserId;
                
                if (userId) {
                    targetUserId = parseInt(userId);
                } else {
                    // свой профиль – берём ID из контекста
                    if (!currentUser) {
                        setLoading(false);
                        navigate('/login');
                        return;
                    }
                    targetUserId = currentUser.user_id;
                }
                
                const response = await userAPI.getUserById(targetUserId);
                const userData = response.data;
                setUser(userData);
                
                // заполнение формы данными пользователя
                setFormData({
                    user_name: userData.user_name || '',
                    email: userData.email || '',
                    user_role: userData.user_role || 'user',
                    avatar: userData.avatar || '',
                    password: ''
                });
            } catch (err) {
                console.error('Ошибка загрузки пользователя:', err);
                
                if (err.response?.status === 401) {
                    setError('Сессия истекла. Пожалуйста, войдите снова.');
                    logout();
                    setTimeout(() => navigate('/login'), 2000);
                } else if (err.response?.status === 403) {
                    setError('У вас нет прав для просмотра этого профиля');
                } else if (err.response?.status === 404) {
                    setError('Пользователь не найден');
                } else {
                    setError('Не удалось загрузить данные пользователя');
                }
            } finally {
                setLoading(false);
            }
        };

        if (!isAuthenticated && !userId) {
            navigate('/login');
            return;
        }
        fetchUser();
    }, [userId, currentUser, isAuthenticated, navigate, logout]);

    const canEdit = currentUser && user && (
        currentUser.user_id === user.user_id || 
        currentUser.user_role === 'admin'
    );

    const canChangeRole = currentUser?.user_role === 'admin' && currentUser.user_id !== user?.user_id;
    const isOwnProfile = currentUser?.user_id === user?.user_id;

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleCancel = () => {
        // восстановление исходных данных
        if (user) {
            setFormData({
                user_name: user.user_name || '',
                email: user.email || '',
                user_role: user.user_role || 'user',
                avatar: user.avatar || '',
                password: ''
            });
        }
        setIsEditing(false);
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!formData.user_name.trim()) {
            setError('Имя пользователя обязательно');
            return;
        }

        if (!formData.email.trim() || !formData.email.includes('@')) {
            setError('Введите корректный email');
            return;
        }

        if (formData.password && formData.password.trim() !== '') {
            if (formData.password.length < 8) {
                setError('Пароль должен быть не менее 8 символов');
                return;
            }
        }

        try {
            setLoadingSave(true);
            const updateData = {
                user_name: formData.user_name.trim(),
                email: formData.email.trim(),
                user_role: canChangeRole ? formData.user_role : user.user_role
            };
            
            updateData.avatar = (formData.avatar && formData.avatar.trim() !== '') 
                ? formData.avatar.trim() 
                : null;
            
            if (formData.password && formData.password.trim() !== '') {
                updateData.password = formData.password.trim();
            }

            console.log('Отправка данных для обновления:', { 
                ...updateData, 
                password: updateData.password ? '***' : 'не указан' 
            });

            await userAPI.updateUser(user.user_id, updateData);
            
            // если обновили свой профиль – обновляем контекст (и заодно данные на странице)
            if (isOwnProfile) {
                await refreshUser();
                // также обновляем локального user, чтобы отобразить изменения сразу
                const refreshedResponse = await userAPI.getUserById(user.user_id);
                setUser(refreshedResponse.data);
            } else {
                // если админ меняет чужой профиль – просто обновляем локального user
                const updatedResponse = await userAPI.getUserById(user.user_id);
                setUser(updatedResponse.data);
            }
            
            alert('Профиль успешно обновлен!');
            setIsEditing(false);
        } catch (err) {
            console.error('Ошибка при обновлении профиля:', err);
            console.error('Детали ошибки:', err.response?.data);
            
            if (err.response?.status === 401) {
                setError('Сессия истекла. Пожалуйста, войдите снова.');
                logout();
                setTimeout(() => navigate('/login'), 2000);
            } else if (err.response?.status === 403) {
                setError('У вас нет прав для редактирования этого профиля');
            } else if (err.response?.status === 400) {
                const detail = err.response.data?.detail;
                if (typeof detail === 'string') {
                    setError('Некорректные данные: ' + detail);
                } else if (Array.isArray(detail)) {
                    const errors = detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                    setError('Ошибка валидации: ' + errors);
                } else {
                    setError('Некорректные данные: ' + JSON.stringify(detail));
                }
            } else if (err.response?.status === 409) {
                setError('Пользователь с таким email уже существует');
            } else if (err.response?.status === 422) {
                const detail = err.response.data?.detail;
                if (typeof detail === 'string') {
                    setError('Ошибка валидации: ' + detail);
                } else if (Array.isArray(detail)) {
                    const errors = detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join(', ');
                    setError('Ошибка валидации: ' + errors);
                } else {
                    setError('Ошибка валидации данных');
                }
            } else if (err.response?.data) {
                const detail = err.response.data?.detail || err.response.data?.message || JSON.stringify(err.response.data);
                setError('Ошибка: ' + detail);
            } else {
                setError('Не удалось обновить профиль. Попробуйте еще раз.');
            }
        } finally {
            setLoadingSave(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleDeleteAccount = async () => {
        // двойное подтверждение для удаления аккаунта
        const confirmation1 = window.confirm(
            '⚠️ ВНИМАНИЕ: Вы собираетесь удалить свой аккаунт!\n\n' +
            'Это действие НЕОБРАТИМО. После удаления:\n' +
            '• Ваш профиль будет удален\n' +
            '• Все ваши данные будут удалены\n' +
            '• Вы не сможете восстановить аккаунт\n\n' +
            'Вы уверены, что хотите продолжить?'
        );
        
        if (!confirmation1) return;
        
        const confirmation2 = window.confirm(
            'Пожалуйста, подтвердите еще раз.\n\n' +
            'Для подтверждения введите "УДАЛИТЬ" в поле ниже:'
        );
        
        if (!confirmation2) return;
        
        const userInput = window.prompt(
            'Введите слово "УДАЛИТЬ" для подтверждения удаления аккаунта:'
        );
        
        if (userInput !== 'УДАЛИТЬ') {
            alert('Удаление отменено. Слово подтверждения введено неверно.');
            return;
        }

        try {
            setDeletingAccount(true);
            await userAPI.deleteUser(user.user_id);
            
            // если удаляем свой аккаунт
            if (isOwnProfile) {
                logout(); // чистим токены и контекст
                alert('Ваш аккаунт был успешно удален. Спасибо, что были с нами!');
                navigate('/');
            } else {
                alert('Аккаунт пользователя успешно удален');
                navigate('/admin/users');
            }
        } catch (err) {
            console.error('Ошибка при удалении аккаунта:', err);
            
            if (err.response?.status === 401) {
                setError('Сессия истекла. Пожалуйста, войдите снова.');
                logout();
                setTimeout(() => navigate('/login'), 2000);
            } else if (err.response?.status === 403) {
                setError('У вас нет прав для удаления этого аккаунта');
            } else if (err.response?.status === 404) {
                setError('Пользователь не найден');
            } else {
                setError('Не удалось удалить аккаунт. Попробуйте еще раз.');
            }
        } finally {
            setDeletingAccount(false);
        }
    };

    if (loading) {
        return (
            <div className="profile-container">
                <div className="loading">Загрузка профиля...</div>
            </div>
        );
    }

    if (error && !user) {
        return (
            <div className="profile-container">
                <div className="error-message">{error}</div>
                <Link to="/" className="back-link">← Вернуться на главную</Link>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="profile-container">
                <div className="error-message">Пользователь не найден</div>
                <Link to="/" className="back-link">← Вернуться на главную</Link>
            </div>
        );
    }

    return (
        <div className="profile-container">
            <Link to="/" className="back-link">← Вернуться на главную</Link>
            
            <div className="profile-header">
                <h1>Профиль пользователя</h1>
                {canEdit && !isEditing && (
                    <div className="profile-header-actions">
                        <button onClick={handleEdit} className="edit-btn">
                            ✏️ Редактировать
                        </button>
                    </div>
                )}
            </div>

            {error && <div className="error-message">{error}</div>}

            {!isEditing ? (
                <div className="profile-info">
                    <div className="avatar-container">
                        <Avatar
                            src={user.avatar ? (user.avatar.startsWith('http') ? user.avatar : `http://localhost:8000/static/${user.avatar}`) : null}
                            alt={user.user_name}
                            size="xlarge"
                        />
                    </div>
                    
                    <div className="info-section">
                        <div className="info-item">
                            <span className="info-label">Имя пользователя:</span>
                            <span className="info-value">{user.user_name}</span>
                        </div>
                        
                        <div className="info-item">
                            <span className="info-label">Email:</span>
                            <span className="info-value">{user.email}</span>
                        </div>
                        
                        <div className="info-item">
                            <span className="info-label">Роль:</span>
                            <span className="info-value">
                                {user.user_role === 'admin' && '👑 Администратор'}
                                {user.user_role === 'author' && '✍️ Автор'}
                                {user.user_role === 'user' && '👤 Пользователь'}
                            </span>
                        </div>
                        
                        <div className="info-item">
                            <span className="info-label">Дата регистрации:</span>
                            <span className="info-value">
                                {new Date(user.registration_date).toLocaleDateString('ru-RU', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                })}
                            </span>
                        </div>
                    </div>
                    
                    {isOwnProfile && !isEditing && (
                        <div className="delete-account-section">
                            <p className="delete-warning">
                                Удаление аккаунта — необратимое действие. После удаления восстановление невозможно.
                            </p>
                            <button 
                                onClick={handleDeleteAccount} 
                                className="delete-account-btn"
                                disabled={deletingAccount}
                            >
                                {deletingAccount ? 'Удаление...' : '🗑️ Удалить мой аккаунт'}
                            </button>
                        </div>
                    )}
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="profile-form">
                    <div className="form-group">
                        <label htmlFor="user_name">Имя пользователя:</label>
                        <input
                            id="user_name"
                            name="user_name"
                            type="text"
                            value={formData.user_name}
                            onChange={handleInputChange}
                            required
                            placeholder="Введите имя пользователя"
                            disabled={loadingSave}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email:</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            required
                            placeholder="Введите email"
                            disabled={loadingSave}
                        />
                    </div>

                    {!canChangeRole && (
                        <div className="form-group">
                            <label htmlFor="password">Пароль:</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                value={formData.password}
                                onChange={handleInputChange}
                                placeholder="••••••••"
                                disabled={loadingSave}
                            />
                            <div className="password-hint">
                                Оставьте поле пустым, чтобы не менять пароль. Введите новый пароль, чтобы изменить его.
                            </div>
                        </div>
                    )}

                    {canChangeRole && (
                        <div className="form-group">
                            <label htmlFor="user_role">Роль:</label>
                            <select
                                id="user_role"
                                name="user_role"
                                value={formData.user_role}
                                onChange={handleInputChange}
                                disabled={loadingSave}
                            >
                                <option value="user">👤 Пользователь</option>
                                <option value="author">✍️ Автор</option>
                                <option value="admin">👑 Администратор</option>
                            </select>
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="avatar">Аватар (URL):</label>
                        <input
                            id="avatar"
                            name="avatar"
                            type="text"
                            value={formData.avatar}
                            onChange={handleInputChange}
                            placeholder="Введите URL изображения (опционально)"
                            disabled={loadingSave}
                        />
                        {formData.avatar && (
                            <div className="avatar-preview">
                                <Avatar
                                    src={formData.avatar ? (formData.avatar.startsWith('http') ? formData.avatar : `http://localhost:8000/static/${formData.avatar}`) : null}
                                    alt={formData.user_name}
                                    size="large"
                                />
                                <div className="avatar-hint">
                                    {formData.avatar 
                                        ? "Предпросмотр аватарки."
                                        : "Аватарка не указана. Будет показана первая буква имени."}
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="form-actions">
                        <button 
                            type="button" 
                            onClick={handleCancel}
                            className="cancel-btn"
                            disabled={loadingSave}
                        >
                            Отмена
                        </button>
                        <button 
                            type="submit" 
                            className="submit-btn"
                            disabled={loadingSave}
                        >
                            {loadingSave ? 'Сохранение...' : 'Сохранить изменения'}
                        </button>
                    </div>
                </form>
            )}
        </div>
    );
}

export default UserProfilePage;