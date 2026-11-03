import React, { createContext, useState, useContext, useEffect, useCallback, useMemo } from 'react';
import { userAPI } from '../api/index';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setLoading(false);
            return;
        }

    // проверка токена при помощи запроса текущего пользователя
    userAPI.getCurrentUser()
        .then(response => {
            setUser(response.data);
            setIsAuthenticated(true);
        })
        .catch(() => {
            // очистка localStorage, если токен невалиден
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            setIsAuthenticated(false);
            setUser(null);
        })
        .finally(() => setLoading(false));
    }, []);

    const login = useCallback((token, refreshToken, userData) => {
        localStorage.setItem('token', token);
        if (refreshToken) localStorage.setItem('refreshToken', refreshToken);
        setUser(userData);
        setIsAuthenticated(true);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        setUser(null);
        setIsAuthenticated(false);
    }, []);

    const refreshUser = useCallback(async () => {
        try {
            const response = await userAPI.getCurrentUser();
            setUser(response.data);
        } catch (e) {
            console.error('Ошибка обновления данных пользователя', e);
        }
    }, []);

    const value = useMemo(
        () => ({ isAuthenticated, user, loading, login, logout, refreshUser }),
        [isAuthenticated, user, loading, login, logout, refreshUser],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);