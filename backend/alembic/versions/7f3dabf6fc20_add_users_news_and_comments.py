"""Add users, news and comments

Revision ID: 7f3dabf6fc20
Revises: b23414ed92bc
Create Date: 2025-11-09 12:30:17.365358

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7f3dabf6fc20'
down_revision: Union[str, Sequence[str], None] = 'b23414ed92bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # создание пользователей
    op.execute(
        '''
            INSERT INTO "user" (user_id, user_name, email, registration_date, avatar, user_role, password)
            VALUES
                    (1, 'polina', 'polina@mail.ru', '2025-11-05 00:00:00', 'polina_ava.jpg', 'admin', '$argon2id$v=19$m=65536,t=3,p=4$U080gdtNdY2QEbp3K5olsA$d6OS6ZzUCBSDDFHKWN/1ba2ZVkkpluwnl5jbTIdvVjw'),
                    (2, 'mitya', 'mitya@mail.ru', '2025-11-05 01:00:00', 'mitya_ava.jpg', 'author', '$argon2id$v=19$m=65536,t=3,p=4$buZBbG9zDDo5CgOgCbD22w$Xx78I9aX3VgF2pYwH3Seim3ojgWWoRbCTNyqK/t+nPE'),
                    (3, 'danya', 'danya@mail.ru', '2025-11-05 02:00:00', 'danya_ava.jpg', 'user', '$argon2id$v=19$m=65536,t=3,p=4$zO1CdR9CsRBnACV460z7+Q$WuCaZzWpy1/NWJyXn+w3DO5HSYfH8uqPmiMouKtvjwc')
        '''
    )
    # создание новости
    op.execute(
        '''
            INSERT INTO news (news_id, header, content, publication_date, author_id, cover)
            VALUES (1, 'Пропажа ключей в ИТМО', '{"blocks": [{"type": "paragraph", "text": "Сегодня в ИТМО на Песочке пропали ключи от 306 аудитории... Из-за этого отменили все лекции"}]}', '2025-11-05 15:00:00', 2, 'news_cover.jpg')
        '''
    )
    # создание комментариев
    op.execute(
        '''
            INSERT INTO comment (comment_id, text, news_id, author_id, publication_date)
            VALUES (1, 'Ура, лекций больше не будет!', 1, 3, '2025-11-05 16:00:00'),
            (2, 'Нет, будут. Ключи были найдены под столом в 311 аудитории!', 1, 2, '2025-11-06 09:00:00')
        '''
    )
    # обновление последовательностей
    op.execute("SELECT setval('user_user_id_seq', (SELECT MAX(user_id) FROM \"user\"))")
    op.execute("SELECT setval('news_news_id_seq', (SELECT MAX(news_id) FROM news))")
    op.execute("SELECT setval('comment_comment_id_seq', (SELECT MAX(comment_id) FROM comment))")

def downgrade() -> None:
    """Downgrade schema."""
    # удаление всех сессий
    op.execute('''TRUNCATE TABLE "session" CASCADE''')
    # удаление всех комментариев
    op.execute('''TRUNCATE TABLE comment CASCADE''')
    # удаление всех новостей
    op.execute('''TRUNCATE TABLE news CASCADE''')
    # удаление всех пользователей
    op.execute('''TRUNCATE TABLE "user" CASCADE''')