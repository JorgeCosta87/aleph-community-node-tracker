import uuid
from fastapi import APIRouter, Depends

from app.db.connection import Session, get_db_session
from app.repositories.user_seasion import UserSessionRepository
from app.services.user_session import UserSessionService
from app.schemas.subscriber import SubscriberCreate
from app.schemas.user_session import UserSessionBodyResponse
from app.repositories.subscribe import SubscribeRepository
from app.services.subscribe import SubscriberService
from app.schemas.node import NodesMetrics
from app.repositories.node import NodeRepository
from app.services.nodes_metrics import NodeMetricsService
from app.repositories.message import MessageRepository

user_session_router = APIRouter(
    prefix="/api/v1",
    tags=["User Session"]
)


@user_session_router.get("/user-session")
async def get_user_session(
    user_session_id: uuid.UUID, db: Session = Depends(get_db_session)
) -> UserSessionBodyResponse:

    repository = UserSessionRepository(db)
    subscriber_repository = SubscribeRepository(db)

    service = UserSessionService(repository)
    response = service.get_user_session(user_session_id, subscriber_repository)

    return response

@user_session_router.post("/register-session")
async def register_session(
    subscriber: SubscriberCreate, db: Session = Depends(get_db_session)
) -> UserSessionBodyResponse:

    repository = UserSessionRepository(db)
    subscriber_repository = SubscribeRepository(db)

    subscriber_service = SubscriberService(subscriber_repository)
    service = UserSessionService(repository)

    response = service.register_user_session(subscriber, subscriber_service)

    return response

@user_session_router.get("/user-session-data")
async def retrieve_user_session_data(
    user_session_id: uuid.UUID, db: Session = Depends(get_db_session)
) -> NodesMetrics:

    repository = UserSessionRepository(db)
    node_repository = NodeRepository(db)
    message_repository = MessageRepository(db)
    subscriber_repository = SubscribeRepository(db)

    node_service = NodeMetricsService(node_repository)
    service = UserSessionService(repository)

    response = service.retrieve_user_session_data(
        user_session_id, subscriber_repository, node_service, message_repository
        )

    return response



@user_session_router.get("/verify")
async def verify_token(
    token: str, db: Session = Depends(get_db_session)
) -> dict:

    repository = UserSessionRepository(db)
    service = UserSessionService(repository)

    response = service.verify_user_session_token(token)

    return response

