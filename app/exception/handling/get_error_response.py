from fastapi.responses import JSONResponse

def get_error_response(status_code, message):
    return JSONResponse(status_code=status_code, content={
        "status_code": status_code,
        "message": message
        })