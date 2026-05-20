from src.ragforge.core.config import get_settings


class BaseMongoStore:
    """
    Base class for MongoDB store classes.

    Store classes are responsible for database operations only.
    They should not contain route logic or business workflow logic.
    """

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_settings()