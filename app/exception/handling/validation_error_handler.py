import app.logger as log
from . import get_error_response

def not_found_error_handler(request, exc):
    log.error(str(exc))
    json_resp = get_error_response(status_code=404, message=str(exc))
    return json_resp