import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { newsAPI } from '../../api/index';
import NewsCard from '../../components/NewsCard/NewsCard';
import CommentCard from '../../components/CommentCard/CommentCard';
import { renderFullContent } from '../../utils/editorjsParser';
import './NewsPage.css';

function NewsPage() {
    const { id } = useParams();
    const [news, setNews] = useState(null);
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    return (
        <div className="news-page-container">

            <NewsCard 
                news={news} 
                showCover={false} 
                showPreview={false}
                goAhead={false}
            />
            
            <div className="news-content-full">
                <h2>Содержание</h2>
                <div className="news-content-body">
                    {renderFullContent(news.content)}
                </div>
            </div>
            
            <div className="comments-section">
                <h2>Комментарии ({comments.length})</h2>
                {comments.length === 0 ? (
                    <div className="no-comments">
                        <p>Комментариев пока нет. Будьте первым!</p>
                    </div>
                ) : (
                    <div className="comments-list">
                        {comments.map((item) => (
                            <CommentCard comment={item}/>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default NewsPage;