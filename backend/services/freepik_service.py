"""
Freepik API service for character replacement video generation
"""
import httpx
from typing import Dict, Optional
from config import (
    FREEPIK_API_KEY,
    FREEPIK_RUNWAY_CREATE_URL,
    FREEPIK_RUNWAY_STATUS_URL_TEMPLATE,
    FREEPIK_SEEDREAM_EDIT_CREATE_URL,
    FREEPIK_SEEDREAM_EDIT_STATUS_URL_TEMPLATE,
    FREEPIK_KLING_CREATE_URL,
    FREEPIK_KLING_STATUS_URL_TEMPLATE,
    MOCK_MODE
)


class FreepikClient:
    """Client for interacting with Freepik RunWay Act Two API"""

    def __init__(self):
        self.api_key = FREEPIK_API_KEY
        self.headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self._status_url_templates = {
            "runway_act_two": FREEPIK_RUNWAY_STATUS_URL_TEMPLATE,
            "seedream_edit": FREEPIK_SEEDREAM_EDIT_STATUS_URL_TEMPLATE,
            "kling_v2_5_pro": FREEPIK_KLING_STATUS_URL_TEMPLATE
        }

    async def create_task(
        self,
        character_url: str,
        reference_url: str,
        ratio: str = "widescreen_16_9",
        expression_intensity: int = 3,
        body_control: bool = True,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Create a character replacement task

        Args:
            character_url: URL to character image
            reference_url: URL to reference video
            ratio: Aspect ratio (widescreen_16_9, portrait_9_16, square_1_1, etc)
            expression_intensity: Expression intensity (1-5)
            body_control: Whether to control body movements
            seed: Optional seed for reproducibility

        Returns:
            dict: Task creation result with task_id and status
        """
        endpoint = FREEPIK_RUNWAY_CREATE_URL

        payload = {
            "character": {
                "type": "image",
                "uri": character_url
            },
            "reference": {
                "type": "video",
                "uri": reference_url
            },
            "ratio": ratio,
            "expression_intensity": expression_intensity,
            "body_control": body_control
        }

        if seed is not None:
            payload["seed"] = seed

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"Sending request to: {endpoint}")
                print(f"Payload: {payload}")

                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self.headers
                )

                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")

                response.raise_for_status()

                data = response.json()
                return {
                    "success": True,
                    "task_id": data["data"]["task_id"],
                    "status": data["data"]["status"],
                    "raw_response": data
                }

        except httpx.HTTPStatusError as e:
            error_details = e.response.text
            print(f"API Error {e.response.status_code}: {error_details}")
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "details": error_details,
                "transient": 500 <= e.response.status_code < 600
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_task_status(self, task_id: str, model: str = "runway_act_two") -> Dict:
        """
        Get the status of a task

        Args:
            task_id: The task ID to check
            model: Model identifier (runway_act_two, seedream_edit, kling_v2_5_pro)

        Returns:
            dict: Task status and result URLs if ready
        """
        template = self._status_url_templates.get(model)
        if not template:
            return {
                "success": False,
                "error": f"Status endpoint not configured for model: {model}"
            }

        endpoint = template.format(task_id=task_id)

        print(f"[STATUS CHECK] Endpoint: {endpoint}")
        print(f"[STATUS CHECK] Task ID: {task_id}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers
                )
                print(f"[STATUS CHECK] Response status: {response.status_code}")
                print(f"[STATUS CHECK] Response body: {response.text}")
                response.raise_for_status()

                data = response.json()
                task_data = data.get("data", {})

                return {
                    "success": True,
                    "task_id": task_id,
                    "status": task_data.get("status", "UNKNOWN"),
                    "result_urls": task_data.get("generated", []),
                    "raw_response": data
                }

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "details": e.response.text,
                "transient": 500 <= e.response.status_code < 600
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_all_tasks(self) -> Dict:
        """
        Get all tasks (optional, for debugging)

        Returns:
            dict: List of all tasks
        """
        endpoint = f"{FREEPIK_RUNWAY_CREATE_URL}-tasks"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "success": True,
                    "tasks": data.get("data", [])
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def create_seedream_edit_task(
        self,
        frame_url: str,
        character_url: str,
        prompt: str = "Reference image 1 is the frame. Reference image 2 is the character. Replace the person in reference image 1 with the person from reference image 2. Preserve the scene, pose, lighting, and camera angle. Keep identity, facial structure, and hairstyle from reference image 2.",
        aspect_ratio: str = "widescreen_16_9",
        guidance_scale: float = 7.5,
        **kwargs
    ) -> Dict:
        """
        Create Seedream 4 Edit task (Step 2 of pipeline)
        Instructional image edit with references

        Args:
            frame_url: URL кадра из видео
            character_url: URL персонажа
            prompt: Промпт редактирования
            aspect_ratio: Seedream aspect ratio

        Returns:
            dict: Task creation result with task_id and status
        """
        if not FREEPIK_SEEDREAM_EDIT_CREATE_URL:
            return {
                "success": False,
                "error": "FREEPIK_SEEDREAM_EDIT_CREATE_URL is not set"
            }
        endpoint = FREEPIK_SEEDREAM_EDIT_CREATE_URL

        payload = {
            "prompt": prompt,
            "reference_images": [frame_url, character_url],
            "aspect_ratio": aspect_ratio,
            "guidance_scale": guidance_scale
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"[SEEDREAM EDIT] Sending request to: {endpoint}")
                print(f"[SEEDREAM EDIT] Payload: {payload}")

                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self.headers
                )

                print(f"[SEEDREAM EDIT] Response status: {response.status_code}")
                print(f"[SEEDREAM EDIT] Response body: {response.text}")

                response.raise_for_status()

                data = response.json()
                return {
                    "success": True,
                    "task_id": data["data"]["task_id"],
                    "status": data["data"]["status"],
                    "raw_response": data
                }

        except httpx.HTTPStatusError as e:
            print(f"[SEEDREAM EDIT] API Error {e.response.status_code}: {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "details": e.response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def create_kling_task(
        self,
        input_image_url: str,
        generation_prompt: str = "Ultra realistic video of a girl smiling and dancing, cinematic lighting",
        duration: str = "5",
        cfg_scale: float = 0.5,
        **kwargs
    ) -> Dict:
        """
        Create Kling 2.5 Pro task (Step 3 of pipeline)
        Image-to-video generation

        Args:
            input_image_url: URL картинки после Seedream Edit
            generation_prompt: Промпт для генерации видео

        Returns:
            dict: Task creation result with task_id and status
        """
        if not FREEPIK_KLING_CREATE_URL:
            return {
                "success": False,
                "error": "FREEPIK_KLING_CREATE_URL is not set"
            }
        endpoint = FREEPIK_KLING_CREATE_URL

        payload = {
            "prompt": generation_prompt,
            "image": input_image_url,
            "duration": duration,
            "cfg_scale": cfg_scale
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"[KLING] Sending request to: {endpoint}")
                print(f"[KLING] Payload: {payload}")

                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self.headers
                )

                print(f"[KLING] Response status: {response.status_code}")
                print(f"[KLING] Response body: {response.text}")

                response.raise_for_status()

                data = response.json()
                return {
                    "success": True,
                    "task_id": data["data"]["task_id"],
                    "status": data["data"]["status"],
                    "raw_response": data
                }

        except httpx.HTTPStatusError as e:
            print(f"[KLING] API Error {e.response.status_code}: {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "details": e.response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Create a singleton instance (mock or real based on MOCK_MODE)
if MOCK_MODE:
    from services.mock_service import MockFreepikClient
    print("⚠️  MOCK MODE ENABLED - API calls will be simulated")
    freepik_client = MockFreepikClient()
else:
    freepik_client = FreepikClient()
