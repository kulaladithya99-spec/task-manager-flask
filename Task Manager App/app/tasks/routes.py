from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Task, Category
from datetime import datetime
from app.form import TaskForm

tasks = Blueprint('tasks', __name__)


# ── View all tasks ──────────────────────────────────────────
@tasks.route('/')
@login_required
def index():
    status      = request.args.get('status',      'all')
    priority    = request.args.get('priority',    'all')
    category_id = request.args.get('category_id', 'all')
    search      = request.args.get('search',      '')

    query = Task.query.filter_by(user_id=current_user.id)

    if status == 'done':
        query = query.filter_by(done=True)
    elif status == 'pending':
        query = query.filter_by(done=False)

    if priority != 'all':
        query = query.filter_by(priority=priority)

    if category_id != 'all':
        query = query.filter_by(category_id=int(category_id))

    if search:
        query = query.filter(Task.title.ilike(f'%{search}%'))

    tasks_list = query.order_by(Task.created_at.desc()).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()

    return render_template('tasks/index.html',
                           tasks=tasks_list,
                           categories=categories,
                           status=status,
                           priority=priority,
                           category_id=category_id,
                           search=search)


# ── Add task ────────────────────────────────────────────────


@tasks.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = Category.query.filter_by(user_id=current_user.id).all()

    form = TaskForm()
    # Populate category choices dynamically — (0, 'None') as a fallback option
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        task = Task(
            title       = form.title.data,
            description = form.description.data,
            priority    = form.priority.data,
            due_date    = form.due_date.data,
            category_id = form.category_id.data if form.category_id.data != 0 else None,
            user_id     = current_user.id
        )
        db.session.add(task)
        db.session.commit()

        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks.index'))

    return render_template('tasks/add.html', form=form)


# ── Edit task ───────────────────────────────────────────────
@tasks.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    categories = Category.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority    = request.form.get('priority', 'medium')
        due_date    = request.form.get('due_date', '')
        category_id = request.form.get('category_id', '')

        if not title:
            flash('Task title is required.', 'error')
            return render_template('tasks/edit.html',
                                   task=task, categories=categories)

        parsed_due = None
        if due_date:
            try:
                parsed_due = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'error')
                return render_template('tasks/edit.html',
                                       task=task, categories=categories)

        task.title       = title
        task.description = description
        task.priority    = priority
        task.due_date    = parsed_due
        task.category_id = int(category_id) if category_id else None
        db.session.commit()

        flash('Task updated!', 'success')
        return redirect(url_for('tasks.index'))

    return render_template('tasks/edit.html', task=task, categories=categories)


# ── Toggle complete ─────────────────────────────────────────
@tasks.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.done = not task.done
    db.session.commit()
    return redirect(url_for('tasks.index'))


# ── Delete task ─────────────────────────────────────────────
@tasks.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('tasks.index'))


# ── Add category ────────────────────────────────────────────
@tasks.route('/category/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Category name is required.', 'error')
        return redirect(url_for('tasks.index'))

    # Check if category already exists for this user
    existing = Category.query.filter_by(
        name=name, user_id=current_user.id
    ).first()

    if existing:
        flash('Category already exists.', 'error')
        return redirect(url_for('tasks.index'))

    category = Category(name=name, user_id=current_user.id)
    db.session.add(category)
    db.session.commit()
    flash(f'Category "{name}" created!', 'success')
    return redirect(url_for('tasks.index'))


# ── Delete category ─────────────────────────────────────────
@tasks.route('/category/delete/<int:cat_id>')
@login_required
def delete_category(cat_id):
    category = Category.query.filter_by(
        id=cat_id, user_id=current_user.id
    ).first_or_404()

    # Tasks in this category become uncategorized — not deleted
    for task in category.tasks:
        task.category_id = None

    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" deleted.', 'info')
    return redirect(url_for('tasks.index'))