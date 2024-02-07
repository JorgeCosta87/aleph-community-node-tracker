import uuid
from fastapi import APIRouter, Depends

from app.db.connection import Session, get_db_session
from app.repositories.subscribe import SubscribeRepository
from app.services.subscribe import SubscriberService

subscriber_router = APIRouter(
    prefix="/api/v1",
    tags=["Subscribe"]
)


@subscriber_router.post("/node/{node_id}/subscriber/{subscriber_id}")
async def subscribe_node(
    node_id: uuid.UUID,
    subscriber_id: uuid.UUID,
    db: Session = Depends(get_db_session)
):
    repository = SubscribeRepository(db)

    subscriber_service = SubscriberService(repository)
    response = subscriber_service.create_subscription(node_id, subscriber_id)

    return response

@subscriber_router.delete("/node/{node_id}/subscriber/{subscriber_id}")
async def unsubscribe_node(
    node_id: uuid.UUID,
    subscriber_id: uuid.UUID,
    db: Session = Depends(get_db_session)
):
    repository = SubscribeRepository(db)

    subscriber_service = SubscriberService(repository)
    response = subscriber_service.unsubscribe(node_id, subscriber_id)

    return response