import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../../api/index';
import './SignUpPage.css';

function SignUpPage() {
    const [userName, setUserName] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // валидация
        if (!userName.trim()) {
            setError('Имя пользователя обязательно');
            return;
        }

        if (!password) {
            setError('Пароль обязателен');
            return;
        }

        if (password !== confirmPassword) {
            setError('Пароли не совпадают');
            return;
        }

        if (password.length < 8) {
            setError('Пароль должен быть не менее 8 символов');
            return;
        }

        try {
            setLoading(true);
            const response = await userAPI.register({
                user_name: userName,
                password: password,
                user_role: "user",
                avatar: null
            });
            if (response.data) {
                // успешная регистрация - перенаправляем на логин
                alert('Регистрация прошла успешно! Теперь вы можете войти.');
                navigate('/');
            }
        } catch (err) {
            console.error('Ошибка регистрации:', err);
            if (err.response?.status === 400) {
                if (err.response.data.detail) {
                    setError(err.response.data.detail);
                } else {
                    setError('Некорректные данные');
                }
            } else if (err.response?.status === 409) {
                setError('Пользователь с таким login уже существует');
            } else if (err.message === 'Network Error') {
                setError('Ошибка сети. Проверьте подключение к серверу');
            } else {
                setError('Произошла ошибка при регистрации');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="signup-container">
            <h1>Регистрация</h1>
            <form onSubmit={handleSubmit} className="signup-form">
                <div className="form-group">
                    <label htmlFor="userName">Имя пользователя:</label>
                    <input
                        id="userName"
                        type="text"
                        value={userName}
                        onChange={(e) => setUserName(e.target.value)}
                        required
                        placeholder="Введите ваше имя"
                    />
                </div>


                <div className="form-group">
                    <label htmlFor="password">Пароль:</label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        placeholder="Введите пароль (мин. 8 символов)"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="confirmPassword">Подтвердите пароль:</label>
                    <input
                        id="confirmPassword"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        placeholder="Повторите пароль"
                    />
                </div>

                {error && <div className="error-message">{error}</div>}

                <button
                    type="submit"
                    className="submit-btn"
                    disabled={loading}
                >
                    {loading ? 'Регистрация...' : 'Зарегистрироваться'}
                </button>
            </form>
        </div>
    );
}

export default SignUpPage;