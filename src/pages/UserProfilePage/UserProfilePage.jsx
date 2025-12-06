import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { userAPI } from '../../api/index';
import './UserProfilePage.css';

function UserProfilePage() {
    const { userId } = useParams();
    const navigate = useNavigate();
    
    const [user, setUser] = useState(null);
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [loadingSave, setLoadingSave] = useState(false);
    
    // Форма редактирования
    const [formData, setFormData] = useState({
        user_name: '',
        email: '',
        user_role: '',
        avatar: '',
        password: ''
    });

    // Получение текущего пользователя из localStorage
    useEffect(() => {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                setCurrentUser(JSON.parse(userStr));
            } catch (e) {
                console.error('Ошибка при чтении пользователя из localStorage:', e);
            }
        }
    }, []);

    // Загрузка данных пользователя
    useEffect(() => {
        const fetchUser = async () => {
            try {
                setLoading(true);
                setError('');
                
                // Определяем, какой userId использовать
                let targetUserId;
                
                if (userId) {
                    // Если userId указан в URL, используем его
                    targetUserId = parseInt(userId);
                } else {
                    // Если userId не указан, пытаемся получить текущего пользователя
                    const userStr = localStorage.getItem('user');
                    if (userStr) {
                        try {
                            const parsedUser = JSON.parse(userStr);
                            targetUserId = parsedUser.user_id;
                        } catch (e) {
                            console.error('Ошибка при чтении пользователя:', e);
                        }
                    }
                }
                
                if (!targetUserId) {
                    // Если нет userId и нет текущего пользователя, перенаправляем на логин
                    setLoading(false);
                    navigate('/login');
                    return;
                }

                const response = await userAPI.getUserById(targetUserId);
                const userData = response.data;
                setUser(userData);
                
                // Заполняем форму данными пользователя
                setFormData({
                    user_name: userData.user_name || '',
                    email: userData.email || '',
                    user_role: userData.user_role || 'user',
                    avatar: userData.avatar || '',
                    password: '' // Пароль не загружаем, пользователь может его изменить
                });
            } catch (err) {
                console.error('Ошибка загрузки пользователя:', err);
                
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
                    setError('Не удалось загрузить данные пользователя');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchUser();
    }, [userId, navigate]);

    // Проверка прав на редактирование
    const canEdit = currentUser && user && (
        currentUser.user_id === user.user_id || 
        currentUser.user_role === 'admin'
    );

    // Проверка, может ли текущий пользователь изменять роль
    const canChangeRole = currentUser?.user_role === 'admin' && currentUser.user_id !== user?.user_id;

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleCancel = () => {
        // Восстанавливаем исходные данные
        if (user) {
            setFormData({
                user_name: user.user_name || '',
                email: user.email || '',
                user_role: user.user_role || 'user',
                avatar: user.avatar || '',
                password: '' // Сбрасываем пароль при отмене
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

        // Валидация пароля, если он указан
        if (formData.password && formData.password.trim() !== '') {
            if (formData.password.length < 8) {
                setError('Пароль должен быть не менее 8 символов');
                return;
            }
        }

        try {
            setLoadingSave(true);
            
            // Формируем данные для обновления
            // Всегда отправляем user_role, так как это обязательное поле в схеме
            const updateData = {
                user_name: formData.user_name.trim(),
                email: formData.email.trim(),
                user_role: canChangeRole ? formData.user_role : user.user_role
            };
            
            // Добавляем аватар
            updateData.avatar = (formData.avatar && formData.avatar.trim() !== '') 
                ? formData.avatar.trim() 
                : null;
            
            // Добавляем пароль только если он указан и не пустой
            // Если пароль не указан, отправляем null (backend должен обработать это корректно)
            if (formData.password && formData.password.trim() !== '') {
                updateData.password = formData.password.trim();
            } else {
                // Не отправляем password вообще, если он не указан
                // Backend должен использовать exclude_unset=True для исключения не установленных полей
            }

            console.log('Отправка данных для обновления:', { 
                ...updateData, 
                password: updateData.password ? '***' : 'не указан' 
            });

            const response = await userAPI.updateUser(user.user_id, updateData);
            
            // Обновляем данные пользователя
            setUser(response.data);
            
            // Если редактировали свой профиль, обновляем данные в localStorage
            if (currentUser?.user_id === user.user_id) {
                const updatedUser = {
                    ...currentUser,
                    user_name: response.data.user_name,
                    email: response.data.email,
                    user_role: response.data.user_role,
                    avatar: response.data.avatar
                };
                localStorage.setItem('user', JSON.stringify(updatedUser));
            }
            
            alert('Профиль успешно обновлен!');
            setIsEditing(false);
        } catch (err) {
            console.error('Ошибка при обновлении профиля:', err);
            console.error('Детали ошибки:', err.response?.data);
            
            if (err.response?.status === 401) {
                setError('Сессия истекла. Пожалуйста, войдите снова.');
                localStorage.removeItem('token');
                localStorage.removeItem('user');
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

    const isOwnProfile = currentUser?.user_id === user.user_id;

    return (
        <div className="profile-container">
            <Link to="/" className="back-link">← Вернуться на главную</Link>
            
            <div className="profile-header">
                <h1>Профиль пользователя</h1>
                {canEdit && !isEditing && (
                    <button onClick={handleEdit} className="edit-btn">
                        ✏️ Редактировать
                    </button>
                )}
            </div>

            {error && <div className="error-message">{error}</div>}

            {!isEditing ? (
                <div className="profile-info">
                    {user.avatar && (
                        <div className="avatar-container">
                            <img 
                                src={user.avatar.startsWith('http') ? user.avatar : `http://localhost:8000/static/${user.avatar}`}
                                alt={user.user_name}
                                className="avatar"
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                }}
                            />
                        </div>
                    )}
                    
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

                    {/* Поле пароля только для обычных пользователей (не для админа при редактировании чужого профиля) */}
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
                                <img 
                                    src={formData.avatar.startsWith('http') ? formData.avatar : `http://localhost:8000/static/${formData.avatar}`}
                                    alt="Preview"
                                    onError={(e) => {
                                        e.target.style.display = 'none';
                                    }}
                                />
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