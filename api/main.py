"""
Financial Analytics API Backend
Enterprise-grade financial data models and API endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import pandas as pd
import numpy as np
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ERP Financial Analytics API",
    description="Enterprise-grade financial analytics and reporting API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./financial_analytics.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class PeriodType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class CompanyUnit(str, Enum):
    CONSOLIDATED = "consolidated"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"


# Database Models
class FinancialPeriod(Base):
    __tablename__ = "financial_periods"

    id = Column(Integer, primary_key=True, index=True)
    period_date = Column(Date, nullable=False)
    company_unit = Column(String, default="consolidated")
    revenue = Column(Float, nullable=False)
    cogs = Column(Float, nullable=False)
    gross_profit = Column(Float, nullable=False)
    salaries = Column(Float, nullable=False)
    marketing = Column(Float, nullable=False)
    rd_expense = Column(Float, nullable=False)
    operations = Column(Float, nullable=False)
    other_expenses = Column(Float, nullable=False)
    total_expenses = Column(Float, nullable=False)
    net_profit = Column(Float, nullable=False)
    gross_margin_pct = Column(Float, nullable=False)
    net_margin_pct = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class BudgetData(Base):
    __tablename__ = "budget_data"

    id = Column(Integer, primary_key=True, index=True)
    period_date = Column(Date, nullable=False)
    company_unit = Column(String, default="consolidated")
    budget_revenue = Column(Float, nullable=False)
    budget_net_profit = Column(Float, nullable=False)
    budget_expenses = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CashFlowData(Base):
    __tablename__ = "cash_flow_data"

    id = Column(Integer, primary_key=True, index=True)
    period_date = Column(Date, nullable=False)
    company_unit = Column(String, default="consolidated")
    operating_cash_flow = Column(Float, nullable=False)
    investing_cash_flow = Column(Float, nullable=False)
    financing_cash_flow = Column(Float, nullable=False)
    net_cash_flow = Column(Float, nullable=False)
    cash_balance = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic Models
class FinancialMetrics(BaseModel):
    period_date: date
    revenue: float
    cogs: float
    gross_profit: float
    salaries: float
    marketing: float
    rd_expense: float
    operations: float
    other_expenses: float
    total_expenses: float
    net_profit: float
    gross_margin_pct: float
    net_margin_pct: float


class KPIResponse(BaseModel):
    total_revenue: float
    revenue_growth_pct: float
    total_profit: float
    profit_growth_pct: float
    net_margin_pct: float
    margin_change_pp: float
    cash_position: float
    period_start: date
    period_end: date


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Data generation functions
def generate_sample_financial_data(db: Session):
    """Generate comprehensive sample financial data"""

    # Check if data already exists
    existing_count = db.query(FinancialPeriod).count()
    if existing_count > 0:
        logger.info(f"Financial data already exists ({existing_count} records)")
        return

    logger.info("Generating sample financial data...")

    # Generate 24 months of data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=730)

    # Create monthly periods
    current_date = start_date.replace(day=1)
    revenue_base = 50000000  # $50M annual revenue

    while current_date <= end_date:
        # Add seasonality and growth
        month_factor = 1 + 0.1 * np.sin(2 * np.pi * current_date.month / 12)
        months_since_start = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
        growth_factor = 1 + (months_since_start * 0.005)  # 0.5% monthly growth
        random_factor = np.random.normal(1, 0.08)

        monthly_revenue = (revenue_base / 12) * month_factor * growth_factor * random_factor
        monthly_revenue = max(monthly_revenue, 0)

        # Calculate expenses
        cogs = monthly_revenue * np.random.normal(0.35, 0.02)
        salaries = monthly_revenue * np.random.normal(0.25, 0.01)
        marketing = monthly_revenue * np.random.normal(0.08, 0.02)
        rd = monthly_revenue * np.random.normal(0.12, 0.01)
        operations = monthly_revenue * np.random.normal(0.06, 0.01)
        other_expenses = monthly_revenue * np.random.normal(0.04, 0.01)

        total_expenses = cogs + salaries + marketing + rd + operations + other_expenses
        gross_profit = monthly_revenue - cogs
        net_profit = monthly_revenue - total_expenses
        gross_margin = (gross_profit / monthly_revenue) * 100
        net_margin = (net_profit / monthly_revenue) * 100

        # Save financial period
        financial_period = FinancialPeriod(
            period_date=current_date,
            revenue=monthly_revenue,
            cogs=cogs,
            gross_profit=gross_profit,
            salaries=salaries,
            marketing=marketing,
            rd_expense=rd,
            operations=operations,
            other_expenses=other_expenses,
            total_expenses=total_expenses,
            net_profit=net_profit,
            gross_margin_pct=gross_margin,
            net_margin_pct=net_margin
        )
        db.add(financial_period)

        # Generate budget data (10% variance from actual)
        budget_variance = np.random.normal(1.1, 0.05)
        budget_data = BudgetData(
            period_date=current_date,
            budget_revenue=monthly_revenue * budget_variance,
            budget_net_profit=net_profit * budget_variance,
            budget_expenses=total_expenses * np.random.normal(0.95, 0.03)
        )
        db.add(budget_data)

        # Generate cash flow data
        operating_cf = net_profit + np.random.normal(500000, 100000)
        investing_cf = np.random.normal(-200000, 50000)
        financing_cf = np.random.normal(-100000, 200000)
        net_cf = operating_cf + investing_cf + financing_cf

        # Calculate cumulative cash balance
        previous_balance = 10000000  # Starting balance
        if current_date > start_date:
            prev_cash = db.query(CashFlowData).filter(
                CashFlowData.period_date < current_date
            ).order_by(CashFlowData.period_date.desc()).first()
            if prev_cash:
                previous_balance = prev_cash.cash_balance

        cash_balance = previous_balance + net_cf

        cash_flow = CashFlowData(
            period_date=current_date,
            operating_cash_flow=operating_cf,
            investing_cash_flow=investing_cf,
            financing_cash_flow=financing_cf,
            net_cash_flow=net_cf,
            cash_balance=cash_balance
        )
        db.add(cash_flow)

        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    db.commit()
    logger.info("Sample financial data generated successfully")


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data"""
    db = SessionLocal()
    try:
        generate_sample_financial_data(db)
    finally:
        db.close()


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Financial Analytics API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/financial/kpis", response_model=KPIResponse)
async def get_financial_kpis(
        period_months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
        company_unit: CompanyUnit = Query(CompanyUnit.CONSOLIDATED, description="Company unit to analyze"),
        db: Session = Depends(get_db)
):
    """Get key financial performance indicators"""

    try:
        # Get current period data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_months * 30)

        current_data = db.query(FinancialPeriod).filter(
            FinancialPeriod.period_date >= start_date,
            FinancialPeriod.period_date <= end_date,
            FinancialPeriod.company_unit == company_unit.value
        ).all()

        # Get previous period for comparison
        prev_start = start_date - timedelta(days=period_months * 30)
        prev_end = start_date

        previous_data = db.query(FinancialPeriod).filter(
            FinancialPeriod.period_date >= prev_start,
            FinancialPeriod.period_date < prev_end,
            FinancialPeriod.company_unit == company_unit.value
        ).all()

        if not current_data:
            raise HTTPException(status_code=404, detail="No financial data found for the specified period")

        # Calculate current metrics
        current_revenue = sum(p.revenue for p in current_data)
        current_profit = sum(p.net_profit for p in current_data)
        current_margin = (current_profit / current_revenue) * 100 if current_revenue > 0 else 0

        # Calculate growth rates
        revenue_growth = 0
        profit_growth = 0
        margin_change = 0

        if previous_data:
            prev_revenue = sum(p.revenue for p in previous_data)
            prev_profit = sum(p.net_profit for p in previous_data)
            prev_margin = (prev_profit / prev_revenue) * 100 if prev_revenue > 0 else 0

            revenue_growth = ((current_revenue - prev_revenue) / prev_revenue) * 100 if prev_revenue > 0 else 0
            profit_growth = ((current_profit - prev_profit) / prev_profit) * 100 if prev_profit > 0 else 0
            margin_change = current_margin - prev_margin

        # Estimate cash position
        cash_data = db.query(CashFlowData).filter(
            CashFlowData.period_date <= end_date,
            CashFlowData.company_unit == company_unit.value
        ).order_by(CashFlowData.period_date.desc()).first()

        cash_position = cash_data.cash_balance if cash_data else current_revenue * 0.15

        return KPIResponse(
            total_revenue=current_revenue,
            revenue_growth_pct=revenue_growth,
            total_profit=current_profit,
            profit_growth_pct=profit_growth,
            net_margin_pct=current_margin,
            margin_change_pp=margin_change,
            cash_position=cash_position,
            period_start=start_date,
            period_end=end_date
        )

    except Exception as e:
        logger.error(f"Error calculating KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating KPIs: {str(e)}")


@app.get("/financial/periods", response_model=List[FinancialMetrics])
async def get_financial_periods(
        start_date: Optional[date] = Query(None, description="Start date for analysis"),
        end_date: Optional[date] = Query(None, description="End date for analysis"),
        company_unit: CompanyUnit = Query(CompanyUnit.CONSOLIDATED, description="Company unit"),
        limit: int = Query(24, ge=1, le=100, description="Maximum number of periods to return"),
        db: Session = Depends(get_db)
):
    """Get financial periods data"""

    try:
        query = db.query(FinancialPeriod).filter(
            FinancialPeriod.company_unit == company_unit.value
        )

        if start_date:
            query = query.filter(FinancialPeriod.period_date >= start_date)
        if end_date:
            query = query.filter(FinancialPeriod.period_date <= end_date)

        periods = query.order_by(FinancialPeriod.period_date.desc()).limit(limit).all()

        return [
            FinancialMetrics(
                period_date=p.period_date,
                revenue=p.revenue,
                cogs=p.cogs,
                gross_profit=p.gross_profit,
                salaries=p.salaries,
                marketing=p.marketing,
                rd_expense=p.rd_expense,
                operations=p.operations,
                other_expenses=p.other_expenses,
                total_expenses=p.total_expenses,
                net_profit=p.net_profit,
                gross_margin_pct=p.gross_margin_pct,
                net_margin_pct=p.net_margin_pct
            )
            for p in reversed(periods)  # Return in chronological order
        ]

    except Exception as e:
        logger.error(f"Error fetching financial periods: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )