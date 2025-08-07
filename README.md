# Venue Booking System

A comprehensive web-based venue booking system with role-based access control, designed for educational institutions to manage venue bookings for faculty, students, and administrative staff.

## 🚀 Features

### 👥 User Roles

#### 🛠 Admin (Facility Manager)
- Pre-created during database initialization
- Full access to all bookings and user data
- View and manage all venue requests
- Approve or reject booking requests from faculty or students
- View uploaded permission documents for each request
- Manually resolve booking conflicts (faculty vs student, etc.)
- Monitor venue utilization and user activity

#### 👩‍🏫 Faculty
- Register and login via secure form
- Submit booking requests for lectures, meetings, or department events
- Select venue, date, and time slot
- Upload required permission documents
- Faculty bookings have higher priority and can override student bookings
- View personal booking history and status of each request
- Receive notifications for approval, rejection, or conflict resolution

#### 👨‍🎓 Student / Club Representative
- Register and login via secure form
- Submit venue booking requests for club events, workshops, etc.
- Upload required permission letters from authorities
- Can check venue availability by date and time slot before submitting
- Cannot override faculty bookings
- View their own booking history and status
- Get notified if booking is approved, rejected, or overridden

### 🌟 Core Functionalities

#### 🔐 Authentication
- Role-based login and access control
- Separate dashboards for Admin, Faculty, and Students

#### 📊 Admin Dashboard
- View all booking requests and their statuses
- Approve or reject any booking
- View uploaded permission documents
- Manually resolve booking conflicts (e.g., override student booking for faculty)
- See calendar-style or list view of all bookings

#### 👨‍🏫 Faculty Dashboard
- Submit new booking requests
- Check slot availability before requesting
- Upload permission letters or official documents
- Automatically override student booking in case of conflict (with alert)
- View personal booking history with status updates

#### 👩‍🎓 Student Dashboard
- Submit new venue requests with required information
- Check slot availability in real time
- Upload permission letters (e.g., club advisor or HOD approval)
- Cannot book a venue if already occupied by faculty
- View history of own bookings and their approval status

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [File Structure](#file-structure)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🛠 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd venue_final_code
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   # or
   python run.py
   ```

5. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - The system will automatically create the database and sample data

### Default Admin Account
- **Username:** `admin`
- **Password:** `admin123`

## 🎯 Usage

### For Admins
1. Login with admin credentials
2. Navigate to Admin Dashboard
3. Review pending booking requests
4. Approve or reject bookings as needed
5. Manage venues through the Venue Management section
6. Monitor system activity and user statistics

### For Faculty
1. Register or login with faculty credentials
2. Use the Faculty Dashboard to manage bookings
3. Check venue availability before making requests
4. Upload required permission documents
5. Faculty bookings automatically override student bookings

### For Students
1. Register or login with student credentials
2. Use the Student Dashboard to manage bookings
3. Check availability before submitting requests
4. Upload permission documents (club advisor approval, etc.)
5. Cannot override faculty bookings

## 🗄️ Database Schema

### User
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password
- `role`: admin, faculty, or student
- `created_at`: Account creation timestamp

### Venue
- `id`: Primary key
- `name`: Venue name
- `location`: Venue location
- `capacity`: Maximum capacity
- `type`: Type of venue (seminar_hall, lab, auditorium, etc.)
- `created_at`: Venue creation timestamp

### Booking
- `id`: Primary key
- `user_id`: Foreign key to User
- `venue_id`: Foreign key to Venue
- `date`: Booking date
- `time_slot`: Time slot (e.g., "09:00-10:00")
- `status`: Pending, Approved, or Rejected
- `document_path`: Path to uploaded permission document
- `override_by`: Who overrode this booking (for faculty overrides)
- `created_at`: Booking creation timestamp
- `updated_at`: Last update timestamp

## 📡 API Documentation

### Endpoints

#### Check Venue Availability
- **URL:** `/api/availability`
- **Method:** `GET`
- **Parameters:**
  - `venue_id` (required): ID of the venue
  - `date` (required): Date in YYYY-MM-DD format
- **Response:** JSON with availability status for all time slots

**Example Response:**
```json
{
  "venue_id": 1,
  "date": "2024-01-15",
  "availability": {
    "09:00-10:00": "available",
    "10:00-11:00": "booked",
    "11:00-12:00": "available"
  }
}
```

## 📁 File Structure

```
venue_final_code/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── run.py               # Application entry point
├── setup.py             # Setup script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Landing page
│   ├── login.html      # Login form
│   ├── register.html   # Registration form
│   ├── admin_dashboard.html    # Admin dashboard
│   ├── faculty_dashboard.html  # Faculty dashboard
│   ├── student_dashboard.html  # Student dashboard
│   ├── new_booking.html       # Booking form
│   ├── booking.html           # Booking details
│   ├── manage_venues.html     # Venue management
│   └── admin_users.html       # User management
├── instance/            # Database files (auto-created)
│   └── venue_booking.db
└── uploads/            # Document uploads (auto-created)
    └── .gitkeep        # Keep directory in git
```

## 🔒 Security Features

- **Password Hashing**: Using Werkzeug security functions
- **Role-based Access Control**: Different permissions for admin, faculty, and students
- **File Upload Validation**: Secure file upload with type and size restrictions
- **Session Management**: Secure session handling
- **SQL Injection Protection**: Using SQLAlchemy ORM
- **Input Validation**: Server-side validation for all user inputs

## ⏰ Time Slots

The system supports the following time slots:
- 09:00 - 10:00
- 10:00 - 11:00
- 11:00 - 12:00
- 12:00 - 13:00
- 13:00 - 14:00
- 14:00 - 15:00
- 15:00 - 16:00
- 16:00 - 17:00

## 📄 Supported File Types

For document uploads, the system accepts:
- **PDF files**: `.pdf`
- **Word documents**: `.doc`, `.docx`
- **Image files**: `.jpg`, `.jpeg`, `.png`

## 🐛 Troubleshooting

### Common Issues

#### Database Issues
- **Problem**: Database not created
- **Solution**: The database is created automatically when you first run the application. Check that you have write permissions in the project directory.

#### Upload Issues
- **Problem**: Upload folder not found
- **Solution**: The uploads folder is created automatically. Ensure the application has write permissions.

#### Port Issues
- **Problem**: Port already in use
- **Solution**: Change the port in `app.py` or kill the process using port 5000.

### Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Username already exists" | Duplicate username during registration | Choose a different username |
| "Invalid username or password" | Incorrect login credentials | Check your login credentials |
| "Access denied" | Insufficient permissions | Contact admin for access |
| "This time slot is already booked" | Venue/time conflict | Choose a different time or venue |

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests (if available)
5. Make your changes
6. Test thoroughly
7. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For support or questions:
- Create an issue in the project repository
- Contact the system administrator
- Check the troubleshooting section above

## 🔄 Version History

- **v1.0.0**: Initial release with basic booking functionality
- **v1.1.0**: Added role-based access control
- **v1.2.0**: Enhanced admin dashboard and conflict resolution
- **v1.3.0**: Improved file upload system and security features

---

**Note**: This system is designed for educational institutions and includes role-based access control to ensure proper venue management and booking prioritization. 