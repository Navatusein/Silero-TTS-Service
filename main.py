import uvicorn

from fastapi import FastAPI

from app.logger import LogConfig
from app.handlers import router


def get_application() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


if __name__ == '__main__':
    app = get_application()
    uvicorn.run(app, host='0.0.0.0', port=9898, log_config=LogConfig().model_dump())
