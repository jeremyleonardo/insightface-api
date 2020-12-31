import app.logger as log
import app.settings as settings
from time import sleep

def wait(engine):
    # Wait until database ready
    # Sometimes postgres is not ready yet because it needs to restart at init

    if(settings.SKIP_DATABASE_CONNECTION_TEST is False):
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