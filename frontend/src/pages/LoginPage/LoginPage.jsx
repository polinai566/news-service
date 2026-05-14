import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../api/index';
import './LoginPage.css';

function LoginPage({ setIsAuthenticated, setUser }) {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');
	const navigate = useNavigate();

  	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');
		if (!email.trim()) {
			setError('Email обязателен');
			return;
		}
		if (!password) {
			setError('Пароль обязателен');
			return;
		}
		if (!email.includes('@')) {
			setError('Введите корректный email');
			return;
		}

    	try {
    	  	setLoading(true);
    	  	const response = await authAPI.login(email, password);

    	  	// получение PASETO токена из заголовка
    	  	const paseto_token = response.headers['x-paseto'];

    	  	if (!paseto_token) {
    	  	  	throw new Error('Токен не получен от сервера');
    	  	}

    	  	// сохранение access токена в localStorage
    	  	localStorage.setItem('token', paseto_token);

            const sessionData = response.data;
            if (!sessionData || !sessionData.user_id) {
                throw new Error('Не удалось получить данные пользователя');
            }

            // сохранение refresh токена и данных сессии
            if (response.data && response.data.refresh_token) {
                localStorage.setItem('refreshToken', response.data.refresh_token);
                localStorage.setItem('session', JSON.stringify(response.data));
            }

            // создание объекта пользователя из данных, полученных от сервера
            const UserData = {
                user_id: sessionData.user_id,
                user_role: sessionData.user_role,
                email: email,
                user_name: email.split('@')[0],
            };
		
			// сохранение данных пользователя в localStorage
            localStorage.setItem('user', JSON.stringify(UserData));
    
            // обновление состояния в App
            if (setIsAuthenticated) setIsAuthenticated(true);
            if (setUser) setUser(UserData);

            // уведомление об успешном входе
            console.log('Успешный вход!', UserData);
            navigate('/');

    	} catch (err) {
            console.error('Ошибка авторизации:', err);
            if (err.response) {
                const status = err.response.status;
                const data = err.response.data;
                switch (status) {
                    case 400: setError('Некорректные данные'); break;
                    case 401: setError(data?.detail || 'Неверный email или пароль'); break;
                    case 404: setError('Пользователь не найден'); break;
                    case 500: setError('Ошибка сервера'); break;
                    default: setError(`Ошибка ${status}: ${data?.detail || 'Неизвестная ошибка'}`);
                }
            } else if (err.request) {
                setError('Не удалось подключиться к серверу');
            } else {
                setError(err.message || 'Произошла ошибка');
            }
        } finally {
            setLoading(false);
        }
    };

  	return (
        <div className="login-container">
            <h1>Авторизация</h1>
            <form onSubmit={handleSubmit} className="login-form">
                <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        placeholder="Введите ваш email"
                        disabled={loading}
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
                        placeholder="Введите ваш пароль"
                        disabled={loading}
                    />
                </div>
                
                {error && <div className="error-message">{error}</div>}
                
                <button 
                    type="submit" 
                    className="submit-btn"
                    disabled={loading}
                >
                    {loading ? 'Вход...' : 'Войти'}
                </button>
                
                <div className="signup-link">
                    Нет аккаунта? <Link to="/signup">Зарегистрироваться</Link>
                </div>
            </form>
        </div>
    );
}

export default LoginPage;