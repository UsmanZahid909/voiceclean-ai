#!/usr/bin/env python3
"""
Debug Flask routes to identify the issue
"""

from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# Simple test routes
@app.route('/')
def index():
    return "VoiceClean AI - Main Page Working"

@app.route('/login')
def login():
    return "Login Page Working"

@app.route('/signup') 
def signup():
    return "Signup Page Working"

@app.route('/pricing')
def pricing():
    return "Pricing Page Working"

@app.route('/dashboard')
def dashboard():
    return "Dashboard Page Working"

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'routes': ['/', '/login', '/signup', '/pricing', '/dashboard'],
        'templates_dir': os.path.exists('api/templates'),
        'debug': True
    })

if __name__ == '__main__':
    app.run(debug=True)