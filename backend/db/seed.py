"""
MAVVE Seed Data Script
======================
Populates the database with 50 realistic Indian e-commerce orders
spanning multiple languages, pincodes, risk profiles, and rural addresses.

Usage:
    cd backend
    python -m db.seed

Requires:
    - PostgreSQL running and accessible via DATABASE_URL
    - Tables already created (via Alembic or create_all_tables)
"""

import asyncio
import uuid
import random
from datetime import datetime, timezone, timedelta

# ─────────────────────────────────────────────────────────
# Realistic Indian Data Sets
# ─────────────────────────────────────────────────────────

USERS_DATA = [
    # (name, phone, language, pincode, rto_rate, orders, returns, trust)
    ("Rajesh Kumar", "+919876543210", "hi", "226001", 0.12, 28, 3, 0.72),
    ("Priya Sharma", "+919812345678", "hi", "302001", 0.05, 42, 2, 0.88),
    ("Anil Patel", "+919723456789", "gu", "380001", 0.22, 15, 3, 0.55),
    ("Sunita Devi", "+919634567890", "hi", "800001", 0.35, 8, 3, 0.38),
    ("Ramesh Yadav", "+919545678901", "hi", "462001", 0.18, 22, 4, 0.62),
    ("Meena Kumari", "+919456789012", "hi", "110001", 0.08, 35, 3, 0.80),
    ("Sanjay Gupta", "+919367890123", "hi", "208001", 0.15, 18, 3, 0.65),
    ("Asha Bai", "+919278901234", "mr", "411001", 0.30, 10, 3, 0.42),
    ("Vikram Singh", "+919189012345", "hi", "302012", 0.10, 30, 3, 0.78),
    ("Kavita Joshi", "+919090123456", "mr", "400001", 0.03, 55, 2, 0.92),
    ("Suresh Reddy", "+918901234567", "te", "500001", 0.20, 16, 3, 0.58),
    ("Lakshmi Naik", "+918812345678", "kn", "560001", 0.07, 40, 3, 0.85),
    ("Manoj Tiwari", "+918723456789", "hi", "452001", 0.28, 12, 3, 0.48),
    ("Geeta Deshpande", "+918634567890", "mr", "411038", 0.14, 25, 4, 0.68),
    ("Ajay More", "+918545678901", "mr", "431001", 0.40, 5, 2, 0.30),
    ("Ritu Verma", "+918456789012", "hi", "226010", 0.06, 38, 2, 0.86),
    ("Deepak Chauhan", "+918367890123", "hi", "141001", 0.25, 14, 4, 0.52),
    ("Parvati Iyer", "+918278901234", "ta", "600001", 0.09, 32, 3, 0.82),
    ("Mohan Das", "+918189012345", "bn", "700001", 0.32, 9, 3, 0.40),
    ("Sita Ram", "+918090123456", "hi", "301001", 0.16, 20, 3, 0.64),
    ("Arjun Nair", "+917901234567", "ml", "682001", 0.04, 48, 2, 0.90),
    ("Rekha Patil", "+917812345678", "mr", "416001", 0.38, 6, 2, 0.32),
    ("Gopal Krishna", "+917723456789", "te", "530001", 0.21, 17, 4, 0.56),
    ("Kamla Rani", "+917634567890", "hi", "244001", 0.33, 7, 2, 0.36),
    ("Bharat Singh", "+917545678901", "hi", "342001", 0.11, 26, 3, 0.74),
]

# Realistic rural Indian addresses — the kind that cause RTO
RURAL_ADDRESSES = [
    {
        "raw": "Bade mandir ke paas, Gupta ji ki dukaan ke peeche, Mohalla Rajputana",
        "district": "Lucknow", "state": "Uttar Pradesh",
        "landmarks": [{"name": "Shiv Mandir", "type": "temple", "distance_m": 150}],
    },
    {
        "raw": "Gram Panchayat office se 200 meter, neem ke ped ke samne",
        "district": "Jaipur", "state": "Rajasthan",
        "landmarks": [{"name": "Panchayat Bhawan", "type": "government", "distance_m": 200}],
    },
    {
        "raw": "Station Road, sabzi mandi ke peeche, galli no 3",
        "district": "Ahmedabad", "state": "Gujarat",
        "landmarks": [{"name": "Railway Station", "type": "transport", "distance_m": 400}],
    },
    {
        "raw": "Near old temple behind primary school village boundary pe",
        "district": "Patna", "state": "Bihar",
        "landmarks": [{"name": "Primary School", "type": "education", "distance_m": 100}],
    },
    {
        "raw": "Bus stand ke samne, Mahatma Gandhi Chowk, purani haveli wali gali",
        "district": "Indore", "state": "Madhya Pradesh",
        "landmarks": [{"name": "Bus Stand", "type": "transport", "distance_m": 50}],
    },
    {
        "raw": "Hanuman temple road, doodh dairy ke samne, Shastri Nagar",
        "district": "Kanpur", "state": "Uttar Pradesh",
        "landmarks": [{"name": "Hanuman Temple", "type": "temple", "distance_m": 80}],
    },
    {
        "raw": "Opposite Maruti Showroom, NH-48 ke paas, Rajiv Gandhi Colony",
        "district": "Pune", "state": "Maharashtra",
        "landmarks": [{"name": "Maruti Showroom", "type": "commercial", "distance_m": 30}],
    },
    {
        "raw": "Kisan Mandi ke peeche, Nehru Park ke samne, Ward 12",
        "district": "Nagpur", "state": "Maharashtra",
        "landmarks": [{"name": "Nehru Park", "type": "park", "distance_m": 120}],
    },
    {
        "raw": "Bazaar Road, cloth market ke andar, Laxmi Narayan Mandir ke paas",
        "district": "Aurangabad", "state": "Maharashtra",
        "landmarks": [{"name": "Laxmi Narayan Mandir", "type": "temple", "distance_m": 200}],
    },
    {
        "raw": "Near water tank, Ambedkar Colony, post office se left",
        "district": "Hyderabad", "state": "Telangana",
        "landmarks": [{"name": "Post Office", "type": "government", "distance_m": 250}],
    },
    {
        "raw": "Purana talab ke kinarey, Ganesh Ghat se aage, Mohalla Sadar",
        "district": "Bengaluru", "state": "Karnataka",
        "landmarks": [{"name": "Ganesh Ghat", "type": "landmark", "distance_m": 180}],
    },
    {
        "raw": "Kovil theruvil, bus stand-ku pakathula, 3-vatu theru",
        "district": "Chennai", "state": "Tamil Nadu",
        "landmarks": [{"name": "Amman Kovil", "type": "temple", "distance_m": 100}],
    },
    {
        "raw": "Bazar er kachhe, school er pashe, Netaji Road, Ward 8",
        "district": "Kolkata", "state": "West Bengal",
        "landmarks": [{"name": "Bazar", "type": "market", "distance_m": 50}],
    },
    {
        "raw": "Talav ni bagal ma, Patel Falia, station road thi right",
        "district": "Surat", "state": "Gujarat",
        "landmarks": [{"name": "Talav", "type": "landmark", "distance_m": 150}],
    },
    {
        "raw": "Devala javaḷa, bazar madhye, shivar road la, ward 5",
        "district": "Nashik", "state": "Maharashtra",
        "landmarks": [{"name": "Dev Mandir", "type": "temple", "distance_m": 90}],
    },
]

# Product catalog for realistic items
PRODUCTS = [
    {"sku": "WF-KURTI-001", "name": "Cotton Anarkali Kurti", "price": 349, "category": "women_fashion"},
    {"sku": "WF-SAREE-002", "name": "Banarasi Silk Saree", "price": 899, "category": "women_fashion"},
    {"sku": "WF-DUPATTA-003", "name": "Chiffon Printed Dupatta", "price": 149, "category": "women_fashion"},
    {"sku": "MF-SHIRT-001", "name": "Cotton Casual Shirt", "price": 399, "category": "men_fashion"},
    {"sku": "MF-JEANS-002", "name": "Slim Fit Denim Jeans", "price": 549, "category": "men_fashion"},
    {"sku": "KF-TSHIRT-001", "name": "Kids Cartoon T-Shirt", "price": 199, "category": "kids_fashion"},
    {"sku": "HG-BEDSHEET-001", "name": "Double Bed Cotton Bedsheet", "price": 449, "category": "home_garden"},
    {"sku": "HG-CURTAIN-002", "name": "Floral Print Curtain Set", "price": 599, "category": "home_garden"},
    {"sku": "EL-EARPHONE-001", "name": "Wireless Bluetooth Earbuds", "price": 299, "category": "electronics"},
    {"sku": "EL-CHARGER-002", "name": "Fast Charging USB-C Cable", "price": 129, "category": "electronics"},
    {"sku": "BT-CREAM-001", "name": "Fair & Lovely Face Cream", "price": 89, "category": "beauty"},
    {"sku": "BT-OIL-002", "name": "Coconut Hair Oil 200ml", "price": 120, "category": "beauty"},
    {"sku": "KT-TIFFIN-001", "name": "Stainless Steel Tiffin Box", "price": 249, "category": "kitchen"},
    {"sku": "KT-BOTTLE-002", "name": "Copper Water Bottle 1L", "price": 399, "category": "kitchen"},
    {"sku": "WF-LEGGINS-004", "name": "Printed Cotton Leggings", "price": 199, "category": "women_fashion"},
]

SELLERS = [
    "SEL-MUM-001", "SEL-DEL-002", "SEL-BLR-003", "SEL-HYD-004", "SEL-JAI-005",
    "SEL-SUR-006", "SEL-PUN-007", "SEL-KOL-008", "SEL-CHN-009", "SEL-LKO-010",
    "SEL-IND-011", "SEL-NGP-012", "SEL-AHM-013", "SEL-PAT-014", "SEL-JPR-015",
]

ORDER_STATUSES = ["PLACED", "INTERCEPTED", "VALIDATED", "DISPATCHED", "DELIVERED", "RTO"]
AGENT_TYPES = ["address_resolution", "intent_verification", "prepaid_conversion"]
OUTCOMES = ["converted", "confirmed", "cancelled", "escalated", "timed_out"]


def _random_items():
    """Generate 1-3 random order items."""
    count = random.randint(1, 3)
    items = random.sample(PRODUCTS, k=min(count, len(PRODUCTS)))
    return [
        {**item, "qty": random.randint(1, 2)}
        for item in items
    ]


def _generate_users():
    """Build User model instances from the data set."""
    from models.user import User

    users = []
    for name, phone, lang, pin, rto, orders, returns, trust in USERS_DATA:
        users.append(User(
            user_id=str(uuid.uuid4()),
            phone_number=phone,
            name=name,
            preferred_language=lang,
            pincode=pin,
            historical_rto_rate=rto,
            total_orders=orders,
            total_returns=returns,
            trust_score=trust,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 365)),
            updated_at=datetime.now(timezone.utc),
        ))
    return users


def _generate_orders(users):
    """Build 50 Order model instances with realistic distributions."""
    from models.order import Order

    orders = []
    for i in range(50):
        user = random.choice(users)
        items = _random_items()
        total = sum(item["price"] * item["qty"] for item in items)
        addr_data = random.choice(RURAL_ADDRESSES)

        # Weighted payment mode: 65% COD, 30% PREPAID, 5% PREPAID_PENDING
        payment_mode = random.choices(
            ["COD", "PREPAID", "PREPAID_PENDING"],
            weights=[65, 30, 5],
        )[0]

        # Risk score correlated with user trust and payment mode
        base_risk = 1.0 - user.trust_score
        if payment_mode == "PREPAID":
            base_risk *= 0.2  # prepaid orders are low risk
        risk_score = round(min(max(base_risk + random.uniform(-0.15, 0.15), 0.02), 0.98), 3)

        # Status distribution
        if risk_score > 0.65 and payment_mode == "COD":
            status = random.choices(
                ["INTERCEPTED", "VALIDATED", "RTO", "CANCELLED"],
                weights=[30, 25, 30, 15],
            )[0]
        elif payment_mode == "PREPAID":
            status = random.choices(
                ["DISPATCHED", "DELIVERED"],
                weights=[40, 60],
            )[0]
        else:
            status = random.choices(
                ORDER_STATUSES,
                weights=[15, 10, 15, 25, 25, 10],
            )[0]

        mavve_session = str(uuid.uuid4()) if status in ("INTERCEPTED", "VALIDATED") else None

        orders.append(Order(
            order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            user_id=user.user_id,
            seller_id=random.choice(SELLERS),
            items=items,
            total_amount=round(total, 2),
            payment_mode=payment_mode,
            delivery_address={
                "raw": addr_data["raw"],
                "district": addr_data["district"],
                "state": addr_data["state"],
            },
            pincode=user.pincode or "226001",
            status=status,
            rto_risk_score=risk_score,
            mavve_session_id=mavve_session,
            created_at=datetime.now(timezone.utc) - timedelta(
                hours=random.randint(1, 720)
            ),
            updated_at=datetime.now(timezone.utc),
        ))
    return orders


def _generate_addresses(users):
    """Build Address records for each user."""
    from models.address import Address

    addresses = []
    for user in users:
        addr_data = random.choice(RURAL_ADDRESSES)
        confidence = round(random.uniform(0.2, 0.95), 2)

        addresses.append(Address(
            address_id=str(uuid.uuid4()),
            user_id=user.user_id,
            raw_address=addr_data["raw"],
            normalized_address=(
                f"{addr_data['district']}, {addr_data['state']}, {user.pincode}"
                if confidence > 0.7 else None
            ),
            pincode=user.pincode or "226001",
            district=addr_data["district"],
            state=addr_data["state"],
            landmarks=addr_data["landmarks"],
            confidence_score=confidence,
            geo_lat=round(random.uniform(12.0, 30.0), 6) if confidence > 0.6 else None,
            geo_lng=round(random.uniform(72.0, 88.0), 6) if confidence > 0.6 else None,
            verified=confidence > 0.85,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 180)),
            updated_at=datetime.now(timezone.utc),
        ))
    return addresses


def _generate_conversations(orders):
    """Build Conversation records for intercepted/validated orders."""
    from models.conversation import Conversation

    conversations = []
    for order in orders:
        if order.status not in ("INTERCEPTED", "VALIDATED", "RTO", "CANCELLED"):
            continue

        agent_type = random.choice(AGENT_TYPES)

        # Build a realistic mini-transcript
        user_lang = random.choice(["hi", "mr", "bn", "ta", "te"])
        greetings = {
            "hi": "Namaste! Aapka order confirm karna chahte hain.",
            "mr": "Namaskar! Tumcha order confirm karaycha aahe.",
            "bn": "Namaskar! Apnar order confirm korte chai.",
            "ta": "Vanakkam! Ungal order-ai confirm seyya virumbugirom.",
            "te": "Namaskaaram! Mee order confirm cheyalanukunnam.",
        }
        user_responses = {
            "hi": "Haan ji, mujhe chahiye yeh saman. Main ghar par hi hoon.",
            "mr": "Ho, malaa hava aahe. Mi ghari ahe.",
            "bn": "Hyan, amar dorkar. Ami barite achi.",
            "ta": "Aam, enakku venum. Naan veetil irukken.",
            "te": "Avunu, naaku kaavali. Nenu intlo unnanu.",
        }

        messages = [
            {
                "role": "agent",
                "content": greetings.get(user_lang, greetings["hi"]),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "language": user_lang,
            },
            {
                "role": "user",
                "content": user_responses.get(user_lang, user_responses["hi"]),
                "timestamp": (datetime.now(timezone.utc) + timedelta(seconds=45)).isoformat(),
                "language": user_lang,
            },
            {
                "role": "agent",
                "content": "Dhanyavaad! Aapka order confirm ho gaya hai.",
                "timestamp": (datetime.now(timezone.utc) + timedelta(seconds=90)).isoformat(),
                "language": user_lang,
            },
        ]

        outcome = random.choices(
            ["confirmed", "converted", "cancelled", "escalated", "timed_out"],
            weights=[35, 20, 25, 10, 10],
        )[0]

        discount = round(random.uniform(10, 50), 2) if outcome == "converted" else 0.0

        conversations.append(Conversation(
            session_id=order.mavve_session_id or str(uuid.uuid4()),
            order_id=order.order_id,
            agent_type=agent_type,
            channel=random.choice(["whatsapp_text", "whatsapp_voice"]),
            user_language=user_lang,
            messages=messages,
            outcome=outcome,
            duration_seconds=random.randint(60, 600),
            discount_applied=discount,
            created_at=order.created_at,
        ))

    return conversations


async def seed_database():
    """
    Main seed function — populates all tables with realistic data.
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from db.database import AsyncSessionLocal, create_all_tables
    from models.user import User
    from sqlalchemy import select

    print("🌱 MAVVE Seed Script")
    print("=" * 50)

    # Create tables if they don't exist
    print("📦 Creating tables...")
    await create_all_tables()
    print("   ✅ Tables created")

    async with AsyncSessionLocal() as session:
        existing_user = await session.execute(select(User).limit(1))
        if existing_user.scalars().first() is not None:
            print("✨ Database is already seeded. Skipping...")
            return

    # Generate data
    print("👤 Generating 25 users...")
    users = _generate_users()

    print("📦 Generating 50 orders...")
    orders = _generate_orders(users)

    print("📍 Generating 25 addresses...")
    addresses = _generate_addresses(users)

    print("💬 Generating conversations...")
    conversations = _generate_conversations(orders)

    # Insert into database
    async with AsyncSessionLocal() as session:
        try:
            session.add_all(users)
            await session.flush()
            print(f"   ✅ {len(users)} users inserted")

            session.add_all(orders)
            await session.flush()
            print(f"   ✅ {len(orders)} orders inserted")

            session.add_all(addresses)
            await session.flush()
            print(f"   ✅ {len(addresses)} addresses inserted")

            session.add_all(conversations)
            await session.flush()
            print(f"   ✅ {len(conversations)} conversations inserted")

            await session.commit()
            print()
            print("🎉 Seed complete!")
            print(f"   Users:         {len(users)}")
            print(f"   Orders:        {len(orders)}")
            print(f"   Addresses:     {len(addresses)}")
            print(f"   Conversations: {len(conversations)}")

            # Print sample data
            print()
            print("📋 Sample Orders:")
            for order in orders[:5]:
                print(
                    f"   {order.order_id}: "
                    f"₹{order.total_amount:>7.0f} | "
                    f"{order.payment_mode:<16} | "
                    f"risk={order.rto_risk_score:.3f} | "
                    f"{order.status}"
                )

        except Exception as e:
            await session.rollback()
            print(f"❌ Seed failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
