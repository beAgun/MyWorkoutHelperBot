from bot.database import Base
from sqlalchemy import (
    Column, Computed, Date, 
    ForeignKey, Identity, Integer, 
    Boolean, CheckConstraint, BigInteger,
    VARCHAR
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Identity(), primary_key=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(VARCHAR, unique=True, nullable=False)
    first_name = Column(VARCHAR)
    last_name = Column(VARCHAR)


class NotificationsRule(Base):
    __tablename__ = 'notifications_rules'

    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    only_enabled = Column(Boolean, nullable=False, default=False)
    workout_id = Column(Integer)
    offset_minutes = Column(Integer, nullable=False)

    user = relationship('User', back_populates='notifications_rules')

    __table_args__ = (
        CheckConstraint('offset_minutes >= 0', name='ch_offset_minutes_not_negative'),
    )


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    chat_id = Column(BigInteger, nullable=False)
    workout_id = Column(Integer)
    rule_id = Column(ForeignKey('notifications_rules.id'))
    notify_at = Column(Date, nullable=False)
    sent = Column(Boolean, nullable=False)

    rule = relationship('NotificationsRule', back_populates='notifications')
    user = relationship('User', back_populates='notifications')
