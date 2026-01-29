"""
Freepik API service for character replacement video generation
"""
import httpx
from typing import Dict, Optional
from config import FREEPIK_API_KEY, FREEPIK_API_BASE_URL


class FreepikClient:
    """Client for interacting with Freepik RunWay Act Two API"""

    def __init__(self):
        self.base_url = FREEPIK_API_BASE_URL
        self.api_key = FREEPIK_API_KEY
        self.headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
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
        endpoint = f"{self.base_url}/runway-act-two"

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
                "details": error_details
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_task_status(self, task_id: str) -> Dict:
        """
        Get the status of a task

        Args:
            task_id: The task ID to check

        Returns:
            dict: Task status and result URLs if ready
        """
        # Правильный endpoint: task_id в пути, без /task-by-id
        endpoint = f"{self.base_url}/runway-act-two/{task_id}"

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
                "details": e.response.text
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
        endpoint = f"{self.base_url}/runway-act-two-tasks"

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


# Create a singleton instance
freepik_client = FreepikClient()
