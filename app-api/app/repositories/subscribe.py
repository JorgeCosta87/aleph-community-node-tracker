import logging
import uuid
from venv import logger
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session


from app.models.subscriber import Subscriber, Subscription
from app.schemas.subscriber import SubscriberCreate, SubscriberSchema
from app.schemas.subscription import SubscriptionSchema

logger = logging.getLogger(__name__) 

class SubscribeRepository():
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_subscriber_by_id(self, subscriber_id: uuid.UUID)-> SubscriberSchema | None:
        model = self.db_session.query(Subscriber).filter(Subscriber.id == subscriber_id).first()

        if model is None:
            return None

        return SubscriberSchema.model_validate(model, from_attributes=True)

    def save(self, subscriber_create: SubscriberCreate) -> SubscriberSchema:
        new_subscriber = Subscriber(
            type=subscriber_create.type.value,
            value=subscriber_create.value
        )

        self.db_session.add(new_subscriber)
        self.db_session.commit()
        self.db_session.refresh(new_subscriber)

        return SubscriberSchema.model_validate(new_subscriber, from_attributes=True)
    
    def save_subscription(self, node_id: uuid.UUID, subscriber_id: uuid.UUID) -> SubscriptionSchema:
            existing_subscription = self.db_session.query(Subscription)\
                                                .filter(Subscription.node_id == node_id,
                                                        Subscription.subscriber_id == subscriber_id)\
                                                .first()
            if existing_subscription:
                raise ValueError("A subscription for the given node and subscriber already exists.")

            new_subscription = Subscription(node_id=node_id, subscriber_id=subscriber_id)
            try:
                self.db_session.add(new_subscription)
                self.db_session.commit()
                self.db_session.refresh(new_subscription)
            except IntegrityError:
                self.db_session.rollback()
                raise

            return SubscriptionSchema.model_validate(new_subscription, from_attributes=True)
    
    def delete_subscription(self, subscription_id: uuid.UUID) -> bool:
        subscription = self.db_session.query(Subscription).filter(Subscription.id == subscription_id).first()
        
        if subscription:
            self.db_session.delete(subscription)
            self.db_session.commit()
            return True
        else:
            return False
    
    def delete_subscription_by_subscriber_and_node(self, node_id: uuid.UUID, subscriber_id: uuid.UUID) -> bool:

        subscription_to_delete = self.db_session.query(Subscription)\
                                                .filter(Subscription.subscriber_id == subscriber_id,
                                                        Subscription.node_id == node_id)\
                                                .first()
        
        logger.info(subscription_to_delete)
        
        if subscription_to_delete:
            self.db_session.delete(subscription_to_delete)
            self.db_session.commit()
            
            return True
        
        return False

    
    def update_subscriber_session_by_email(self, email: str, new_session_id: uuid.UUID) -> SubscriberSchema:
        subscriber = self.db_session.query(Subscriber).filter(Subscriber.value == email).first()

        if not subscriber:
            return None

        subscriber.session_id = new_session_id

        self.db_session.commit()

        return SubscriberSchema.model_validate(subscriber, from_attributes=True)

    def get_subscriber_by_email(self, email: str) -> SubscriberSchema | None:
        model = self.db_session.query(Subscriber).filter(Subscriber.value == email).first()

        if not model:
            return None

        return SubscriberSchema.model_validate(model, from_attributes=True)

    def get_subscriber_by_session_id(session: Session, session_id: uuid.UUID):
        session_obj = session.query(Session).filter(Session.id == session_id).first()

        if not session_obj:
            return None

        subscriber = session_obj.subscriber

        return SubscriberSchema.model_validate(subscriber, from_attributes=True)
    
    def get_subscriptions_by_subscriber_id(self, subscriber_id: uuid.UUID) -> list[SubscriptionSchema]:

        model = self.db_session.query(Subscriber)\
                                    .filter(Subscriber.id == subscriber_id)\
                                    .first()
        
        if model is None or model.subscriptions is None:
            return None
        
        return [
            SubscriptionSchema.model_validate(model_sub, from_attributes=True) for model_sub in model.subscriptions
        ]
    