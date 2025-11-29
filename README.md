# 🚗 Vehicle Parking Management System

A comprehensive web-based parking management system built with Flask (Backend) and Vue.js (Frontend). Features include real-time parking spot availability, user reservations, admin dashboard with analytics, and automated email notifications.

## 🌟 Features

### **Admin Features**
- 📊 **Dashboard** - Real-time statistics, occupancy rates, revenue charts
- 🏢 **Parking Lot Management** - Create, edit, delete parking lots
- 🔍 **Advanced Search** - Search by location, user name, or vehicle number
- 👥 **User Management** - View, manage registered users
- 📈 **Analytics** - Monthly revenue trends, booking statistics
- 🚦 **Spot Control** - Block/unblock individual parking spots
- 💰 **Reservation Tracking** - View all active and historical reservations

### **User Features**
- 🅿️ **Book Parking** - Real-time spot availability with visual grid
- 📅 **My Reservations** - View active and past bookings
- 💳 **Checkout** - Calculate and pay parking charges
- 📊 **Personal Dashboard** - Spending statistics and usage charts
- 📥 **Export History** - Download reservation history as CSV

### **Automated Jobs (Celery)**
- 📧 **Daily Reminders** - Email reminders to inactive users (6 PM UTC daily)
- 📊 **Monthly Reports** - Automated CSV reports via email (1st of month)
- ⚡ **Async Exports** - Background CSV generation

## 🛠️ Tech Stack

### **Backend**
- **Framework:** Flask 3.0
- **Database:** SQLite (SQLAlchemy ORM)
- **Authentication:** JWT (Flask-JWT-Extended)
- **Caching:** Redis
- **Task Queue:** Celery
- **Email:** Flask-Mail (Gmail SMTP)

### **Frontend**
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **UI:** Bootstrap 5
- **Charts:** Chart.js
- **Icons:** Bootstrap Icons
- **HTTP Client:** Axios

## 📋 Prerequisites

- Python 3.10+
- Node.js 16+ & npm
- Redis (Memurai for Windows)
- Gmail account (for email notifications)

## 🚀 Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/vehicle-parking-app.git
cd vehicle-parking-app
```

### **2. Backend Setup**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file (copy from env.example)
cp env.example .env

# Edit .env with your credentials
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-gmail-app-password
```

### **3. Frontend Setup**

```bash
cd frontend
npm install
```

### **4. Redis Setup**

**Windows (Memurai):**
- Download from https://www.memurai.com/get-memurai
- Install and start service

**Linux/Mac:**
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu
brew install redis                  # macOS

# Start Redis
redis-server
```

## ▶️ Running the Application

### **Development Mode (4 terminals required)**

**Terminal 1: Backend**
```bash
python run_backend.py
# Runs on http://localhost:5000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

**Terminal 3: Celery Worker**
```bash
# Windows
start_celery_worker.bat

# Linux/Mac
celery -A backend.tasks.celery_config worker --loglevel=info
```

**Terminal 4: Celery Beat (Scheduler)**
```bash
# Windows
start_celery_beat.bat

# Linux/Mac
celery -A backend.tasks.celery_config beat --loglevel=info
```

### **Quick Start Scripts (Windows)**
- `start_backend.bat` - Start Flask backend
- `start_frontend.bat` - Start Vue.js frontend
- `start_celery_worker.bat` - Start Celery worker
- `start_celery_beat.bat` - Start Celery scheduler

## 🔐 Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@parkingapp.com`

⚠️ **Change admin password in production!**

## 📧 Email Configuration

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and generate password
3. **Update .env:**
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   ```

## 📁 Project Structure

```
vehicle-parking-app/
├── backend/
│   ├── config/          # Configuration files
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── tasks/           # Celery tasks
│   └── utils/           # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/  # Reusable Vue components
│   │   ├── views/       # Page components
│   │   ├── services/    # API service
│   │   └── router/      # Vue Router config
│   └── public/
├── instance/            # SQLite database (auto-created)
├── .env                 # Environment variables (create from env.example)
├── env.example          # Environment template
├── requirements.txt     # Python dependencies
├── run_backend.py       # Backend entry point
└── README.md
```

## 🧪 Testing

### **Backend API**
```bash
# Test endpoint
curl http://localhost:5000/api/parking-lots

# Test with authentication
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/admin/dashboard-stats
```

### **Celery Tasks**
```bash
# Trigger monthly report manually (Admin only)
POST http://localhost:5000/api/admin/trigger-monthly-report

# Trigger daily reminder manually (Admin only)
POST http://localhost:5000/api/admin/trigger-daily-reminder
```

## 📅 Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Daily Reminders | 6:00 PM UTC daily | Email inactive users |
| Monthly Reports | 1st of month, midnight | CSV report via email |

## 🔍 API Endpoints

### **Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### **Parking Lots**
- `GET /api/parking-lots` - List all parking lots
- `POST /api/parking-lots` - Create parking lot (Admin)
- `PUT /api/parking-lots/:id` - Update parking lot (Admin)
- `DELETE /api/parking-lots/:id` - Delete parking lot (Admin)

### **Reservations**
- `GET /api/reservations/my` - User's reservations
- `POST /api/reservations` - Create reservation
- `PUT /api/reservations/:id/checkout` - Checkout
- `GET /api/reservations/export` - Export CSV

### **Admin**
- `GET /api/admin/dashboard-stats` - Dashboard statistics
- `GET /api/admin/users` - List all users
- `GET /api/admin/reservations` - All reservations
- `POST /api/admin/trigger-monthly-report` - Manual report trigger

## 🌐 Environment Variables

See `env.example` for all available configuration options.

**Required:**
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `MAIL_USERNAME` - Gmail address
- `MAIL_PASSWORD` - Gmail app password
- `REDIS_URL` - Redis connection string

## 🐛 Troubleshooting

### **Backend won't start**
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Verify dependencies
pip install -r requirements.txt
```

### **Frontend won't start**
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install
```

### **Celery not working**
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Windows: Check Memurai service
Get-Service Memurai
```

### **Email not sending**
- Verify Gmail App Password (not regular password)
- Check 2FA is enabled on Gmail
- Check .env file has correct credentials

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Developed by Your Name

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show your support

Give a ⭐️ if this project helped you!
