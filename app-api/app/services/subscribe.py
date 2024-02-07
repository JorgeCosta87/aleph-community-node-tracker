import logging

import uuid

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.subscribe import SubscribeRepository
from app.schemas.subscriber import SubscriberCreate, SubscriberSchema
from app.utils.constants import SubscribeType
from app.schemas.subscription import SubscriptionSchema


logger = logging.getLogger(__name__) 


class SubscriberService():

    def __init__(self, repository: SubscribeRepository):
        self.repository = repository


    def register_subscriber(
            self,
            subscriber_create: SubscriberCreate,
        ) -> SubscriberSchema:

        if subscriber_create.type == SubscribeType.EMAIL:
            try:
                subscriber_db = self._check_if_subscriber_exist(subscriber_create.value.lower())  
                if subscriber_db:
                    return SubscriberSchema.model_validate(subscriber_db, from_attributes=True)
                
                subscriber_create.value = subscriber_create.value.lower() 
                subscriber_db = self.repository.save(subscriber_create)

                return SubscriberSchema.model_validate(subscriber_db, from_attributes=True)

            except SQLAlchemyError as e:
                print(f"Database error: {e}")
                raise HTTPException(status_code=500, detail="Could not register subscriber due to a server error.")

        elif subscriber_create.type == SubscribeType.TELEGRAM:
            raise HTTPException(status_code=404, detail="Telegram subscription not implemented yet.")
        else:
            raise HTTPException(status_code=400, detail="Unsupported subscription type.")

    
    def _check_if_subscriber_exist(self, email: str) -> SubscriberSchema:
        subscriber = self.repository.get_subscriber_by_email(email)

        return subscriber
    
    def create_subscription(
        self,
        node_id: uuid.UUID,
        subscriber_id: uuid.UUID
    ) -> SubscriptionSchema:
        try:
            subscription_schema = self.repository.save_subscription(
                node_id, subscriber_id
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        return subscription_schema
    
    def unsubscribe(self, node_id: uuid.UUID, subscriber_id: uuid.UUID) -> bool:
        result = self.repository.delete_subscription_by_subscriber_and_node(node_id, subscriber_id)


        return result
    
