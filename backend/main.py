"""
FastAPI application for character replacement video generation
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
from typing import Dict

from models import (
    GenerateRequest,
    GenerateResponse,
    UploadResponse,
    StatusResponse,
    ErrorResponse,
    TaskStatus
)
from services.cloudinary_service import upload_file
from services.freepik_service import freepik_client

# Create FastAPI app
app = FastAPI(
    title="Character Replacement MVP",
    description="API for replacing characters in videos using AI",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploads and tasks
# In production, use Redis or a database
uploads: Dict[str, dict] = {}
tasks: Dict[str, dict] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Character Replacement MVP",
        "version": "0.1.0"
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(
    character: UploadFile = File(..., description="Character image file"),
    reference: UploadFile = File(..., description="Reference video file")
):
    """
    Upload character image and reference video to Cloudinary

    Args:
        character: Character image file (jpg, png, webp)
        reference: Reference video file (mp4, mov)

    Returns:
        UploadResponse with upload_id and file URLs
    """
    try:
        # Validate file types
        valid_image_types = ["image/jpeg", "image/png", "image/webp"]
        valid_video_types = ["video/mp4", "video/quicktime", "video/x-msvideo"]

        if character.content_type not in valid_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid character file type. Allowed: jpg, png, webp"
            )

        if reference.content_type not in valid_video_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid reference file type. Allowed: mp4, mov, avi"
            )

        # Upload character image
        char_result = await upload_file(character, resource_type="image")
        if not char_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload character: {char_result.get('error')}"
            )

        # Upload reference video
        ref_result = await upload_file(reference, resource_type="video")
        if not ref_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload reference: {ref_result.get('error')}"
            )

        # Generate upload ID and store
        upload_id = str(uuid.uuid4())
        uploads[upload_id] = {
            "character_url": char_result["url"],
            "reference_url": ref_result["url"],
            "character_public_id": char_result["public_id"],
            "reference_public_id": ref_result["public_id"]
        }

        return UploadResponse(
            upload_id=upload_id,
            character_url=char_result["url"],
            reference_url=ref_result["url"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_video(request: GenerateRequest):
    """
    Start video generation task

    Supports two modes:
    1. upload_id: Use URLs from previously uploaded files
    2. direct_urls: Use URLs provided directly (skip upload)

    Args:
        request: GenerateRequest with either upload_id or direct_urls, plus settings

    Returns:
        GenerateResponse with task_id and initial status
    """
    try:
        # Determine URLs based on mode
        if request.upload_id:
            # Mode 1: Get URLs from upload storage
            upload_data = uploads.get(request.upload_id)
            if not upload_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Upload not found: {request.upload_id}"
                )
            character_url = upload_data["character_url"]
            reference_url = upload_data["reference_url"]
        else:
            # Mode 2: Use direct URLs
            character_url = request.direct_urls.character_url
            reference_url = request.direct_urls.reference_url

        # Create generation task via Freepik API
        result = await freepik_client.create_task(
            character_url=character_url,
            reference_url=reference_url,
            ratio=request.settings.ratio.value,
            expression_intensity=request.settings.expression_intensity,
            body_control=request.settings.body_control,
            seed=request.settings.seed
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create task: {result.get('error')}"
            )

        # Store task info
        task_id = result["task_id"]
        tasks[task_id] = {
            "upload_id": request.upload_id,
            "direct_urls": request.direct_urls.model_dump() if request.direct_urls else None,
            "character_url": character_url,
            "reference_url": reference_url,
            "status": result["status"],
            "settings": request.settings.model_dump()
        }

        return GenerateResponse(
            task_id=task_id,
            status=result["status"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a generation task

    Args:
        task_id: The task ID to check

    Returns:
        StatusResponse with current status and result URLs if ready
    """
    try:
        # Check task exists in our storage
        if task_id not in tasks:
            raise HTTPException(
                status_code=404,
                detail=f"Task not found: {task_id}"
            )

        # Get status from Freepik API
        result = await freepik_client.get_task_status(task_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get status: {result.get('error')}"
            )

        status = result["status"]
        result_urls = result.get("result_urls", [])

        # Update our storage
        tasks[task_id]["status"] = status
        if result_urls:
            tasks[task_id]["result_urls"] = result_urls

        # Map status to progress stage for UI
        progress_stage_map = {
            "CREATED": "Uploaded",
            "IN_PROGRESS": "In Progress",
            "PROCESSING": "Processing",
            "FINALIZING": "Finalizing",
            "READY": "Ready",
            "COMPLETED": "Ready",  # Freepik использует COMPLETED
            "FAILED": "Failed"
        }

        return StatusResponse(
            task_id=task_id,
            status=TaskStatus(status),
            result_urls=result_urls,
            progress_stage=progress_stage_map.get(status, status)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks")
async def list_tasks():
    """
    List all tasks (for debugging)

    Returns:
        dict: All tasks in storage
    """
    return {
        "tasks": tasks,
        "uploads": uploads
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
