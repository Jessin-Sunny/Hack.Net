#run.py
#!/usr/bin/env python3
"""
Simple run script for Venue Booking System
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🏢 Venue Booking System")
    print("=" * 30)
    print("📱 Starting server at http://localhost:5000")
    print("👤 Admin login: admin / admin123")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 30)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have installed dependencies: pip install -r requirements.txt") 