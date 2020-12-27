import app.logger as log
from app.models import Base
import app.settings as settings
from time import sleep


def create_database(engine):

    if settings.DROP_ALL_EACH_RUN:
        try:
            log.debug("Dropping tables.")
            Base.metadata.drop_all(engine)
        except Exception as exc:
            log.error("Failed to drop tables.")
            log.error(exc)
    
    if settings.CREATE_ALL_EACH_RUN:
        try:
            log.debug("Creating tables.")
            Base.metadata.create_all(engine)
        except Exception as exc:
            log.error("Failed to create tables.")
            log.error(exc)


def wait_database(engine):
    # Wait until database ready
    # Sometimes postgres is not ready yet because it needs to restart at init

    if(settings.SKIP_DATABASE_CONNECTION_TEST):
        success = 0
        for i in range(30):
            sleep(2)
            try:
                engine.execute('select 1')
            except Exception as exc:
                log.info("Waiting for database.")
            else:
                success += 1
                log.info("Database connection tested.")
            if(success == 3): 
                log.info("Connection with database established.")
                break
        