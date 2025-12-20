import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import SignUpPage from './pages/SignUpPage/SignUpPage';
import { decodeJWT } from './utils/jwtDecoder';
import { authAPI } from './api/index';
import './styles/App.css';
import RegistrationSuccessPage from "./pages/RegistrationSuccessPage/RegistrationSuccessPage.jsx";

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
                // декодировка токена для получения актуальных данных
                const decodedToken = decodeJWT(token);

                if (decodedToken && decodedToken.user_id) {
                    // обновление данных пользователя из токена
                    const userData = JSON.parse(storedUser);
                    userData.user_id = parseInt(decodedToken.user_id);
                    userData.user_role = decodedToken.user_role || userData.user_role || 'user';

                    console.log('Восстановление пользователя из localStorage:', userData);
                    setUser(userData);
                    setIsAuthenticated(true);
                } else {
                    console.log('Токен недействителен или поврежден');
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

    // проверка пользователя на создание новости
    const canCreateNews = user?.user_role && ['admin', 'author'].includes(user.user_role);

    return (
        <Router>
            <div className="app">
                <Routes>
                    {/* Главная страница */}
                    <Route
                        path="/"
                        element={
                            <div className="home-page">
                                <h1>Добро пожаловать</h1>

                                <Link to="/register" className="signup-main-btn">
                                    Зарегистрироваться
                                </Link>
                            </div>
                        }
                    />

                    {/* Страница регистрации */}
                    <Route path="/register" element={<SignUpPage />} />
                    <Route path="/userpage" element={<RegistrationSuccessPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;