from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from alembic.config import Config
from alembic.command import upgrade

from app.routers.nodes_metrics import node_metrics_router
from app.routers.user_session import user_session_router
from app.routers.subscribe_node import subscriber_router

import logging

logging.config.fileConfig('../logging.conf', disable_existing_loggers=False)  #type: ignore
logger = logging.getLogger(__name__) 

app = FastAPI()


app.include_router(node_metrics_router)
app.include_router(user_session_router)
app.include_router(subscriber_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    logger.info("Execute Migrations")

    alembic_ini_path = settings.root_dir / 'app' / 'db' / 'migrations'

    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', str(alembic_ini_path))
    alembic_cfg.set_main_option('prepend_sys_path', '.')
    alembic_cfg.set_main_option('version_path_separator', 'os')

    upgrade(alembic_cfg, "head")



