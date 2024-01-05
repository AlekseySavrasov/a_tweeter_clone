from os import getenv
from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr, StrictStr

load_dotenv()


class SiteSettings(BaseSettings):
    """Класс SiteSettings. Родитель: BaseSettings.
    Содержит атрибуты в которых хранится информация о скрытых данных из среды окружения
    """
    database_user: SecretStr = getenv("POSTGRES_USER", None)
    database_psw: SecretStr = getenv("POSTGRES_PASSWORD", None)
    database_db: StrictStr = getenv("POSTGRES_DB", None)


site: SiteSettings = SiteSettings()
