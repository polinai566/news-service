import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// добавление токена к запросам, если он есть
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // ошибка 401 и это не запрос на обновление токена
        if (error.response?.status === 401 && !originalRequest.url.includes('/session/')) {

            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                })
                    .then(token => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return api(originalRequest);
                    })
                    .catch(err => {
                        return Promise.reject(err);
                    });
            }

            isRefreshing = true;
            const refreshToken = localStorage.getItem('refreshToken');

            if (!refreshToken) {
                console.log('Нет refresh токена, требуется повторная авторизация');
                logoutAndRedirect();
                return Promise.reject(error);
            }

            try {
                // попытка обновить токен
                const refreshResponse = await authAPI.refresh(refreshToken);
                const newJwtToken = refreshResponse.headers['x-jwt'];
                const newRefreshToken = refreshResponse.data.refresh_token;

                if (!newJwtToken) {
                    throw new Error('Новый токен не получен от сервера');
                }

                // сохранение новых токенов
                localStorage.setItem('token', newJwtToken);
                localStorage.setItem('refreshToken', newRefreshToken);

                // обновление заголовка оригинального запроса
                originalRequest.headers.Authorization = `Bearer ${newJwtToken}`;

                // обработка очереди запросов
                processQueue(null, newJwtToken);
                isRefreshing = false;

                // повторение оригинального запроса
                return api(originalRequest);
            } catch (refreshError) {
                console.error('Ошибка обновления токена:', refreshError);
                processQueue(refreshError, null);
                logoutAndRedirect();
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// функция для выхода и перенаправления на страницу логина
const logoutAndRedirect = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('session');
    localStorage.removeItem('user');
    localStorage.removeItem('userId');

    // если не на странице логина, перенаправление туда
    if (!window.location.pathname.includes('/login') &&
        !window.location.pathname.includes('/signup')) {
        window.location.href = '/login';
    }
};

// экспорт методов для работы с API

export const newsAPI = {
    // получение списка новостей
    getNewsList: () => api.get('/news/'),
    // получение одной новости по ID
    getNewsById: (id) => api.get(`/news/${id}`),
    // получение комментариев к новости
    getCommentsByNews: (newsId) => api.get(`/comment/news/${newsId}`),
    // создание новости
    createNews: (newsData) => api.post('/news/', newsData),
    // обновление новости
    updateNews: (id, newsData) => api.put(`/news/${id}`, newsData),
    // удаление новости
    deleteNews: (id) => api.delete(`/news/${id}`),
};

export const authAPI = {
    // авторизация
    login: (login, password) => api.post('/session/', {
        login,
        password,
    }),
    // обновление токена
    refresh: (refreshToken) => api.put('/session/', {
        refresh_token: refreshToken,
    }),
    // выход
    logout: () => api.delete('/session/'),
    // получение сессий пользователя (для админа или самого пользователя)
    getUserSessions: (userId) => api.get(`/session/${userId}`),
    // получение сессий пользователя для админа (с refresh токенами)
    getAdminUserSessions: (userId) => api.get(`/session/admin/${userId}`),
};

export const userAPI = {
    // регистрация пользователя
    register: (userData) => api.post('/user/', userData),
    // получение пользователя по ID
    getUserById: (userId) => api.get(`/user/${userId}`),
    // получение всех пользователей (для админа)
    getAllUsers: () => api.get('/user/'),
    // обновление пользователя
    updateUser: (userId, userData) => api.put(`/user/${userId}`, userData),
    // удаление пользователя (для админа)
    deleteUser: (userId) => api.delete(`/user/${userId}`),
};

export const commentAPI = {
    // создание комментария
    createComment: (commentData) => api.post('/comment/', commentData),
    // получение комментариев к новости
    getCommentsByNews: (newsId) => api.get(`/comment/news/${newsId}`),
    // обновление комментария
    updateComment: (id, commentData) => api.put(`/comment/${id}`, commentData),
    // удаление комментария
    deleteComment: (id) => api.delete(`/comment/${id}`),
};

export default api;