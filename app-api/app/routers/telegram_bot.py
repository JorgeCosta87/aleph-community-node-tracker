
from http import HTTPStatus
import logging
import threading
import time
from fastapi import APIRouter, Depends, Request, Response
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Updater, Application
from telegram.ext._contexttypes import ContextTypes

from asyncio.queues import Queue

from app.db.connection import Session, get_db_session
from app.repositories.node import NodeRepository
from app.repositories.message import MessageRepository
from app.services.nodes_metrics import NodeMetricsService
from app.schemas.crn_metrics import CrnMetricsResponseSchema
from app.config.settings import settings

logger = logging.getLogger(__name__) 

telegram_bot_api = APIRouter(
    prefix='/api/v1',
    tags=["Telegram"]
)


ptb = (
    Application.builder()
    .updater(None)
    .token(settings.telegram_bot_token)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

TELEGRAM_API_URL = f'https://api.telegram.org/bot{settings.telegram_bot_token}/'


@telegram_bot_api.on_event("startup")
async def on_train_job_router_startup():

    db_session = get_db_session()
    session = next(db_session)

    await ptb.bot.setWebhook(
        TELEGRAM_API_URL, allowed_updates=Update.ALL_TYPES
    )
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()


@telegram_bot_api.post("/telegram")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)

    return Response(status_code=HTTPStatus.OK)


async def start(update, _: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    logger.info("Command start")
    await update.message.reply_text("starting...")

ptb.add_handler(CommandHandler("start", start))
