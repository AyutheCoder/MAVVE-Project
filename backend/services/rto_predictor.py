"""
RTO Risk Prediction Engine.
Computes P(RTO) for orders and routes high-risk ones to MAVVE.
"""

import math
import structlog
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from models.order import Order
from models.address import Address
from core.exceptions import OrderNotFoundError
from config import settings

logger = structlog.get_logger()

# ── Pincode Risk Database (~100 Realistic Indian Pincodes) ──
PINCODE_RISK_DB = {
    # Tier 1 Metros (Low to Medium Risk)
    "400001": 0.05, "400050": 0.06, "400099": 0.08, "400708": 0.07, "411001": 0.06,
    "411038": 0.05, "411057": 0.07, "110001": 0.08, "110020": 0.06, "110092": 0.07,
    "122001": 0.05, "122018": 0.06, "201301": 0.07, "560001": 0.05, "560034": 0.04,
    "560095": 0.06, "560100": 0.05, "600001": 0.08, "600028": 0.07, "600040": 0.06,
    "500001": 0.09, "500032": 0.07, "500081": 0.08, "700001": 0.10, "700016": 0.09,
    "700091": 0.11,
    
    # Tier 2 Cities (Medium Risk)
    "302001": 0.14, "302015": 0.15, "302017": 0.13, "226001": 0.16, "226010": 0.15,
    "226020": 0.18, "462001": 0.15, "462016": 0.14, "462021": 0.16, "380001": 0.12,
    "380015": 0.11, "380054": 0.13, "395001": 0.14, "395007": 0.15, "390001": 0.13,
    "390007": 0.14, "141001": 0.18, "141008": 0.19, "143001": 0.20, "160017": 0.12,
    "248001": 0.16, "248005": 0.17, "800001": 0.22, "800013": 0.24, "800020": 0.21,
    "208001": 0.20, "208012": 0.22, "211001": 0.19, "211008": 0.21, "221001": 0.18,
    "221005": 0.19,
    
    # Tier 3 & Rural / High Risk Areas
    "431001": 0.32, "431005": 0.35, "416001": 0.28, "416012": 0.30, "413001": 0.33,
    "413006": 0.34, "422001": 0.25, "422009": 0.27, "424001": 0.30, "425001": 0.28,
    "301001": 0.31, "305001": 0.26, "313001": 0.24, "334001": 0.29, "342001": 0.22,
    "342008": 0.24, "244001": 0.28, "244005": 0.30, "243001": 0.26, "243005": 0.29,
    "282001": 0.21, "282005": 0.23, "284001": 0.27, "284003": 0.29, "273001": 0.25,
    "273008": 0.28, "842001": 0.35, "842002": 0.38, "823001": 0.32, "823003": 0.34,
    "812001": 0.30, "812005": 0.33, "827001": 0.28, "827013": 0.31, "826001": 0.29,
    "826004": 0.32, "781001": 0.25, "781005": 0.27, "786001": 0.30, "786005": 0.33,
    "734001": 0.24, "734005": 0.26, "713301": 0.29, "713304": 0.31,
    
    # Default fallback
    "default": 0.20
}

class RTOPredictor:
    """
    Predicts the probability of Return to Origin (RTO) for a given order.
    Uses a weighted feature vector including user history, pincode risk,
    address anomaly, amount deviation, time of day, and payment mode.
    """

    def __init__(self, threshold: float = settings.RTO_RISK_THRESHOLD):
        self.threshold = threshold
        logger.info("rto_predictor_initialized", threshold=threshold)

    def _calculate_address_anomaly_score(self, address: Address) -> float:
        """Heuristic to determine if an address looks suspiciously short or incomplete."""
        score = 0.0
        if not address:
            return 1.0

        # Missing standard fields
        if not address.district or not address.state:
            score += 0.3
            
        # Missing landmarks
        if not address.landmarks:
            score += 0.2

        # Shorter address strings in rural areas often mean missing information
        raw_len = len(address.raw_address) if address.raw_address else 0
        if raw_len < 15:
            score += 0.5
        elif raw_len < 30:
            score += 0.25

        return min(score, 1.0)

    def _calculate_time_of_day_risk(self, created_at: datetime) -> float:
        """Orders placed late at night (e.g. 12 AM to 5 AM) often have higher impulse/RTO rates."""
        if not created_at:
            return 0.0
            
        # Ensure we use UTC for consistent evaluation (assuming timestamps are stored in UTC)
        hour = created_at.hour
        # Late night / early morning impulse buys
        if 0 <= hour <= 5:
            return 0.8
        # Late evening
        elif 22 <= hour <= 23:
            return 0.4
        # Standard daytime
        else:
            return 0.1

    def _calculate_amount_deviation(self, order_amount: float, user: User) -> float:
        """Check if this order amount deviates significantly from the user's implicit average."""
        # We don't store exact average, so we'll simulate a baseline of 500 INR
        user_baseline = 500.0
        # If user has a high trust score, we can assume they have a higher spending capacity
        if user and user.trust_score > 0.7:
            user_baseline = 1500.0
        elif user and user.trust_score > 0.4:
            user_baseline = 800.0
            
        # Calculate ratio
        ratio = order_amount / user_baseline
        if ratio > 3.0:
            return 0.9 # Very high deviation
        elif ratio > 2.0:
            return 0.6 # High deviation
        elif ratio > 1.5:
            return 0.3 # Moderate deviation
        
        return 0.0

    async def predict(self, db: AsyncSession, order_id: str) -> dict[str, Any]:
        """
        Compute RTO risk score for an order using a weighted logistic function.
        """
        # Fetch the order, user, and address
        stmt = select(Order).where(Order.order_id == order_id)
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise OrderNotFoundError(order_id)

        stmt_user = select(User).where(User.user_id == order.user_id)
        result_user = await db.execute(stmt_user)
        user = result_user.scalar_one_or_none()
        
        stmt_addr = select(Address).where(Address.user_id == order.user_id).order_by(Address.created_at.desc())
        result_addr = await db.execute(stmt_addr)
        address = result_addr.scalars().first()

        risk_factors: List[str] = []
        features: Dict[str, float] = {}

        # 1. Historical RTO rate
        features['historical_rto'] = user.historical_rto_rate if user else 0.25
        if features['historical_rto'] > 0.3:
            risk_factors.append("high_historical_rto")

        # 2. Payment mode
        if order.payment_mode == "COD":
            features['payment_risk'] = 0.85
            risk_factors.append("cod_payment")
        elif order.payment_mode == "PREPAID_PENDING":
            features['payment_risk'] = 0.4
            risk_factors.append("prepaid_pending")
        else:
            features['payment_risk'] = 0.05

        # 3. Pincode risk
        features['pincode_risk'] = PINCODE_RISK_DB.get(order.pincode, PINCODE_RISK_DB["default"])
        if features['pincode_risk'] > 0.25:
            risk_factors.append("high_risk_pincode")

        # 4. Address anomaly score
        features['address_anomaly'] = self._calculate_address_anomaly_score(address)
        if features['address_anomaly'] > 0.6:
            risk_factors.append("address_anomaly")
        elif features['address_anomaly'] == 1.0:
            risk_factors.append("missing_address")

        # 5. Order amount deviation
        features['amount_deviation'] = self._calculate_amount_deviation(order.total_amount, user)
        if features['amount_deviation'] > 0.5:
            risk_factors.append("unusually_high_amount")

        # 6. Time of day risk
        features['time_of_day_risk'] = self._calculate_time_of_day_risk(order.created_at)
        if features['time_of_day_risk'] > 0.6:
            risk_factors.append("late_night_impulse")

        # 7. Is first order
        features['is_first_order'] = 1.0 if (not user or user.total_orders <= 1) else 0.0
        if features['is_first_order'] > 0:
            risk_factors.append("first_time_user")

        # Calculate weighted logistic score (simulate ML output)
        weights = {
            'historical_rto': 2.5,
            'payment_risk': 1.8,
            'pincode_risk': 1.5,
            'address_anomaly': 2.0,
            'amount_deviation': 1.2,
            'time_of_day_risk': 0.8,
            'is_first_order': 0.9,
        }

        # Linear combination
        linear_sum = sum(features[k] * weights[k] for k in weights)
        bias = -3.8 # Adjust bias to keep average around 0.2 - 0.3
        
        z = linear_sum + bias
        # Sigmoid function for probability
        p_rto = 1 / (1 + math.exp(-z))

        # Adjust score between 0.0 and 1.0
        risk_score = round(max(0.0, min(1.0, p_rto)), 3)

        should_intercept = risk_score > self.threshold

        logger.info(
            "rto_prediction_complete",
            order_id=order_id,
            risk_score=risk_score,
            should_intercept=should_intercept,
            risk_factors=risk_factors
        )

        return {
            "order_id": order_id,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "should_intercept": should_intercept,
            "features": features
        }
