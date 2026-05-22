"""
AI Trend Daily — Web Server

Serves the frontend, JSON data, and runs the daily pipeline scheduler.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=1)

# ── Scheduler ──────────────────────────────────────────────────────────────

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = AsyncIOScheduler()
    SCHEDULER_AVAILABLE = True
except ImportError:
    scheduler = None
    SCHEDULER_AVAILABLE = False
    logger.warning("APScheduler not installed — daily cron disabled")


def _run_pipeline_blocking() -> None:
    """Run the full pipeline synchronously (called from executor)."""
    try:
        from src.pipeline import run_pipeline

        logger.info("Pipeline: starting daily run...")
        report = run_pipeline(since="daily", enhance_api=True, generate_ai=True)
        logger.info(
            "Pipeline: done — %d repos, %d AI-related, %d categories",
            report.total_repos,
            report.total_ai_repos,
            len(report.categories),
        )
    except Exception:
        logger.exception("Pipeline run failed")


async def run_pipeline_task() -> None:
    """Run the pipeline in a thread pool to avoid blocking the event loop."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, _run_pipeline_blocking)


# ── FastAPI App ────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    if SCHEDULER_AVAILABLE and scheduler:
        trigger = CronTrigger(hour=0, minute=30, timezone=timezone.utc)
        scheduler.add_job(run_pipeline_task, trigger, id="daily_pipeline")
        scheduler.start()
        logger.info("Scheduler started — daily pipeline at 00:30 UTC")
    yield
    if SCHEDULER_AVAILABLE and scheduler:
        scheduler.shutdown(wait=False)
    executor.shutdown(wait=False)


app = FastAPI(
    title="AI Trend Daily",
    version="1.0.0",
    lifespan=lifespan,
)


# ── API ────────────────────────────────────────────────────────────────────


@app.post("/api/pipeline")
async def trigger_pipeline():
    """Manually trigger the pipeline."""
    logger.info("Manual pipeline trigger via API")
    await run_pipeline_task()
    return {"status": "ok", "message": "Pipeline completed"}


@app.get("/api/status")
async def status():
    """Check server status."""
    latest_path = "data/reports/latest.json"
    last_run = None
    if os.path.exists(latest_path):
        import json
        with open(latest_path) as f:
            data = json.load(f)
            last_run = data.get("date")
    return {
        "status": "running",
        "last_run": last_run,
        "scheduler": SCHEDULER_AVAILABLE,
    }


# ── Static Files ───────────────────────────────────────────────────────────

# Serve JSON report data
data_dir = "data/reports"
if os.path.exists(data_dir):
    app.mount("/data/reports", StaticFiles(directory=data_dir), name="reports")
    logger.info("Serving data reports from %s", data_dir)
else:
    logger.warning("Data directory %s not found", data_dir)

# Serve built frontend
frontend_dist = "frontend/dist"
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    logger.info("Serving frontend from %s", frontend_dist)
else:
    logger.warning("Frontend build not found at %s", frontend_dist)

    @app.get("/")
    async def root():
        return {
            "message": "AI Trend Daily — frontend not built yet",
            "docs": "Run: cd frontend && npm run build",
        }
