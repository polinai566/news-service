import React from 'react';

export function getContentPreview(content, maxLength = 150) {
    if (!content) return 'Нет содержания';

    if (typeof content === 'string') {
        return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
    }

    let blocks = [];

    if (Array.isArray(content)) {
        blocks = content;
    } else if (content.blocks && Array.isArray(content.blocks)) {
        blocks = content.blocks;
    }

    if (blocks.length > 0) {
        const firstParagraph = blocks.find(block =>
            block.type === 'paragraph'
        );

        if (firstParagraph && firstParagraph.text !== undefined) {
            const text = firstParagraph.text;
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        }

        const firstHeader = blocks.find(block =>
            block.type === 'header'
        );

        if (firstHeader && firstHeader.text !== undefined) {
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

    let blocks = [];

    if (Array.isArray(content)) {
        blocks = content;
    } else if (content.blocks && Array.isArray(content.blocks)) {
        blocks = content.blocks;
    }

    if (!blocks.length) {
        return <p>[Контент пуст]</p>;
    }

    return (
        <div className="news-content-editorjs">
            {blocks.map((block, index) => {
                console.log('Обрабатываем блок:', block);

                switch (block.type) {
                    case 'header':
                        const level = block.level || 2;
                        const HeaderTag = `h${level}`;
                        const headerText = block.text || '';
                        return <HeaderTag key={index} className="news-header">{headerText}</HeaderTag>;

                    case 'paragraph':
                        const paragraphText = block.text || '';
                        return <p key={index} className="news-paragraph">{paragraphText}</p>;

                    case 'delimiter':
                        return <hr key={index} className="news-delimiter" />;

                    case 'list':
                        const listStyle = block.style || 'unordered';
                        const ListTag = listStyle === 'ordered' ? 'ol' : 'ul';
                        const items = block.items || [];
                        return (
                            <ListTag key={index} className="news-list">
                                {items.map((item, i) => (
                                    <li key={i}>{item}</li>
                                ))}
                            </ListTag>
                        );

                    case 'image':
                        const imageUrl = block.url || '';
                        const caption = block.caption || '';
                        return (
                            <div key={index} className="news-image-block">
                                {imageUrl && <img
                                    src={imageUrl}
                                    alt={caption || 'Изображение'}
                                    className="news-image"
                                />}
                                {caption && <p className="image-caption">{caption}</p>}
                            </div>
                        );

                    case 'quote':
                        const quoteText = block.text || '';
                        const quoteCaption = block.caption || '';
                        return (
                            <blockquote key={index} className="news-quote">
                                <p>{quoteText}</p>
                                {quoteCaption && <cite>— {quoteCaption}</cite>}
                            </blockquote>
                        );

                    default:
                        console.warn('Неизвестный тип блока:', block.type);
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