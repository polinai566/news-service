import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage/HomePage';
import NewsPage from './pages/NewsPage/NewsPage';
import LoginPage from './pages/LoginPage/LoginPage';
import SignUpPage from './pages/SignUpPage/SignUpPage';
import CreateNewsPage from './pages/CreateNewsPage/CreateNewsPage';
import EditNewsPage from './pages/EditNewsPage/EditNewsPage';
import UserProfilePage from './pages/UserProfilePage/UserProfilePage';
import AdminUsersPage from './pages/AdminUsersPage/AdminUsersPage';
import { authAPI } from './api/index';
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
                const userData = JSON.parse(storedUser);
				if (userData.user_id) {
                    console.log('Восстановление пользователя из localStorage:', userData);
                    setUser(userData);
                    setIsAuthenticated(true);
                } else {
                    console.log('Данные пользователя некорректны');
                    handleLogout();
                }
            } catch (error) {
                console.error('Ошибка при чтении данных пользователя:', error);
                handleLogout();
            }
		} else {
            console.log('Нет токена или пользователя в localStorage');
        }
		
		// установка loading в false после проверки
		setLoading(false);
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

	// проверка пользователя на создание новости
    const canCreateNews = user?.user_role && ['admin', 'author'].includes(user.user_role);

	return (
        <Router>
            <div className="app">
                <nav>
                    <ul>
                        <li><Link to="/">Главная</Link></li>
                        
                        {isAuthenticated && canCreateNews && (
                            <li>
                                <Link to="/news/create" className="create-news-link">
                                    ➕ Создать новость
                                </Link>
                            </li>
                        )}
                        
                        {isAuthenticated && user?.user_role === 'admin' && (
                            <li>
                                <Link to="/admin/users" className="admin-link">
                                    👑 Админ-панель
                                </Link>
                            </li>
                        )}
                        
                        {isAuthenticated ? (
                            <>
                                <li>
                                    <Link to="/profile">Профиль</Link>
                                </li>
                                <li className="user-info">
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
                        <Route path="/news/create" element={<CreateNewsPage />} />
                        <Route path="/news/:id/edit" element={<EditNewsPage />} />
                        <Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} setUser={setUser} />} />
                        <Route path="/signup" element={<SignUpPage />} />
                        <Route path="/profile" element={<UserProfilePage />} />
                        <Route path="/profile/:userId" element={<UserProfilePage />} />
                        <Route path="/admin/users" element={user?.user_role === 'admin' ? <AdminUsersPage /> : <div>Доступ запрещён</div>} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;