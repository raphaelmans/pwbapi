from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ImageData(BaseModel):
    datauri: str
    batch_id: str
    
class ClassificationResultBase(BaseModel):
    class_name: str
    batch_id: str
    created_at: datetime
    probability: float = 0.0
    image_data: Optional[bytes]

    class Config:
        orm_mode = True


class ClassificationResult(ClassificationResultBase):
    id: int
    pass

class ClassificationResultCreate(ClassificationResultBase):
    pass
