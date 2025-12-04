import React from 'react';

export function getContentPreview(content, maxLength = 150) {
    if (!content) return 'Нет содержания';
    
    if (typeof content === 'string') {
        return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
    }
    
    if (content.blocks && Array.isArray(content.blocks)) {
        const firstParagraph = content.blocks.find(block => 
            block.type === 'paragraph' || block.type === 'text'
        );
        
        if (firstParagraph && firstParagraph.text) {
            const text = firstParagraph.text;
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        }
        
        const firstHeader = content.blocks.find(block => 
            block.type === 'header' || block.type === 'heading'
        );
        
        if (firstHeader && firstHeader.text) {
            return firstHeader.text;
        }
        
        return '[Текст новости]';
    }
    
    return '[Содержимое новости]';
}

export function renderFullContent(content) {
    if (!content) {
        return <p>Контент недоступен</p>;
    }

    if (typeof content === 'string') {
        return (
            <div className="news-content-text">
                {content.split('\n').map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                ))}
            </div>
        );
    }

    if (content.blocks && Array.isArray(content.blocks)) {
        return (
            <div className="news-content-editorjs">
                {content.blocks.map((block, index) => {
                    switch (block.type) {
                        case 'header':
                        case 'heading':
                            const level = block.level || 2;
                            const HeaderTag = `h${level}`;
                            return <HeaderTag key={index} className="news-header">{block.text}</HeaderTag>;
                        
                        case 'paragraph':
                        case 'text':
                            return <p key={index} className="news-paragraph">{block.text}</p>;
                        
                        case 'list':
                            const ListTag = block.style === 'ordered' ? 'ol' : 'ul';
                            return (
                                <ListTag key={index} className="news-list">
                                    {block.items.map((item, i) => (
                                        <li key={i}>{item}</li>
                                    ))}
                                </ListTag>
                            );
                        
                        case 'image':
                            return (
                                <div key={index} className="news-image-block">
                                    <img 
                                        src={block.file?.url || block.url} 
                                        alt={block.caption || 'Изображение'} 
                                        className="news-image"
                                    />
                                    {block.caption && <p className="image-caption">{block.caption}</p>}
                                </div>
                            );
                        
                        case 'quote':
                            return (
                                <blockquote key={index} className="news-quote">
                                    {block.text}
                                    {block.caption && <cite>— {block.caption}</cite>}
                                </blockquote>
                            );
                        
                        default:
                            return (
                                <div key={index} className="news-unknown-block">
                                    [Неизвестный тип блока: {block.type}]
                                </div>
                            );
                    }
                })}
            </div>
        );
    }

    return <p>[Формат контента не поддерживается]</p>;
}