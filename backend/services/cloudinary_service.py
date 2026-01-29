"""
Cloudinary service for uploading files and getting public URLs
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)


async def upload_file(file: UploadFile, resource_type: str = "auto") -> dict:
    """
    Upload a file to Cloudinary and return the result

    Args:
        file: UploadFile object from FastAPI
        resource_type: Type of resource ("image", "video", or "auto")

    Returns:
        dict: Cloudinary upload result containing secure_url and other metadata
    """
    try:
        # Read file contents
        contents = await file.read()

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            resource_type=resource_type,
            folder="character-replacement-mvp"  # Organize files in a folder
        )

        return {
            "success": True,
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "resource_type": result["resource_type"],
            "format": result["format"],
            "size": result.get("bytes", 0)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def delete_file(public_id: str, resource_type: str = "image"):
    """
    Delete a file from Cloudinary

    Args:
        public_id: The public ID of the file to delete
        resource_type: Type of resource ("image" or "video")

    Returns:
        dict: Result of the deletion
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
