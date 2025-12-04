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
});

// экспорт методов для работы с API

export const newsAPI = {
  // получение списка новостей
  getNewsList: () => api.get('/news/'),
  // получение одной новости по ID
  getNewsById: (id) => api.get(`/news/${id}`),
  // получение комментариев к новости
  getCommentsByNews: (newsId) => api.get(`/comment/news/${newsId}`),
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
  
  // получение информации о текущем пользователе
  getCurrentUser: () => api.get('/user/me'),
  
  // обновление пользователя
  updateUser: (userId, userData) => api.put(`/user/${userId}`, userData),
  
  // удаление пользователя (для админа)
  deleteUser: (userId) => api.delete(`/user/${userId}`),
};

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истек или невалиден
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;