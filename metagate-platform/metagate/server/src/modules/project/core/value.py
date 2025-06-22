from enum import Enum


class ProjectStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    PLANNING = "planning"
    REVIEW = "review"
