import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './CommentForm.css';

function CommentForm({ onSubmit, isAuthenticated, loading = false }) {
    const [text, setText] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!text.trim()) {
            setError('Комментарий не может быть пустым');
            return;
        }

        try {
            await onSubmit(text);
            setText('');
        } catch (err) {
            setError('Не удалось добавить комментарий. Попробуйте еще раз.');
            console.error('Ошибка при добавлении комментария:', err);
        }
    };

    if (!isAuthenticated) {
        return (
            <div className="login-prompt">
                <p>Чтобы оставить комментарий, <Link to="/login">войдите</Link> или <Link to="/signup">зарегистрируйтесь</Link></p>
            </div>
        );
    }

    return (
        <div className="comment-form-container">
            <h3>Добавить комментарий</h3>
            <form onSubmit={handleSubmit} className="comment-form">
        <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Напишите ваш комментарий..."
            className="comment-textarea"
            disabled={loading}
        />
                {error && <div className="comment-error">{error}</div>}
                <button
                    type="submit"
                    className="comment-submit-btn"
                    disabled={loading || !text.trim()}
                >
                    {loading ? 'Отправка...' : 'Отправить'}
                </button>
            </form>
        </div>
    );
}

export default CommentForm;