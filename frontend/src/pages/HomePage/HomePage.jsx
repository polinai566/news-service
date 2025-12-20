import React, { useState, useEffect } from 'react';
import { newsAPI } from '../../api/index.js';
import NewsCard from '../../components/NewsCard/NewsCard.jsx';
import './HomePage.css';

function HomePage() {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchNews = async () => {
            try {
                const response = await newsAPI.getNewsList();
                setNews(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Ошибка загрузки новостей:', err);
                setError('Не удалось загрузить новости');
                setLoading(false);
            }
        };

        fetchNews();
    }, []);

    if (loading) {
        return (
            <div className="home-container">
                <h1>Новости</h1>
                <div className="loading">Загрузка...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="home-container">
                <h1>Новости</h1>
                <div className="error-message">
                    <p>{error}</p>
                    <button 
                        onClick={() => window.location.reload()} 
                        className="retry-btn"
                    >
                        Попробовать снова
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="home-container">
            <h1>Новости</h1>
            <div className="news-list">
                {news.length === 0 ? (
                    <div className="no-news">
                        <p>Новостей пока нет. Будьте первым, кто добавит новость!</p>
                    </div>
                ) : (
                    news.map((item) => (
                        <NewsCard 
                            key={item.news_id} 
                            news={item}
                            showCover={true}
                            showPreview={true}
                            goAhead={true}
                        />
                    ))
                )}
            </div>
        </div>
    );
}

export default HomePage;