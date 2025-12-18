import React, { useState } from 'react';
import './Avatar.css';

function Avatar({ src, alt, size = 'medium', className = '' }) {
    const [imageError, setImageError] = useState(false);

    const getInitial = (name) => {
        if (!name || name.trim().length === 0) return '?';
        return name.trim()[0].toUpperCase();
    };

    const getColor = (name) => {
        if (!name) return '#007bff';

        const colors = [
            '#007bff', '#28a745', '#dc3545', '#fd7e14', '#6f42c1',
            '#20c997', '#17a2b8', '#ffc107', '#e83e8c', '#6c757d'
        ];

        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    };

    if (src && !imageError) {
        return (
            <img
                src={src}
                alt={alt}
                className={`avatar avatar-${size} ${className}`}
                onError={() => setImageError(true)}
            />
        );
    }

    return (
        <div
            className={`avatar avatar-fallback avatar-${size} ${className}`}
            style={{ backgroundColor: getColor(alt) }}
            title={alt}
        >
            {getInitial(alt)}
        </div>
    );
}

export default Avatar;