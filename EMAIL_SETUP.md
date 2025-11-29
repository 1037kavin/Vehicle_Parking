# Email Configuration Setup Guide

## 📧 Email Settings for Scheduled Jobs

Your app will send emails for:
1. **Monthly Reports** (1st of every month) - CSV attachment with parking history
2. **Daily Reminders** (Every day at 6 PM) - Reminder to inactive users

---

## 🔧 How to Configure Email

### **Option 1: Use Gmail (Recommended for Testing)**

1. **Update `backend/config/config.py`** - Change these lines:

```python
MAIL_USERNAME = 'your-gmail@gmail.com'  # Your Gmail address
MAIL_PASSWORD = 'your-app-password'      # Gmail App Password (NOT your regular password)
MAIL_DEFAULT_SENDER = 'Parking Manager <your-gmail@gmail.com>'
```

2. **Get Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in with your Gmail account
   - Select "Mail" and device type
   - Copy the 16-character password
   - Paste it in `MAIL_PASSWORD`

3. **Enable 2-Factor Authentication:**
   - App Passwords only work if 2FA is enabled
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

---

### **Option 2: Use Environment Variables (Recommended for Production)**

Instead of hardcoding in config.py, set environment variables:

**Windows PowerShell:**
```powershell
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-app-password"
$env:MAIL_DEFAULT_SENDER="Parking Manager <your-email@gmail.com>"
```

**Or create a `.env` file:**
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=Parking Manager <your-email@gmail.com>
```

---

## 📨 Email Details

### **Sender Email:**
- The emails will be sent **FROM** the email you configure in `MAIL_USERNAME`
- Example: If you set `parkingapp123@gmail.com`, all emails come from that address

### **Recipients:**
- **Monthly Reports:** Sent to each user's registered email
- **Daily Reminders:** Sent to inactive users' registered emails

### **Current Schedule:**
- **Daily Reminders:** Every day at 6:00 PM (18:00)
- **Monthly Reports:** 1st day of every month at midnight

To change timing, edit `backend/tasks/celery_config.py`:
```python
'send-daily-reminders': {
    'schedule': crontab(hour=18, minute=0),  # Change hour here (0-23)
}
```

---

## 🚀 Running the Scheduled Jobs

### **Requirements:**
1. ✅ Redis server running
2. ✅ Celery worker running
3. ✅ Celery beat (scheduler) running

### **Start Commands:**

**Terminal 1: Redis**
```bash
redis-server
```

**Terminal 2: Celery Worker**
```bash
cd C:\Users\rkkav\OneDrive\Desktop\VP
celery -A backend.tasks.celery_config worker --loglevel=info --pool=solo
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
cd C:\Users\rkkav\OneDrive\Desktop\VP
celery -A backend.tasks.celery_config beat --loglevel=info
```

---

## 🧪 Testing Emails Manually

To test if email works without waiting for scheduled time:

**Add this test route to `backend/routes/admin.py`:**
```python
@admin_bp.route('/test-email', methods=['POST'])
@jwt_required()
def test_email():
    """Test email sending"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from flask_mail import Message
        msg = Message(
            subject='Test Email - Parking Manager',
            recipients=['test@example.com'],  # Change to your email
            body='This is a test email from Parking Manager!'
        )
        mail.send(msg)
        return jsonify({'message': 'Test email sent successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Then call: `POST http://localhost:5000/api/admin/test-email`

---

## ⚠️ Common Issues

### **Error: "Authentication failed"**
- Check: Gmail App Password is correct
- Check: 2FA is enabled on Gmail

### **Error: "Connection refused"**
- Check: `MAIL_SERVER` and `MAIL_PORT` are correct
- Try: `MAIL_PORT = 465` with `MAIL_USE_SSL = True`

### **Emails not sending:**
- Check: All 3 services are running (Redis, Celery Worker, Celery Beat)
- Check: Celery logs for errors

---

## 📝 Summary

**Emails will be sent FROM:** The email you set in `MAIL_USERNAME` (e.g., parkingmanager@gmail.com)

**Email Content:**
- **Monthly Report:** CSV file with all parking history for the month
- **Daily Reminder:** Plain text reminder to book parking

**Next Steps:**
1. Set up Gmail App Password
2. Update config.py with your email
3. Start Redis + Celery services
4. Test with the test endpoint above

