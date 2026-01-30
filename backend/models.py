"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ModelType(str, Enum):
    """Поддерживаемые AI модели"""
    RUNWAY_ACT_TWO = "runway_act_two"
    SEEDREAM_KLING = "seedream_kling"


class PipelineStage(str, Enum):
    """Этапы pipeline для multi-step генерации"""
    FRAME_EXTRACTION = "FRAME_EXTRACTION"  # Шаг 1: Извлечение кадра из видео
    FRAME_UPLOADED = "FRAME_UPLOADED"  # Кадр загружен в Cloudinary
    IMAGE_EDIT_STARTED = "IMAGE_EDIT_STARTED"  # Шаг 2: Редактирование кадра (Seedream Edit)
    IMAGE_EDIT_COMPLETED = "IMAGE_EDIT_COMPLETED"
    VIDEO_STARTED = "VIDEO_STARTED"  # Шаг 3: Генерация видео (Kling)
    VIDEO_COMPLETED = "VIDEO_COMPLETED"
    PIPELINE_COMPLETED = "PIPELINE_COMPLETED"
    FAILED = "FAILED"


class AspectRatio(str, Enum):
    """Supported aspect ratios - Freepik format"""
    WIDESCREEN_16_9 = "1280:720"     # 16:9
    PORTRAIT_9_16 = "720:1280"       # 9:16
    LANDSCAPE_4_3 = "1104:832"       # 4:3
    PORTRAIT_3_4 = "832:1104"        # 3:4
    SQUARE_1_1 = "960:960"           # 1:1
    ULTRAWIDE_21_9 = "1584:672"      # 21:9


class GenerationSettings(BaseModel):
    """Settings for video generation"""
    model: ModelType = Field(default=ModelType.RUNWAY_ACT_TWO)
    ratio: AspectRatio = Field(default=AspectRatio.WIDESCREEN_16_9)
    expression_intensity: int = Field(default=3, ge=1, le=5)
    body_control: bool = Field(default=True)
    seed: Optional[int] = Field(default=None, ge=0, le=4294967295)


class UploadResponse(BaseModel):
    """Response from file upload"""
    upload_id: str
    character_url: str
    reference_url: str


class DirectUrls(BaseModel):
    """Direct URLs for character and reference"""
    character_url: str = Field(..., description="Direct URL to character image")
    reference_url: str = Field(..., description="Direct URL to reference video")


class GenerateRequest(BaseModel):
    """Request to generate a video - supports either upload_id or direct URLs"""
    upload_id: Optional[str] = Field(default=None, description="Upload ID from /api/upload")
    direct_urls: Optional[DirectUrls] = Field(default=None, description="Direct URLs (skip upload)")
    settings: GenerationSettings
    frame_url: Optional[str] = Field(default=None, description="URL извлечённого кадра для pipeline")

    def model_post_init(self, __context):
        """Validate that either upload_id or direct_urls is provided"""
        if not self.upload_id and not self.direct_urls:
            raise ValueError("Either upload_id or direct_urls must be provided")
        if self.upload_id and self.direct_urls:
            raise ValueError("Cannot provide both upload_id and direct_urls")


class GenerateResponse(BaseModel):
    """Response from video generation"""
    task_id: str
    status: str


class TaskStatus(str, Enum):
    """Task status enum"""
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    PROCESSING = "PROCESSING"
    FINALIZING = "FINALIZING"
    READY = "READY"
    COMPLETED = "COMPLETED"  # Freepik использует COMPLETED вместо READY
    FAILED = "FAILED"


class StatusResponse(BaseModel):
    """Response from status check"""
    task_id: str
    status: TaskStatus
    result_urls: List[str] = Field(default_factory=list)
    progress_stage: Optional[str] = None
    # Новые поля для pipeline
    pipeline_stage: Optional[PipelineStage] = None
    frame_url: Optional[str] = None  # URL извлечённого кадра
    intermediate_url: Optional[str] = None  # URL после Seedream Edit (новая картинка)
    model_used: Optional[ModelType] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    details: Optional[str] = None
