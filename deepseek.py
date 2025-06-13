import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)

# Configuration (in production, use environment variables)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT') or secrets.token_hex(16)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
app.config['RESET_TOKEN_EXPIRES'] = 3600  # 1 hour in seconds

# Mock database
users_db = {
    "user@example.com": {
        "password_hash": generate_password_hash("current_password"),
        "reset_tokens": []
    }
}

def generate_reset_token(email):
    """Generate a secure password reset token"""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def verify_reset_token(token, expiration=3600):
    """Verify the reset token and return email if valid"""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def send_reset_email(email, token):
    """Mock function to send reset email (implement with your email service)"""
    reset_link = f"http://example.com/reset-password?token={token}"
    print(f"Password reset link for {email}: {reset_link}")
    # In production, use a real email service like SendGrid, Mailgun, etc.

@app.route('/request-reset', methods=['POST'])
def request_password_reset():
    """Endpoint to request a password reset"""
    email = request.json.get('email')
    
    if email not in users_db:
        # Don't reveal whether email exists to prevent enumeration attacks
        return jsonify({"message": "If this email exists, a reset link has been sent"}), 200
    
    # Generate token
    token = generate_reset_token(email)
    
    # Store token (in production, use database with expiration)
    users_db[email]['reset_tokens'].append({
        'token': token,
        'expires': datetime.utcnow() + timedelta(seconds=app.config['RESET_TOKEN_EXPIRES'])
    })
    
    # Send email
    send_reset_email(email, token)
    
    return jsonify({"message": "If this email exists, a reset link has been sent"}), 200

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Endpoint to reset password with a valid token"""
    token = request.json.get('token')
    new_password = request.json.get('new_password')
    
    # Verify token
    email = verify_reset_token(token)
    if not email or email not in users_db:
        return jsonify({"error": "Invalid or expired token"}), 400
    
    # Check if token exists in user's valid tokens
    valid_tokens = [
        t for t in users_db[email]['reset_tokens']
        if t['token'] == token and t['expires'] > datetime.utcnow()
    ]
    
    if not valid_tokens:
        return jsonify({"error": "Invalid or expired token"}), 400
    
    # Update password
    users_db[email]['password_hash'] = generate_password_hash(new_password)
    
    # Invalidate all reset tokens for this user
    users_db[email]['reset_tokens'] = []
    
    return jsonify({"message": "Password updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=False)  # Always set debug=False in production
