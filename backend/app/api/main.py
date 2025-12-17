from fastapi import APIRouter

from app.api.routes import admin_analytics, admin_connectors, admin_system, agents, browser, chat, code, connectors, dashboard_ws, login, ocr, osint, private, rag, scraping, stats, storage, users, utils, workflows
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(workflows.router)
api_router.include_router(connectors.router)
api_router.include_router(admin_connectors.router)
api_router.include_router(admin_analytics.router)
api_router.include_router(admin_system.router)
api_router.include_router(agents.router)
api_router.include_router(rag.router)
api_router.include_router(ocr.router)
api_router.include_router(scraping.router)
api_router.include_router(browser.router)
api_router.include_router(osint.router)
api_router.include_router(code.router)
api_router.include_router(chat.router)
api_router.include_router(chat.ws_router)
api_router.include_router(stats.router)
api_router.include_router(storage.router)
api_router.include_router(dashboard_ws.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
