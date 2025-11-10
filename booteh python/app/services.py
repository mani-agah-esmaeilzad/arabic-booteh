from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiomysql

from .database import DatabaseManager

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Raised when a service level validation or domain error occurs."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class SelfAssessmentService:
    def __init__(self, database: DatabaseManager) -> None:
        self._database = database

    async def submit_answers(self, user_id: int, answers: Dict[str, int]) -> Dict[str, Any]:
        if not user_id:
            raise ServiceError("دسترسی غیرمجاز", status_code=401)

        if len(answers) != 22 or any(
            (not isinstance(value, int)) or value < 1 or value > 5 for value in answers.values()
        ):
            raise ServiceError("داده‌های ارسالی نامعتبر است", status_code=400)

        async with self._database.connection() as conn:
            try:
                await conn.begin()
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(
                        "INSERT INTO soft_skills_self_assessment (user_id) VALUES (%s)",
                        (user_id,),
                    )
                    assessment_id = cursor.lastrowid

                    set_clause = ", ".join(f"{key} = %s" for key in answers.keys())
                    values = list(answers.values())

                    await cursor.execute(
                        f"UPDATE soft_skills_self_assessment SET {set_clause} WHERE id = %s",
                        values + [assessment_id],
                    )

                await conn.commit()
                return {
                    "success": True,
                    "message": "پاسخ‌های شما با موفقیت ثبت شد.",
                    "data": {"assessmentId": assessment_id},
                }
            except Exception:
                await conn.rollback()
                logger.exception("Submit Self-Assessment Error")
                raise ServiceError("خطای داخلی سرور", status_code=500)


class BlogService:
    def __init__(self, database: DatabaseManager) -> None:
        self._database = database

    @staticmethod
    def _sanitize_limit(limit: Optional[str]) -> Optional[int]:
        if limit is None:
            return None
        try:
            parsed = int(limit)
        except ValueError:
            return None
        if parsed <= 0:
            return None
        return min(parsed, 50)

    async def list_posts(self, limit: Optional[str]) -> List[Dict[str, Any]]:
        sanitized = self._sanitize_limit(limit)
        base_query = (
            "SELECT id, title, slug, excerpt, cover_image_url, author, published_at, created_at "
            "FROM blog_posts "
            "WHERE is_published = 1 "
            "ORDER BY COALESCE(published_at, created_at) DESC"
        )
        if sanitized:
            return await self._database.fetch_all(f"{base_query} LIMIT %s", (sanitized,))
        return await self._database.fetch_all(base_query)


class MysteryService:
    def __init__(self, database: DatabaseManager) -> None:
        self._database = database

    async def list_assessments(self) -> List[Dict[str, Any]]:
        query = """
            SELECT
                ma.id,
                ma.name,
                ma.slug,
                ma.short_description,
                ma.created_at,
                (
                    SELECT image_url
                    FROM mystery_assessment_images mi
                    WHERE mi.mystery_assessment_id = ma.id
                    ORDER BY mi.display_order ASC, mi.id ASC
                    LIMIT 1
                ) AS preview_image
            FROM mystery_assessments ma
            WHERE ma.is_active = 1
            ORDER BY ma.created_at DESC
        """
        return await self._database.fetch_all(query)


class PersonalityService:
    def __init__(self, database: DatabaseManager) -> None:
        self._database = database

    async def list_tests(self) -> List[Dict[str, Any]]:
        query = """
            SELECT id, name, slug, tagline, description, report_name, highlights
            FROM personality_assessments
            WHERE is_active = 1
            ORDER BY id ASC
        """
        rows = await self._database.fetch_all(query)
        for row in rows:
            highlights = row.get("highlights")
            if highlights:
                try:
                    if isinstance(highlights, str):
                        row["highlights"] = json.loads(highlights)
                    else:
                        row["highlights"] = highlights
                except Exception:
                    row["highlights"] = []
            else:
                row["highlights"] = []
        return rows


class HealthService:
    def __init__(self, database: DatabaseManager) -> None:
        self._database = database

    async def health_status(self) -> Dict[str, Any]:
        db_connected = await self._database.test_connection()
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected" if db_connected else "disconnected",
        }

    async def environment_status(self) -> Dict[str, Any]:
        payload = await self.health_status()
        from os import getenv

        payload["environment"] = getenv("NODE_ENV", getenv("ENVIRONMENT", "development"))
        return payload

    async def verify_database(self) -> Dict[str, Any]:
        is_connected = await self._database.test_connection()
        if not is_connected:
            raise ServiceError("خطا در اتصال به دیتابیس", status_code=500)

        tables_created = await self._database.create_tables()
        if not tables_created:
            raise ServiceError("خطا در ایجاد جداول", status_code=500)

        return {
            "success": True,
            "message": "دیتابیس با موفقیت راه‌اندازی شد",
            "data": {"connection": "OK", "tables": "Created"},
        }


class DebugService:
    @staticmethod
    def echo_get() -> Dict[str, Any]:
        return {
            "message": "Debug API is working",
            "timestamp": datetime.utcnow().isoformat(),
            "success": True,
        }

    @staticmethod
    def echo_post(body: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "message": "POST request received",
            "data": body,
            "timestamp": datetime.utcnow().isoformat(),
            "success": True,
        }

    @staticmethod
    def chat_status() -> Dict[str, Any]:
        return {
            "message": "Chat debug API is working",
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def handle_chat_action(action: str) -> Dict[str, Any]:
        if action == "test_session":
            session_id = f"test-session-{int(datetime.utcnow().timestamp() * 1000)}"
            return {
                "message": "Session test successful",
                "sessionId": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
            }
        raise ServiceError("Unknown action", status_code=400)


__all__ = [
    "ServiceError",
    "SelfAssessmentService",
    "BlogService",
    "MysteryService",
    "PersonalityService",
    "HealthService",
    "DebugService",
]
