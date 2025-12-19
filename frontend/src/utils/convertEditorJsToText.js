export const convertEditorJsToText = (editorJsContent) => {
    if (!editorJsContent) return '';

    let blocks = [];

    if (Array.isArray(editorJsContent)) {
        blocks = editorJsContent;
    } else if (editorJsContent.blocks && Array.isArray(editorJsContent.blocks)) {
        blocks = editorJsContent.blocks;
    } else {
        return String(editorJsContent);
    }

    const paragraphs = [];
    let currentParagraph = [];

    blocks.forEach((block, index) => {
        if (block.type === 'paragraph' && block.text) {
            currentParagraph.push(block.text);
        } else if (block.type === 'delimiter') {
            if (currentParagraph.length > 0) {
                paragraphs.push(currentParagraph.join('\n'));
                currentParagraph = [];
            }
        } else if (block.type === 'header' && block.text) {
            if (currentParagraph.length > 0) {
                paragraphs.push(currentParagraph.join('\n'));
                currentParagraph = [];
            }
            // заголовки как отдельные строки
            paragraphs.push(block.text);
        }

        // если последний блок - не разделитель, добавляем текущий параграф
        if (index === blocks.length - 1 && currentParagraph.length > 0) {
            paragraphs.push(currentParagraph.join('\n'));
        }
    });

    return paragraphs.join('\n\n');
};