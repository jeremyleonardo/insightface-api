import app.logger as log
from app.models import Base
from app.settings import RECREATE_TABLES_EACH_RUN


def create_database(engine):

    if RECREATE_TABLES_EACH_RUN:
        try:
            log.debug("Dropping tables.")
            Base.metadata.drop_all(engine)
        except Exception as exc:
            log.error("Failed to drop tables.")
            log.error(exc)
    
    try:
        log.debug("Creating tables.")
        Base.metadata.create_all(engine)
    except Exception as exc:
        log.error("Failed to create tables.")
        log.error(exc)
