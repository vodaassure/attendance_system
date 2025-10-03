from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Attendance
from app.forms import RegistrationForm, LoginForm, AttendanceForm, DateRangeForm
from datetime import datetime, date, timedelta
from sqlalchemy import func

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
attendance = Blueprint('attendance', __name__)

# Main routes
@main.route('/')
@main.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    
    # Get attendance stats for current month
    today = date.today()
    first_day = date(today.year, today.month, 1)
    
    # Calculate working days (excluding weekends)
    working_days = get_working_days_count(first_day, today)
    
    # Get user's attendance for current month
    attendances = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= first_day,
        Attendance.date <= today
    ).all()
    
    present_days = sum(1 for a in attendances if a.status in ['present', 'half-day'])
    
    # Calculate attendance percentage
    attendance_percentage = (present_days / working_days * 100) if working_days > 0 else 0
    meets_requirement = attendance_percentage >= 60
    
    # Get today's attendance
    today_attendance = Attendance.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    attendance_form = AttendanceForm()
    date_range_form = DateRangeForm()  # Add this line
    
    if today_attendance:
        attendance_form.status.data = today_attendance.status
        attendance_form.notes.data = today_attendance.notes
    
    return render_template('dashboard.html', 
                          title='Dashboard',
                          attendance_form=attendance_form,
                          date_range_form=date_range_form,  # Add this line
                          today_attendance=today_attendance,
                          working_days=working_days,
                          present_days=present_days,
                          attendance_percentage=round(attendance_percentage, 2),
                          meets_requirement=meets_requirement)

@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get all employees
    employees = User.query.filter_by(role='employee').all()
    
    # Get attendance stats for current month
    today = date.today()
    first_day = date(today.year, today.month, 1)
    working_days = get_working_days_count(first_day, today)
    
    employee_stats = []
    for employee in employees:
        attendances = Attendance.query.filter(
            Attendance.user_id == employee.id,
            Attendance.date >= first_day,
            Attendance.date <= today
        ).all()
        
        present_days = sum(1 for a in attendances if a.status in ['present', 'half-day'])
        attendance_percentage = (present_days / working_days * 100) if working_days > 0 else 0
        
        employee_stats.append({
            'employee': employee,
            'present_days': present_days,
            'attendance_percentage': round(attendance_percentage, 2),
            'meets_requirement': attendance_percentage >= 60
        })
    
    date_range_form = DateRangeForm()
    
    return render_template('admin_dashboard.html',
                          title='Admin Dashboard',
                          employee_stats=employee_stats,
                          working_days=working_days,
                          date_range_form=date_range_form)

# Auth routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Attendance routes
@attendance.route('/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    form = AttendanceForm()
    if form.validate_on_submit():
        today = date.today()
        attendance_record = Attendance.query.filter_by(
            user_id=current_user.id, 
            date=today
        ).first()
        
        if attendance_record:
            # Update existing record
            attendance_record.status = form.status.data
            attendance_record.notes = form.notes.data
            if not attendance_record.check_out and attendance_record.check_in:
                attendance_record.check_out = datetime.now()
            flash('Attendance updated successfully!', 'success')
        else:
            # Create new record
            new_attendance = Attendance(
                user_id=current_user.id,
                date=today,
                status=form.status.data,
                notes=form.notes.data,
                check_in=datetime.now()
            )
            db.session.add(new_attendance)
            flash('Attendance marked successfully!', 'success')
        
        db.session.commit()
    
    return redirect(url_for('main.dashboard'))

@attendance.route('/attendance_history')
@login_required
def attendance_history():
    page = request.args.get('page', 1, type=int)
    
    attendances = Attendance.query.filter_by(user_id=current_user.id)\
        .order_by(Attendance.date.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('attendance.html', 
                          title='Attendance History',
                          attendances=attendances)

@attendance.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    form = DateRangeForm()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        if current_user.role == 'admin':
            return redirect(url_for('attendance.admin_report', 
                                   start_date=start_date.strftime('%Y-%m-%d'),
                                   end_date=end_date.strftime('%Y-%m-%d')))
        else:
            return redirect(url_for('attendance.employee_report',
                                   start_date=start_date.strftime('%Y-%m-%d'),
                                   end_date=end_date.strftime('%Y-%m-%d')))
    
    flash('Invalid date range', 'danger')
    return redirect(url_for('main.dashboard'))

@attendance.route('/employee_report')
@login_required
def employee_report():
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
    
    working_days = get_working_days_count(start_date, end_date)
    
    attendances = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).order_by(Attendance.date).all()
    
    present_days = sum(1 for a in attendances if a.status in ['present', 'half-day'])
    attendance_percentage = (present_days / working_days * 100) if working_days > 0 else 0
    meets_requirement = attendance_percentage >= 60
    
    return render_template('report.html',
                          title='Attendance Report',
                          attendances=attendances,
                          start_date=start_date,
                          end_date=end_date,
                          working_days=working_days,
                          present_days=present_days,
                          attendance_percentage=round(attendance_percentage, 2),
                          meets_requirement=meets_requirement)

@attendance.route('/admin_report')
@login_required
def admin_report():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
    
    working_days = get_working_days_count(start_date, end_date)
    
    employees = User.query.filter_by(role='employee').all()
    employee_stats = []
    
    for employee in employees:
        attendances = Attendance.query.filter(
            Attendance.user_id == employee.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        
        present_days = sum(1 for a in attendances if a.status in ['present', 'half-day'])
        attendance_percentage = (present_days / working_days * 100) if working_days > 0 else 0
        
        employee_stats.append({
            'employee': employee,
            'present_days': present_days,
            'attendance_percentage': round(attendance_percentage, 2),
            'meets_requirement': attendance_percentage >= 60
        })
    
    return render_template('admin_report.html',
                          title='Admin Attendance Report',
                          employee_stats=employee_stats,
                          start_date=start_date,
                          end_date=end_date,
                          working_days=working_days)

# Helper function to count working days (Mon-Fri) between two dates
def get_working_days_count(start_date, end_date):
    count = 0
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday (0-4)
            count += 1
        current_date += timedelta(days=1)
    
    return count