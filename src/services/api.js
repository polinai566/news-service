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

export default api;