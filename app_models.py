from sqlalchemy import LargeBinary, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
class ClassificationResult(Base):
    __tablename__ = "ClassificationResult"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(10), index=True)
    batch_id = Column(String(20), index=True)
    created_at = Column(DateTime)
    probability = Column(Float(5, 4), nullable=False, default=0.0, server_default='0.0')
    image_data = Column(LargeBinary, nullable=True)