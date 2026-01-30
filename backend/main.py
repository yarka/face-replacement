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
    TaskStatus,
    ModelType,
    PipelineStage
)
from services.cloudinary_service import upload_file
from config import MOCK_MODE
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

# Map Freepik ratio values to Seedream aspect ratios
SEEDREAM_ASPECT_MAP = {
    "1280:720": "widescreen_16_9",
    "720:1280": "social_story_9_16",
    "960:960": "square_1_1",
    "1104:832": "classic_4_3",
    "832:1104": "traditional_3_4",
    "1584:672": "widescreen_16_9"
}


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


@app.post("/api/upload-frame")
async def upload_frame(file: UploadFile = File(..., description="Video frame image")):
    """
    Upload extracted video frame to Cloudinary

    Args:
        file: Frame image file (jpg, png)

    Returns:
        dict with frame_url and public_id
    """
    try:
        if MOCK_MODE:
            return {
                "frame_url": "https://storage.googleapis.com/mock-frame-result.jpg",
                "public_id": "mock-frame"
            }

        valid_image_types = ["image/jpeg", "image/png"]
        if file.content_type not in valid_image_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid frame file type. Allowed: jpg, png"
            )

        result = await upload_file(file, resource_type="image")
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload frame: {result.get('error')}"
            )

        return {"frame_url": result["url"], "public_id": result["public_id"]}

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
            upload_data = uploads.get(request.upload_id)
            if not upload_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Upload not found: {request.upload_id}"
                )
            character_url = upload_data["character_url"]
            reference_url = upload_data["reference_url"]
        else:
            character_url = request.direct_urls.character_url
            reference_url = request.direct_urls.reference_url

        # Route by model
        if request.settings.model == ModelType.RUNWAY_ACT_TWO:
            result = await freepik_client.create_task(
                character_url=character_url,
                reference_url=reference_url,
                ratio=request.settings.ratio.value,
                expression_intensity=request.settings.expression_intensity,
                body_control=request.settings.body_control,
                seed=request.settings.seed
            )
        else:
            frame_url = request.frame_url
            if not frame_url:
                raise HTTPException(
                    status_code=400,
                    detail="frame_url is required for pipeline model"
                )

            aspect_ratio = SEEDREAM_ASPECT_MAP.get(request.settings.ratio.value, "widescreen_16_9")
            edit_result = await freepik_client.create_seedream_edit_task(
                frame_url=frame_url,
                character_url=character_url,
                prompt=(
                    "Reference image 1 is the frame. Reference image 2 is the character. "
                    "Replace the person in reference image 1 with the person from reference image 2. "
                    "Preserve the scene, actions, pose, lighting, and camera angle. "
                    "Keep identity, facial structure, proportions, and hairstyle from reference image 2."
                ),
                aspect_ratio=aspect_ratio,
                guidance_scale=7.5
            )

            if not edit_result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=edit_result.get("error")
                )

            result = {
                "success": True,
                "task_id": edit_result["task_id"],
                "status": edit_result["status"],
                "pipeline_stage": PipelineStage.IMAGE_EDIT_STARTED,
                "seedream_task_id": edit_result["task_id"]
            }

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create task: {result.get('error')}"
            )

        task_id = result["task_id"]
        tasks[task_id] = {
            "upload_id": request.upload_id,
            "direct_urls": request.direct_urls.model_dump() if request.direct_urls else None,
            "character_url": character_url,
            "reference_url": reference_url,
            "status": result["status"],
            "settings": request.settings.model_dump(),
            "model": request.settings.model,
            # pipeline extras
            "frame_url": request.frame_url if request.settings.model == ModelType.SEEDREAM_KLING else None,
            "pipeline_stage": result.get("pipeline_stage"),
            "seedream_task_id": result.get("seedream_task_id"),
            "kling_task_id": None,
            "intermediate_url": None,
            "result_urls": []
        }

        return GenerateResponse(task_id=task_id, status=result["status"])

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
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

        task_data = tasks[task_id]
        model = task_data.get("model", ModelType.RUNWAY_ACT_TWO)

        # Single-step RunWay
        if model == ModelType.RUNWAY_ACT_TWO:
            result = await freepik_client.get_task_status(task_id, model="runway_act_two")

            if not result.get("success"):
                if result.get("transient"):
                    status = task_data.get("status", "IN_PROGRESS")
                    progress_stage_map = {
                        "CREATED": "Uploaded",
                        "IN_PROGRESS": "In Progress",
                        "PROCESSING": "Processing",
                        "FINALIZING": "Finalizing",
                        "READY": "Ready",
                        "COMPLETED": "Ready",
                        "FAILED": "Failed"
                    }
                    return StatusResponse(
                        task_id=task_id,
                        status=TaskStatus(status),
                        result_urls=task_data.get("result_urls", []),
                        progress_stage=progress_stage_map.get(status, status),
                        model_used=model
                    )
                raise HTTPException(status_code=500, detail=result.get("error"))

            status = result["status"]
            result_urls = result.get("result_urls", [])

            task_data["status"] = status
            if result_urls:
                task_data["result_urls"] = result_urls

            progress_stage_map = {
                "CREATED": "Uploaded",
                "IN_PROGRESS": "In Progress",
                "PROCESSING": "Processing",
                "FINALIZING": "Finalizing",
                "READY": "Ready",
                "COMPLETED": "Ready",
                "FAILED": "Failed"
            }

            return StatusResponse(
                task_id=task_id,
                status=TaskStatus(status),
                result_urls=result_urls,
                progress_stage=progress_stage_map.get(status, status),
                model_used=model
            )

        # Pipeline flow: Seedream 4 Edit → Kling 2.5 Pro
        pipeline_stage = task_data.get("pipeline_stage", PipelineStage.IMAGE_EDIT_STARTED)

        # Stage 1: Check Seedream Edit
        if pipeline_stage in [PipelineStage.IMAGE_EDIT_STARTED, PipelineStage.FRAME_UPLOADED]:
            seedream_task_id = task_data.get("seedream_task_id")
            edit_result = await freepik_client.get_task_status(seedream_task_id, model="seedream_edit")

            if not edit_result.get("success"):
                if edit_result.get("transient"):
                    return StatusResponse(
                        task_id=task_id,
                        status=TaskStatus(task_data.get("status", "IN_PROGRESS")),
                        progress_stage=task_data.get("status", "IN_PROGRESS"),
                        pipeline_stage=pipeline_stage,
                        frame_url=task_data.get("frame_url"),
                        intermediate_url=task_data.get("intermediate_url"),
                        result_urls=task_data.get("result_urls", []),
                        model_used=model
                    )
                raise HTTPException(status_code=500, detail=edit_result.get("error"))

            edit_status = edit_result["status"]

            # Completed -> launch Kling
            if edit_status == "COMPLETED":
                intermediate_url = edit_result.get("result_urls", [None])[0]
                task_data["intermediate_url"] = intermediate_url
                task_data["pipeline_stage"] = PipelineStage.IMAGE_EDIT_COMPLETED

                video_result = await freepik_client.create_kling_task(
                    input_image_url=intermediate_url,
                    generation_prompt="Ultra realistic video of a girl smiling and dancing, cinematic lighting",
                    duration="5"
                )

                if not video_result.get("success"):
                    task_data["pipeline_stage"] = PipelineStage.FAILED
                    tasks[task_id] = task_data
                    raise HTTPException(status_code=500, detail=video_result.get("error"))

                task_data["kling_task_id"] = video_result["task_id"]
                task_data["pipeline_stage"] = PipelineStage.VIDEO_STARTED
                task_data["status"] = video_result["status"]
                tasks[task_id] = task_data

                return StatusResponse(
                    task_id=task_id,
                    status=TaskStatus(video_result["status"]),
                    progress_stage="VIDEO_STARTED",
                    pipeline_stage=PipelineStage.VIDEO_STARTED,
                    frame_url=task_data.get("frame_url"),
                    intermediate_url=intermediate_url,
                    result_urls=[],
                    model_used=model
                )

            if edit_status == "FAILED":
                task_data["pipeline_stage"] = PipelineStage.FAILED
                task_data["status"] = edit_status
                tasks[task_id] = task_data
                return StatusResponse(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    progress_stage="FAILED",
                    pipeline_stage=PipelineStage.FAILED,
                    model_used=model
                )

            # Still running
            task_data["status"] = edit_status
            tasks[task_id] = task_data
            return StatusResponse(
                task_id=task_id,
                status=TaskStatus(edit_status),
                progress_stage=edit_status,
                pipeline_stage=pipeline_stage,
                frame_url=task_data.get("frame_url"),
                model_used=model
            )

        # Stage 2: Check Kling
        if pipeline_stage == PipelineStage.VIDEO_STARTED:
            kling_task_id = task_data.get("kling_task_id")
            video_result = await freepik_client.get_task_status(kling_task_id, model="kling_v2_5_pro")

            if not video_result.get("success"):
                if video_result.get("transient"):
                    return StatusResponse(
                        task_id=task_id,
                        status=TaskStatus(task_data.get("status", "IN_PROGRESS")),
                        progress_stage=task_data.get("status", "IN_PROGRESS"),
                        pipeline_stage=pipeline_stage,
                        frame_url=task_data.get("frame_url"),
                        intermediate_url=task_data.get("intermediate_url"),
                        result_urls=task_data.get("result_urls", []),
                        model_used=model
                    )
                raise HTTPException(status_code=500, detail=video_result.get("error"))

            video_status = video_result["status"]

            if video_status == "COMPLETED":
                result_urls = video_result.get("result_urls", [])
                task_data["pipeline_stage"] = PipelineStage.PIPELINE_COMPLETED
                task_data["status"] = video_status
                if result_urls:
                    task_data["result_urls"] = result_urls
                tasks[task_id] = task_data

                return StatusResponse(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED,
                    progress_stage="PIPELINE_COMPLETED",
                    pipeline_stage=PipelineStage.PIPELINE_COMPLETED,
                    frame_url=task_data.get("frame_url"),
                    intermediate_url=task_data.get("intermediate_url"),
                    result_urls=result_urls,
                    model_used=model
                )

            if video_status == "FAILED":
                task_data["pipeline_stage"] = PipelineStage.FAILED
                task_data["status"] = video_status
                tasks[task_id] = task_data
                return StatusResponse(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    progress_stage="FAILED",
                    pipeline_stage=PipelineStage.FAILED,
                    intermediate_url=task_data.get("intermediate_url"),
                    model_used=model
                )

            task_data["status"] = video_status
            tasks[task_id] = task_data
            return StatusResponse(
                task_id=task_id,
                status=TaskStatus(video_status),
                progress_stage=video_status,
                pipeline_stage=PipelineStage.VIDEO_STARTED,
                intermediate_url=task_data.get("intermediate_url"),
                frame_url=task_data.get("frame_url"),
                model_used=model
            )

        # Fallback
        return StatusResponse(
            task_id=task_id,
            status=TaskStatus(task_data.get("status", TaskStatus.PROCESSING)),
            progress_stage=str(task_data.get("pipeline_stage", "PROCESSING")),
            pipeline_stage=task_data.get("pipeline_stage"),
            frame_url=task_data.get("frame_url"),
            intermediate_url=task_data.get("intermediate_url"),
            result_urls=task_data.get("result_urls", []),
            model_used=model
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
