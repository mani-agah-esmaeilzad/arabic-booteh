from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .auth import get_session
from .database import db_manager
from .services import (
    BlogService,
    DebugService,
    HealthService,
    MysteryService,
    PersonalityService,
    SelfAssessmentService,
    ServiceError,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Booteh FastAPI", version="1.0.0")

self_assessment_service = SelfAssessmentService(db_manager)
blog_service = BlogService(db_manager)
mystery_service = MysteryService(db_manager)
personality_service = PersonalityService(db_manager)
health_service = HealthService(db_manager)
debug_service = DebugService()


class AnswersPayload(BaseModel):
    answers: Dict[str, int]


class DebugChatRequest(BaseModel):
    action: str


@app.on_event("shutdown")
async def shutdown_event() -> None:
    # Ensure the database pool is closed when the application stops.
    await db_manager.close()


@app.post("/api")
async def submit_self_assessment(payload: AnswersPayload, request: Request):
    session = await get_session(request)
    user = session.get("user") if session else None
    user_id = user.get("userId") if user else None
    answers = payload.answers or {}
    try:
        result = await self_assessment_service.submit_answers(user_id or 0, answers)
        return JSONResponse(result)
    except ServiceError as exc:
        return JSONResponse({"success": False, "message": exc.message}, status_code=exc.status_code)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Submit Self-Assessment Unexpected Error: %s", exc)
        return JSONResponse({"success": False, "message": "خطای داخلی سرور"}, status_code=500)


@app.get("/api/blog")
async def get_blog_posts(limit: Optional[str] = Query(default=None)):
    try:
        rows = await blog_service.list_posts(limit)
        return {"success": True, "data": rows}
    except ServiceError as exc:
        return JSONResponse({"success": False, "message": exc.message}, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Get Blog Posts Error: %s", exc)
        return JSONResponse({"success": False, "message": "خطای سرور"}, status_code=500)


@app.get("/api/mystery")
async def get_mystery_assessments():
    try:
        rows = await mystery_service.list_assessments()
        return {"success": True, "data": rows}
    except Exception as exc:
        logger.exception("Get Mystery Assessments Error: %s", exc)
        return JSONResponse({"success": False, "message": "خطای سرور"}, status_code=500)


@app.get("/api/personality-tests")
async def get_personality_tests():
    try:
        rows = await personality_service.list_tests()
        return {"success": True, "data": rows}
    except Exception as exc:
        logger.exception("Get Personality Tests Error: %s", exc)
        return JSONResponse({"success": False, "message": "خطای سرور"}, status_code=500)


@app.get("/api/health")
async def health_check():
    try:
        payload = await health_service.environment_status()
        return payload
    except Exception as exc:
        logger.exception("Health check failed: %s", exc)
        return JSONResponse(
            {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(exc),
            },
            status_code=500,
        )


@app.get("/api/debug")
async def debug_get():
    return debug_service.echo_get()


@app.post("/api/debug")
async def debug_post(request: Request):
    try:
        body = await request.json()
    except Exception as exc:
        return JSONResponse(
            {
                "message": "Error processing request",
                "error": str(exc),
                "success": False,
            },
            status_code=400,
        )
    return debug_service.echo_post(body)


@app.get("/api/debug-chat")
async def debug_chat_get():
    return debug_service.chat_status()


@app.post("/api/debug-chat")
async def debug_chat_post(payload: DebugChatRequest):
    try:
        return debug_service.handle_chat_action(payload.action)
    except ServiceError as exc:
        return JSONResponse({"message": exc.message, "action": payload.action, "success": False}, status_code=exc.status_code)


@app.get("/api/test")
async def api_test():
    return {"success": True, "message": "Backend is running correctly!"}


@app.get("/api/test-db")
async def api_test_db():
    try:
        return await health_service.verify_database()
    except ServiceError as exc:
        return JSONResponse({"success": False, "message": exc.message}, status_code=exc.status_code)
    except Exception as exc:
        logger.exception("خطا در تست دیتابیس: %s", exc)
        return JSONResponse(
            {"success": False, "message": "خطای سرور در تست دیتابیس"},
            status_code=500,
        )


@app.get("/api/healthz")
async def simple_healthz():
    return {"status": "healthy"}
