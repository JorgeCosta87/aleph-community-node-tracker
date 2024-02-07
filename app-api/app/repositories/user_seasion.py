from ast import mod
import uuid
from sqlalchemy import true
from sqlalchemy.orm import Session

from app.models.user_session import UserSession
from app.schemas.user_session import UserSessionCreate, UserSessionSchema, UserSessionUpdate


class UserSessionRepository():
    def __init__(self, db_session: Session):
        self.db_session = db_session


    def get_user_session_by_session_id(self, session_id: uuid.UUID) -> UserSessionSchema | None:
        model = self.db_session.query(UserSession).filter(UserSession.session_id == session_id).first()

        if model is None:
            return None
        
        return UserSessionSchema.model_validate(model, from_attributes=True) 

    def update_session(self, session_id: uuid.UUID, update_data: UserSessionUpdate) -> UserSessionSchema | None:
        model = self.db_session.query(UserSession).filter(UserSession.id == session_id).first()

        if model is None:
            return None

        model.is_verified = False

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(model, key, value)

        self.db_session.commit()

        return UserSessionSchema.model_validate(model, from_attributes=True)

    def save_session(self, user_session_create: UserSessionCreate) -> UserSessionSchema:
        model = UserSession(
            session_id=user_session_create.session_id,
            subscriber_id=user_session_create.subscriber_id,
            verification_token=user_session_create.verification_token,
            is_verified=user_session_create.is_verified,
        )

        self.db_session.add(model)
        self.db_session.commit()
        self.db_session.refresh(model)

        return UserSessionSchema.model_validate(model, from_attributes=True)

    def verify_token(self, token: str) -> str:
        model = self.db_session.query(UserSession).filter(UserSession.verification_token == token).first()

        if model is None:
            return None
        
        model.is_verified = True
        self.db_session.commit()

        return True
    
    def delete_session(self, session_id: uuid.UUID) -> bool:
        model = self.db_session.query(UserSession).filter(UserSession.id == session_id).first()

        if model is None:
            return False

        self.db_session.delete(model)
        self.db_session.commit()

        return True