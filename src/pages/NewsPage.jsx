// frontend/src/pages/NewsPage.jsx
import React from 'react';
import { useParams } from 'react-router-dom';
import './NewsPage.css';

function NewsPage() {
    const { id } = useParams();

    return (
        <div className="news-container">
            <h1>Страница новости #{id}</h1>
            <div className="news-content">
                <p>Здесь будет содержимое новости и комментарии</p>
                <div className="news-details">
                    <p><strong>Дата публикации:</strong> Скоро загрузится...</p>
                    <p><strong>Автор:</strong> Скоро загрузится...</p>
                </div>
            </div>
        </div>
    );
}

export default NewsPage;