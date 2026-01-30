"""
Mock service для тестирования без вызова реального API
Симулирует Freepik API для разработки без трат
"""
import asyncio
import uuid
from typing import Dict


class MockFreepikClient:
    """Mock client для локального тестирования"""

    def __init__(self):
        self.tasks = {}  # Хранение состояний mock tasks

    async def create_task(self, **kwargs) -> Dict:
        """Mock RunWay Act Two task (legacy method for compatibility)"""
        return await self.create_runway_task(**kwargs)

    async def create_runway_task(self, **kwargs) -> Dict:
        """Mock RunWay Act Two task"""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": "CREATED",
            "model": "runway_act_two",
            "start_time": asyncio.get_event_loop().time()
        }

        return {
            "success": True,
            "task_id": task_id,
            "status": "CREATED"
        }

    async def create_nano_banana_task(
        self,
        character_url: str,
        frame_url: str,
        **kwargs
    ) -> Dict:
        return {
            "success": False,
            "error": "Nano Banana is not supported in this pipeline"
        }

    async def create_seedream_edit_task(
        self,
        frame_url: str,
        character_url: str,
        **kwargs
    ) -> Dict:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": "CREATED",
            "model": "seedream_edit",
            "start_time": asyncio.get_event_loop().time(),
            "frame_url": frame_url,
            "character_url": character_url
        }

        return {
            "success": True,
            "task_id": task_id,
            "status": "CREATED"
        }

    async def create_kling_task(
        self,
        input_image_url: str,
        **kwargs
    ) -> Dict:
        """
        Mock Kling task (image-to-video)

        Args:
            input_image_url: URL картинки с заменённым лицом
        """
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": "CREATED",
            "model": "kling",
            "start_time": asyncio.get_event_loop().time(),
            "input_image_url": input_image_url
        }

        return {
            "success": True,
            "task_id": task_id,
            "status": "CREATED"
        }

    async def get_task_status(self, task_id: str, model: str = "runway_act_two") -> Dict:
        """
        Mock status check - симулирует прогресс

        Прогресс:
        0-10 секунд: IN_PROGRESS
        10-15 секунд: PROCESSING
        15+ секунд: COMPLETED
        """
        if task_id not in self.tasks:
            return {
                "success": False,
                "error": "Task not found"
            }

        task = self.tasks[task_id]
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - task["start_time"]

        # Симуляция прогресса
        if elapsed < 10:
            status = "IN_PROGRESS"
            result_urls = []
        elif elapsed < 15:
            status = "PROCESSING"
            result_urls = []
        else:
            status = "COMPLETED"
            # Mock URL для результата (зависит от модели)
            model = task.get("model", "runway_act_two")
            if model == "seedream_edit":
                result_urls = ["https://storage.googleapis.com/mock-image-result.jpg"]
            elif model == "kling":
                # Kling возвращает VIDEO
                result_urls = ["https://storage.googleapis.com/mock-video-result.mp4"]
            else:
                # RunWay возвращает VIDEO
                result_urls = ["https://storage.googleapis.com/mock-video-result.mp4"]

        return {
            "success": True,
            "task_id": task_id,
            "status": status,
            "result_urls": result_urls
        }
