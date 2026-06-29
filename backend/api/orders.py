"""
Order management API endpoints.
Handles order CRUD, RTO interception, and status management.
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
import structlog
import uuid

from db.database import get_db
from models.order import Order
from models.user import User
from services.rto_predictor import RTOPredictor
from core.exceptions import OrderNotFoundError

from services.session_manager import SessionManager
from services.whatsapp_service import whatsapp

router = APIRouter()
logger = structlog.get_logger()


@router.get("")
async def list_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    payment_mode: Optional[str] = Query(None, description="COD or PREPAID"),
    min_risk: Optional[float] = Query(None, ge=0, le=1),
    max_risk: Optional[float] = Query(None, ge=0, le=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List orders with filtering, sorting, and pagination."""
    stmt = select(Order).order_by(Order.created_at.desc())
    
    if status:
        stmt = stmt.where(Order.status == status.upper())
    if payment_mode:
        stmt = stmt.where(Order.payment_mode == payment_mode.upper())
    if min_risk is not None:
        stmt = stmt.where(Order.rto_risk_score >= min_risk)
    if max_risk is not None:
        stmt = stmt.where(Order.rto_risk_score <= max_risk)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    # Pagination
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    orders = result.scalars().all()

    orders_data = []
    for o in orders:
        orders_data.append({
            "order_id": o.order_id,
            "user_id": o.user_id,
            "seller_id": o.seller_id,
            "total_amount": o.total_amount,
            "payment_mode": o.payment_mode,
            "pincode": o.pincode,
            "status": o.status,
            "rto_risk_score": o.rto_risk_score,
            "created_at": o.created_at.isoformat(),
        })

    return {
        "orders": orders_data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{order_id}")
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed order information by ID."""
    stmt = select(Order).where(Order.order_id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order.order_id,
        "user_id": order.user_id,
        "seller_id": order.seller_id,
        "items": order.items,
        "total_amount": order.total_amount,
        "payment_mode": order.payment_mode,
        "delivery_address": order.delivery_address,
        "pincode": order.pincode,
        "status": order.status,
        "rto_risk_score": order.rto_risk_score,
        "mavve_session_id": order.mavve_session_id,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
        "conversations": [],
        "risk_factors": ["address_anomaly", "first_order"] if (order.rto_risk_score and order.rto_risk_score > 0.5) else [],
    }


class InterceptRequest(BaseModel):
    order_id: str

@router.post("/intercept")
async def intercept_order(
    req: InterceptRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger MAVVE intervention for a specific order.
    Computes RTO risk score and routes high-risk orders to the agent pipeline.
    """
    logger.info("order_intercept_triggered", order_id=req.order_id)

    predictor = RTOPredictor()
    try:
        prediction = await predictor.predict(db, req.order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")

    risk_score = prediction["risk_score"]
    should_intercept = prediction["should_intercept"]
    risk_factors = prediction["risk_factors"]

    update_data = {"rto_risk_score": risk_score}
    session_id = None

    if should_intercept:
        # Fetch the user to get their phone number
        stmt = select(Order, User).join(User, Order.user_id == User.user_id).where(Order.order_id == req.order_id)
        result = await db.execute(stmt)
        row = result.first()
        
        if row:
            order, user = row
            phone = user.phone_number
            
            # Create LangGraph session
            session_id = SessionManager.create_session(
                phone=phone,
                order_id=req.order_id,
                risk_factors=risk_factors
            )
            
            update_data["status"] = "INTERCEPTED"
            update_data["mavve_session_id"] = session_id
            
            # Send initial message via WhatsApp
            initial_msg = f"Hi {user.name}, we received an order for ₹{order.total_amount}. Just confirming you placed this and have the cash ready for delivery in the next few days?"
            await whatsapp.send_text_message(phone, initial_msg)
            
            # Optionally update state to reflect this first message
            session = SessionManager.get_session(phone)
            if session:
                from langchain_core.messages import AIMessage
                session["state"]["messages"].append(AIMessage(content=initial_msg))
                SessionManager.update_session_state(phone, session["state"])
                
    else:
        update_data["status"] = "DISPATCHED"

    stmt = update(Order).where(Order.order_id == req.order_id).values(**update_data)
    await db.execute(stmt)

    return {
        "order_id": req.order_id,
        "rto_risk_score": risk_score,
        "risk_factors": risk_factors,
        "intercepted": should_intercept,
        "mavve_session_id": session_id,
        "message": (
            "Order flagged for MAVVE intervention. WhatsApp message sent."
            if should_intercept
            else "Order risk below threshold — proceeding to dispatch"
        ),
    }
