// функция преобразования обычного текста в формат Editor.js
export const convertTextToEditorJs = (text) => {
    // разбиение текста на абзацы (по пустым строкам)
    const paragraphs = text.split(/\n\s*\n/);

    const blocks = [];

    paragraphs.forEach(paragraph => {
        const lines = paragraph.split('\n').filter(line => line.trim() !== '');

        lines.forEach(line => {
            blocks.push({
                type: "paragraph",
                text: line.trim()
            });
        });

        // добавление разделителя между абзацами
        if (blocks.length > 0 && paragraph.trim() !== '') {
            blocks.push({
                type: "delimiter",
                data: {}
            });
        }
    });

    // удаление последнего разделителя, если он есть
    if (blocks.length > 0 && blocks[blocks.length - 1].type === "delimiter") {
        blocks.pop();
    }

    // добавление пустого параграфа, если текст пустой
    if (blocks.length === 0) {
        blocks.push({
            type: "paragraph",
            text: ""
        });
    }

    return {
        blocks: blocks
    };
};