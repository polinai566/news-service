import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../api/index.js';
import { decodeJWT } from '../../utils/jwtDecoder.js';
import './LoginPage.css';

function LoginPage({ setIsAuthenticated, setUser }) {
	const [login, setLogin] = useState('');
	const [password, setPassword] = useState('');
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');
	const navigate = useNavigate();

  	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');
		if (!login.trim()) {
			setError('Login обязателен');
			return;
		}
		if (!password) {
			setError('Пароль обязателен');
			return;
		}

    	try {
    	  	setLoading(true);
    	  	const response = await authAPI.login(login, password);

    	  	// получение JWT токена из заголовка
    	  	const jwtToken = response.headers['x-jwt'];

    	  	if (!jwtToken) {
    	  	  	throw new Error('Токен не получен от сервера');
    	  	}

    	  	// сохранение jwt токена в localStorage
    	  	localStorage.setItem('token', jwtToken);

		  	// декодировка JWT токена для получения данных пользователя
    	    const decodedToken = decodeJWT(jwtToken);

			if (!decodedToken) {
    	        throw new Error('Не удалось декодировать токен');
    	    }

    	    // сохранение jwt токена в localStorage
    	    localStorage.setItem('token', jwtToken);

            // сохранение refresh токена и данных сессии
            if (response.data && response.data.refresh_token) {
                localStorage.setItem('refreshToken', response.data.refresh_token);
                localStorage.setItem('session', JSON.stringify(response.data));
            }

            // создание базового объекта пользователя из декодированного токена
            const basicUserData = {
                login: login,
                user_name: login.split('@')[0],
                user_id: parseInt(decodedToken.user_id),
                user_role: decodedToken.user_role || 'user'
            };
		
			// сохранение данных пользователя в localStorage
            localStorage.setItem('user', JSON.stringify(basicUserData));
    
            // обновление состояния в App.jsx
            if (setIsAuthenticated) {
                setIsAuthenticated(true);
            }
            if (setUser) {
                setUser(basicUserData);
            }

            // уведомление об успешном входе
            console.log('Успешный вход!', basicUserData);
            navigate('/');

    	} catch (err) {
            console.error('Ошибка авторизации:', err);
            
            if (err.response) {
                const status = err.response.status;
                const data = err.response.data;
                
                switch (status) {
                    case 400:
                        setError('Некорректные данные');
                        break;
                    case 401:
                        if (data && data.detail) {
                            setError(data.detail);
                        } else if (typeof data === 'string') {
                            setError(data);
                        } else {
                            setError('Неверный login или пароль');
                        }
                        break;
                    case 404:
                        setError('Пользователь не найден');
                        break;
                    case 500:
                        setError('Ошибка сервера. Попробуйте позже');
                        break;
                    default:
                        setError(`Ошибка ${status}: ${data?.detail || 'Неизвестная ошибка'}`);
                }
            } else if (err.request) {
                setError('Не удалось подключиться к серверу. Проверьте подключение');
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
                    <label htmlFor="login">Login:</label>
                    <input
                        id="login"
                        type="login"
                        value={login}
                        onChange={(e) => setLogin(e.target.value)}
                        required
                        placeholder="Введите ваш login"
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