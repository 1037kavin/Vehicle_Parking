"""
Backend application runner
Run this file from the project root: python run_backend.py
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app

if __name__ == '__main__':
    app = create_app('development')
    print("\n" + "="*50)
    print("Vehicle Parking Management System - Backend")
    print("="*50)
    print("Backend running on: http://localhost:5000")
    print("API documentation: http://localhost:5000/api")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

