from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Task, Category
from datetime import datetime

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
def home():
    # Task counts
    total    = Task.query.filter_by(user_id=current_user.id).count()
    done     = Task.query.filter_by(user_id=current_user.id, done=True).count()
    pending  = Task.query.filter_by(user_id=current_user.id, done=False).count()

    # Overdue — pending tasks where due_date has passed
    today    = datetime.utcnow().date()
    overdue  = Task.query.filter(
        Task.user_id == current_user.id,
        Task.done    == False,
        Task.due_date < today
    ).count()

    # Progress percentage
    percent  = round((done / total * 100)) if total > 0 else 0

    # Recent 5 tasks
    recent   = Task.query.filter_by(user_id=current_user.id)\
                         .order_by(Task.created_at.desc()).limit(5).all()

    # Categories with task counts
    categories = Category.query.filter_by(user_id=current_user.id).all()

    return render_template('dashboard/index.html',
                           total=total,
                           done=done,
                           pending=pending,
                           overdue=overdue,
                           percent=percent,
                           recent=recent,
                           categories=categories)