"""
Order Generator for MAVVE Simulator
Generates batches of realistic Indian e-commerce orders and saves them to the DB.
"""
import random
import uuid
import sys
import os

# Add backend directory to sys.path to import DB models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import SessionLocal
from models.order import Order
from models.user import User

# --- Realistic Indian Data ---
FIRST_NAMES = ['Aarav', 'Vihaan', 'Aditya', 'Ramesh', 'Suresh', 'Priya', 'Neha', 'Sunita', 'Kavita', 'Vikram', 'Rajesh', 'Amit']
LAST_NAMES = ['Sharma', 'Patil', 'Singh', 'Kumar', 'Das', 'Mishra', 'Yadav', 'Deshmukh', 'Kulkarni', 'Joshi']
STATES = [
    {'name': 'Maharashtra', 'pincodes': ['411001', '400001', '413709', '422001']},
    {'name': 'Uttar Pradesh', 'pincodes': ['226001', '201301', '211001']},
    {'name': 'Karnataka', 'pincodes': ['560001', '570001', '574104']},
    {'name': 'West Bengal', 'pincodes': ['700001', '734001']}
]
PRODUCTS = [
    {'name': 'Cotton Kurti Floral Print', 'price': 299},
    {'name': 'Men Solid T-Shirt Pack of 3', 'price': 399},
    {'name': 'Wireless Bluetooth Earphones', 'price': 349},
    {'name': 'Kitchen Storage Containers Set', 'price': 249},
    {'name': 'Saree with Blouse Piece', 'price': 449}
]

def generate_phone():
    return f"+919{random.randint(100000000, 999999999)}"

def generate_address(is_bad=False):
    state_obj = random.choice(STATES)
    pincode = random.choice(state_obj['pincodes'])
    
    if is_bad:
        # Generate an ambiguous/rural address missing key components
        raw = f"Near temple, {random.choice(['blue gate', 'banyan tree', 'school'])}, {state_obj['name']}"
    else:
        # Generate a good address
        raw = f"House No {random.randint(1, 100)}, Street {random.randint(1, 15)}, {state_obj['name']}, {pincode}"
        
    return {"raw": raw}, pincode

async def generate_orders(count=10, cod_ratio=0.8, high_risk_ratio=0.3):
    """Generates mock orders and saves them to the DB."""
    
    async with SessionLocal() as db:
        generated_orders = []
        
        for _ in range(count):
            phone = generate_phone()
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            is_high_risk = random.random() < high_risk_ratio
            is_cod = random.random() < cod_ratio
            
            # Create Mock User
            user = User(
                user_id=f"sim_user_{uuid.uuid4().hex[:8]}",
                phone_number=phone,
                name=name,
                preferred_language=random.choice(["hi", "mr", "bn", "en"]),
                pincode="411001",
                historical_rto_rate=0.7 if is_high_risk else 0.1,
                total_orders=random.randint(1, 20),
                total_returns=random.randint(0, 5)
            )
            db.add(user)
            await db.flush()
            
            # Create Mock Order
            prod = random.choice(PRODUCTS)
            addr, pin = generate_address(is_bad=is_high_risk)
            
            order = Order(
                order_id=f"sim_ord_{uuid.uuid4().hex[:8]}",
                user_id=user.user_id,
                seller_id="SIM-SELLER",
                items=[{"name": prod['name'], "price": prod['price'], "qty": 1}],
                total_amount=prod['price'],
                payment_mode="COD" if is_cod else "PREPAID",
                delivery_address=addr,
                pincode=pin,
                status="PLACED"
            )
            db.add(order)
            generated_orders.append((order, user))
            
        await db.commit()
        
        print(f"✅ Generated {count} realistic mock orders.")
        return generated_orders

if __name__ == "__main__":
    asyncio.run(generate_orders(count=5))
