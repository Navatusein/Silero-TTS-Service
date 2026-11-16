import asyncio
import uvicorn

from fastapi import FastAPI

from app.config import Settings
from app.logger import LogConfig
from app.handlers import router
from app.wyoming_server import start_wyoming_server


def get_application() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


async def main() -> None:
    settings = Settings()
    app = get_application()

    uvicorn_config = uvicorn.Config(app, host='0.0.0.0', port=9898, log_config=LogConfig().model_dump())
    uvicorn_server = uvicorn.Server(uvicorn_config)

    tasks = [uvicorn_server.serve()]

    if settings.wyoming_enabled:
        tasks.append(start_wyoming_server(settings))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
