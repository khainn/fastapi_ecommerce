import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.db import engine
from app.common.exceptions import APIException, api_error_handler
from app.models.models import SQLModel

SQLModel.metadata.create_all(bind=engine)


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME, docs_url="/docs", redoc_url='/re-docs',
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(DBSessionMiddleware, db_url=settings.DATABASE_URL)
    application.include_router(api_router, prefix=settings.API_PREFIX)
    application.add_exception_handler(APIException, api_error_handler)

    return application


app = get_application()



if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
