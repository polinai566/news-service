"""Add mock data

Revision ID: 90a3d95b9b36
Revises: 91ef940f81f3
Create Date: 2025-12-10 17:48:54.782714

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90a3d95b9b36"
down_revision: Union[str, Sequence[str], None] = "91ef940f81f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # создание пользователей
    op.execute(
        """
            INSERT INTO "user" (user_id, user_name, email, registration_date, is_verified, avatar)
            VALUES  (0, 'Ivan', 'ivan@gmail.com', '2025-10-01 18:00:00', true, 'ivan_avatar.jpg'),
                    (1, 'Maria', 'maria@gmail.com', '2025-10-01 16:00:00', false, 'maria_avatar.jpg')
        """
    )
    # создание новости
    op.execute(
        """
            INSERT INTO news (news_id, header, content, publication_date, author_id, cover)
            VALUES  (0, 'Пропажа ключей в ИТМО', '{"blocks": [{"type": "paragraph", "text": "Сегодня в ИТМО пропали ключи от 306 аудитории..."}]}', '2025-10-01 22:00:00', 0, 'news_cover.jpg')
        """
    )
    # создание комментария
    op.execute(
        """
            INSERT INTO comment (comment_id, text, news_id, author_id, publication_date)
            VALUES (0, 'Ключи были найдены под столом в 311 аудитории!', 0, 1, '2025-10-02 15:00:00')
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    # удаление комментария
    op.execute("""DELETE FROM comment WHERE comment_id = 0""")
    # удаление новости
    op.execute("""DELETE FROM news WHERE news_id = 0""")
    # удаление пользователей
    op.execute("""DELETE FROM "user" WHERE user_id IN (0, 1)""")
