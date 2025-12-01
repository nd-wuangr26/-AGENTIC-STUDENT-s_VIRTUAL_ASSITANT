from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import List
from app.core.schenma.dashboard_schema import (
    RoomStatusResponse,
    BuildingStatistics,
    DormitoryOverview,
    StudentInfo,
    UploadDocumentRequest,
    UploadDocumentResponse
)
from app.core.services.mysql_service import get_mysql_service, MySQLService
from app.api.auth import get_current_admin_user
import os
import shutil
from pathlib import Path
import asyncio

router = APIRouter()

@router.get("/rooms", response_model=List[RoomStatusResponse])
async def get_all_rooms_status(
    current_user: dict = Depends(get_current_admin_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Lấy trạng thái tất cả các phòng (chỉ admin)"""
    rooms = await db.get_all_room_status()
    
    result = []
    for room in rooms:
        result.append(RoomStatusResponse(
            room_id=room['room_id'],
            current_students=room['current_students'],
            capacity=room['capacity'],
            available_slots=room['available_slots'],
            last_updated=room['last_updated'],
            building=room['building'],
            floor=room['floor'],
            room_number=room['room_number'],
            occupancy_rate=round((room['current_students'] / room['capacity']) * 100, 2) if room['capacity'] > 0 else 0
        ))
    
    return result

@router.get("/buildings/{building}", response_model=BuildingStatistics)
async def get_building_stats(
    building: str,
    current_user: dict = Depends(get_current_admin_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Lấy thống kê theo tòa nhà (chỉ admin)"""
    if building not in ['A', 'B', 'C', 'D']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid building. Must be A, B, C, or D"
        )
    
    rooms = await db.get_room_status_by_building(building)
    
    if not rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No rooms found for building {building}"
        )
    
    total_rooms = len(rooms)
    total_capacity = sum(r['capacity'] for r in rooms)
    total_students = sum(r['current_students'] for r in rooms)
    available_slots = sum(r['available_slots'] for r in rooms)
    occupancy_rate = round((total_students / total_capacity) * 100, 2) if total_capacity > 0 else 0
    
    room_list = []
    for room in rooms:
        room_list.append(RoomStatusResponse(
            room_id=room['room_id'],
            current_students=room['current_students'],
            capacity=room['capacity'],
            available_slots=room['available_slots'],
            last_updated=room['last_updated'],
            building=room['building'],
            floor=room['floor'],
            room_number=room['room_number'],
            occupancy_rate=round((room['current_students'] / room['capacity']) * 100, 2) if room['capacity'] > 0 else 0
        ))
    
    return BuildingStatistics(
        building=building,
        total_rooms=total_rooms,
        total_capacity=total_capacity,
        total_students=total_students,
        available_slots=available_slots,
        occupancy_rate=occupancy_rate,
        rooms=room_list
    )

@router.get("/overview", response_model=DormitoryOverview)
async def get_dormitory_overview(
    current_user: dict = Depends(get_current_admin_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Lấy tổng quan toàn bộ ký túc xá (chỉ admin)"""
    overview = await db.get_dormitory_overview()
    building_stats_data = await db.get_building_statistics()
    
    buildings_stats = []
    for building_data in building_stats_data:
        # Lấy chi tiết phòng cho mỗi tòa
        rooms = await db.get_room_status_by_building(building_data['building'])
        room_list = []
        for room in rooms:
            room_list.append(RoomStatusResponse(
                room_id=room['room_id'],
                current_students=room['current_students'],
                capacity=room['capacity'],
                available_slots=room['available_slots'],
                last_updated=room['last_updated'],
                building=room['building'],
                floor=room['floor'],
                room_number=room['room_number'],
                occupancy_rate=round((room['current_students'] / room['capacity']) * 100, 2) if room['capacity'] > 0 else 0
            ))
        
        buildings_stats.append(BuildingStatistics(
            building=building_data['building'],
            total_rooms=building_data['total_rooms'],
            total_capacity=building_data['total_capacity'],
            total_students=building_data['total_students'],
            available_slots=building_data['available_slots'],
            occupancy_rate=building_data['occupancy_rate'],
            rooms=room_list
        ))
    
    return DormitoryOverview(
        total_buildings=overview['total_buildings'],
        total_rooms=overview['total_rooms'],
        total_capacity=overview['total_capacity'],
        total_students=overview['total_students'],
        total_available_slots=overview['total_available_slots'],
        overall_occupancy_rate=overview['overall_occupancy_rate'],
        buildings_stats=buildings_stats
    )

@router.get("/students", response_model=List[StudentInfo])
async def get_all_students(
    current_user: dict = Depends(get_current_admin_user),
    db: MySQLService = Depends(get_mysql_service)
):
    """Lấy danh sách tất cả sinh viên (chỉ admin)"""
    students = await db.get_all_students()
    return [StudentInfo(**student) for student in students]

@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Upload document và xử lý để lưu vào vector database (chỉ admin).
    File sẽ được lưu vào thư mục document và sau đó xử lý bởi save_vectordb.py
    """
    try:
        # Tạo thư mục document nếu chưa tồn tại
        project_root = Path(__file__).resolve().parents[3]
        document_dir = project_root / "document"
        document_dir.mkdir(exist_ok=True)
        
        # Lưu file
        file_path = document_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Import và chạy save_vectordb
        import sys
        sys.path.insert(0, str(project_root))
        
        from app.core.save_vectordb import SaveVectorDB
        from app.startup.startup import init_qdrant_service, get_qdrant_service
        
        # Initialize Qdrant service nếu chưa
        init_qdrant_service()
        qdrant_service = get_qdrant_service()
        
        # Xử lý document
        chunker = SaveVectorDB(file_path=str(file_path))
        docs = chunker.load_docling()
        
        # Lưu vào vector DB
        await chunker.save_document_openai(docs)
        
        return UploadDocumentResponse(
            success=True,
            message=f"Document {file.filename} uploaded and processed successfully",
            chunks_processed=len(docs)
        )
        
    except Exception as e:
        return UploadDocumentResponse(
            success=False,
            message="Failed to upload and process document",
            error=str(e)
        )
