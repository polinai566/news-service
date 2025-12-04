import React from 'react';
import './CommentCard.css';

function CommentCard({comment}) {
    return (
        <div key={comment.comment_id} className="comment-card">
            <div className="comment-meta">
                <span>
                    👤 Пользователь: {comment.author.user_name}
                </span>
                <span>
                    📅 {new Date(comment.publication_date).toLocaleDateString('ru-RU')}
                </span>
            </div>
            <div className="comment-content">
                {comment.text}
            </div>
        </div>
    )
}

export default CommentCard;