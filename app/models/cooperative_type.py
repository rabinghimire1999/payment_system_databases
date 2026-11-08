# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class fpsType(Base):
    """Table representing fps types."""
    __tablename__ = 'fps_types'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    def __init__(self, name: str, description: str = None, id: int = None, **kwargs):
        super().__init__(name=name, description=description, id=id, **kwargs)
