from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Task

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm',  '')

        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('auth/register.html')

        # Create user — hash the password
        hashed = generate_password_hash(password)
        user   = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email',    '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        # Check user exists and password is correct
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')

        login_user(user)
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('dashboard.home'))

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


from flask_login import login_required, current_user
from datetime import datetime

# ── Profile page ────────────────────────────────────────────
@auth.route('/profile')
@login_required
def profile():
    total   = Task.query.filter_by(user_id=current_user.id).count()
    done    = Task.query.filter_by(user_id=current_user.id, done=True).count()
    pending = Task.query.filter_by(user_id=current_user.id, done=False).count()
    return render_template('auth/profile.html',
                           total=total, done=done, pending=pending)


# ── Account settings ────────────────────────────────────────
@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')

        # Change username
        if action == 'username':
            new_username = request.form.get('username', '').strip()
            if not new_username:
                flash('Username cannot be empty.', 'error')
            elif User.query.filter_by(username=new_username).first():
                flash('Username already taken.', 'error')
            else:
                current_user.username = new_username
                db.session.commit()
                flash('Username updated!', 'success')

        # Change password
        elif action == 'password':
            current_pw = request.form.get('current_password', '')
            new_pw     = request.form.get('new_password',     '')
            confirm_pw = request.form.get('confirm_password', '')

            if not check_password_hash(current_user.password, current_pw):
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            elif new_pw != confirm_pw:
                flash('New passwords do not match.', 'error')
            else:
                current_user.password = generate_password_hash(new_pw)
                db.session.commit()
                flash('Password updated!', 'success')

        return redirect(url_for('auth.settings'))

    return render_template('auth/settings.html')