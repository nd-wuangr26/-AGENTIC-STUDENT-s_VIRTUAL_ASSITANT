from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RoomStatusResponse(BaseModel):
    """Schema cho trạng thái phòng"""
    room_id: str
    current_students: int
    capacity: int
    available_slots: int
    last_updated: datetime
    building: str
    floor: int
    room_number: int
    occupancy_rate: float  # Tỷ lệ lấp đầy (%)

    class Config:
        from_attributes = True

class BuildingStatistics(BaseModel):
    """Thống kê theo tòa nhà"""
    building: str
    total_rooms: int
    total_capacity: int
    total_students: int
    available_slots: int
    occupancy_rate: float
    rooms: List[RoomStatusResponse]

class DormitoryOverview(BaseModel):
    """Tổng quan toàn bộ ký túc xá"""
    total_buildings: int
    total_rooms: int
    total_capacity: int
    total_students: int
    total_available_slots: int
    overall_occupancy_rate: float
    buildings_stats: List[BuildingStatistics]

class StudentInfo(BaseModel):
    """Thông tin sinh viên"""
    mssv: str
    ten: str
    nam_sinh: int
    room_id: Optional[str] = None

    class Config:
        from_attributes = True

class UploadDocumentRequest(BaseModel):
    """Request cho upload document"""
    file_path: str
    description: Optional[str] = None

class UploadDocumentResponse(BaseModel):
    """Response cho upload document"""
    success: bool
    message: str
    chunks_processed: Optional[int] = None
    error: Optional[str] = None
