"""
Demo API Endpoints.
Endpoints for simulating the end-to-end MAVVE flow easily from a UI.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import uuid
import asyncio

from db.database import get_db
from models.order import Order
from models.user import User
from api.orders import intercept_order, InterceptRequest
from services.session_manager import SessionManager

router = APIRouter()
logger = structlog.get_logger()

class DemoSimulateRequest(BaseModel):
    phone_number: str = "+919876543210"
    scenario: str = "address_anomaly"

@router.post("/simulate")
async def demo_simulate_flow(req: DemoSimulateRequest, db: AsyncSession = Depends(get_db)):
    """
    Creates a mock high-risk order for the given phone number,
    triggers the intercept flow, and returns the initial state.
    """
    # 1. Ensure user exists
    stmt = select(User).where(User.phone_number == req.phone_number)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Create a mock user
        user = User(
            user_id=f"demo_user_{uuid.uuid4().hex[:8]}",
            phone_number=req.phone_number,
            name="Demo User",
            preferred_language="hi",
            pincode="411001",
            historical_rto_rate=0.8,
            total_orders=10,
            total_returns=8
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    # 2. Create a mock high-risk order
    order = Order(
        order_id=f"demo_order_{uuid.uuid4().hex[:8]}",
        user_id=user.user_id,
        seller_id="SELLER-DEMO",
        items=[{"name": "Demo Kurti", "price": 499, "qty": 1}],
        total_amount=499,
        payment_mode="COD",
        delivery_address={"raw": "Demo Address Missing details, near tree"},
        pincode="411001",
        status="PLACED"
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # 3. Trigger Intercept Flow
    intercept_req = InterceptRequest(order_id=order.order_id)
    intercept_res = await intercept_order(intercept_req, db)
    
    # 4. Wait slightly to allow session to initialize and WhatsApp mock to be sent
    await asyncio.sleep(1)
    
    session = SessionManager.get_session(req.phone_number)
    
    return {
        "status": "success",
        "demo_order": {
            "order_id": order.order_id,
            "total_amount": order.total_amount,
            "payment_mode": order.payment_mode
        },
        "intercept_result": intercept_res,
        "session_initialized": session is not None,
        "next_steps": "Open the Simulator UI and chat using this phone number."
    }
