from flask import Flask
from app.routes import init_routes
import os
import sys
from datetime import timedelta

# Ensure the app directory is in the python path for absolute imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

app = Flask(__name__, 
            template_folder='app/templates', 
            static_folder='app/static')

# 1. SECURITY & SESSION CONFIGURATION
# Using a strong key to protect the RAG and salary prediction data
app.secret_key = os.environ.get("SECRET_KEY", "career_platform_xgb_91_stable")

# 2. PERFORMANCE & LIFECYCLE TUNING
# Set session lifetime to 1 hour so the Job Analysis stays active for the user
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config['JSON_SORT_KEYS'] = False

# 3. ROUTE INITIALIZATION
# Connects the upgraded XGBoost logic and the new /jobs Adzuna route
init_routes(app)

if __name__ == "__main__":
    # 4. SERVER EXECUTION
    # Debug mode remains True for development to catch any API integration errors
    print("\n" + "="*50)
    print("🚀 CAREER INTELLIGENCE SYSTEM STARTING...")
    print("🤖 RAG Engine: Grounded with S-BERT")
    print("💼 Live Job Market: Enabled (Adzuna API)")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)