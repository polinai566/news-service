import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
});

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
            console.log('Токен недействителен, требуется повторная авторизация');
            
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('session');
            localStorage.removeItem('user');
            localStorage.removeItem('userId');

            // если не на странице логина, перенаправление туда
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
        }
        
        return Promise.reject(error);
    }
);

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
  login: (email, password) => api.post('/session/', {
    email,
    password,
  }),
  // обновление токена
  refresh: (refreshToken) => api.put('/session/', {
    refresh_token: refreshToken,
  }),
  // выход
  logout: () => api.delete('/session/'),
};

export const userAPI = {
  // регистрация пользователя
  register: (userData) => api.post('/user/', userData),
  // получение пользователя по ID 
  getUserById: (userId) => api.get(`/user/${userId}`),
  // обновление пользователя
  updateUser: (userId, userData) => api.put(`/user/${userId}`, userData),
  // удаление пользователя (для админа)
  deleteUser: (userId) => api.delete(`/user/${userId}`),
};

export const commentAPI = {
    // создание комментария
    createComment: (commentData) => api.post('/comment/', commentData),
    // обновление комментария
    updateComment: (id, commentData) => api.put(`/comment/${id}`, commentData),
    // удаление комментария
    deleteComment: (id) => api.delete(`/comment/${id}`),
};

export default api;