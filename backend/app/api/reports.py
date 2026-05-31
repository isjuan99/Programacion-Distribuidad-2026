from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.category import Review

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
async def dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    now = datetime.utcnow()
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_last_month = (start_month - timedelta(days=1)).replace(day=1)

    total_revenue = db.query(func.sum(Order.total)).filter(
        Order.status != OrderStatus.cancelled
    ).scalar() or 0

    month_revenue = db.query(func.sum(Order.total)).filter(
        Order.created_at >= start_month,
        Order.status != OrderStatus.cancelled,
    ).scalar() or 0

    last_month_revenue = db.query(func.sum(Order.total)).filter(
        Order.created_at >= start_last_month,
        Order.created_at < start_month,
        Order.status != OrderStatus.cancelled,
    ).scalar() or 0

    total_orders = db.query(func.count(Order.id)).scalar()
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.pending
    ).scalar()
    total_customers = db.query(func.count(User.id)).filter(User.is_admin == False).scalar()
    total_products = db.query(func.count(Product.id)).scalar()

    # Revenue last 6 months
    monthly = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        rev = db.query(func.sum(Order.total)).filter(
            Order.created_at >= month_start,
            Order.created_at < month_end,
            Order.status != OrderStatus.cancelled,
        ).scalar() or 0
        monthly.append({
            "month": month_start.strftime("%b"),
            "revenue": round(float(rev), 2),
        })

    # Top 5 products by revenue
    top_products = db.query(
        OrderItem.product_name,
        func.sum(OrderItem.total_price).label("revenue"),
        func.sum(OrderItem.quantity).label("units"),
    ).group_by(OrderItem.product_name).order_by(
        func.sum(OrderItem.total_price).desc()
    ).limit(5).all()

    return {
        "total_revenue": round(float(total_revenue), 2),
        "month_revenue": round(float(month_revenue), 2),
        "last_month_revenue": round(float(last_month_revenue), 2),
        "revenue_growth": round(
            ((month_revenue - last_month_revenue) / last_month_revenue * 100)
            if last_month_revenue > 0 else 0, 1
        ),
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_customers": total_customers,
        "total_products": total_products,
        "monthly_revenue": monthly,
        "top_products": [
            {"name": p.product_name, "revenue": round(float(p.revenue), 2), "units": p.units}
            for p in top_products
        ],
    }
