import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { newsAPI } from '../../api/index';
import { convertEditorJsToText } from '../../utils/convertEditorJsToText';
import { convertTextToEditorJs } from '../../utils/convertTextToEditorJs';
import { useAuth } from '../../context/AuthContext';
import './EditNewsPage.css';

function EditNewsPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user: currentUser, isAuthenticated, logout } = useAuth();
    
    const [header, setHeader] = useState('');
    const [content, setContent] = useState('');
    const [cover, setCover] = useState('');
    const [loading, setLoading] = useState(false);
    const [loadingNews, setLoadingNews] = useState(true);
    const [error, setError] = useState('');
    const [hasPermission, setHasPermission] = useState(true);

    useEffect(() => {
        if (!isAuthenticated || !currentUser) {
            setHasPermission(false);
            setLoadingNews(false);
            return;
        }

        if (!['admin', 'author'].includes(currentUser.user_role)) {
            setHasPermission(false);
            setLoadingNews(false);
            return;
        }
        
        // загрузка новости
        const fetchNews = async () => {
            try {
                const response = await newsAPI.getNewsById(id);
                const news = response.data;
                setOriginalNews(news);
                
                // проверка, является ли пользователь автором или админом
                if (currentUser.user_role !== 'admin' && currentUser.user_id !== news.author_id) {
                    setHasPermission(false);
                    setLoadingNews(false);
                    return;
                }
                
                // заполнение формы данными новости
                setHeader(news.header || '');
                
                // конвертация Editor.js контента в текст
                const textContent = convertEditorJsToText(news.content);
                setContent(textContent);
                setCover(news.cover || '');
                setLoadingNews(false);
            } catch (err) {
                console.error('Ошибка загрузки новости:', err);
                setError('Не удалось загрузить новость для редактирования');
                setLoadingNews(false);
            }
        };
        fetchNews();
    }, [id, currentUser, isAuthenticated]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!header.trim()) {
            setError('Заголовок обязателен');
            return;
        }

        if (!content.trim()) {
            setError('Текст новости обязателен');
            return;
        }

        try {
            setLoading(true);
            
            // преобразование обычного текста в формат Editor.js
            const editorJsContent = convertTextToEditorJs(content);
            
            const response = await newsAPI.updateNews(id, {
                header: header.trim(),
                content: editorJsContent,
                cover: cover.trim() || null
            });
            
            alert('Новость успешно обновлена!');
            navigate(`/news/${id}`);
        } catch (err) {
            console.error('Ошибка при обновлении новости:', err);
            
            if (err.response?.status === 401) {
                setError('Сессия истекла. Пожалуйста, войдите снова.');
                logout();
                setTimeout(() => navigate('/login'), 2000);
            } else if (err.response?.status === 403) {
                setError('У вас нет прав для редактирования этой новости');
            } else if (err.response?.status === 400) {
                setError('Некорректные данные: ' + (err.response.data?.detail || ''));
            } else if (err.response?.status === 404) {
                setError('Новость не найдена');
            } else {
                setError('Не удалось обновить новость. Попробуйте еще раз.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loadingNews) {
        return (
            <div className="edit-news-container">
                <h1>Загрузка...</h1>
            </div>
        );
    }

    if (!hasPermission) {
        return (
            <div className="edit-news-container">
                <div className="permission-error">
                    <h2>Доступ запрещен</h2>
                    <p>У вас нет прав для редактирования этой новости.</p>
                    <p>Только автор новости или администратор могут редактировать новость.</p>
                    <p>
                        <Link to={`/news/${id}`}>Вернуться к новости</Link>
                    </p>
                </div>
            </div>
        );
    }

    if (error && !header) {
        return (
            <div className="edit-news-container">
                <div className="error-message">{error}</div>
                <p>
                    <Link to={`/news/${id}`}>Вернуться к новости</Link>
                </p>
            </div>
        );
    }

    return (
        <div className="edit-news-container">
            <Link to={`/news/${id}`} className="back-link">← Назад к новости</Link>
            <h1>Редактирование новости</h1>
            
            <form onSubmit={handleSubmit} className="edit-news-form">
                <div className="form-group">
                    <label htmlFor="header">Заголовок:</label>
                    <input
                        id="header"
                        type="text"
                        value={header}
                        onChange={(e) => setHeader(e.target.value)}
                        required
                        placeholder="Введите заголовок новости"
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="content">Текст новости:</label>
                    <textarea
                        id="content"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        required
                        placeholder="Введите текст новости здесь..."
                        disabled={loading}
                        rows={12}
                    />
                    <div className="content-info">
                        Введите текст новости. Для создания нового абзаца оставьте пустую строку.
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="cover">Обложка (URL):</label>
                    <input
                        id="cover"
                        type="text"
                        value={cover}
                        onChange={(e) => setCover(e.target.value)}
                        placeholder="Введите URL изображения (опционально)"
                        disabled={loading}
                    />
                </div>

                {error && <div className="error-message">{error}</div>}

                <div className="form-actions">
                    <button 
                        type="button" 
                        className="cancel-btn"
                        onClick={() => navigate(`/news/${id}`)}
                        disabled={loading}
                    >
                        Отмена
                    </button>
                    <button 
                        type="submit" 
                        className="submit-btn"
                        disabled={loading}
                    >
                        {loading ? 'Сохранение...' : 'Сохранить изменения'}
                    </button>
                </div>
            </form>
        </div>
    );
}

export default EditNewsPage;