from os import getenv
from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr, StrictStr

load_dotenv()


class SiteSettings(BaseSettings):
    """Класс SiteSettings. Родитель: BaseSettings.
    Содержит атрибуты в которых хранится информация о скрытых данных из среды окружения

    Attributes:
        db_host (SecretStr): хост для бд
    """
    db_host: SecretStr = getenv("DB_HOST", None)
    db_port: SecretStr = getenv("DB_PORT", None)
    db_name: SecretStr = getenv("DB_NAME", None)
    db_user: SecretStr = getenv("DB_USER", None)
    db_pass: SecretStr = getenv("DB_PASS", None)

    db_host_test: SecretStr = getenv("DB_HOST_TEST", None)
    db_port_test: SecretStr = getenv("DB_PORT_TEST", None)
    db_name_test: SecretStr = getenv("DB_NAME_TEST", None)
    db_user_test: SecretStr = getenv("DB_USER_TEST", None)
    db_pass_test: SecretStr = getenv("DB_PASS_TEST", None)


site: SiteSettings = SiteSettings()
