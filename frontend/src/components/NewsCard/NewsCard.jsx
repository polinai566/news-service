import React from 'react';
import { Link } from 'react-router-dom';
import { getContentPreview } from '../../utils/editorjsParser';
import './NewsCard.css';

function NewsCard({ news, showCover = true, showPreview = true, goAhead = true }) {
    return (
        <div className="news-card">

            <h2>
                <Link to={`/news/${news.news_id}`}>
                    {news.header}
                </Link>
            </h2>

            <div className="news-meta">
                <span className="date">
                    📅 {new Date(news.publication_date).toLocaleDateString('ru-RU')}
                </span>
                <span className="time">
                    🕐 {new Date(news.publication_date).toLocaleTimeString('ru-RU', {
                    hour: '2-digit',
                    minute: '2-digit'
                })}
                </span>
                <span className="author">
                    👤 Автор: {news.author.user_name}
                </span>
            </div>

            {showCover && news.cover && (
                <div className="cover-container">
                    <img
                        src={`http://localhost:8000/static/${news.cover}`}
                        alt={news.header}
                        className="news-cover"
                        onError={(e) => {
                            e.target.style.display = 'none';
                        }}
                    />
                </div>
            )}

            {showPreview && (
                <div className="content-preview">
                    <p>{getContentPreview(news.content, 150)}</p>
                </div>
            )}

            {goAhead ? (
                <Link to={`/news/${news.news_id}`} className="read-more">
                    📖 Посмотреть обсуждение →
                </Link>
            ) : (
                <Link to={`/`} className="read-more">
                    📖 ← К списку новостей
                </Link>
            )}
        </div>
    );
}

export default NewsCard;