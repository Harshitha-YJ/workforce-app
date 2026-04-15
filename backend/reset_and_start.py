"""
Run this ONCE to completely reset the database and start fresh.
Usage: python reset_and_start.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

# Only delete DB in the main process, not Flask's reloader child process
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'employee_mgmt.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✅ Deleted old database")
        except PermissionError:
            print("⚠️  Could not delete DB (in use) — continuing with existing DB")
    else:
        print("ℹ️  No existing database found")

# Create fresh app and database
from app import create_app
app = create_app('development')

print("✅ Fresh database created with:")
print("   → Admin user: admin / admin123")
print("   → 5 sample employees")
print("   → 25 attendance records")
print("")
print("🚀 Starting server on http://127.0.0.1:5000")
print("   Press CTRL+C to stop")
print("")

app.run(debug=True, port=5000)
