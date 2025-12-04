import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage/HomePage';
import NewsPage from './pages/NewsPage/NewsPage';
import LoginPage from './pages/LoginPage/LoginPage';
import SignUpPage from './pages/SignUpPage/SignUpPage';
import { userAPI, authAPI } from './api/index';
import './styles/App.css';

function App() {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [user, setUser] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		// проверка авторизации при загрузке приложения
		const token = localStorage.getItem('token');
		const storedUser = localStorage.getItem('user');

		if (token && storedUser) {
			try {
				// используем сохраненные данные пользователя
				const userData = JSON.parse(storedUser);
				console.log('Восстановление пользователя из localStorage:', userData);
				setUser(userData);
				setIsAuthenticated(true);
			} catch (error) {
				console.error('Ошибка при чтении данных пользователя:', error);
				handleLogout();
			}
		} else {
			console.log('Нет токена или пользователя в localStorage');
		}
		
		// всегда устанавливаем loading в false после проверки
		setLoading(false);
		
		// отладочный вывод
		console.log('App.jsx: Проверка авторизации завершена', {
			token: !!token,
			hasUser: !!storedUser,
			isAuthenticated
		});
	}, []);

	const handleLogout = async () => {
		try {
			await authAPI.logout();
		} catch (error) {
			console.error('ошибка при выходе:', error);
		} finally {
			// очистка данных
			localStorage.removeItem('token');
			localStorage.removeItem('refreshToken');
			localStorage.removeItem('session');
			localStorage.removeItem('user');
			localStorage.removeItem('userId');
			setIsAuthenticated(false);
			setUser(null);
			window.location.href = '/';
		}
	};

	if (loading) {
		return <div className="loading">Проверка авторизации...</div>;
	}

	// отладочный вывод для рендера
	console.log('App.jsx рендер:', { isAuthenticated, user });

	return (
		<Router>
			<div className="app">
				<nav>
					<ul>
						<li><Link to="/">Главная</Link></li>
						{isAuthenticated ? (
							<>
								<li className="user-info">
									<span>👤 {user?.user_name || user?.email || 'Пользователь'}</span>
									<button onClick={handleLogout} className="logout-btn">Выйти</button>
								</li>
							</>
						) : (
							<>
								<li><Link to="/login">Войти</Link></li>
								<li><Link to="/signup">Регистрация</Link></li>
							</>
						)}
					</ul>
				</nav>

				<div className="content">
					<Routes>
						<Route path="/" element={<HomePage />} />
						<Route path="/news/:id" element={<NewsPage />} />
						<Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} setUser={setUser} />} />
						<Route path="/signup" element={<SignUpPage />} />
					</Routes>
				</div>
			</div>
		</Router>
	);
}

export default App;