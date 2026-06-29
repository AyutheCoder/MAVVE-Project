import pytest
from services.rto_predictor import RTOPredictor
from models.order import Order
from models.user import User

@pytest.fixture
def predictor():
    return RTOPredictor()

@pytest.mark.asyncio
async def test_rto_scoring_high_risk_user(predictor, sample_order, sample_user):
    # Setup high risk scenario
    sample_user['historical_rto_rate'] = 0.8
    sample_order['pincode'] = "845438" # high risk pincode
    
    order = Order(**sample_order)
    user = User(**sample_user)
    
    score, factors = await predictor.compute_risk_score(order, user)
    
    assert score > 0.65, "Expected high risk score for user with 80% historical RTO."
    assert "historical_rto_rate" in factors
    assert factors["historical_rto_rate"] == 0.8

@pytest.mark.asyncio
async def test_rto_scoring_bad_address(predictor, sample_order, sample_user):
    # Setup bad address, low risk user
    sample_user['historical_rto_rate'] = 0.05
    sample_order['delivery_address'] = {"raw": "near tree"}
    
    order = Order(**sample_order)
    user = User(**sample_user)
    
    score, factors = await predictor.compute_risk_score(order, user)
    
    assert factors["address_anomaly_score"] > 0.5, "Expected high address anomaly score."

@pytest.mark.asyncio
async def test_rto_scoring_prepaid(predictor, sample_order, sample_user):
    # Setup prepaid order
    sample_user['historical_rto_rate'] = 0.9 # Even with high history
    sample_order['payment_mode'] = "PREPAID"
    
    order = Order(**sample_order)
    user = User(**sample_user)
    
    score, factors = await predictor.compute_risk_score(order, user)
    
    # Prepaid heavily discounts risk
    assert score < 0.3, "Prepaid orders should have low RTO risk despite user history."
