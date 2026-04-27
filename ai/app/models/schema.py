from pydantic import BaseModel
from typing import List

# UI 강조를 위한 좌표 모델
class BoxCoordinates(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

# 프론트엔드에서 보낼 요청 규격
class FrontendRequest(BaseModel):
    mime_type: str
    image_base64: str