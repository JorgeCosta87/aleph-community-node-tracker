
import logging
import threading
import time
from fastapi import APIRouter, Depends

from app.db.connection import Session, get_db_session
from app.repositories.node import NodeRepository
from app.repositories.message import MessageRepository
from app.services.nodes_metrics import NodeMetricsService
from app.schemas.crn_metrics import CrnMetricsResponseSchema

logger = logging.getLogger(__name__) 

node_metrics_router = APIRouter(
    prefix='/api/v1',
    tags=["Nodes"]
)

@node_metrics_router.on_event("startup")
async def on_train_job_router_startup():

    db_session = get_db_session()
    session = next(db_session)


    repository = NodeRepository(session)
    messageRepository = MessageRepository(session)

    service = NodeMetricsService(repository)

    thread = threading.Thread(
        target= service.update_nodes_and_notify_subscribers, args=(messageRepository,)
    )
    
    thread.setDaemon(True)
    thread.start()
    

@node_metrics_router.get("/crn-metrics", response_model=list[CrnMetricsResponseSchema])
async def get_crn_metrics(
    db: Session = Depends(get_db_session)
):

    repository = NodeRepository(db)
    service = NodeMetricsService(repository)

    response = service.get_crn_metrics()

    return response


@node_metrics_router.get("/ccn-metrics")
async def get_ccn_metrics():

    repository = NodeRepository(db)
    service = NodeMetricsService(repository)

    response = service.get_crn_metrics()

    return response
