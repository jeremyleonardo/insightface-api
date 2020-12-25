import app.logger as log
from app.models import Base
import app.settings as settings


def create_database(engine):

    if settings.DROP_ALL_EACH_RUN == 'True':
        try:
            log.debug("Dropping tables.")
            Base.metadata.drop_all(engine)
        except Exception as exc:
            log.error("Failed to drop tables.")
            log.error(exc)
    
    if settings.CREATE_ALL_EACH_RUN == 'True':
        try:
            log.debug("Creating tables.")
            Base.metadata.create_all(engine)
        except Exception as exc:
            log.error("Failed to create tables.")
            log.error(exc)
