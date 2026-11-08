# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String
# pyrefly: ignore [missing-import]
from app.core.database import Base

class Status(Base):
    """Table representing fps statuses."""
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    def __init__(self, name: str, description: str = None, id: int = None, **kwargs):
        super().__init__(name=name, description=description, id=id, **kwargs)
