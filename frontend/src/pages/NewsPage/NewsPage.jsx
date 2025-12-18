import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { newsAPI, commentAPI } from '../../api/index';
import NewsCard from '../../components/NewsCard/NewsCard';
import CommentCard from '../../components/CommentCard/CommentCard';
import CommentForm from '../../components/CommentForm/CommentForm';
import { renderFullContent } from '../../utils/editorjsParser';
import './NewsPage.css';

function NewsPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [news, setNews] = useState(null);
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [commentLoading, setCommentLoading] = useState(false);
    const [error, setError] = useState(null);
    const [currentUser, setCurrentUser] = useState(null);

    // получение текущего пользователя из localStorage
    useEffect(() => {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                setCurrentUser(JSON.parse(userStr));
            } catch (e) {
                console.error('Ошибка при чтении пользователя из localStorage:', e);
            }
        }
    }, []);

    // загрузка новости и комментариев
    useEffect(() => {
        const fetchNewsData = async () => {
            try {
                setLoading(true);
                const newsResponse = await newsAPI.getNewsById(id);
                setNews(newsResponse.data);

                try {
                    const commentsResponse = await newsAPI.getCommentsByNews(id);
                    setComments(commentsResponse.data);
                } catch (commentErr) {
                    console.warn('Не удалось загрузить комментарии:', commentErr);
                    setComments([]);
                }

                setLoading(false);
            } catch (err) {
                console.error('Ошибка загрузки новости:', err);
                setError('Не удалось загрузить новость');
                setLoading(false);
            }
        };

        fetchNewsData();
    }, [id]);

    // обработчик добавления комментария
    const handleAddComment = async (text) => {
        if (!currentUser) {
            navigate('/login');
            return;
        }

        setCommentLoading(true);
        try {
            const response = await commentAPI.createComment({
                news_id: parseInt(id),
                text: text
            });

            // добавляем новый комментарий в начало списка
            setComments([response.data, ...comments]);
        } catch (err) {
            console.error('Ошибка при создании комментария:', err);

            if (err.response?.status === 401) {
                // токен недействителен, перенаправляем на логин
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                navigate('/login');
                alert('Сессия истекла. Пожалуйста, войдите снова.');
            } else {
                alert('Не удалось добавить комментарий. Проверьте ваши права доступа.');
            }
            throw err;
        } finally {
            setCommentLoading(false);
        }
    };

    // обработчик редактирования комментария
    const handleEditComment = async (commentId, newText) => {
        try {
            const response = await commentAPI.updateComment(commentId, {
                text: newText
            });

            // Обновляем комментарий в списке
            setComments(comments.map(comment =>
                comment.comment_id === commentId ? response.data : comment
            ));
        } catch (err) {
            console.error('Ошибка при редактировании комментария:', err);

            if (err.response?.status === 401) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                navigate('/login');
                alert('Сессия истекла. Пожалуйста, войдите снова.');
            } else if (err.response?.status === 403) {
                alert('У вас нет прав для редактирования этого комментария');
            } else {
                alert('Не удалось отредактировать комментарий');
            }
            throw err;
        }
    };

    // обработчик удаления комментария
    const handleDeleteComment = async (commentId) => {
        try {
            await commentAPI.deleteComment(commentId);

            // удаление комментария из списка
            setComments(comments.filter(comment => comment.comment_id !== commentId));
        } catch (err) {
            console.error('Ошибка при удалении комментария:', err);

            if (err.response?.status === 401) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                navigate('/login');
                alert('Сессия истекла. Пожалуйста, войдите снова.');
            } else if (err.response?.status === 403) {
                alert('У вас нет прав для удаления этого комментария');
            } else {
                alert('Не удалось удалить комментарий');
            }
        }
    };

    // обработчик удаления новости
    const handleDeleteNews = async () => {
        if (!window.confirm('Вы уверены, что хотите удалить эту новость? Это действие нельзя отменить.')) {
            return;
        }

        try {
            await newsAPI.deleteNews(id);
            alert('Новость успешно удалена');
            navigate('/');
        } catch (err) {
            console.error('Ошибка при удалении новости:', err);

            if (err.response?.status === 401) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                navigate('/login');
                alert('Сессия истекла. Пожалуйста, войдите снова.');
            } else if (err.response?.status === 403) {
                alert('У вас нет прав для удаления этой новости');
            } else {
                alert('Не удалось удалить новость');
            }
        }
    };

    if (loading) {
        return (
            <div className="news-page-container">
                <h1>Загрузка новости...</h1>
            </div>
        );
    }

    if (error) {
        return (
            <div className="news-page-container">
                <h1>Ошибка</h1>
                <p>{error}</p>
            </div>
        );
    }

    if (!news) {
        return (
            <div className="news-page-container">
                <h1>Новость не найдена</h1>
            </div>
        );
    }

    const isAdmin = currentUser?.user_role === 'admin';
    const isNewsAuthor = currentUser?.user_id === news.author_id;
    const canEditNews = isAdmin || isNewsAuthor;

    return (
        <div className="news-page-container">
            <NewsCard
                news={news}
                showCover={false}
                showPreview={false}
                goAhead={false}
            />

            {canEditNews && (
                <div className="news-management" style={{ marginTop: '1rem', marginBottom: '2rem' }}>
                    <div className="news-actions" style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                            onClick={() => navigate(`/news/${id}/edit`)}
                            className="news-edit-btn"
                            style={{
                                padding: '0.5rem 1rem',
                                backgroundColor: '#646cff',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            ✏️ Редактировать новость
                        </button>
                        <button
                            onClick={handleDeleteNews}
                            className="news-delete-btn"
                            style={{
                                padding: '0.5rem 1rem',
                                backgroundColor: '#ff6b6b',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            🗑️ Удалить новость
                        </button>
                    </div>
                </div>
            )}

            <div className="news-content-full">
                <h2>Содержание</h2>
                <div className="news-content-body">
                    {renderFullContent(news.content)}
                </div>
            </div>

            <div className="comments-section">
                <h2>Комментарии ({comments.length})</h2>

                <CommentForm
                    onSubmit={handleAddComment}
                    isAuthenticated={!!currentUser}
                    loading={commentLoading}
                />

                {comments.length === 0 ? (
                    <div className="no-comments">
                        <p>Комментариев пока нет. Будьте первым!</p>
                    </div>
                ) : (
                    <div className="comments-list">
                        {comments.map((comment) => (
                            <CommentCard
                                key={comment.comment_id}
                                comment={comment}
                                currentUser={currentUser}
                                onEdit={handleEditComment}
                                onDelete={handleDeleteComment}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default NewsPage;