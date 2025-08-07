#app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///venue_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import models first
from models import db, User, Venue, Booking

# Initialize SQLAlchemy with app
db.init_app(app)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Add cache control headers to prevent browser caching
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Before request handler to check session validity
@app.before_request
def before_request():
    # List of routes that don't require authentication
    public_routes = ['index', 'login', 'register', 'static']
    
    # Check if the current route is public
    if request.endpoint in public_routes or request.endpoint.startswith('static'):
        return
    
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    
    # Verify user still exists in database
    user = User.query.get(session['user_id'])
    if not user or not user.is_active:
        session.clear()
        flash('Your session has expired. Please log in again.', 'error')
        return redirect(url_for('login'))

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def faculty_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['faculty', 'admin']:
            flash('Faculty access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow admin to register new users
    if 'user_id' not in session:
        flash('Registration is disabled. Please contact administrator.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('Only administrators can register new users.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        is_representative = request.form.get('is_representative', False)
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        user = User(
            username=username, 
            password=generate_password_hash(password), 
            role=role,
            is_representative=is_representative
        )
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} registered successfully as {role}!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administrator.', 'error')
                return render_template('login.html')
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['is_representative'] = user.is_representative
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    response = make_response(redirect(url_for('index')))
    return add_cache_headers(response)

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    if user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user.role == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    bookings = Booking.query.order_by(Booking.date.desc()).all()
    venues = Venue.query.all()
    users = User.query.all()
    
    response = make_response(render_template('admin_dashboard.html', 
                         bookings=bookings, 
                         venues=venues, 
                         users=users))
    return add_cache_headers(response)

@app.route('/faculty/dashboard')
@faculty_required
def faculty_dashboard():
    user = User.query.get(session['user_id'])
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.date.desc()).all()
    venues = Venue.query.all()
    
    response = make_response(render_template('faculty_dashboard.html', 
                         bookings=bookings, 
                         venues=venues))
    return add_cache_headers(response)

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.date.desc()).all()
    venues = Venue.query.all()
    
    response = make_response(render_template('student_dashboard.html', 
                         bookings=bookings, 
                         venues=venues,
                         user=user))
    return add_cache_headers(response)

@app.route('/booking/new', methods=['GET', 'POST'])
@login_required
def new_booking():
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        venue_id = request.form['venue_id']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        # Validate time
        if end_time <= start_time:
            flash('End time must be after start time.', 'error')
            return redirect(url_for('new_booking'))
        if start_time < '09:00' or end_time > '17:00':
            flash('Booking time must be between 09:00 and 17:00.', 'error')
            return redirect(url_for('new_booking'))
        time_slot = f"{start_time}-{end_time}"
        # Check for conflicts (overlap)
        existing_bookings = Booking.query.filter_by(
            venue_id=venue_id,
            date=date,
            status='Approved'
        ).all()
        def times_overlap(a_start, a_end, b_start, b_end):
            return a_start < b_end and b_start < a_end
        
        for booking in existing_bookings:
            b_start, b_end = booking.time_slot.split('-')
            if times_overlap(start_time, end_time, b_start, b_end):
                # Faculty can override both students and representatives
                if user.role == 'faculty':
                    if booking.user.role in ['student', 'faculty']:
                        # Check if the existing booking is by a representative
                        if booking.user.role == 'student' and booking.user.is_representative:
                            # Faculty can override representatives
                            booking.status = 'Rejected'
                            booking.override_by = user.id
                            db.session.commit()
                            flash('Representative booking has been overridden by faculty.', 'warning')
                        elif booking.user.role == 'student' and not booking.user.is_representative:
                            # Faculty can override regular students
                            booking.status = 'Rejected'
                            booking.override_by = user.id
                            db.session.commit()
                            flash('Student booking has been overridden by faculty.', 'warning')
                        else:
                            flash('This time period is already booked by faculty.', 'error')
                            return redirect(url_for('new_booking'))
                # Representatives can override regular students (but not other representatives or faculty)
                elif user.role == 'student' and user.is_representative:
                    if booking.user.role == 'student' and not booking.user.is_representative:
                        # Representatives can override regular students
                        booking.status = 'Rejected'
                        booking.override_by = user.id
                        db.session.commit()
                        flash('Regular student booking has been overridden by representative.', 'warning')
                    else:
                        flash('This time period overlaps with a booking by faculty or another representative.', 'error')
                        return redirect(url_for('new_booking'))
                # Regular students cannot override anyone
                elif user.role == 'student' and not user.is_representative:
                    flash('This time period overlaps with an existing booking. Representatives and faculty have priority.', 'error')
                    return redirect(url_for('new_booking'))
        
        # Handle file upload
        document_path = None
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{user.id}_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                document_path = filename
        
        booking = Booking(
            user_id=user.id,
            venue_id=venue_id,
            date=date,
            time_slot=time_slot,
            status='Pending',
            document_path=document_path
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking request submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    venues = Venue.query.all()
    response = make_response(render_template('new_booking.html', venues=venues))
    return add_cache_headers(response)

@app.route('/booking/<int:booking_id>/approve')
@admin_required
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check for conflicts with existing approved bookings
    existing_bookings = Booking.query.filter_by(
        venue_id=booking.venue_id,
        date=booking.date,
        status='Approved'
    ).all()
    
    def times_overlap(a_start, a_end, b_start, b_end):
        return a_start < b_end and b_start < a_end
    
    # Check if this booking conflicts with any existing approved booking
    for existing_booking in existing_bookings:
        if existing_booking.id != booking.id:  # Don't check against self
            existing_start, existing_end = existing_booking.time_slot.split('-')
            new_start, new_end = booking.time_slot.split('-')
            
            if times_overlap(new_start, new_end, existing_start, existing_end):
                # Determine who should win based on hierarchy
                if booking.user.role == 'faculty':
                    # Faculty can override students and representatives
                    if existing_booking.user.role in ['student', 'faculty']:
                        existing_booking.status = 'Rejected'
                        existing_booking.override_by = booking.user.id
                        db.session.commit()
                        flash(f'Faculty booking approved. {existing_booking.user.username}\'s booking has been overridden.', 'warning')
                    else:
                        flash('Cannot approve: This conflicts with another faculty booking.', 'error')
                        return redirect(url_for('admin_dashboard'))
                elif booking.user.role == 'student' and booking.user.is_representative:
                    # Representatives can override regular students
                    if existing_booking.user.role == 'student' and not existing_booking.user.is_representative:
                        existing_booking.status = 'Rejected'
                        existing_booking.override_by = booking.user.id
                        db.session.commit()
                        flash(f'Representative booking approved. {existing_booking.user.username}\'s booking has been overridden.', 'warning')
                    else:
                        flash('Cannot approve: Representatives cannot override faculty or other representatives.', 'error')
                        return redirect(url_for('admin_dashboard'))
                else:
                    # Regular students cannot override anyone
                    flash('Cannot approve: This conflicts with an existing booking. Higher priority users have precedence.', 'error')
                    return redirect(url_for('admin_dashboard'))
    
    booking.status = 'Approved'
    db.session.commit()
    flash('Booking approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/booking/<int:booking_id>/reject')
@admin_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'Rejected'
    db.session.commit()
    flash('Booking rejected.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/booking/<int:booking_id>/delete')
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    user = User.query.get(session['user_id'])
    
    if user.role != 'admin' and booking.user_id != user.id:
        flash('You can only delete your own bookings.', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/booking/<int:booking_id>/cancel')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    user = User.query.get(session['user_id'])
    
    # Only allow cancellation if user is admin, faculty, or the booking owner
    if user.role not in ['admin', 'faculty'] and booking.user_id != user.id:
        flash('You can only cancel your own bookings.', 'error')
        return redirect(url_for('dashboard'))
    
    # Only allow cancellation of approved bookings
    if booking.status != 'Approved':
        flash('Only approved bookings can be cancelled.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if booking is in the past
    if booking.date < datetime.now().date():
        flash('Cannot cancel past bookings.', 'error')
        return redirect(url_for('dashboard'))
    
    booking.status = 'Cancelled'
    db.session.commit()
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/availability')
def check_availability():
    venue_id = request.args.get('venue_id', type=int)
    date = request.args.get('date')
    
    if not venue_id or not date:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get all approved bookings for the date and venue
    bookings = Booking.query.filter_by(
        venue_id=venue_id,
        date=date_obj,
        status='Approved'
    ).all()
    
    # Create time slots from 09:00 to 17:00
    time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
                  '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00']
    
    results = {}
    for slot in time_slots:
        slot_start, slot_end = slot.split('-')
        is_available = True
        booked_by = None
        user_role = None
        
        # Check if this slot overlaps with any booking
        for booking in bookings:
            booking_start, booking_end = booking.time_slot.split('-')
            
            # Check for overlap
            if (slot_start < booking_end and slot_end > booking_start):
                is_available = False
                booked_by = booking.user.username
                user_role = booking.user.role
                break
        
        results[slot] = {
            'available': is_available,
            'booked_by': booked_by,
            'user_role': user_role
        }
    
    return jsonify(results)

@app.route('/admin/venues')
@admin_required
def manage_venues():
    venues = Venue.query.all()
    response = make_response(render_template('manage_venues.html', venues=venues))
    return add_cache_headers(response)

@app.route('/admin/venues/add', methods=['POST'])
@admin_required
def add_venue():
    name = request.form['name']
    location = request.form['location']
    capacity = request.form['capacity']
    venue_type = request.form['type']
    
    venue = Venue(name=name, location=location, capacity=capacity, type=venue_type)
    db.session.add(venue)
    db.session.commit()
    
    flash('Venue added successfully!', 'success')
    return redirect(url_for('manage_venues'))

@app.route('/admin/venues/<int:venue_id>/delete')
@admin_required
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue deleted successfully!', 'success')
    return redirect(url_for('manage_venues'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    response = make_response(render_template('admin_users.html', users=users))
    return add_cache_headers(response)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        is_representative = 'is_representative' in request.form
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('add_user.html')
        
        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            is_representative=is_representative
        )
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('add_user.html')

@app.route('/admin/users/<int:user_id>/toggle-representative')
@admin_required
def toggle_representative(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'student':
        user.is_representative = not user.is_representative
        db.session.commit()
        status = 'granted' if user.is_representative else 'revoked'
        flash(f'Representative status {status} for {user.username}', 'success')
    else:
        flash('Only students can be representatives.', 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/toggle-active')
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {status}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted successfully.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    user = User.query.get(session['user_id'])
    booking = Booking.query.filter_by(document_path=filename).first()
    
    if not booking:
        flash('File not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Only allow access if user is admin or the booking owner
    if user.role != 'admin' and booking.user_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
        
        # Create some sample venues if they don't exist
        if Venue.query.count() == 0:
            venues = [
                Venue(name='Seminar Hall A', location='Main Building', capacity=100, type='seminar_hall'),
                Venue(name='Conference Room B', location='Engineering Block', capacity=50, type='conference_room'),
                Venue(name='Computer Lab 1', location='IT Department', capacity=30, type='lab'),
                Venue(name='Auditorium', location='Central Block', capacity=200, type='auditorium'),
            ]
            for venue in venues:
                db.session.add(venue)
            db.session.commit()
            print("Sample venues created")
    
    app.run(debug=True)
