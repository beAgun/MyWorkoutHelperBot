from app.db.database import Base
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Boolean,
    CheckConstraint,
    BigInteger,
    String,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String(length=64), unique=True, nullable=False
    )
    first_name: Mapped[str | None] = mapped_column(String(length=64))
    last_name: Mapped[str | None] = mapped_column(String(length=64))

    rules: Mapped[list["Rule"]] = relationship(
        "NotificationsRule", back_populates="user"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user"
    )


class NotificationsRule(Base):
    __tablename__ = "notifications_rules"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    only_enabled: Mapped[bool | None] = mapped_column(
        Boolean, nullable=False, default=False
    )
    workout_id: Mapped[int | None] = mapped_column(Integer)
    offset_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="rules")
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="rule"
    )

    __table_args__ = (
        CheckConstraint("offset_minutes >= 0", name="ch_offset_minutes_not_negative"),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"), nullable=False)
    rule_id: Mapped[int] = mapped_column(
        ForeignKey("notifications_rules.id"), nullable=False
    )
    notify_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent: Mapped[bool | None] = mapped_column(Boolean, nullable=False, default=False)

    rule: Mapped["Rule"] = relationship(
        "NotificationsRule", back_populates="notifications"
    )
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    workout: Mapped["Workout"] = relationship("Workout", back_populates="notifications")


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    name: Mapped[str | None] = mapped_column(String)

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="workout"
    )
