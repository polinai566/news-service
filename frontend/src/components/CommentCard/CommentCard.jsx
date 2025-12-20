import React, { useState } from 'react';
import Avatar from '../Avatar/Avatar.jsx';
import './CommentCard.css';

function CommentCard({comment, currentUser, onDelete, onEdit}) {
    const [isEditing, setIsEditing] = useState(false);
    const [editedText, setEditedText] = useState(comment.text);
    const [loading, setLoading] = useState(false);

    // проверка прав доступа
    const isAdmin = currentUser?.user_role === 'admin';
    const isAuthor = currentUser?.user_id === comment.author_id;
    const canEdit = isAdmin || isAuthor;
    const canDelete = isAdmin || isAuthor;

    const handleSave = async () => {
        if (!editedText.trim() || editedText === comment.text) {
            setIsEditing(false);
            return;
        }
        setLoading(true);
        try {
            await onEdit(comment.comment_id, editedText);
            setIsEditing(false);
        } catch (error) {
            console.error('Ошибка при сохранении комментария:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        setEditedText(comment.text);
        setIsEditing(false);
    };

    const handleDelete = () => {
        if (window.confirm('Вы уверены, что хотите удалить этот комментарий?')) {
            onDelete(comment.comment_id);
        }
    };

	const getAvatarUrl = (avatar) => {
        if (!avatar) return null;
        if (avatar.startsWith('http')) return avatar;
        return `http://localhost:8000/static/${avatar}`;
    };

    return (
	    <div className={`comment-card ${isEditing ? 'comment-editing' : ''}`}>
	    	<div className="comment-meta">
	    		<div className="author-info">
	    			<Avatar
                        src={getAvatarUrl(comment.author?.avatar)}
                        alt={comment.author?.user_name || 'Автор'}
                        size="small"
                        className="author-avatar"
                    />
	    			<span className="author-name">
	    				{comment.author.user_name}
	    				{comment.author.user_role === 'admin' && (
	    					<span className="admin-badge" style={{ marginLeft: '0.5rem' }}>Админ</span>
	    				)}
	    			</span>
	    		</div>
	    		<span className="comment-date">
	    			📅 {new Date(comment.publication_date).toLocaleDateString('ru-RU')}
	    			{' '}
	    			🕐 {new Date(comment.publication_date).toLocaleTimeString('ru-RU', {
	    				hour: '2-digit',
	    				minute: '2-digit'
	    			})}
	    		</span>
	    	</div>

	    	{isEditing ? (
	    		<>
	    			<textarea
	    				value={editedText}
	    				onChange={(e) => setEditedText(e.target.value)}
	    				className="edit-textarea"
	    				disabled={loading}
	    			/>
	    			<div className="edit-actions">
	    				<button 
	    					onClick={handleSave} 
	    					className="save-btn"
	    					disabled={loading || !editedText.trim()}
	    				>
	    					{loading ? 'Сохранение...' : 'Сохранить'}
	    				</button>
	    				<button 
	    					onClick={handleCancel} 
	    					className="cancel-btn"
	    					disabled={loading}
	    				>
	    					Отмена
	    				</button>
	    			</div>
	    		</>
	    	) : (
	    		<>
	    			<div className="comment-content">
	    				{comment.text}
	    			</div>
            
	    			{canEdit && (
	    				<div className="comment-actions">
	    					{(canEdit || canDelete) && (
	    						<>
	    							<button 
	    								onClick={() => setIsEditing(true)}
	    								className="comment-edit-btn"
	    							>
	    								✏️ Редактировать
	    							</button>
	    							<button 
	    								onClick={handleDelete}
	    								className="comment-delete-btn"
	    							>
	    								🗑️ Удалить
	    							</button>
	    						</>
	    					)}
	    				</div>
	    			)}
	    		</>
	    	)}
	    </div>
    );
}

export default CommentCard;