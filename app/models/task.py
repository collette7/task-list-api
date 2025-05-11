from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, DateTime, ForeignKey
from ..db import db


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    goal_id = mapped_column(ForeignKey("goal.id"), nullable=True)
    goal = relationship("Goal", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }

    @classmethod
    def from_dict(cls, task_data):
        return cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at=task_data.get("completed_at")
        )
