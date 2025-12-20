import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { newsAPI } from '../../api/index.js';
import { convertTextToEditorJs } from '../../utils/convertTextToEditorJs.js'
import './CreateNewsPage.css';

function CreateNewsPage() {
    const [header, setHeader] = useState('');
    const [content, setContent] = useState('');
    const [cover, setCover] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [currentUser, setCurrentUser] = useState(null);
    const [hasPermission, setHasPermission] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const userStr = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        
        if (!userStr || !token) {
            setHasPermission(false);
            return;
        }

        try {
            const user = JSON.parse(userStr);
            setCurrentUser(user);
            
            const tokenParts = token.split('.');
            if (tokenParts.length === 3) {
                const payload = JSON.parse(atob(tokenParts[1]));
                const userRole = payload.user_role;

                if (!['admin', 'author'].includes(userRole)) {
                    setHasPermission(false);
                }
            }
        } catch (e) {
            console.error('Ошибка при проверке прав:', e);
            setHasPermission(false);
        }
    }, []);

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
            
            // преобразование обычного текста в упрощенный формат Editor.js
            const editorJsContent = convertTextToEditorJs(content);
            
            const response = await newsAPI.createNews({
                header: header.trim(),
                content: editorJsContent,
                cover: cover.trim() || null
            });
            
            alert('Новость успешно создана!');
            navigate(`/news/${response.data.news_id}`);
        } catch (err) {
            console.error('Ошибка при создании новости:', err);
            
            if (err.response?.status === 401) {
                setError('Сессия истекла. Пожалуйста, войдите снова.');
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                setTimeout(() => navigate('/login'), 2000);
            } else if (err.response?.status === 403) {
                setError('У вас нет прав для создания новостей');
            } else if (err.response?.status === 400) {
                setError('Некорректные данные: ' + (err.response.data?.detail || ''));
            } else {
                setError('Не удалось создать новость. Попробуйте еще раз.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (!hasPermission) {
        return (
            <div className="create-news-container">
                <div className="permission-error">
                    <h2>Доступ запрещен</h2>
                    <p>У вас нет прав для создания новостей.</p>
                    <p>Только пользователи с ролями "admin" или "author" могут создавать новости.</p>
                    <p>
                        <Link to="/">Вернуться на главную</Link>
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="create-news-container">
            <Link to="/" className="back-link">← Назад к списку новостей</Link>
            <h1>Создание новости</h1>
            
            <form onSubmit={handleSubmit} className="create-news-form">
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

                <button 
                    type="submit" 
                    className="submit-btn"
                    disabled={loading}
                >
                    {loading ? 'Создание...' : 'Создать новость'}
                </button>
            </form>
        </div>
    );
}

export default CreateNewsPage;