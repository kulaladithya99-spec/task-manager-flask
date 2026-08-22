from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Task, Category
from datetime import datetime

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def home():
    if not current_user.is_authenticated:
        return render_template('welcome.html')

    # Task counts
    total    = Task.query.filter_by(user_id=current_user.id, is_deleted=False).count()
    done     = Task.query.filter_by(user_id=current_user.id, is_deleted=False, done=True).count()
    pending  = Task.query.filter_by(user_id=current_user.id, is_deleted=False, done=False).count()

    # Overdue — pending tasks where due_date has passed
    today    = datetime.utcnow().date()
    overdue  = Task.query.filter(
        Task.user_id    == current_user.id,
        Task.is_deleted == False,
        Task.done       == False,
        Task.due_date   < today
    ).count()

    # Progress percentage
    percent  = round((done / total * 100)) if total > 0 else 0

    # Recent 5 tasks
    recent   = Task.query.filter_by(user_id=current_user.id, is_deleted=False)\
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