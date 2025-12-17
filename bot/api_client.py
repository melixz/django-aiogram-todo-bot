from typing import Any

import httpx
from config import settings


class APIClient:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        self.base_url = settings.api_base_url
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-Telegram-ID": str(self.telegram_id),
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_tasks(self) -> list[dict[str, Any]]:
        client = await self._get_client()
        response = await client.get("/tasks/")
        response.raise_for_status()
        data = response.json()
        return data.get("results", data) if isinstance(data, dict) else data

    async def get_task(self, task_id: str) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.get(f"/tasks/{task_id}/")
        response.raise_for_status()
        return response.json()

    async def create_task(
        self,
        title: str,
        description: str = "",
        category_id: str | None = None,
        due_date: str | None = None,
    ) -> dict[str, Any]:
        client = await self._get_client()
        payload = {
            "title": title,
            "description": description,
        }
        if category_id:
            payload["category"] = category_id
        if due_date:
            payload["due_date"] = due_date

        response = await client.post("/tasks/", json=payload)
        response.raise_for_status()
        return response.json()

    async def update_task(self, task_id: str, **data) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.patch(f"/tasks/{task_id}/", json=data)
        response.raise_for_status()
        return response.json()

    async def delete_task(self, task_id: str) -> None:
        client = await self._get_client()
        response = await client.delete(f"/tasks/{task_id}/")
        response.raise_for_status()

    async def complete_task(self, task_id: str) -> dict[str, Any]:
        return await self.update_task(task_id, is_completed=True)

    async def get_categories(self) -> list[dict[str, Any]]:
        client = await self._get_client()
        response = await client.get("/categories/")
        response.raise_for_status()
        data = response.json()
        return data.get("results", data) if isinstance(data, dict) else data

    async def create_category(self, name: str) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.post("/categories/", json={"name": name})
        response.raise_for_status()
        return response.json()


def get_api_client(telegram_id: int) -> APIClient:
    return APIClient(telegram_id)
