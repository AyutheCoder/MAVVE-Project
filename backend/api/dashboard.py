"""
Dashboard data API endpoints.
Provides aggregate statistics, trends, and real-time metrics.
"""

from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import random
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.get("/stats")
async def dashboard_stats():
    """Get aggregate dashboard statistics."""
    return {
        "total_orders_today": 42_187,
        "cod_orders_today": 14_765,
        "rto_rate_current": 18.7,
        "rto_rate_previous": 24.3,
        "rto_rate_change": -5.6,
        "orders_saved_by_mavve": 1_243,
        "savings_inr": 9_944_000,
        "active_sessions": 47,
        "prepaid_conversions_today": 312,
        "addresses_resolved_today": 487,
        "intents_verified_today": 891,
        "avg_response_time_ms": 1_340,
        "languages_active": ["hi", "mr", "bn", "ta", "te", "kn", "gu"],
    }


@router.get("/rto-trend")
async def rto_trend():
    """Get RTO rate time-series data for the last 30 days."""
    base_date = datetime.now(timezone.utc) - timedelta(days=30)
    data = []

    for day in range(30):
        date = base_date + timedelta(days=day)
        # Simulate declining RTO rate after MAVVE deployment (day 15)
        if day < 15:
            rto_rate = round(23.0 + random.uniform(-2, 2), 1)
            mavve_active = False
        else:
            rto_rate = round(18.0 + random.uniform(-2, 2) - (day - 15) * 0.1, 1)
            mavve_active = True

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "rto_rate": max(rto_rate, 12.0),
            "orders_total": random.randint(38_000, 48_000),
            "orders_cod": random.randint(13_000, 17_000),
            "orders_rto": random.randint(2_000, 5_000),
            "mavve_active": mavve_active,
        })

    return {"trend": data, "period": "30d"}


@router.get("/agent-performance")
async def agent_performance():
    """Get performance metrics for each MAVVE agent."""
    return {
        "agents": [
            {
                "agent_type": "address_resolution",
                "display_name": "Address Resolution Agent",
                "emoji": "🏠",
                "total_sessions": 4_872,
                "success_rate": 73.2,
                "avg_rounds": 2.4,
                "avg_duration_seconds": 180,
                "outcomes": {
                    "resolved": 3_566,
                    "partially_resolved": 789,
                    "failed": 517,
                },
            },
            {
                "agent_type": "intent_verification",
                "display_name": "Intent Verification Agent",
                "emoji": "🧠",
                "total_sessions": 8_914,
                "success_rate": 86.1,
                "avg_rounds": 1.8,
                "avg_duration_seconds": 120,
                "outcomes": {
                    "verified": 7_675,
                    "cancelled_preemptively": 891,
                    "escalated": 348,
                },
            },
            {
                "agent_type": "prepaid_conversion",
                "display_name": "Prepaid Conversion Agent",
                "emoji": "💳",
                "total_sessions": 6_203,
                "success_rate": 22.8,
                "avg_rounds": 3.1,
                "avg_duration_seconds": 240,
                "outcomes": {
                    "converted": 1_414,
                    "declined": 4_012,
                    "timed_out": 777,
                },
            },
        ],
        "overall": {
            "total_sessions": 19_989,
            "overall_success_rate": 63.3,
            "orders_saved": 12_655,
            "total_savings_inr": 101_240_000,
        },
    }


@router.get("/language-distribution")
async def language_distribution():
    """Get conversation distribution by language."""
    return {
        "languages": [
            {"code": "hi", "name": "Hindi", "percentage": 38.4, "sessions": 7_676},
            {"code": "mr", "name": "Marathi", "percentage": 18.2, "sessions": 3_638},
            {"code": "bn", "name": "Bengali", "percentage": 14.7, "sessions": 2_938},
            {"code": "ta", "name": "Tamil", "percentage": 10.3, "sessions": 2_059},
            {"code": "te", "name": "Telugu", "percentage": 8.9, "sessions": 1_779},
            {"code": "kn", "name": "Kannada", "percentage": 5.8, "sessions": 1_159},
            {"code": "gu", "name": "Gujarati", "percentage": 3.7, "sessions": 740},
        ]
    }
