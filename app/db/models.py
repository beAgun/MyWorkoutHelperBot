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
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, init=False)

    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(length=64), nullable=False)

    username: Mapped[str] = mapped_column(
        String(length=64), unique=True, nullable=True, default=None
    )

    last_name: Mapped[str | None] = mapped_column(String(length=64), default=None)

    site_user_id: Mapped[int | None] = mapped_column(
        Integer, unique=True, nullable=True, default=None
    )

    notifications_enabled: Mapped[bool | None] = mapped_column(Boolean, default=False)

    rules: Mapped[list["NotificationsRule"]] = relationship(
        "NotificationsRule", back_populates="user", init=False
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", init=False
    )

    workouts: Mapped[list["Workout"]] = relationship(
        "Workout", back_populates="user", init=False
    )

    competitions_notifications: Mapped[bool] = mapped_column(Boolean, default=False)


class NotificationsRule(Base):
    __tablename__ = "notifications_rules"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, init=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, init=False
    )
    user: Mapped["User"] = relationship("User", back_populates="rules")

    offset_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    workout_id: Mapped[int | None] = mapped_column(Integer, default=None)

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="rule", init=False, passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("offset_minutes >= 0", name="ch_offset_minutes_not_negative"),
        UniqueConstraint(
            "user_id",
            "workout_id",
            "offset_minutes",
            name="uq_notifications_rules_specific",
        ),
        Index(
            "uq_notifications_rules_default",
            "user_id",
            "offset_minutes",
            unique=True,
            postgresql_where=workout_id.is_(None),
        ),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, init=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, init=False
    )
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False, init=False
    )
    workout: Mapped["Workout"] = relationship("Workout", back_populates="notifications")

    rule_id: Mapped[int] = mapped_column(
        ForeignKey("notifications_rules.id", ondelete="CASCADE"),
        nullable=False,
        init=False,
    )
    rule: Mapped["NotificationsRule"] = relationship(
        "NotificationsRule", back_populates="notifications"
    )

    notify_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    sent: Mapped[bool | None] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint(
            "workout_id",
            "rule_id",
            name="uq_notification_workout_rule",
        ),
    )


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True, init=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, init=False
    )
    user: Mapped["User"] = relationship("User", back_populates="workouts")

    site_workout_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    title: Mapped[str | None] = mapped_column(String, default=None)

    workout_type: Mapped[str | None] = mapped_column(String, default=None)

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="workout", init=False, passive_deletes=True
    )


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )


class CompetitionMonitorState(Base):
    __tablename__ = "competitions_monitor_state"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    event_name: Mapped[str] = mapped_column(String, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
