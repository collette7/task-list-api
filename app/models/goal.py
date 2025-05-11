from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from typing import Dict, Any, List

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")

    @classmethod
    def from_dict(cls, goal_data: Dict[str, Any]) -> "Goal":
        """Create a Goal instance from a dictionary."""
        return cls(
            title=goal_data["title"]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Goal instance to a dictionary."""
        return {
            "id": self.id,
            "title": self.title
        }
