import app.logger as log
import app.settings as settings
from app.database.models import Base


def init(engine):

    if settings.DROP_ALL_EACH_RUN:
        try:
            log.debug("Dropping tables.")
            Base.metadata.drop_all(engine)
        except Exception as exc:
            log.error("Failed to drop tables.")
            log.error(exc)
    
    if settings.CREATE_ALL_EACH_RUN:
        try:
            log.debug("Creating extension cube.")
            engine.execute("create extension cube;")
        except Exception as exc:
            pass
        try:
            log.debug("Creating tables.")
            Base.metadata.create_all(engine)
        except Exception as exc:
            log.error("Failed to create tables.")
            log.error(exc)