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

      // получение JWT токена из заголовка
      const jwtToken = response.headers['x-jwt'];

      if (!jwtToken) {
        throw new Error('Токен не получен от сервера');
      }

      // сохранение jwt токена в localStorage
      localStorage.setItem('token', jwtToken);

      // сохранение refresh токена и данных сессии
      if (response.data && response.data.refresh_token) {
        localStorage.setItem('refreshToken', response.data.refresh_token);
        localStorage.setItem('session', JSON.stringify(response.data));
      }
    
      // создаем базовый объект пользователя из ответа сервера
      const userDataFromServer = response.data;
      const basicUserData = {
        email: email,
        user_name: email.split('@')[0],
        user_id: userDataFromServer.user_id || null // извлекаем user_id из ответа
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
				switch (err.response.status) {
					case 400:
						setError('Некорректные данные');
						break;
					case 401:
						if (err.response.data && err.response.data.detail) {
							setError(err.response.data.detail);
						} else if (typeof err.response.data === 'string') {
							setError(err.response.data);
						} else {
							setError('Неверный email или пароль');
						}
						break;
					case 404:
						setError('Пользователь не найден');
						break;
					case 500:
						setError('Ошибка сервера. Попробуйте позже');
						break;
					default:
						setError('Произошла ошибка при авторизации');
				}
			} else if (err.request) {
				setError('Не удалось подключиться к серверу. Проверьте подключение');
			} else if (err.message === 'Токен не получен от сервера') {
				setError(err.message);
			} else {
				setError('Произошла ошибка');
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