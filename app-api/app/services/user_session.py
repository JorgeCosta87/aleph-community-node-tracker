import logging
import secrets
import smtplib

import uuid

from fastapi import HTTPException

from app.repositories.subscribe import SubscribeRepository
from app.schemas.subscriber import SubscriberCreate
from app.repositories.user_seasion import UserSessionRepository
from app.schemas.user_session import UserSessionBodyResponse, UserSessionCreate, UserSessionUpdate
from app.services.subscribe import SubscriberService
from app.services.nodes_metrics import NodeMetricsService
from app.schemas.node import NodesMetrics
from app.repositories.message import MessageRepository
from app.repositories.subscribe import SubscribeRepository
from app.config.settings import settings

logger = logging.getLogger(__name__) 


class UserSessionService():

    def __init__(self, repository: UserSessionRepository):
        self.repository = repository

    def get_user_session(self, session_id: uuid.UUID, subscriber_repository: SubscribeRepository) -> UserSessionBodyResponse:
        user_session_db = self.repository.get_user_session_by_session_id(session_id)

        if user_session_db is None:
            raise HTTPException(status_code=404, detail="User session, not found.")
        
        subscriber_schema = subscriber_repository.get_subscriber_by_id(user_session_db.subscriber_id)

        if user_session_db.is_verified == False:
            raise HTTPException(
                status_code=403, detail=f"Verify email first. Check your indbox at {subscriber_schema.value}"
            )


        user_session_data = UserSessionBodyResponse(
                subscriber_id=subscriber_schema.id,
                type=subscriber_schema.type,
                value=subscriber_schema.value,
                session_id=user_session_db.session_id,
            )
        
        return user_session_data


    def register_user_session(
            self,
            subscriber: SubscriberCreate,
            subscriber_service: SubscriberService
        ) -> UserSessionBodyResponse:


        subscriber_db = subscriber_service.register_subscriber(subscriber)

        if subscriber_db is None:
            raise HTTPException(status_code=404, detail="Unable to register subscriber")
        
        user_session = None
        
        if subscriber_db.user_session is None:
            session_id = uuid.uuid4()
            user_session_create = UserSessionCreate(
                session_id=session_id,
                subscriber_id=subscriber_db.id,
                verification_token=secrets.token_urlsafe(),
                is_verified=False
            )

            user_session = self.repository.save_session(user_session_create)
        else:
           user_session_update = UserSessionUpdate(
                session_id = uuid.uuid4(),
                is_verified = False
            ) 

           user_session = (
                self.repository.update_session(subscriber_db.user_session.id, user_session_update)
            )
           
           logger.info(f"User session id updated: {user_session}")

        if user_session.is_verified == False:
            self._send_verification_email(subscriber_db.value, user_session.verification_token)

        return UserSessionBodyResponse.model_validate(
            UserSessionBodyResponse(
                subscriber_id=subscriber_db.id,
                type=subscriber_db.type,
                value=subscriber_db.value,
                session_id=user_session.session_id,
            ), from_attributes=True
        )


    def retrieve_user_session_data(
            self,
            user_session: uuid.UUID,
            subscriber_repository: SubscribeRepository,
            node_service: NodeMetricsService,
            messageRepository: MessageRepository
        ) -> NodesMetrics:

        user_session_db = self.repository.get_user_session_by_session_id(user_session)

        if user_session_db is None:
            raise HTTPException(status_code=404, detail="User session Not Found")
        
        if user_session_db.is_verified == False:
            raise HTTPException(status_code=403, detail="Verify email first.")
        
        return node_service.fetch_all_nodes_and_subscribed(
            user_session_db.subscriber_id,
            subscriber_repository,
            messageRepository
            ) 
        
        
    def verify_user_session_token(self, token: str):
        is_verified = self.repository.verify_token(token)

        if not is_verified:
            raise HTTPException(status_code=400, detail="Invalid token, request a new token.")
        
        return {"message": "Account successfully verified"}
    

    @staticmethod
    def _send_verification_email(email_to: str, token: str):
        sender_email = "aleph.community.node.tracker@gmail.com"
        sender_password = "ejzh rreu wkyt fgqi"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        verification_link = f"http://{settings.email_verify_domain}/api/v1/verify?token={token}"
        email_subject = "Aleph community node tracker Verify your email"
        email_body = f"Please click on the link to verify your email: {verification_link}"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_to, f"Subject: {email_subject}\n\n{email_body}")

 