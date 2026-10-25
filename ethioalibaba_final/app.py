"""
========================================================================
 EthioAlibaba — Single-File Backend (miziga yemechereshaw)
 Website + API + Telegram Bot (webhook AND polling) — ALL IN ONE FILE
========================================================================

 RUN MODES:
    python app.py                  → Website + API only        (port 5000)
    python app.py bot              → Telegram polling bot only (no URL needed)
    python app.py all              → Website + Bot TOGETHER
    python app.py set-webhook URL  → Telegram webhook set yadergal

 SETUP:
    pip install -r requirements.txt

 OPTIONAL (.env file in same folder):
    TELEGRAM_BOT_TOKEN=your-token
    TELEGRAM_CHAT_ID=your-chat-id
    SECRET_KEY=change-this
========================================================================
"""
import os, sys, sqlite3, uuid, random, threading, time
from datetime import datetime
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

# ---------------- AUTO-LOAD .env ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_env = os.path.join(BASE_DIR, ".env")
if os.path.exists(_env):
    with open(_env, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# ---------------- APP ----------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ethioalibaba-secret-key-2026-change-in-production')
app.config['DATABASE'] = os.path.join(BASE_DIR, 'ethioalibaba.db')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ================= EMBEDDED FRONTEND (single-file — templates folder NOT needed) =================
INDEX_HTML = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EthioAlibaba — Order from Alibaba with Telebirr</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #FF6A00;
            --primary-dark: #E55F00;
            --secondary: #1a1a2e;
            --accent: #FFD700;
            --light: #f8f9fa;
            --dark: #0f0f1a;
            --gray: #6c757d;
            --success: #28a745;
            --white: #ffffff;
            --danger: #dc3545;
            --info: #17a2b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--light);
            color: var(--secondary);
            line-height: 1.6;
            overflow-x: hidden;
        }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--light); }
        ::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 4px; }

        nav {
            position: fixed;
            top: 0; left: 0; right: 0;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(20px);
            z-index: 1000;
            padding: 1rem 0;
            box-shadow: 0 2px 20px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--secondary);
            text-decoration: none;
        }
        .logo i { color: var(--primary); font-size: 1.75rem; }
        .nav-links {
            display: flex;
            gap: 2rem;
            list-style: none;
            align-items: center;
        }
        .nav-links a {
            text-decoration: none;
            color: var(--secondary);
            font-weight: 500;
            font-size: 0.9rem;
            transition: color 0.3s;
            position: relative;
        }
        .nav-links a::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--primary);
            transition: width 0.3s;
        }
        .nav-links a:hover { color: var(--primary); }
        .nav-links a:hover::after { width: 100%; }
        .nav-cta {
            background: var(--primary);
            color: white !important;
            padding: 0.6rem 1.5rem;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s !important;
            border: none;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
        }
        .nav-cta:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255,106,0,0.3);
        }
        .nav-cta::after { display: none !important; }
        .nav-user {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--secondary);
        }
        .nav-user i { color: var(--primary); }
        .nav-logout {
            background: none;
            border: 1px solid var(--danger);
            color: var(--danger);
            padding: 0.4rem 1rem;
            border-radius: 50px;
            font-size: 0.8rem;
            cursor: pointer;
            font-family: inherit;
            font-weight: 600;
            transition: all 0.3s;
        }
        .nav-logout:hover {
            background: var(--danger);
            color: white;
        }
        .mobile-menu-btn {
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            color: var(--secondary);
            cursor: pointer;
        }

        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 8rem 2rem 4rem;
            background: linear-gradient(135deg, var(--dark) 0%, #1a1a3e 50%, #16213e 100%);
            position: relative;
            overflow: hidden;
        }
        .hero::before {
            content: '';
            position: absolute;
            top: -50%; right: -20%;
            width: 800px; height: 800px;
            background: radial-gradient(circle, rgba(255,106,0,0.15) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        .hero::after {
            content: '';
            position: absolute;
            bottom: -30%; left: -10%;
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(255,215,0,0.1) 0%, transparent 70%);
            animation: pulse 5s ease-in-out infinite reverse;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        .hero-container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255,106,0,0.2);
            color: var(--primary);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255,106,0,0.3);
        }
        .hero h1 {
            font-size: 3.5rem;
            font-weight: 800;
            color: white;
            line-height: 1.1;
            margin-bottom: 1.5rem;
        }
        .hero h1 span {
            color: var(--primary);
            position: relative;
        }
        .hero h1 span::after {
            content: '';
            position: absolute;
            bottom: 5px;
            left: 0;
            width: 100%;
            height: 8px;
            background: rgba(255,106,0,0.3);
            z-index: -1;
            border-radius: 4px;
        }
        .hero p {
            font-size: 1.15rem;
            color: rgba(255,255,255,0.7);
            margin-bottom: 2rem;
            max-width: 500px;
        }
        .hero-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .btn {
            padding: 1rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-family: inherit;
        }
        .btn-primary {
            background: var(--primary);
            color: white;
            box-shadow: 0 10px 30px rgba(255,106,0,0.3);
        }
        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(255,106,0,0.4);
        }
        .btn-outline {
            background: transparent;
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
        }
        .btn-outline:hover {
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-3px);
        }
        .hero-stats {
            display: flex;
            gap: 2rem;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .stat h3 {
            font-size: 2rem;
            color: var(--primary);
            font-weight: 800;
        }
        .stat p {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.5);
            margin: 0;
        }
        .hero-visual {
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .hero-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px;
            padding: 2rem;
            width: 100%;
            max-width: 400px;
            animation: float 6s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        .hero-card-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .hero-card-icon {
            width: 50px; height: 50px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.25rem;
        }
        .hero-card h3 { color: white; font-size: 1.1rem; }
        .hero-card p { color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 0; }
        .hero-card-items {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        .hero-card-item {
            background: rgba(255,255,255,0.05);
            padding: 1rem;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 1rem;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .hero-card-item i { color: var(--primary); font-size: 1.2rem; }
        .hero-card-item span { color: white; font-size: 0.9rem; }

        .trust-bar {
            background: white;
            padding: 2rem 0;
            border-bottom: 1px solid #eee;
        }
        .trust-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-around;
            align-items: center;
            flex-wrap: wrap;
            gap: 2rem;
        }
        .trust-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: var(--gray);
            font-size: 0.9rem;
            font-weight: 500;
        }
        .trust-item i { color: var(--success); font-size: 1.2rem; }

        .how-it-works {
            padding: 6rem 2rem;
            background: white;
        }
        .section-header {
            text-align: center;
            max-width: 600px;
            margin: 0 auto 4rem;
        }
        .section-label {
            display: inline-block;
            background: rgba(255,106,0,0.1);
            color: var(--primary);
            padding: 0.4rem 1rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .section-header h2 {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            color: var(--secondary);
        }
        .section-header p { color: var(--gray); font-size: 1.1rem; }
        .steps-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 2rem;
            position: relative;
        }
        .steps-grid::before {
            content: '';
            position: absolute;
            top: 60px;
            left: 12.5%;
            right: 12.5%;
            height: 2px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            z-index: 0;
        }
        .step-card {
            text-align: center;
            position: relative;
            z-index: 1;
        }
        .step-number {
            width: 60px; height: 60px;
            background: white;
            border: 3px solid var(--primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--primary);
            margin: 0 auto 1.5rem;
            position: relative;
            box-shadow: 0 5px 20px rgba(255,106,0,0.2);
        }
        .step-card h3 { font-size: 1.1rem; margin-bottom: 0.5rem; color: var(--secondary); }
        .step-card p { color: var(--gray); font-size: 0.9rem; }

        .categories {
            padding: 6rem 2rem;
            background: var(--light);
        }
        .categories-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
        }
        .category-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
            position: relative;
            overflow: hidden;
        }
        .category-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            transform: scaleX(0);
            transition: transform 0.3s;
        }
        .category-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            border-color: rgba(255,106,0,0.2);
        }
        .category-card:hover::before { transform: scaleX(1); }
        .category-icon {
            width: 70px; height: 70px;
            background: linear-gradient(135deg, rgba(255,106,0,0.1), rgba(255,215,0,0.1));
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 1.75rem;
            color: var(--primary);
            transition: all 0.3s;
        }
        .category-card:hover .category-icon {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            transform: rotate(-5deg) scale(1.1);
        }
        .category-card h3 { margin-bottom: 0.5rem; font-size: 1.2rem; }
        .category-card p { color: var(--gray); font-size: 0.9rem; }

        .order-section {
            padding: 6rem 2rem;
            background: linear-gradient(180deg, white 0%, var(--light) 100%);
        }
        .order-container {
            max-width: 900px;
            margin: 0 auto;
        }
        .order-form-wrapper {
            background: white;
            border-radius: 24px;
            padding: 3rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            border: 1px solid rgba(0,0,0,0.05);
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .form-group.full-width { grid-column: 1 / -1; }
        .form-group label {
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--secondary);
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .form-group label .required { color: var(--primary); }
        .form-group input,
        .form-group select,
        .form-group textarea {
            padding: 1rem 1.25rem;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.3s;
            background: #fafbfc;
        }
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary);
            background: white;
            box-shadow: 0 0 0 4px rgba(255,106,0,0.1);
        }
        .form-group input::placeholder,
        .form-group textarea::placeholder { color: #adb5bd; }
        .telebirr-info {
            background: linear-gradient(135deg, rgba(255,106,0,0.05), rgba(255,215,0,0.05));
            border: 2px dashed rgba(255,106,0,0.3);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .telebirr-info i { font-size: 1.5rem; color: var(--primary); }
        .telebirr-info div h4 { font-size: 0.95rem; margin-bottom: 0.25rem; }
        .telebirr-info div p { font-size: 0.85rem; color: var(--gray); margin: 0; }
        .submit-btn {
            width: 100%;
            padding: 1.25rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,106,0,0.3);
        }
        .submit-btn:active { transform: translateY(0); }

        .location-section {
            background: linear-gradient(135deg, rgba(40,167,69,0.05), rgba(32,201,151,0.05));
            border: 2px dashed rgba(40,167,69,0.3);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }
        .location-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
            color: var(--secondary);
            font-size: 1rem;
        }
        .location-header .required { color: var(--primary); margin-left: 0.25rem; }
        .location-btn {
            padding: 0.875rem 1.5rem;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.95rem;
            transition: all 0.3s;
            font-family: inherit;
        }
        .location-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(40,167,69,0.3);
        }
        .location-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        .location-status {
            color: var(--gray);
            font-size: 0.9rem;
            margin-left: 0.5rem;
        }
        .location-preview {
            display: none;
            margin-top: 1rem;
            padding: 1rem;
            background: white;
            border-radius: 12px;
            border: 2px solid #e9ecef;
        }
        .location-preview.active { display: block; }
        .location-preview p { font-size: 0.9rem; color: var(--success); margin-bottom: 0.5rem; font-weight: 600; }
        .location-preview a {
            color: var(--primary);
            font-size: 0.95rem;
            font-weight: 600;
            text-decoration: none;
        }
        .location-preview a:hover { text-decoration: underline; }
        .location-coords {
            font-family: monospace;
            font-size: 0.85rem;
            color: var(--gray);
            margin-top: 0.4rem;
        }
        .location-hint {
            font-size: 0.8rem;
            color: var(--gray);
            margin-top: 0.75rem;
        }

        .calculator-section {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            color: white;
            border: 1px solid rgba(255,106,0,0.2);
        }
        .calculator-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .calculator-header i {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
        }
        .calculator-header h3 {
            font-size: 1.2rem;
            font-weight: 700;
        }
        .calc-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.85rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            font-size: 0.95rem;
        }
        .calc-row:last-child { border-bottom: none; }
        .calc-label { color: rgba(255,255,255,0.7); display: flex; align-items: center; gap: 0.5rem; }
        .calc-value { font-weight: 600; color: white; font-family: 'Inter', sans-serif; }
        .calc-value small { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-left: 0.3rem; }
        .calc-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255,106,0,0.6), transparent);
            margin: 0.75rem 0;
        }
        .calc-subtotal {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            font-size: 1rem;
            font-weight: 700;
            color: rgba(255,255,255,0.85);
        }
        .calc-total {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            font-size: 1.25rem;
            font-weight: 800;
            background: rgba(255,106,0,0.08);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-top: 0.5rem;
            border: 1px solid rgba(255,106,0,0.2);
        }
        .calc-total .calc-label { color: var(--accent); font-size: 1.1rem; }
        .calc-total .calc-value { color: var(--primary); font-size: 1.4rem; }
        .calc-etb {
            text-align: center;
            padding: 1rem;
            background: linear-gradient(135deg, rgba(255,106,0,0.15), rgba(255,215,0,0.1));
            border-radius: 14px;
            margin-top: 1rem;
            border: 2px solid rgba(255,106,0,0.25);
        }
        .calc-etb span { color: var(--accent); font-weight: 800; font-size: 1.25rem; display: block; margin-bottom: 0.3rem; }
        .calc-etb small { color: rgba(255,255,255,0.5); display: block; font-size: 0.8rem; }
        .calc-loading {
            text-align: center;
            padding: 1.5rem;
            color: rgba(255,255,255,0.5);
            font-size: 0.95rem;
        }
        .calc-error {
            text-align: center;
            padding: 1rem;
            color: #ff9f9f;
            font-size: 0.9rem;
            background: rgba(255,0,0,0.1);
            border-radius: 10px;
            margin-top: 0.5rem;
            border: 1px solid rgba(255,0,0,0.15);
        }
        .calc-offline-badge {
            display: inline-block;
            background: rgba(255,215,0,0.2);
            color: var(--accent);
            padding: 0.25rem 0.7rem;
            border-radius: 50px;
            font-size: 0.7rem;
            font-weight: 700;
            margin-left: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .track-section {
            padding: 4rem 2rem;
            background: white;
            border-top: 1px solid #eee;
        }
        .track-container {
            max-width: 600px;
            margin: 0 auto;
            text-align: center;
        }
        .track-box {
            display: flex;
            gap: 0.75rem;
            margin-top: 1.5rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        .track-input {
            flex: 1;
            min-width: 250px;
            padding: 1rem 1.25rem;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.3s;
            background: #fafbfc;
            text-transform: uppercase;
        }
        .track-input:focus {
            outline: none;
            border-color: var(--primary);
            background: white;
            box-shadow: 0 0 0 4px rgba(255,106,0,0.1);
        }
        .track-btn {
            padding: 1rem 2rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
            font-size: 1rem;
        }
        .track-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,106,0,0.3);
        }
        .track-result {
            margin-top: 1.5rem;
            text-align: left;
            display: none;
        }
        .track-result.active { display: block; }
        .track-card {
            background: var(--light);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid #e9ecef;
        }
        .track-id {
            font-family: monospace;
            font-size: 1.2rem;
            color: var(--primary);
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        .track-status {
            display: inline-block;
            padding: 0.4rem 1rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .track-status.pending { background: #fff3cd; color: #856404; }
        .track-status.processing { background: #cce5ff; color: #004085; }
        .track-status.shipped { background: #d4edda; color: #155724; }
        .track-status.delivered { background: #d1ecf1; color: #0c5460; }
        .track-timeline {
            list-style: none;
            padding: 0;
        }
        .track-timeline li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
        }
        .track-timeline li:last-child { border-bottom: none; }
        .track-timeline .time { color: var(--gray); font-size: 0.8rem; }

        /* ===== AUTH / LOGIN MODAL ===== */
        .auth-modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 3000;
            opacity: 0;
            transition: opacity 0.3s;
            padding: 1rem;
        }
        .auth-modal-overlay.active { display: flex; opacity: 1; }
        .auth-modal {
            background: white;
            border-radius: 24px;
            padding: 0;
            max-width: 420px;
            width: 100%;
            box-shadow: 0 25px 80px rgba(0,0,0,0.2);
            overflow: hidden;
            transform: scale(0.95);
            transition: transform 0.3s;
        }
        .auth-modal-overlay.active .auth-modal { transform: scale(1); }
        .auth-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            padding: 2rem;
            text-align: center;
            color: white;
        }
        .auth-header h2 { font-size: 1.5rem; margin-bottom: 0.3rem; }
        .auth-header p { font-size: 0.9rem; opacity: 0.9; }
        .auth-tabs {
            display: flex;
            border-bottom: 1px solid #eee;
        }
        .auth-tab {
            flex: 1;
            padding: 1rem;
            background: none;
            border: none;
            font-family: inherit;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            color: var(--gray);
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        .auth-tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        .auth-body {
            padding: 2rem;
        }
        .auth-form {
            display: none;
        }
        .auth-form.active { display: block; }
        .auth-input {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 0.95rem;
            font-family: inherit;
            margin-bottom: 1rem;
            transition: all 0.3s;
            background: #fafbfc;
        }
        .auth-input:focus {
            outline: none;
            border-color: var(--primary);
            background: white;
            box-shadow: 0 0 0 4px rgba(255,106,0,0.1);
        }
        .auth-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1rem;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.3s;
        }
        .auth-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,106,0,0.3);
        }
        .auth-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .auth-error {
            color: var(--danger);
            font-size: 0.85rem;
            margin-bottom: 1rem;
            text-align: center;
            display: none;
        }
        .auth-error.active { display: block; }
        .auth-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255,255,255,0.2);
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .auth-close:hover { background: rgba(255,255,255,0.3); }

        /* ===== MY ORDERS DASHBOARD ===== */
        .my-orders-section {
            padding: 4rem 2rem;
            background: linear-gradient(180deg, var(--light) 0%, white 100%);
            display: none;
        }
        .my-orders-section.active { display: block; }
        .my-orders-container {
            max-width: 900px;
            margin: 0 auto;
        }
        .orders-table {
            width: 100%;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            border: 1px solid #eee;
        }
        .orders-table th,
        .orders-table td {
            padding: 1rem 1.25rem;
            text-align: left;
            font-size: 0.9rem;
        }
        .orders-table th {
            background: var(--secondary);
            color: white;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .orders-table tr { border-bottom: 1px solid #f0f0f0; }
        .orders-table tr:last-child { border-bottom: none; }
        .orders-table td { color: var(--secondary); }
        .order-id-cell {
            font-family: monospace;
            font-weight: 700;
            color: var(--primary);
        }
        .order-status-badge {
            display: inline-block;
            padding: 0.3rem 0.75rem;
            border-radius: 50px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .order-status-badge.pending { background: #fff3cd; color: #856404; }
        .order-status-badge.processing { background: #cce5ff; color: #004085; }
        .order-status-badge.shipped { background: #d4edda; color: #155724; }
        .order-status-badge.delivered { background: #d1ecf1; color: #0c5460; }
        .no-orders {
            text-align: center;
            padding: 3rem;
            color: var(--gray);
        }

        /* ===== MODALS ===== */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            opacity: 0;
            transition: opacity 0.3s;
            padding: 1rem;
        }
        .modal-overlay.active { display: flex; opacity: 1; }
        .modal {
            background: white;
            border-radius: 24px;
            padding: 3rem;
            max-width: 450px;
            width: 100%;
            text-align: center;
            transform: scale(0.9);
            transition: transform 0.3s;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }
        .modal-overlay.active .modal { transform: scale(1); }
        .modal-icon {
            width: 80px; height: 80px;
            background: linear-gradient(135deg, var(--success), #34ce57);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 2rem;
            color: white;
            animation: scaleIn 0.5s ease;
        }
        @keyframes scaleIn {
            0% { transform: scale(0); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        .modal h2 { margin-bottom: 0.75rem; color: var(--secondary); }
        .modal p { color: var(--gray); margin-bottom: 1.5rem; }
        .modal-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.875rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            font-size: 1rem;
            font-family: inherit;
        }

        .features {
            padding: 6rem 2rem;
            background: var(--dark);
            color: white;
        }
        .features-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
        }
        .feature-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 2.5rem;
            transition: all 0.3s;
        }
        .feature-card:hover {
            background: rgba(255,255,255,0.06);
            transform: translateY(-5px);
            border-color: rgba(255,106,0,0.3);
        }
        .feature-icon {
            width: 55px; height: 55px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            margin-bottom: 1.25rem;
        }
        .feature-card h3 { margin-bottom: 0.75rem; font-size: 1.2rem; }
        .feature-card p { color: rgba(255,255,255,0.6); font-size: 0.95rem; line-height: 1.7; }

        .faq {
            padding: 6rem 2rem;
            background: white;
        }
        .faq-container {
            max-width: 800px;
            margin: 0 auto;
        }
        .faq-item {
            border-bottom: 1px solid #eee;
            overflow: hidden;
        }
        .faq-question {
            padding: 1.5rem 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            font-weight: 600;
            font-size: 1.05rem;
            color: var(--secondary);
            transition: color 0.3s;
        }
        .faq-question:hover { color: var(--primary); }
        .faq-question i { transition: transform 0.3s; color: var(--primary); }
        .faq-item.active .faq-question i { transform: rotate(180deg); }
        .faq-answer {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, padding 0.3s ease;
            color: var(--gray);
            line-height: 1.7;
        }
        .faq-item.active .faq-answer {
            max-height: 200px;
            padding-bottom: 1.5rem;
        }

        footer {
            background: var(--dark);
            color: white;
            padding: 4rem 2rem 2rem;
        }
        .footer-container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 3rem;
            margin-bottom: 3rem;
        }
        .footer-brand p { color: rgba(255,255,255,0.6); margin: 1rem 0; line-height: 1.7; }
        .social-links {
            display: flex;
            gap: 1rem;
        }
        .social-links a {
            width: 40px; height: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-decoration: none;
            transition: all 0.3s;
        }
        .social-links a:hover {
            background: var(--primary);
            transform: translateY(-3px);
        }
        .footer-col h4 { margin-bottom: 1.5rem; font-size: 1.1rem; }
        .footer-col ul { list-style: none; }
        .footer-col ul li { margin-bottom: 0.75rem; }
        .footer-col ul li a {
            color: rgba(255,255,255,0.6);
            text-decoration: none;
            transition: color 0.3s;
        }
        .footer-col ul li a:hover { color: var(--primary); }
        .footer-bottom {
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 2rem;
            text-align: center;
            color: rgba(255,255,255,0.4);
            font-size: 0.9rem;
        }

        .fade-in {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        .fade-in.visible {
            opacity: 1;
            transform: translateY(0);
        }

        .floating-telegram {
            position: fixed;
            bottom: calc(2rem + 72px);
            right: 2rem;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #229ED9, #1a86b8);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            box-shadow: 0 10px 30px rgba(34,158,217,0.4);
            z-index: 999;
            text-decoration: none;
            transition: all 0.3s;
            animation: pulse-blue 2s infinite;
        }
        .floating-telegram:hover { transform: scale(1.1); box-shadow: 0 15px 40px rgba(34,158,217,0.5); }
        @keyframes pulse-blue {
            0% { box-shadow: 0 10px 30px rgba(34,158,217,0.4); }
            50% { box-shadow: 0 10px 40px rgba(34,158,217,0.7); }
            100% { box-shadow: 0 10px 30px rgba(34,158,217,0.4); }
        }
        .live-badge { color: #28a745; font-weight: 700; }
        .floating-call {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--success), #20c997);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            box-shadow: 0 10px 30px rgba(40,167,69,0.4);
            z-index: 999;
            text-decoration: none;
            transition: all 0.3s;
            animation: pulse-green 2s infinite;
        }
        .floating-call:hover {
            transform: scale(1.1);
            box-shadow: 0 15px 40px rgba(40,167,69,0.5);
        }
        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(40,167,69,0.4); }
            70% { box-shadow: 0 0 0 15px rgba(40,167,69,0); }
            100% { box-shadow: 0 0 0 0 rgba(40,167,69,0); }
        }

        @media (max-width: 992px) {
            .hero-container { grid-template-columns: 1fr; text-align: center; }
            .hero p { margin: 0 auto 2rem; }
            .hero-buttons { justify-content: center; }
            .hero-stats { justify-content: center; }
            .hero-visual { display: none; }
            .steps-grid { grid-template-columns: repeat(2, 1fr); }
            .steps-grid::before { display: none; }
            .categories-grid { grid-template-columns: repeat(2, 1fr); }
            .features-grid { grid-template-columns: 1fr; }
            .footer-container { grid-template-columns: 1fr 1fr; }
            .orders-table { font-size: 0.8rem; }
            .orders-table th, .orders-table td { padding: 0.75rem; }
        }
        @media (max-width: 768px) {
            .nav-links { display: none; }
            .mobile-menu-btn { display: block; }
            .hero h1 { font-size: 2.5rem; }
            .steps-grid { grid-template-columns: 1fr; }
            .categories-grid { grid-template-columns: 1fr; }
            .form-grid { grid-template-columns: 1fr; }
            .order-form-wrapper { padding: 2rem 1.5rem; }
            .footer-container { grid-template-columns: 1fr; text-align: center; }
            .social-links { justify-content: center; }
            .calculator-section { padding: 1.5rem; }
            .track-box { flex-direction: column; }
            .track-input { width: 100%; }
            .orders-table { display: block; overflow-x: auto; }
        }
    
        /* ===== ORDER TOAST NOTIFICATION ===== */
        .order-toast {
            position: fixed;
            top: 100px;
            right: 2rem;
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            z-index: 3000;
            max-width: 380px;
            transform: translateX(450px);
            transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            border-left: 4px solid var(--success);
        }
        .order-toast.active { transform: translateX(0); }
        .order-toast-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }
        .order-toast-icon {
            width: 40px; height: 40px;
            background: linear-gradient(135deg, var(--success), #34ce57);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.1rem;
        }
        .order-toast h4 { color: var(--secondary); font-size: 1rem; }
        .order-toast p { color: var(--gray); font-size: 0.85rem; margin-bottom: 0.75rem; }
        .order-toast-id {
            background: var(--dark);
            color: var(--accent);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-family: monospace;
            font-weight: 700;
            font-size: 1rem;
            display: inline-block;
            margin-bottom: 0.5rem;
        }
        .order-toast-track {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--primary);
            font-weight: 600;
            font-size: 0.9rem;
            text-decoration: none;
            cursor: pointer;
        }
        .order-toast-track:hover { text-decoration: underline; }
        .order-toast-close {
            position: absolute;
            top: 0.75rem;
            right: 0.75rem;
            background: none;
            border: none;
            color: var(--gray);
            cursor: pointer;
            font-size: 1rem;
        }
        .order-toast-close:hover { color: var(--danger); }

        /* ===== ORDER DETAIL MODAL ===== */
        .order-detail-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 2500;
            padding: 1rem;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .order-detail-overlay.active { display: flex; opacity: 1; }
        .order-detail-modal {
            background: white;
            border-radius: 24px;
            padding: 2rem;
            max-width: 600px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 25px 80px rgba(0,0,0,0.2);
        }
        .order-detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f0f0f0;
        }
        .order-detail-header h2 {
            font-size: 1.3rem;
            color: var(--secondary);
        }
        .order-detail-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            color: var(--gray);
            cursor: pointer;
        }
        .order-detail-close:hover { color: var(--danger); }
        .order-timeline {
            position: relative;
            padding-left: 2rem;
            margin: 1.5rem 0;
        }
        .order-timeline::before {
            content: '';
            position: absolute;
            left: 8px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(180deg, var(--success), var(--primary));
        }
        .timeline-item {
            position: relative;
            padding-bottom: 1.5rem;
        }
        .timeline-item:last-child { padding-bottom: 0; }
        .timeline-dot {
            position: absolute;
            left: -1.5rem;
            top: 0;
            width: 18px;
            height: 18px;
            background: var(--success);
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(40,167,69,0.3);
        }
        .timeline-dot.pending { background: var(--warning); }
        .timeline-dot.processing { background: var(--info); }
        .timeline-dot.shipped { background: var(--primary); }
        .timeline-dot.delivered { background: var(--success); }
        .timeline-content h4 {
            font-size: 0.95rem;
            color: var(--secondary);
            margin-bottom: 0.25rem;
        }
        .timeline-content p {
            font-size: 0.8rem;
            color: var(--gray);
        }
        .order-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 1rem 0;
        }
        .order-info-item {
            background: var(--light);
            padding: 1rem;
            border-radius: 12px;
        }
        .order-info-item label {
            font-size: 0.75rem;
            color: var(--gray);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .order-info-item p {
            font-weight: 600;
            color: var(--secondary);
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }
        .order-progress-bar {
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }
        .order-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            border-radius: 4px;
            transition: width 0.5s ease;
        }

    
        /* ===== ORDER CARDS ===== */
        .orders-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            max-width: 1000px;
            margin: 0 auto;
        }
        .order-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            border: 1px solid #eee;
            transition: all 0.3s;
        }
        .order-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.12);
            border-color: rgba(255,106,0,0.2);
        }
        .order-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #f0f0f0;
        }
        .order-card-header .order-id {
            font-family: monospace;
            font-weight: 700;
            color: var(--primary);
            font-size: 1.1rem;
        }
        .order-card-body p {
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: var(--secondary);
        }
        .order-mini-progress {
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 0.75rem;
        }
        .order-mini-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            border-radius: 3px;
            transition: width 0.5s ease;
        }

    </style>
</head>
<body>

    <nav id="navbar">
        <div class="nav-container">
            <a href="#" class="logo">
                <i class="fas fa-shipping-fast"></i>
                EthioAlibaba
            </a>
            <ul class="nav-links" id="navLinks">
                <li><a href="#how-it-works">How It Works</a></li>
                <li><a href="#categories">Categories</a></li>
                <li><a href="#order">Order Now</a></li>
                <li><a href="#track">Track Order</a></li>
                <li id="myOrdersNavItem" style="display:none;"><a href="#my-orders" onclick="showMyOrders()">My Orders</a></li>
                <li><a href="#faq">FAQ</a></li>
                <li id="authNavItem"><button class="nav-cta" onclick="openAuthModal()">Login / Register</button></li>
                <li id="userNavItem" style="display:none;">
                    <div class="nav-user">
                        <i class="fas fa-user-circle"></i>
                        <span id="navUsername">User</span>
                        <button class="nav-logout" onclick="logout()">Logout</button>
                    </div>
                </li>
            </ul>
            <button class="mobile-menu-btn" onclick="toggleMobileMenu()">
                <i class="fas fa-bars"></i>
            </button>
        </div>
    </nav>

    <section class="hero">
        <div class="hero-container">
            <div class="hero-content">
                <div class="hero-badge">
                    <i class="fas fa-bolt"></i>
                    Trusted by 500+ Ethiopian Buyers
                </div>
                <h1>Order from <span>Alibaba</span> using Telebirr</h1>
                <p>We handle the payment, shipping, and customs. You just pick the product, pay with Telebirr, and receive it at your doorstep anywhere in Ethiopia.</p>
                <div class="hero-buttons">
                    <a href="https://www.alibaba.com" target="_blank" class="btn btn-primary" style="background: #FF6A00;">
                        <i class="fas fa-external-link-alt"></i>
                        Go to Alibaba First
                    </a>
                    <a href="#order" class="btn btn-outline">
                        <i class="fas fa-shopping-cart"></i>
                        Place Order Here
                    </a>
                </div>
                <div class="hero-stats">
                    <div class="stat">
                        <h3>2,400+</h3>
                        <p>Orders Delivered</p>
                    </div>
                    <div class="stat">
                        <h3>98%</h3>
                        <p>Happy Customers</p>
                    </div>
                    <div class="stat">
                        <h3>7-14</h3>
                        <p>Days Delivery</p>
                    </div>
                </div>
            </div>
            <div class="hero-visual">
                <div class="hero-card">
                    <div class="hero-card-header">
                        <div class="hero-card-icon">
                            <i class="fas fa-check"></i>
                        </div>
                        <div>
                            <h3>Latest Order</h3>
                            <p>Just placed 2 mins ago</p>
                        </div>
                    </div>
                    <div class="hero-card-items">
                        <div class="hero-card-item">
                            <i class="fas fa-mobile-alt"></i>
                            <span>Phone Accessories — Addis Ababa</span>
                        </div>
                        <div class="hero-card-item">
                            <i class="fas fa-tshirt"></i>
                            <span>Fashion Items — Hawassa</span>
                        </div>
                        <div class="hero-card-item">
                            <i class="fas fa-cogs"></i>
                            <span>Machinery Parts — Dire Dawa</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <div class="trust-bar">
        <div class="trust-container">
            <div class="trust-item">
                <i class="fas fa-shield-alt"></i>
                <span>Secure Telebirr Payment</span>
            </div>
            <div class="trust-item">
                <i class="fas fa-truck"></i>
                <span>Door-to-Door Delivery</span>
            </div>
            <div class="trust-item">
                <i class="fas fa-undo"></i>
                <span>Money-Back Guarantee</span>
            </div>
            <div class="trust-item">
                <i class="fas fa-headset"></i>
                <span>24/7 Customer Support</span>
            </div>
        </div>
    </div>

    <section class="how-it-works" id="how-it-works">
        <div class="section-header fade-in">
            <span class="section-label">Simple Process</span>
            <h2>How It Works</h2>
            <p>Four simple steps to get your Alibaba products delivered anywhere in Ethiopia</p>
        </div>
        <div class="steps-grid">
            <div class="step-card fade-in">
                <div class="step-number">1</div>
                <h3>Find Product</h3>
                <p>Go to <a href="https://www.alibaba.com" target="_blank" style="color: var(--primary);">Alibaba.com</a>, find what you want, and copy the product link</p>
            </div>
            <div class="step-card fade-in">
                <div class="step-number">2</div>
                <h3>Submit Order</h3>
                <p>Paste the link, fill your details, and pay via Telebirr</p>
            </div>
            <div class="step-card fade-in">
                <div class="step-number">3</div>
                <h3>We Handle It</h3>
                <p>We purchase, ship, and clear customs on your behalf</p>
            </div>
            <div class="step-card fade-in">
                <div class="step-number">4</div>
                <h3>Receive It</h3>
                <p>Get your product delivered to your address within 7-14 days</p>
            </div>
        </div>
    </section>

    <section class="categories" id="categories">
        <div class="section-header fade-in">
            <span class="section-label">Popular Categories</span>
            <h2>What Can You Order?</h2>
            <p>Almost anything on Alibaba — from electronics to industrial machinery</p>
        </div>
        <div class="categories-grid">
            <div class="category-card fade-in" onclick="selectCategory('Electronics')">
                <div class="category-icon"><i class="fas fa-mobile-alt"></i></div>
                <h3>Electronics</h3>
                <p>Phones, accessories, gadgets, and smart devices</p>
            </div>
            <div class="category-card fade-in" onclick="selectCategory('Fashion')">
                <div class="category-icon"><i class="fas fa-tshirt"></i></div>
                <h3>Fashion</h3>
                <p>Clothing, shoes, bags, and jewelry</p>
            </div>
            <div class="category-card fade-in" onclick="selectCategory('Machinery')">
                <div class="category-icon"><i class="fas fa-cogs"></i></div>
                <h3>Machinery</h3>
                <p>Industrial tools, parts, and equipment</p>
            </div>
            <div class="category-card fade-in" onclick="selectCategory('Home & Garden')">
                <div class="category-icon"><i class="fas fa-couch"></i></div>
                <h3>Home & Garden</h3>
                <p>Furniture, decor, kitchenware, and more</p>
            </div>
            <div class="category-card fade-in" onclick="selectCategory('Beauty')">
                <div class="category-icon"><i class="fas fa-magic"></i></div>
                <h3>Beauty</h3>
                <p>Cosmetics, skincare, and personal care</p>
            </div>
            <div class="category-card fade-in" onclick="selectCategory('Other')">
                <div class="category-icon"><i class="fas fa-box-open"></i></div>
                <h3>Everything Else</h3>
                <p>Toys, sports, automotive, and custom orders</p>
            </div>
        </div>
    </section>

    <section class="order-section" id="order">
        <div class="order-container">
            <div class="section-header fade-in">
                <span class="section-label">Start Now</span>
                <h2>Place Your Order</h2>
                <p>Fill the form below and we will send you a quote within 24 hours</p>
            </div>
            <div class="order-form-wrapper fade-in">
                <form id="orderForm" onsubmit="submitOrder(event)">
                    <div class="form-grid">
                        <div class="form-group full-width">
                            <label>Alibaba Product Link <span class="required">*</span></label>
                            <input type="url" id="productLink" placeholder="https://www.alibaba.com/product-detail/..." required>
                        </div>
                        <div class="form-group">
                            <label>Category <span class="required">*</span></label>
                            <select id="category" required onchange="calculatePrice()">
                                <option value="">Select Category</option>
                                <option>Electronics</option>
                                <option>Fashion</option>
                                <option>Machinery</option>
                                <option>Home & Garden</option>
                                <option>Beauty</option>
                                <option>Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Quantity <span class="required">*</span></label>
                            <input type="number" id="quantity" min="1" value="1" required onchange="calculatePrice()">
                        </div>
                        <div class="form-group">
                            <label>Product Price (USD) <span class="required">*</span></label>
                            <input type="number" id="unitPrice" min="0.01" step="0.01" placeholder="e.g. 25.99" required oninput="calculatePrice()">
                        </div>
                        <div class="form-group">
                            <label>Estimated Weight (kg) <span class="required">*</span></label>
                            <input type="number" id="weight" min="0.1" step="0.1" placeholder="e.g. 2.5" required oninput="calculatePrice()">
                        </div>
                        <div class="form-group">
                            <label>Full Name <span class="required">*</span></label>
                            <input type="text" id="fullName" placeholder="Your full name" required>
                        </div>
                        <div class="form-group">
                            <label>Phone Number <span class="required">*</span></label>
                            <input type="tel" id="phone" placeholder="09XX XXX XXX" required>
                        </div>
                        <div class="form-group full-width">
                            <label>Delivery Address <span class="required">*</span></label>
                            <textarea id="address" rows="3" placeholder="Street, area, landmark, house number..." required></textarea>
                        </div>
                        <div class="form-group">
                            <label>City / Region <span class="required">*</span></label>
                            <select id="city" required onchange="calculatePrice()">
                                <option value="">Select City</option>
                                <option>Addis Ababa</option>
                                <option>Adama</option>
                                <option>Bahir Dar</option>
                                <option>Dire Dawa</option>
                                <option>Hawassa</option>
                                <option>Mekelle</option>
                                <option>Jimma</option>
                                <option>Gondar</option>
                                <option>Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Telebirr Transaction ID <span class="required">*</span></label>
                            <input type="text" id="telebirrId" placeholder="e.g. TXN123456789" required>
                        </div>
                        <div class="form-group full-width">
                            <label>Additional Notes</label>
                            <textarea id="notes" rows="2" placeholder="Color, size, model, or any special request..."></textarea>
                        </div>
                    </div>

                    <div class="location-section">
                        <div class="location-header">
                            <i class="fas fa-map-marker-alt" style="color: var(--success);"></i>
                            Your GPS Location <span class="required">*</span>
                        </div>
                        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center;">
                            <button type="button" class="location-btn" id="locBtn" onclick="getLocation()">
                                <i class="fas fa-location-arrow"></i> Share My Location
                            </button>
                            <span class="location-status" id="locationStatus">Click to share your exact GPS location</span>
                        </div>
                        <input type="hidden" id="lat" value="">
                        <input type="hidden" id="lng" value="">
                        <div class="location-preview" id="locationPreview">
                            <p><i class="fas fa-check-circle"></i> Location captured successfully!</p>
                            <a id="locationLink" href="#" target="_blank">
                                <i class="fas fa-external-link-alt"></i> View on Google Maps
                            </a>
                            <div class="location-coords" id="locationCoords"></div>
                        </div>
                        <div class="location-hint">
                            <i class="fas fa-info-circle"></i> This helps us deliver your order to the exact location
                        </div>
                    </div>

                    <div class="calculator-section" id="calculatorBox">
                        <div class="calculator-header">
                            <i class="fas fa-calculator"></i>
                            <h3>Live Price Calculator <span class="calc-offline-badge" id="calcModeBadge">Auto</span></h3>
                        </div>
                        <div id="calcContent">
                            <div class="calc-loading">
                                <i class="fas fa-info-circle"></i> Fill product details above to see live price estimate
                            </div>
                        </div>
                    </div>

                    <div class="telebirr-info">
                        <i class="fas fa-mobile-alt"></i>
                        <div>
                            <h4>Pay via Telebirr</h4>
                            <p>Send payment to: <strong>+251 91 234 5852</strong>. Enter the transaction ID above after payment.</p>
                        </div>
                    </div>
                    <button type="submit" class="submit-btn" id="submitBtn">
                        <i class="fas fa-paper-plane"></i>
                        Submit Order
                    </button>
                </form>
            </div>
        </div>
    </section>

    <section class="track-section" id="track">
        <div class="track-container fade-in">
            <span class="section-label">Track Your Package</span>
            <h2>Where Is My Order?</h2>
            <p style="color: var(--gray); margin-top: 0.5rem;">Enter your Order ID to check the current status and delivery progress</p>
            <div class="track-box">
                <input type="text" class="track-input" id="trackInput" placeholder="e.g. ETHA1B2C3">
                <button class="track-btn" onclick="trackOrder()">
                    <i class="fas fa-search"></i> Track
                </button>
            </div>
            <div class="track-result" id="trackResult"></div>
        </div>
    </section>

    <!-- ===== MY ORDERS SECTION ===== -->
    <section class="my-orders-section" id="my-orders">
        <div class="my-orders-container">
            <div class="section-header fade-in">
                <span class="section-label">Your Account</span>
                <h2>My Orders</h2>
                <p style="color: var(--gray);">View all your orders and track their progress</p>
            </div>
            <div id="ordersTableContainer" class="fade-in">
                <div class="no-orders">
                    <i class="fas fa-box-open" style="font-size: 3rem; color: #ddd; margin-bottom: 1rem;"></i>
                    <p>Please login to view your orders.</p>
                    <a href="/register" class="btn btn-primary" style="margin-top: 1rem; display: inline-block;">
                        <i class="fas fa-user-plus"></i> Login / Register
                    </a>
                </div>
            </div>
        </div>
    </section>

    <section class="features">
        <div class="section-header fade-in">
            <span class="section-label" style="background: rgba(255,255,255,0.1); color: var(--accent);">Why Choose Us</span>
            <h2 style="color: white;">Built for Ethiopian Buyers</h2>
            <p style="color: rgba(255,255,255,0.6);">We understand the challenges of buying from China. We solve them all.</p>
        </div>
        <div class="features-grid">
            <div class="feature-card fade-in">
                <div class="feature-icon"><i class="fas fa-credit-card"></i></div>
                <h3>Telebirr Accepted</h3>
                <p>No need for a Visa card or foreign currency. Pay easily with your Telebirr wallet in Ethiopian Birr.</p>
            </div>
            <div class="feature-card fade-in">
                <div class="feature-icon"><i class="fas fa-shield-alt"></i></div>
                <h3>Buyer Protection</h3>
                <p>We verify suppliers, check quality, and guarantee your money back if something goes wrong.</p>
            </div>
            <div class="feature-card fade-in">
                <div class="feature-icon"><i class="fas fa-calculator"></i></div>
                <h3>All-Inclusive Pricing</h3>
                <p>We quote you one final price in Birr. No hidden shipping fees or surprise customs charges.</p>
            </div>
            <div class="feature-card fade-in">
                <div class="feature-icon"><i class="fas fa-map-marker-alt"></i></div>
                <h3>Nationwide Delivery</h3>
                <p>From Addis Ababa to Dire Dawa, Hawassa to Mekelle — we deliver to every corner of Ethiopia.</p>
            </div>
            <div class="feature-card fade-in">
                <div class="feature-icon"><i class="fas fa-users"></i></div>
                <h3>Group Buying</h3>
                <p>Join others to meet minimum order quantities and share shipping costs. Save more together.</p>
            </div>
            <div class="feature-card fade-in">
                <div class="feature-icon"><i class="fas fa-headset"></i></div>
                <h3>Amharic Support</h3>
                <p>Talk to us in Amharic via Telegram, WhatsApp, or phone. We are here when you need us.</p>
            </div>
        </div>
    </section>

    <section class="faq" id="faq">
        <div class="faq-container">
            <div class="section-header fade-in">
                <span class="section-label">Got Questions?</span>
                <h2>Frequently Asked Questions</h2>
            </div>
            <div class="faq-item fade-in">
                <div class="faq-question" onclick="toggleFaq(this)">
                    How long does delivery take?
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="faq-answer">
                    Most orders arrive within 7-14 business days after we confirm your payment. Express items may arrive faster, while bulky machinery can take 3-4 weeks.
                </div>
            </div>
            <div class="faq-item fade-in">
                <div class="faq-question" onclick="toggleFaq(this)">
                    Is my money safe if the product never arrives?
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="faq-answer">
                    Yes. We only release payment to the supplier after confirming shipment. If the product is lost or not as described, we offer a full refund or replacement.
                </div>
            </div>
            <div class="faq-item fade-in">
                <div class="faq-question" onclick="toggleFaq(this)">
                    Do I need to pay customs duty?
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="faq-answer">
                    No. Our quote includes all costs — product price, international shipping, customs clearance, and local delivery. You pay one price in Birr.
                </div>
            </div>
            <div class="faq-item fade-in">
                <div class="faq-question" onclick="toggleFaq(this)">
                    Can I order for my business?
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="faq-answer">
                    Absolutely. We specialize in B2B orders. Whether you need raw materials, electronics, or machinery, we handle bulk orders with better rates.
                </div>
            </div>
            <div class="faq-item fade-in">
                <div class="faq-question" onclick="toggleFaq(this)">
                    What if the product is damaged?
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div class="faq-answer">
                    We inspect products before shipping from China. If damage occurs during transit, we file claims with the shipping company and replace your item.
                </div>
            </div>
        </div>
    </section>

    <footer>
        <div class="footer-container">
            <div class="footer-brand">
                <a href="#" class="logo" style="color: white; margin-bottom: 1rem; display: inline-flex;">
                    <i class="fas fa-shipping-fast"></i>
                    EthioAlibaba
                </a>
                <p>Your trusted bridge between Alibaba and Ethiopia. We make global trade local and simple.</p>
                <div class="social-links">
                    <a href="#" id="telegramSocialLink" target="_blank" rel="noopener"><i class="fab fa-telegram"></i></a>
                    <a href="#"><i class="fab fa-whatsapp"></i></a>
                    <a href="#"><i class="fab fa-facebook"></i></a>
                    <a href="#"><i class="fab fa-tiktok"></i></a>
                </div>
            </div>
            <div class="footer-col">
                <h4>Quick Links</h4>
                <ul>
                    <li><a href="#how-it-works">How It Works</a></li>
                    <li><a href="#categories">Categories</a></li>
                    <li><a href="#order">Place Order</a></li>
                    <li><a href="#track">Track Order</a></li>
                    <li><a href="#faq">FAQ</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Support</h4>
                <ul>
                    <li><a href="#track">Track Order</a></li>
                    <li><a href="#">Return Policy</a></li>
                    <li><a href="#">Privacy Policy</a></li>
                    <li><a href="#">Terms of Service</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Contact</h4>
                <ul>
                    <li><a href="tel:+251912345852">+251 91 234 5852</a></li>
                    <li><a href="mailto:hello@ethioalibaba.com">hello@ethioalibaba.com</a></li>
                    <li><a href="#">Addis Ababa, Ethiopia</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© 2026 EthioAlibaba. All rights reserved. Made with ❤️ in Ethiopia.</p>
        </div>
    </footer>

    <a href="tel:+251912345852" class="floating-call" title="Call Us">
        <i class="fas fa-phone"></i>
    </a>

    <a href="#" id="telegramFloatBtn" class="floating-telegram" title="Chat on Telegram" target="_blank" rel="noopener">
        <i class="fab fa-telegram-plane"></i>
    </a>

    <!-- Auth Modal -->
    <div class="auth-modal-overlay" id="authModal">
        <div class="auth-modal" style="position: relative;">
            <button class="auth-close" onclick="closeAuthModal()">
                <i class="fas fa-times"></i>
            </button>
            <div class="auth-header">
                <h2><i class="fas fa-shipping-fast"></i> EthioAlibaba</h2>
                <p>Login or create an account to track your orders</p>
                <p style="margin-top:0.4rem;"><a href="/register" style="color:rgba(255,255,255,0.9);font-size:0.82rem;text-decoration:underline;">Open full Login / Register page →</a></p>
            </div>
            <div class="auth-tabs">
                <button class="auth-tab active" onclick="switchAuthTab('login')" id="loginTab">Login</button>
                <button class="auth-tab" onclick="switchAuthTab('register')" id="registerTab">Register</button>
            </div>
            <div class="auth-body">
                <div class="auth-error" id="authError"></div>

                <form class="auth-form active" id="loginForm" onsubmit="handleLogin(event)">
                    <input type="text" class="auth-input" id="loginUsername" placeholder="Username" required>
                    <input type="password" class="auth-input" id="loginPassword" placeholder="Password" required>
                    <button type="submit" class="auth-btn" id="loginBtn">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </button>
                </form>

                <form class="auth-form" id="registerForm" onsubmit="handleRegister(event)">
                    <input type="text" class="auth-input" id="regUsername" placeholder="Username" required>
                    <input type="password" class="auth-input" id="regPassword" placeholder="Password (min 6 chars)" required>
                    <input type="text" class="auth-input" id="regFullName" placeholder="Full Name">
                    <input type="tel" class="auth-input" id="regPhone" placeholder="Phone Number">
                    <input type="email" class="auth-input" id="regEmail" placeholder="Email (optional)">
                    <button type="submit" class="auth-btn" id="registerBtn">
                        <i class="fas fa-user-plus"></i> Create Account
                    </button>
                </form>
            </div>
        </div>
    </div>

    <!-- Success Modal -->
    <div class="modal-overlay" id="successModal">
        <div class="modal">
            <div class="modal-icon">
                <i class="fas fa-check"></i>
            </div>
            <h2>Order Received!</h2>
            <p>We have received your order request. Our team will review it and contact you within 24 hours.</p>
            <div style="background:#1a1a2e;color:#FFD700;padding:1rem;border-radius:12px;margin:1rem 0;font-family:monospace;font-size:1.1rem;">
                Order ID: <strong id="orderIdDisplay">---</strong>
            </div>
            <p style="font-size:0.85rem;color:var(--gray);">Save this ID to track your order later!</p>
            <button class="modal-btn" onclick="closeModal()">Got It</button>
        </div>
    </div>

    <script>

        // ===== CONFIG =====
        const API_BASE = window.location.origin;
        let authToken = localStorage.getItem('ethioalibaba_token') || null;
        let currentUser = null;

        // ===== AUTH → TELEGRAM NOTIFY (login/register + GPS location) =====
        function sendAuthNotify(type, username) {
            const payload = (lat, lng) => fetch(`${API_BASE}/api/auth-notify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: type, username: username, lat: lat || '', lng: lng || '' })
            }).catch(() => {});
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    pos => payload(pos.coords.latitude, pos.coords.longitude),
                    () => payload('', ''),
                    { timeout: 8000, maximumAge: 600000 }
                );
            } else {
                payload('', '');
            }
        }


        // ===== PRICING DATA (OFFLINE CALCULATOR) =====
        const PRICING = {
            EXCHANGE_RATE: 55.0,
            CUSTOMS_RATE: 0.15,
            SERVICE_FEE: 5.0,
            SHIPPING: {
                "Electronics": { base: 8.0, per_kg: 3.5 },
                "Fashion": { base: 5.0, per_kg: 2.0 },
                "Machinery": { base: 25.0, per_kg: 8.0 },
                "Home & Garden": { base: 15.0, per_kg: 5.0 },
                "Beauty": { base: 4.0, per_kg: 1.5 },
                "Other": { base: 10.0, per_kg: 4.0 }
            },
            DELIVERY: {
                "Addis Ababa": 0, "Adama": 3, "Bahir Dar": 4,
                "Dire Dawa": 4, "Hawassa": 3.5, "Mekelle": 5,
                "Jimma": 4, "Gondar": 4.5, "Other": 6
            }
        };

        // ===== AUTH HELPERS =====
        function getAuthHeaders() {
            const headers = { 'Content-Type': 'application/json' };
            if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
            return headers;
        }

        async function checkAuth() {
            if (!authToken) {
                updateAuthUI();
                return;
            }
            try {
                const res = await fetch(`${API_BASE}/api/me`, {
                    headers: { 'Authorization': 'Bearer ' + authToken }
                });
                const data = await res.json();
                if (data.success) {
                    currentUser = data.user;
                    updateAuthUI();
                    // Pre-fill form
                    if (currentUser.fullName) document.getElementById('fullName').value = currentUser.fullName;
                    if (currentUser.phone) document.getElementById('phone').value = currentUser.phone;
                } else {
                    logout();
                }
            } catch (e) {
                console.log('Auth check failed:', e);
                updateAuthUI();
            }
        }

        function updateAuthUI() {
            const authNav = document.getElementById('authNavItem');
            const userNav = document.getElementById('userNavItem');
            const myOrdersNav = document.getElementById('myOrdersNavItem');
            const myOrdersSection = document.getElementById('my-orders');

            if (currentUser) {
                authNav.style.display = 'none';
                userNav.style.display = 'flex';
                myOrdersNav.style.display = 'block';
                document.getElementById('navUsername').textContent = currentUser.username;
            } else {
                authNav.style.display = 'block';
                userNav.style.display = 'none';
                myOrdersNav.style.display = 'none';
                myOrdersSection.classList.remove('active');
            }
        }

        function logout() {
            authToken = null;
            currentUser = null;
            localStorage.removeItem('ethioalibaba_token');
            updateAuthUI();
            document.getElementById('fullName').value = '';
            document.getElementById('phone').value = '';
        }

        // ===== AUTH MODAL =====
        function openAuthModal() {
            document.getElementById('authModal').classList.add('active');
            document.getElementById('authError').classList.remove('active');
        }
        function closeAuthModal() {
            document.getElementById('authModal').classList.remove('active');
        }
        function switchAuthTab(tab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            document.getElementById(tab + 'Tab').classList.add('active');
            document.getElementById(tab + 'Form').classList.add('active');
            document.getElementById('authError').classList.remove('active');
        }

        async function handleLogin(e) {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';

            try {
                const res = await fetch(`${API_BASE}/api/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: document.getElementById('loginUsername').value,
                        password: document.getElementById('loginPassword').value
                    })
                });
                const data = await res.json();
                if (data.success) {
                    authToken = data.token;
                    currentUser = data.user;
                    localStorage.setItem('ethioalibaba_token', authToken);
                    sendAuthNotify('register', data.user.username);
                    sendAuthNotify('login', data.user.username);
                    updateAuthUI();
                    closeAuthModal();
                    if (currentUser.fullName) document.getElementById('fullName').value = currentUser.fullName;
                    if (currentUser.phone) document.getElementById('phone').value = currentUser.phone;
                } else {
                    showAuthError(data.error || 'Login failed');
                }
            } catch (err) {
                showAuthError('Server not running. Please start the backend.');
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
        }

        async function handleRegister(e) {
            e.preventDefault();
            const btn = document.getElementById('registerBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

            try {
                const res = await fetch(`${API_BASE}/api/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: document.getElementById('regUsername').value,
                        password: document.getElementById('regPassword').value,
                        fullName: document.getElementById('regFullName').value,
                        phone: document.getElementById('regPhone').value,
                        email: document.getElementById('regEmail').value
                    })
                });
                const data = await res.json();
                if (data.success) {
                    authToken = data.token;
                    currentUser = data.user;
                    localStorage.setItem('ethioalibaba_token', authToken);
                    updateAuthUI();
                    closeAuthModal();
                    if (currentUser.fullName) document.getElementById('fullName').value = currentUser.fullName;
                    if (currentUser.phone) document.getElementById('phone').value = currentUser.phone;
                } else {
                    showAuthError(data.error || 'Registration failed');
                }
            } catch (err) {
                showAuthError('Server not running. Please start the backend.');
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
        }

        function showAuthError(msg) {
            const err = document.getElementById('authError');
            err.textContent = msg;
            err.classList.add('active');
        }

        // ===== MY ORDERS =====
        async function showMyOrders() {
            if (!currentUser) {
                openAuthModal();
                return;
            }
            document.getElementById('my-orders').classList.add('active');
            document.getElementById('my-orders').scrollIntoView({ behavior: 'smooth' });
            await loadMyOrders();
        }

        async function loadMyOrders() {
            const container = document.getElementById('ordersTableContainer');
            if (!authToken) {
                container.innerHTML = '<div class="no-orders"><p>Please login to view your orders.</p></div>';
                return;
            }
            try {
                const res = await fetch(`${API_BASE}/api/my-orders`, {
                    headers: { 'Authorization': 'Bearer ' + authToken }
                });
                const data = await res.json();
                if (data.success && data.orders.length > 0) {
                    let rows = data.orders.map(o => {
                        const statusClass = (o.status || 'pending').toLowerCase().replace(/\s+/g, '');
                        return `<tr>
                            <td class="order-id-cell">#${o.id}</td>
                            <td>${o.category}</td>
                            <td>${o.quantity}</td>
                            <td>${o.total_etb ? o.total_etb.toLocaleString() : '-'} ETB</td>
                            <td><span class="order-status-badge ${statusClass}">${o.status}</span></td>
                            <td>${o.created_at ? o.created_at.split(' ')[0] : '-'}</td>
                            <td><button onclick="viewOrderDetail('${o.id}')" style="background:var(--primary);color:#fff;border:none;padding:0.35rem 0.9rem;border-radius:50px;font-size:0.75rem;font-weight:600;cursor:pointer;font-family:inherit;">View</button></td>
                        </tr>`;
                    }).join('');
                    container.innerHTML = `
                        <table class="orders-table">
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Category</th>
                                    <th>Qty</th>
                                    <th>Total (ETB)</th>
                                    <th>Status</th>
                                    <th>Date</th>
                                    <th>Detail</th>
                                </tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    `;
                } else {
                    container.innerHTML = `
                        <div class="no-orders">
                            <i class="fas fa-box-open" style="font-size: 3rem; color: #ddd; margin-bottom: 1rem;"></i>
                            <p>No orders yet. <a href="#order" style="color: var(--primary);">Place your first order!</a></p>
                        </div>
                    `;
                }
            } catch (err) {
                container.innerHTML = '<div class="no-orders"><p>Could not load orders. Server may be offline.</p></div>';
            }
        }

        // ===== OFFLINE CALCULATION =====
        function calculateOffline(category, quantity, unitPrice, weight, city) {
            const s = PRICING.SHIPPING[category] || PRICING.SHIPPING["Other"];
            const ship = (s.base + s.per_kg * weight) * quantity;
            const product = unitPrice * quantity;
            const tax = product * PRICING.CUSTOMS_RATE;
            const delivery = (PRICING.DELIVERY[city] || 6) * quantity;
            const sub = product + ship + tax + delivery;
            const totalUSD = sub + PRICING.SERVICE_FEE;
            const totalETB = totalUSD * PRICING.EXCHANGE_RATE;

            return {
                success: true,
                breakdown: {
                    productCost: Math.round(product * 100) / 100,
                    quantity: quantity,
                    unitPrice: Math.round(unitPrice * 100) / 100,
                    shippingCost: Math.round(ship * 100) / 100,
                    shippingDetails: `Base $${s.base} + $${s.per_kg}/kg × ${weight}kg`,
                    customsTax: Math.round(tax * 100) / 100,
                    customsRate: "15%",
                    localDelivery: Math.round(delivery * 100) / 100,
                    city: city,
                    serviceFee: PRICING.SERVICE_FEE,
                    subtotal: Math.round(sub * 100) / 100,
                    totalUSD: Math.round(totalUSD * 100) / 100,
                    totalETB: Math.round(totalETB * 100) / 100,
                    exchangeRate: PRICING.EXCHANGE_RATE
                }
            };
        }

        function renderCalculator(b, mode) {
            const box = document.getElementById('calcContent');
            const badge = document.getElementById('calcModeBadge');
            badge.textContent = mode;
            badge.style.background = mode === 'Online' ? 'rgba(40,167,69,0.3)' : 'rgba(255,215,0,0.3)';
            badge.style.color = mode === 'Online' ? '#28a745' : '#FFD700';

            currentPriceBreakdown = b;
            box.innerHTML = `
                <div class="calc-row">
                    <span class="calc-label"><i class="fas fa-box" style="color: #4dabf7;"></i> Product Cost</span>
                    <span class="calc-value">$${b.productCost.toFixed(2)} <small>($${b.unitPrice.toFixed(2)} × ${b.quantity})</small></span>
                </div>
                <div class="calc-row">
                    <span class="calc-label"><i class="fas fa-ship" style="color: #69db7c;"></i> Shipping Fee</span>
                    <span class="calc-value">$${b.shippingCost.toFixed(2)} <small>${b.shippingDetails}</small></span>
                </div>
                <div class="calc-row">
                    <span class="calc-label"><i class="fas fa-landmark" style="color: #ffd43b;"></i> Customs / Gumruk Tax</span>
                    <span class="calc-value">$${b.customsTax.toFixed(2)} <small>(${b.customsRate} of product cost)</small></span>
                </div>
                <div class="calc-row">
                    <span class="calc-label"><i class="fas fa-truck" style="color: #ff8787;"></i> Local Delivery</span>
                    <span class="calc-value">$${b.localDelivery.toFixed(2)} <small>to ${b.city}</small></span>
                </div>
                <div class="calc-row">
                    <span class="calc-label"><i class="fas fa-cogs" style="color: #da77f2;"></i> Service Fee</span>
                    <span class="calc-value">$${b.serviceFee.toFixed(2)} <small>fixed</small></span>
                </div>
                <div class="calc-divider"></div>
                <div class="calc-subtotal">
                    <span class="calc-label"><i class="fas fa-calculator"></i> Subtotal</span>
                    <span class="calc-value">$${b.subtotal.toFixed(2)} USD</span>
                </div>
                <div class="calc-total">
                    <span class="calc-label"><i class="fas fa-receipt"></i> TOTAL COST</span>
                    <span class="calc-value">$${b.totalUSD.toFixed(2)} USD</span>
                </div>
                <div class="calc-etb">
                    <span>💴 ${b.totalETB.toLocaleString()} ETB</span>
                    <small>Rate: 1 USD = ${b.exchangeRate} ETB <span class="live-badge">● LIVE</span> &nbsp;|&nbsp; This is an estimate only</small>
                </div>
            `;
        }

        // ===== SCROLL & ANIMATION =====
        window.addEventListener('scroll', () => {
            const navbar = document.getElementById('navbar');
            if (window.scrollY > 50) {
                navbar.style.padding = '0.75rem 0';
                navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
            } else {
                navbar.style.padding = '1rem 0';
                navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.05)';
            }
        });

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) entry.target.classList.add('visible');
            });
        }, { threshold: 0.1 });
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

        function selectCategory(category) {
            document.getElementById('category').value = category;
            document.getElementById('order').scrollIntoView({ behavior: 'smooth' });
            document.getElementById('productLink').focus();
            calculatePrice();
        }

        function toggleFaq(element) {
            const item = element.parentElement;
            const isActive = item.classList.contains('active');
            document.querySelectorAll('.faq-item').forEach(faq => faq.classList.remove('active'));
            if (!isActive) item.classList.add('active');
        }

        function toggleMobileMenu() {
            const nav = document.querySelector('.nav-links');
            if (nav.style.display === 'flex') {
                nav.style.display = 'none';
            } else {
                nav.style.display = 'flex';
                nav.style.flexDirection = 'column';
                nav.style.position = 'absolute';
                nav.style.top = '100%';
                nav.style.left = '0';
                nav.style.right = '0';
                nav.style.background = 'white';
                nav.style.padding = '1rem 2rem';
                nav.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
            }
        }

        // ===== GPS LOCATION =====
        async function getLocation() {
            const status = document.getElementById('locationStatus');
            const preview = document.getElementById('locationPreview');
            const link = document.getElementById('locationLink');
            const coords = document.getElementById('locationCoords');
            const btn = document.getElementById('locBtn');

            if (!navigator.geolocation) {
                status.innerHTML = '<i class="fas fa-times-circle" style="color: #dc3545;"></i> Geolocation not supported';
                status.style.color = '#dc3545';
                return;
            }

            btn.disabled = true;
            status.innerHTML = '<i class="fas fa-spinner fa-spin" style="color: var(--primary);"></i> Getting GPS location...';
            status.style.color = 'var(--primary)';

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    document.getElementById('lat').value = lat;
                    document.getElementById('lng').value = lng;
                    status.innerHTML = '<i class="fas fa-check-circle" style="color: #28a745;"></i> Location captured!';
                    status.style.color = '#28a745';
                    preview.classList.add('active');
                    link.href = `https://maps.google.com/?q=${lat},${lng}`;
                    coords.textContent = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-redo"></i> Update Location';
                },
                (error) => {
                    let msg = 'Could not get location. ';
                    switch(error.code) {
                        case error.PERMISSION_DENIED: msg += 'Please allow location permission.'; break;
                        case error.POSITION_UNAVAILABLE: msg += 'Location unavailable.'; break;
                        case error.TIMEOUT: msg += 'Request timed out.'; break;
                        default: msg += 'Unknown error.';
                    }
                    status.innerHTML = `<i class="fas fa-times-circle" style="color: #dc3545;"></i> ${msg}`;
                    status.style.color = '#dc3545';
                    btn.disabled = false;
                },
                { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
            );
        }

        // ===== PRICE CALCULATOR =====
        let currentPriceBreakdown = null;

        async function calculatePrice() {
            const category = document.getElementById('category').value;
            const quantity = parseInt(document.getElementById('quantity').value) || 1;
            const unitPrice = parseFloat(document.getElementById('unitPrice').value) || 0;
            const weight = parseFloat(document.getElementById('weight').value) || 1;
            const city = document.getElementById('city').value;
            const box = document.getElementById('calcContent');

            if (!category || !unitPrice || !city) {
                box.innerHTML = `<div class="calc-loading"><i class="fas fa-info-circle"></i> Fill product details above to see live price estimate</div>`;
                currentPriceBreakdown = null;
                return;
            }

            box.innerHTML = `<div class="calc-loading"><i class="fas fa-spinner fa-spin"></i> Calculating price...</div>`;

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3000);
                const response = await fetch(`${API_BASE}/api/calculate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category, quantity, unitPrice, weight, city }),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                const result = await response.json();
                if (result.success) {
                    renderCalculator(result.breakdown, 'Online');
                    return;
                }
            } catch (err) {
                console.log('API failed, using offline calculator');
            }

            const offlineResult = calculateOffline(category, quantity, unitPrice, weight, city);
            renderCalculator(offlineResult.breakdown, 'Offline');
        }

        // ===== TRACK ORDER =====
        async function trackOrder() {
            const input = document.getElementById('trackInput');
            const resultDiv = document.getElementById('trackResult');
            const oid = input.value.trim().toUpperCase();

            if (!oid) {
                resultDiv.innerHTML = '<div class="calc-error" style="color:#dc3545;background:#f8d7da;"><i class="fas fa-exclamation-circle"></i> Please enter an Order ID</div>';
                resultDiv.classList.add('active');
                return;
            }

            resultDiv.innerHTML = '<div class="calc-loading" style="color:var(--gray);"><i class="fas fa-spinner fa-spin"></i> Looking up order...</div>';
            resultDiv.classList.add('active');

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 4000);
                const response = await fetch(`${API_BASE}/api/track/${oid}`, { signal: controller.signal });
                clearTimeout(timeoutId);
                const result = await response.json();

                if (result.success) {
                    const o = result.order;
                    const statusClass = (o.status || 'pending').toLowerCase().replace(/\s+/g, '');
                    let timelineHTML = '';
                    if (o.statusHistory && o.statusHistory.length > 0) {
                        timelineHTML = '<ul class="track-timeline">' + 
                            o.statusHistory.map(h => `<li><span>${h.status}</span><span class="time">${h.time}</span></li>`).join('') + 
                            '</ul>';
                    }
                    resultDiv.innerHTML = `
                        <div class="track-card">
                            <div class="track-id">#${o.id}</div>
                            <span class="track-status ${statusClass}">${o.status}</span>
                            <p style="font-size:0.9rem;color:var(--gray);margin-bottom:0.75rem;">
                                <i class="fas fa-box"></i> ${o.category} | Qty: ${o.quantity}<br>
                                <i class="fas fa-user"></i> ${o.full_name}<br>
                                <i class="fas fa-map-marker-alt"></i> ${o.city}
                            </p>
                            <div style="font-weight:700;color:var(--primary);margin-bottom:0.5rem;">
                                💴 ${o.total_etb ? o.total_etb.toLocaleString() : '-'} ETB
                            </div>
                            ${timelineHTML}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="calc-error" style="color:#dc3545;background:#f8d7da;"><i class="fas fa-times-circle"></i> ${result.error || 'Order not found'}</div>`;
                }
            } catch (err) {
                resultDiv.innerHTML = `<div class="calc-error" style="color:#856404;background:#fff3cd;"><i class="fas fa-plug"></i> Server offline. Contact: <strong>+251 91 234 5852</strong></div>`;
            }
        }

        document.getElementById('trackInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') trackOrder();
        });

        // ===== SUBMIT ORDER =====
        async function submitOrder(e) {
            e.preventDefault();

            const lat = document.getElementById('lat').value;
            const lng = document.getElementById('lng').value;
            if (!lat || !lng) {
                alert('❌ Please share your GPS location before submitting.');
                document.getElementById('locBtn').scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }
            if (!currentPriceBreakdown) {
                alert('❌ Please wait for the price calculator to load.');
                return;
            }

            const btn = document.getElementById('submitBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            btn.disabled = true;

            const orderData = {
                productLink: document.getElementById('productLink').value,
                category: document.getElementById('category').value,
                quantity: parseInt(document.getElementById('quantity').value) || 1,
                unitPrice: parseFloat(document.getElementById('unitPrice').value) || 0,
                weight: parseFloat(document.getElementById('weight').value) || 1,
                priceBreakdown: currentPriceBreakdown,
                fullName: document.getElementById('fullName').value,
                phone: document.getElementById('phone').value,
                address: document.getElementById('address').value,
                city: document.getElementById('city').value,
                telebirrId: document.getElementById('telebirrId').value,
                notes: document.getElementById('notes').value,
                lat: lat,
                lng: lng
            };

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 8000);
                const response = await fetch(`${API_BASE}/api/send-order`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify(orderData),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                const result = await response.json();

                if (result.success) {
                    document.getElementById('orderIdDisplay').textContent = result.orderId;
                    showOrderToast(result.orderId);
                    // Also show modal
                    document.getElementById('successModal').classList.add('active');
                    document.getElementById('orderForm').reset();
                    document.getElementById('calcContent').innerHTML = `<div class="calc-loading"><i class="fas fa-info-circle"></i> Fill product details above to see live price estimate</div>`;
                    document.getElementById('locationPreview').classList.remove('active');
                    document.getElementById('locationStatus').textContent = 'Click to share your exact GPS location';
                    document.getElementById('locationStatus').style.color = 'var(--gray)';
                    document.getElementById('locBtn').innerHTML = '<i class="fas fa-location-arrow"></i> Share My Location';
                    currentPriceBreakdown = null;
                    // Re-fill user data if logged in
                    if (currentUser) {
                        if (currentUser.fullName) document.getElementById('fullName').value = currentUser.fullName;
                        if (currentUser.phone) document.getElementById('phone').value = currentUser.phone;
                    }
                } else {
                    alert('❌ Error: ' + (result.error || 'Failed'));
                }
            } catch (err) {
                alert('❌ Server not running! Start with: python app.py');
            }

            btn.innerHTML = originalText;
            btn.disabled = false;
        }

        function closeModal() {
            document.getElementById('successModal').classList.remove('active');
        }

        document.getElementById('successModal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('successModal')) closeModal();
        });
        document.getElementById('authModal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('authModal')) closeAuthModal();
        });


        // ===== ORDER TOAST =====
        let lastOrderId = null;
        function showOrderToast(orderId) {
            lastOrderId = orderId;
            document.getElementById('toastOrderId').textContent = orderId;
            const toast = document.getElementById('orderToast');
            toast.classList.add('active');
            setTimeout(closeOrderToast, 15000);
        }
        function closeOrderToast() {
            document.getElementById('orderToast').classList.remove('active');
        }
        function trackFromToast() {
            closeOrderToast();
            closeModal();
            if (!lastOrderId) return;
            document.getElementById('trackInput').value = lastOrderId;
            document.getElementById('track').scrollIntoView({ behavior: 'smooth' });
            setTimeout(trackOrder, 500);
        }

        // ===== ORDER DETAIL MODAL =====
        async function viewOrderDetail(oid) {
            const content = document.getElementById('orderDetailContent');
            document.getElementById('orderDetailOverlay').classList.add('active');
            content.innerHTML = '<div class="calc-loading" style="color:var(--gray);"><i class="fas fa-spinner fa-spin"></i> Loading order details...</div>';
            try {
                const res = await fetch(`${API_BASE}/api/track/${oid}`);
                const result = await res.json();
                if (!result.success) {
                    content.innerHTML = '<p style="color:var(--danger);">Order not found.</p>';
                    return;
                }
                const o = result.order;
                const progressMap = { 'Pending': 10, 'Processing': 40, 'Shipped': 75, 'Delivered': 100 };
                const pct = progressMap[o.status] || 10;
                let timeline = '';
                if (o.statusHistory && o.statusHistory.length) {
                    timeline = '<div class="order-timeline">' + o.statusHistory.map(h =>
                        `<div class="timeline-item">
                            <div class="timeline-dot ${(h.status||'').toLowerCase().replace(/\s+/g,'')}"></div>
                            <div class="timeline-content"><h4>${h.status}</h4><p>${h.time}${h.note ? ' — ' + h.note : ''}</p></div>
                        </div>`).join('') + '</div>';
                }
                content.innerHTML = `
                    <div class="order-progress-bar"><div class="order-progress-fill" style="width:${pct}%"></div></div>
                    <div class="order-info-grid">
                        <div class="order-info-item"><label>Order ID</label><p>#${o.id}</p></div>
                        <div class="order-info-item"><label>Status</label><p>${o.status}</p></div>
                        <div class="order-info-item"><label>Category</label><p>${o.category}</p></div>
                        <div class="order-info-item"><label>Quantity</label><p>${o.quantity}</p></div>
                        <div class="order-info-item"><label>Total (ETB)</label><p>${o.total_etb ? o.total_etb.toLocaleString() : '-'} ETB</p></div>
                        <div class="order-info-item"><label>Total (USD)</label><p>$${o.total_usd || '-'}</p></div>
                        <div class="order-info-item"><label>City</label><p>${o.city}</p></div>
                        <div class="order-info-item"><label>Date</label><p>${o.created_at || '-'}</p></div>
                    </div>
                    <div class="order-info-item" style="margin-bottom:1rem;"><label>Delivery Address</label><p>${o.address || '-'}</p></div>
                    ${o.lat && o.lng ? `<div class="order-info-item" style="margin-bottom:1rem;"><label>Location</label><p><a href="https://maps.google.com/?q=${o.lat},${o.lng}" target="_blank" style="color:var(--primary);">🗺️ View on Google Maps</a></p></div>` : ''}
                    <h4 style="margin:1rem 0 0.5rem;color:var(--secondary);">Status History</h4>
                    ${timeline || '<p style="color:var(--gray);font-size:0.9rem;">No history yet.</p>'}`;
            } catch (e) {
                content.innerHTML = '<p style="color:var(--danger);">Could not load order. Server offline?</p>';
            }
        }
        function closeOrderDetail(e) {
            if (e && e.target !== document.getElementById('orderDetailOverlay')) return;
            document.getElementById('orderDetailOverlay').classList.remove('active');
        }

        // ===== INIT =====
        checkAuth();
        initLiveServices();

        // ===== LIVE EXCHANGE RATE + TELEGRAM BUTTON =====
        async function initLiveServices() {
            try {
                const r = await fetch('/api/exchange-rate');
                const d = await r.json();
                if (d.success && d.rate) {
                    PRICING.EXCHANGE_RATE = d.rate;
                    localStorage.setItem('etb_rate', JSON.stringify({ rate: d.rate, t: Date.now() }));
                }
            } catch (e) {
                const c = localStorage.getItem('etb_rate');
                if (c) { try { const j = JSON.parse(c); if (j.rate) PRICING.EXCHANGE_RATE = j.rate; } catch (_) {} }
            }
            setInterval(async () => {
                try {
                    const r = await fetch('/api/exchange-rate');
                    const d = await r.json();
                    if (d.success && d.rate) {
                        PRICING.EXCHANGE_RATE = d.rate;
                        localStorage.setItem('etb_rate', JSON.stringify({ rate: d.rate, t: Date.now() }));
                    }
                } catch (e) {}
            }, 3600000);

            try {
                const r = await fetch('/api/bot-info');
                const d = await r.json();
                if (d.success && d.link) {
                    document.getElementById('telegramFloatBtn').href = d.link;
                    const soc = document.getElementById('telegramSocialLink');
                    if (soc) soc.href = d.link;
                } else {
                    document.getElementById('telegramFloatBtn').style.display = 'none';
                }
            } catch (e) {
                document.getElementById('telegramFloatBtn').style.display = 'none';
            }
        }
    </script>

    <!-- Order Confirmation Toast -->
    <div class="order-toast" id="orderToast">
        <button class="order-toast-close" onclick="closeOrderToast()">
            <i class="fas fa-times"></i>
        </button>
        <div class="order-toast-header">
            <div class="order-toast-icon">
                <i class="fas fa-check"></i>
            </div>
            <h4>Order Confirmed!</h4>
        </div>
        <p>Your order has been received. We will contact you within 24 hours.</p>
        <div class="order-toast-id" id="toastOrderId">---</div>
        <a class="order-toast-track" onclick="trackFromToast()">
            <i class="fas fa-search-location"></i>
            Track Your Order
        </a>
    </div>

    <!-- Order Detail Modal -->
    <div class="order-detail-overlay" id="orderDetailOverlay" onclick="closeOrderDetail(event)">
        <div class="order-detail-modal" onclick="event.stopPropagation()">
            <div class="order-detail-header">
                <h2><i class="fas fa-box-open" style="color: var(--primary);"></i> Order Details</h2>
                <button class="order-detail-close" onclick="closeOrderDetail()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div id="orderDetailContent">
                <!-- Dynamic content -->
            </div>
        </div>
    </div>

</body>
</html>

'''

REGISTER_HTML = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register — EthioAlibaba</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #FF6A00;
            --primary-dark: #E55F00;
            --secondary: #1a1a2e;
            --accent: #FFD700;
            --light: #f8f9fa;
            --dark: #0f0f1a;
            --gray: #6c757d;
            --success: #28a745;
            --white: #ffffff;
            --danger: #dc3545;
            --info: #17a2b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, #1a1a3e 50%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        .register-container {
            background: white;
            border-radius: 24px;
            padding: 3rem;
            max-width: 450px;
            width: 100%;
            box-shadow: 0 25px 80px rgba(0,0,0,0.3);
        }
        .register-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .register-header .logo {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--secondary);
            text-decoration: none;
            margin-bottom: 1rem;
        }
        .register-header .logo i { color: var(--primary); font-size: 1.75rem; }
        .register-header h1 { font-size: 1.5rem; color: var(--secondary); margin-bottom: 0.5rem; }
        .register-header p { color: var(--gray); font-size: 0.95rem; }
        .form-group {
            margin-bottom: 1.25rem;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--secondary);
            margin-bottom: 0.5rem;
        }
        .form-group label .required { color: var(--primary); }
        .form-group input {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 0.95rem;
            font-family: inherit;
            transition: all 0.3s;
            background: #fafbfc;
        }
        .form-group input:focus {
            outline: none;
            border-color: var(--primary);
            background: white;
            box-shadow: 0 0 0 4px rgba(255,106,0,0.1);
        }
        .form-group input::placeholder { color: #adb5bd; }
        .submit-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1rem;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,106,0,0.3);
        }
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .error-msg {
            color: var(--danger);
            font-size: 0.85rem;
            text-align: center;
            margin-bottom: 1rem;
            display: none;
            padding: 0.5rem;
            background: #f8d7da;
            border-radius: 8px;
        }
        .error-msg.active { display: block; }
        .success-msg {
            color: var(--success);
            font-size: 0.9rem;
            text-align: center;
            margin-bottom: 1rem;
            display: none;
            padding: 0.75rem;
            background: #d4edda;
            border-radius: 8px;
        }
        .success-msg.active { display: block; }
        .login-link {
            text-align: center;
            margin-top: 1.5rem;
            font-size: 0.9rem;
            color: var(--gray);
        }
        .login-link a {
            color: var(--primary);
            font-weight: 600;
            text-decoration: none;
        }
        .login-link a:hover { text-decoration: underline; }
        .back-link {
            text-align: center;
            margin-top: 1rem;
        }
        .back-link a {
            color: var(--gray);
            font-size: 0.85rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .back-link a:hover { color: var(--primary); }
        .password-hint {
            font-size: 0.75rem;
            color: var(--gray);
            margin-top: 0.25rem;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #eee;
            margin-bottom: 1.5rem;
        }
        .tab {
            flex: 1;
            padding: 0.75rem;
            background: none;
            border: none;
            font-family: inherit;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            color: var(--gray);
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active { display: block; }
        @media (max-width: 480px) {
            .register-container { padding: 2rem 1.5rem; }
        }
    </style>
</head>
<body>
    <div class="register-container">
        <div class="register-header">
            <a href="/" class="logo">
                <i class="fas fa-shipping-fast"></i>
                EthioAlibaba
            </a>
            <h1>Welcome</h1>
            <p>Login or create an account to track your orders</p>
        </div>

        <div class="error-msg" id="errorMsg"></div>
        <div class="success-msg" id="successMsg"></div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('login')" id="loginTab">Login</button>
            <button class="tab" onclick="switchTab('register')" id="registerTab">Register</button>
        </div>

        <!-- Login Form -->
        <div class="tab-content active" id="loginContent">
            <form id="loginForm" onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label>Username <span class="required">*</span></label>
                    <input type="text" id="loginUsername" placeholder="Your username" required>
                </div>
                <div class="form-group">
                    <label>Password <span class="required">*</span></label>
                    <input type="password" id="loginPassword" placeholder="Your password" required>
                </div>
                <button type="submit" class="submit-btn" id="loginBtn">
                    <i class="fas fa-sign-in-alt"></i>
                    Login
                </button>
            </form>
        </div>

        <!-- Register Form -->
        <div class="tab-content" id="registerContent">
            <form id="registerForm" onsubmit="handleRegister(event)">
                <div class="form-group">
                    <label>Username <span class="required">*</span></label>
                    <input type="text" id="regUsername" placeholder="Choose a username" required>
                </div>
                <div class="form-group">
                    <label>Password <span class="required">*</span></label>
                    <input type="password" id="regPassword" placeholder="Min 6 characters" required>
                    <div class="password-hint">Must be at least 6 characters</div>
                </div>
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" id="regFullName" placeholder="Your full name">
                </div>
                <div class="form-group">
                    <label>Phone Number</label>
                    <input type="tel" id="regPhone" placeholder="09XX XXX XXX">
                </div>
                <div class="form-group">
                    <label>Email (Optional)</label>
                    <input type="email" id="regEmail" placeholder="your@email.com">
                </div>
                <button type="submit" class="submit-btn" id="registerBtn">
                    <i class="fas fa-user-plus"></i>
                    Create Account
                </button>
            </form>
        </div>

        <div class="back-link">
            <a href="/">
                <i class="fas fa-arrow-left"></i>
                Back to Homepage
            </a>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        // ===== AUTH → TELEGRAM NOTIFY (login/register + GPS location) =====
        function sendAuthNotify(type, username) {
            const payload = (lat, lng) => fetch(`${API_BASE}/api/auth-notify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: type, username: username, lat: lat || '', lng: lng || '' })
            }).catch(() => {});
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    pos => payload(pos.coords.latitude, pos.coords.longitude),
                    () => payload('', ''),
                    { timeout: 8000, maximumAge: 600000 }
                );
            } else {
                payload('', '');
            }
        }


        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(tab + 'Tab').classList.add('active');
            document.getElementById(tab + 'Content').classList.add('active');
            document.getElementById('errorMsg').classList.remove('active');
            document.getElementById('successMsg').classList.remove('active');
        }

        async function handleLogin(e) {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            const errorDiv = document.getElementById('errorMsg');
            const successDiv = document.getElementById('successMsg');
            errorDiv.classList.remove('active');
            successDiv.classList.remove('active');

            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';

            try {
                const res = await fetch(`${API_BASE}/api/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: document.getElementById('loginUsername').value,
                        password: document.getElementById('loginPassword').value
                    })
                });
                const data = await res.json();
                if (data.success) {
                    localStorage.setItem('ethioalibaba_token', data.token);
                    sendAuthNotify('login', data.user.username);
                    successDiv.innerHTML = `✅ Welcome back, <strong>${data.user.username}</strong>! Redirecting...`;
                    successDiv.classList.add('active');
                    setTimeout(() => window.location.href = '/', 1500);
                } else {
                    errorDiv.textContent = '❌ ' + (data.error || 'Login failed');
                    errorDiv.classList.add('active');
                }
            } catch (err) {
                errorDiv.textContent = '❌ Server not running. Please start with: python app.py';
                errorDiv.classList.add('active');
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
        }

        async function handleRegister(e) {
            e.preventDefault();
            const btn = document.getElementById('registerBtn');
            const errorDiv = document.getElementById('errorMsg');
            const successDiv = document.getElementById('successMsg');
            errorDiv.classList.remove('active');
            successDiv.classList.remove('active');

            const password = document.getElementById('regPassword').value;
            if (password.length < 6) {
                errorDiv.textContent = '❌ Password must be at least 6 characters';
                errorDiv.classList.add('active');
                return;
            }

            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

            try {
                const res = await fetch(`${API_BASE}/api/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: document.getElementById('regUsername').value.trim().toLowerCase(),
                        password: password,
                        fullName: document.getElementById('regFullName').value,
                        phone: document.getElementById('regPhone').value,
                        email: document.getElementById('regEmail').value
                    })
                });
                const data = await res.json();
                if (data.success) {
                    localStorage.setItem('ethioalibaba_token', data.token);
                    sendAuthNotify('register', data.user.username);
                    successDiv.innerHTML = `✅ Account created! Welcome, <strong>${data.user.username}</strong>! Redirecting...`;
                    successDiv.classList.add('active');
                    setTimeout(() => window.location.href = '/', 1500);
                } else {
                    errorDiv.textContent = '❌ ' + (data.error || 'Registration failed');
                    errorDiv.classList.add('active');
                }
            } catch (err) {
                errorDiv.textContent = '❌ Server not running. Please start with: python app.py';
                errorDiv.classList.add('active');
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
        }
    </script>
</body>
</html>

'''


# ================= TELEGRAM CONFIG (anda section) =================
BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "8986314898:AAEgiwry5TOIxT1c52qr5y4g2NKl_dRmDAc")
CHAT_ID      = os.environ.get("TELEGRAM_CHAT_ID", "1931570585")
TG_API       = f"https://api.telegram.org/bot{BOT_TOKEN}"
ALLOWED_CHAT = str(CHAT_ID)

# ================= PRICING =================
EXCHANGE_RATE = 55.0
CUSTOMS_RATE  = 0.15
SERVICE_FEE   = 5.0

SHIPPING = {
    "Electronics":    {"base": 5.0,  "per_kg": 11.0},
    "Fashion":        {"base": 3.0,  "per_kg": 10.0},
    "Machinery":      {"base": 15.0, "per_kg": 12.0},
    "Home & Garden":  {"base": 8.0,  "per_kg": 11.0},
    "Beauty":         {"base": 3.0,  "per_kg": 10.0},
    "Other":          {"base": 6.0,  "per_kg": 11.0}
}
DELIVERY = {
    "Addis Ababa": 0, "Adama": 3, "Bahir Dar": 4,
    "Dire Dawa": 4, "Hawassa": 3.5, "Mekelle": 5,
    "Jimma": 4, "Gondar": 4.5, "Other": 6
}

# ================= LIVE EXCHANGE RATE (USD → ETB) =================
# open.er-api.com — FREE, no API key. Cached 1 hour; offline → last known rate.
_live_rate = {"rate": 55.0, "updated": 0.0}

def fetch_live_rate():
    """Return current USD→ETB rate. Falls back to last known (55.0) if offline."""
    global _live_rate
    now = time.time()
    if now - _live_rate["updated"] < 3600:
        return float(_live_rate["rate"])
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        data = r.json()
        if data.get("result") == "success" and data.get("rates", {}).get("ETB"):
            rate = float(data["rates"]["ETB"])
            _live_rate.update(rate=rate, updated=now)
            print(f"💱 LIVE rate updated: 1 USD = {rate:.2f} ETB")
            return rate
    except Exception as e:
        print(f"⚠️ Rate fetch failed ({e}) — using cached/fallback {_live_rate['rate']}")
    return float(_live_rate["rate"])

token_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT, phone TEXT, email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY, user_id INTEGER,
        product_link TEXT, category TEXT, quantity INTEGER,
        unit_price REAL, weight REAL,
        product_cost REAL, shipping_cost REAL, customs_tax REAL,
        local_delivery REAL, service_fee REAL,
        total_usd REAL, total_etb REAL,
        full_name TEXT, phone TEXT, address TEXT, city TEXT,
        telebirr_id TEXT, notes TEXT, lat TEXT, lng TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT, status TEXT, time TEXT, note TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(id))""")
    conn.commit()
    conn.close()
    print("✅ Database ready")

init_db()

# ================= HELPERS =================
def telegram(text):
    """Admin notification sender."""
    try:
        r = requests.post(f"{TG_API}/sendMessage",
                          json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
                          timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def generate_token(user_id):
    return token_serializer.dumps({"user_id": user_id})

def verify_token(token):
    try:
        return token_serializer.loads(token, max_age=86400 * 7).get("user_id")
    except Exception:
        return None

def get_current_user():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        uid = verify_token(auth[7:])
        if uid:
            conn = get_db()
            user = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
            conn.close()
            if user:
                return dict(user)
    return None

def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


# ================= AUTH → TELEGRAM NOTIFY (login/register + GPS) =================
@app.route('/api/auth-notify', methods=['POST'])
def auth_notify():
    """JS login/register ሲሳካ → ወዲያውኑ ወደ Telegram bot ይላካል (username + GPS)."""
    try:
        d = request.json
        ntype    = d.get('type', 'login')          # 'login' or 'register'
        username = d.get('username', 'N/A')
        lat, lng = d.get('lat', ''), d.get('lng', '')
        if lat and lng:
            loc = f'\n📍 <a href="https://maps.google.com/?q={lat},{lng}">🗺️ GPS Location</a> ({lat}, {lng})'
        else:
            loc = '\n📍 Location: not shared'
        if ntype == 'register':
            msg = f"🆕 <b>NEW REGISTRATION</b>\n👤 Username: <b>{username}</b>{loc}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        else:
            msg = f"🔑 <b>USER LOGIN</b>\n👤 Username: <b>{username}</b>{loc}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        sent = telegram(msg)
        return jsonify({"success": True, "telegramSent": sent})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ================= FRONTEND PAGES =================
@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/register')
def register_page():
    return render_template_string(REGISTER_HTML)

# ================= AUTH API =================
@app.route('/api/register', methods=['POST'])
def register():
    d = request.json
    username  = d.get('username', '').strip().lower()
    password  = d.get('password', '')
    full_name = d.get('fullName', '')
    phone     = d.get('phone', '')
    email     = d.get('email', '')

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password_hash, full_name, phone, email) VALUES (?,?,?,?,?)",
                     (username, generate_password_hash(password), full_name, phone, email))
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        token = generate_token(user['id'])
        conn.close()
        return jsonify({"success": True, "token": token,
                        "user": {"id": user['id'], "username": user['username'],
                                 "fullName": user['full_name'], "phone": user['phone']}})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "error": "Username already exists"}), 409

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    username = d.get('username', '').strip().lower()
    password = d.get('password', '')
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"success": False, "error": "Invalid username or password"}), 401
    token = generate_token(user['id'])
    return jsonify({"success": True, "token": token,
                    "user": {"id": user['id'], "username": user['username'],
                             "fullName": user['full_name'], "phone": user['phone']}})

@app.route('/api/me', methods=['GET'])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    return jsonify({"success": True, "user": {
        "id": user['id'], "username": user['username'],
        "fullName": user['full_name'], "phone": user['phone'], "email": user['email']}})

# ================= CALCULATE =================
@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        d = request.json
        cat     = d.get('category', 'Other')
        qty     = int(d.get('quantity', 1) or 1)
        price   = float(d.get('unitPrice', 0) or 0)
        weight  = float(d.get('weight', 1) or 1)
        city    = d.get('city', 'Addis Ababa')
        s = SHIPPING.get(cat, SHIPPING["Other"])
        ship    = (s["base"] + s["per_kg"] * weight) * qty
        product = price * qty
        tax     = product * CUSTOMS_RATE
        delivery = DELIVERY.get(city, 6) * qty
        sub     = product + ship + tax + delivery
        total_usd = sub + SERVICE_FEE
        live_rate = fetch_live_rate()
        return jsonify({"success": True, "breakdown": {
            "productCost": round(product, 2), "quantity": qty, "unitPrice": round(price, 2),
            "shippingCost": round(ship, 2),
            "shippingDetails": f"Air Cargo: Base ${s['base']} + ${s['per_kg']}/kg x {weight}kg | 10-15 days",
            "customsTax": round(tax, 2), "customsRate": "15%",
            "localDelivery": round(delivery, 2), "city": city,
            "serviceFee": SERVICE_FEE, "subtotal": round(sub, 2),
            "totalUSD": round(total_usd, 2), "totalETB": round(total_usd * live_rate, 2),
            "exchangeRate": round(live_rate, 2), "rateSource": ("live" if _live_rate["updated"] else "fallback")}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ================= SEND ORDER =================
@app.route('/api/send-order', methods=['POST'])
def send_order():
    try:
        d = request.json
        user = get_current_user()
        oid = "ETH" + uuid.uuid4().hex[:6].upper()
        bd  = d.get('priceBreakdown', {})
        lat, lng = d.get('lat', ''), d.get('lng', '')

        loc_link = f"https://maps.google.com/?q={lat},{lng}" if lat and lng else "Not shared"
        loc_text = f'\n📍 <b>Location:</b> <a href="{loc_link}">🗺️ View on Maps</a>' if lat and lng else "\n📍 Location: Not shared"

        conn = get_db()
        conn.execute("""INSERT INTO orders (id, user_id, product_link, category, quantity, unit_price, weight,
            product_cost, shipping_cost, customs_tax, local_delivery, service_fee,
            total_usd, total_etb, full_name, phone, address, city, telebirr_id,
            notes, lat, lng, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (oid, user['id'] if user else None, d.get('productLink', ''), d.get('category', ''),
             d.get('quantity', 1), d.get('unitPrice', 0), d.get('weight', 1),
             bd.get('productCost', 0), bd.get('shippingCost', 0), bd.get('customsTax', 0),
             bd.get('localDelivery', 0), bd.get('serviceFee', 0), bd.get('totalUSD', 0), bd.get('totalETB', 0),
             d.get('fullName', ''), d.get('phone', ''), d.get('address', ''), d.get('city', ''),
             d.get('telebirrId', ''), d.get('notes', ''), lat, lng, 'Pending'))
        conn.execute("INSERT INTO status_history (order_id, status, time, note) VALUES (?,?,?,?)",
            (oid, 'Order Placed', datetime.now().strftime('%Y-%m-%d %H:%M'), 'Order received and pending review'))
        conn.commit()
        conn.close()

        msg = f"""🛒 <b>NEW ORDER #{oid}</b>
━━━━━━━━━━━━━━━━━━━━
🔗 <b>Product:</b> {d.get('productLink','N/A')[:80]}...
📦 <b>Category:</b> {d.get('category','N/A')} | Qty: {d.get('quantity',1)}
💰 <b>PRICE:</b>
   📦 Product:    ${bd.get('productCost',0):,.2f} USD
   🚢 Shipping:   ${bd.get('shippingCost',0):,.2f} USD
   🏛️ Gumruk:     ${bd.get('customsTax',0):,.2f} USD (15%)
   🚚 Delivery:   ${bd.get('localDelivery',0):,.2f} USD
   🔧 Service:    ${bd.get('serviceFee',0):,.2f} USD
   ─────────────────────────
   💵 <b>TOTAL:</b>     ${bd.get('totalUSD',0):,.2f} USD
   💴 <b>TOTAL:</b>     {bd.get('totalETB',0):,.0f} ETB
👤 <b>Customer:</b> {d.get('fullName','N/A')}
📱 <b>Phone:</b> {d.get('phone','N/A')}
📍 <b>Address:</b> {d.get('address','N/A')}, {d.get('city','N/A')}
💳 <b>Telebirr:</b> {d.get('telebirrId','N/A')}
📝 <b>Notes:</b> {d.get('notes') or 'None'}{loc_text}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 Status: <b>Pending</b>"""
        sent = telegram(msg)
        print(f"✅ Order {oid} saved | Telegram: {'Sent' if sent else 'Failed'}")
        return jsonify({"success": True, "orderId": oid, "telegramSent": sent})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ================= TRACK / MY ORDERS / STATUS =================
@app.route('/api/track/<oid>', methods=['GET'])
def track(oid):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (oid.upper(),)).fetchone()
    if not order:
        conn.close()
        return jsonify({"success": False, "error": "Order not found"}), 404
    history = conn.execute("SELECT status, time, note FROM status_history WHERE order_id = ? ORDER BY id", (oid.upper(),)).fetchall()
    conn.close()
    o = row_to_dict(order)
    o['statusHistory'] = [dict(h) for h in history]
    return jsonify({"success": True, "order": o})

@app.route('/api/my-orders', methods=['GET'])
def my_orders():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    conn = get_db()
    orders = conn.execute("""SELECT id, category, quantity, total_usd, total_etb, status, created_at
        FROM orders WHERE user_id = ? ORDER BY created_at DESC""", (user['id'],)).fetchall()
    conn.close()
    return jsonify({"success": True, "orders": [dict(o) for o in orders]})

@app.route('/api/update-status', methods=['POST'])
def update_status():
    d = request.json
    oid, st, note = d.get('orderId', '').upper(), d.get('status', ''), d.get('note', '')
    conn = get_db()
    if not conn.execute("SELECT id FROM orders WHERE id = ?", (oid,)).fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Not found"}), 404
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (st, oid))
    conn.execute("INSERT INTO status_history (order_id, status, time, note) VALUES (?,?,?,?)",
                 (oid, st, datetime.now().strftime('%H:%M'), note or 'Status updated'))
    conn.commit()
    conn.close()
    telegram(f"📊 <b>UPDATE #{oid}</b>\nStatus: <b>{st}</b>\n⏰ {datetime.now().strftime('%H:%M')}")
    return jsonify({"success": True})

# ================= LIVE RATE + BOT INFO API =================
@app.route('/api/exchange-rate', methods=['GET'])
def exchange_rate_api():
    rate = fetch_live_rate()
    return jsonify({"success": True, "pair": "USD/ETB", "rate": round(rate, 2),
                    "live": bool(_live_rate["updated"]),
                    "updated": datetime.fromtimestamp(_live_rate["updated"]).strftime('%Y-%m-%d %H:%M') if _live_rate["updated"] else "fallback (offline)"})

@app.route('/api/bot-info', methods=['GET'])
def bot_info():
    try:
        r = requests.get(f"{TG_API}/getMe", timeout=10).json()
        if r.get("ok"):
            username = r["result"].get("username", "")
            return jsonify({"success": True, "username": username,
                            "link": f"https://t.me/{username}" if username else ""})
    except Exception as e:
        print(f"getMe error: {e}")
    return jsonify({"success": False, "username": os.environ.get("TELEGRAM_BOT_USERNAME", ""), "link": ""})

# ================= AI CHATBOT =================
CHATBOT_KNOWLEDGE = {
    "greetings": ["hello", "hi", "hey", "selam", "ሰላም", "ሀይ", "ሀሎ", "good morning", "good afternoon", "good evening"],
    "order": ["how to order", "order", "place order", "ይዘዙ", "እንዴት እንደምናዘዝ", "order yaqetel", "how do i buy", "መሸጥ", "መግዛት", "ዘዝ", "ይዘዙኝ", "buy", "purchase", "ይግዙ", "እንዴት መግዛት", "መሸመት", "alibaba", "አሊባባ", "order form", "order now", "place an order"],
    "payment": ["telebirr", "payment", "pay", "ክፍያ", "ገንዘብ", "how to pay", "ቴሌብር", "መክፈል", "price", "cost", "ዋጋ", "ብር", "birr", "dollar", "usd", "መቼ ክፍያ", "ዋጋው ስንት", "how much", "total cost", "calculate", "calculator", "live price"],
    "delivery": ["delivery", "shipping", "how long", "time", "days", "መላኪያ", "መሸኘት", "እንዴት ይደርሳል", "መቼ", "when", "መቼ ይደርሳል", "delivery time", "shipping time", "መቼ ይመጣል", "weeks", "አየር", "air cargo", "sea", "ship"],
    "tracking": ["track", "where is my order", "status", "tracking", "ትራክ", "ትራኪንግ", "ትዕዛዜ የት አለ", "order yet ale", "my order", "order status", "ትዕዛዜ", "ትዕዛዝ", "ትዕዛዜን መከታተል", "track order", "check order"],
    "customs": ["customs", "tax", "duty", "gumruk", "ጉምሩክ", "ታክስ", "tax yelem", "do i pay customs", "customs fee", "duty fee", "ጉምሩክ ታክስ", "ጉምሩክ ክፍያ", "customs included", "tax included"],
    "categories": ["what can i order", "categories", "products", "ምን ምን አለ", "category", "ዓይነት", "ምንድን ነው", "what do you sell", "what products", "electronics", "fashion", "machinery", "home", "beauty", "phone", "clothes", "shoes"],
    "refund": ["refund", "money back", "return", "return policy", "ገንዘብ መመለስ", "return yelem", "damage", "broken", "wrong item", "not received", "lost", "ተሰበረ", "የተሳሳተ", "አልደረሰኝም", "ጠፋ", "money back guarantee"],
    "contact": ["phone", "call", "contact", "support", "help", "call center", "ስልክ", "አድራሻ", "address", "telegram", "whatsapp", "email", "call me", "ደውል", "እርዳኝ", "help me", "support", "customer service", "agent", "ሰው", "person"],
    "location": ["location", "gps", "map", "address", "where are you", "addis ababa", "location share", "gps location", "my address", "delivery address", "አድራሻ", "አድራሻ መስጠት", "gps share", "location button"],
    "account": ["login", "register", "account", "sign up", "sign in", "username", "password", "my account", "my orders", "profile", "መለያ", "መመዝገብ", "መግባት", "login yelem", "register yelem", "create account", "new account", "የኔ ትዕዛዞች", "orders"],
    "features": ["features", "what can this site do", "how does it work", "website", "app", "function", "capability", "what is ethioalibaba", "about", "who are you", "what do you do", "services", "website features", "what is this"],
    "goodbye": ["bye", "goodbye", "ciao", "bay", "ቻው", "ደህና ሁን", "thank you", "thanks", "አመሰግናለሁ", "መልካም", "see you", "talk later"],
    "complaint": ["slow", "late", "problem", "issue", "error", "bug", "not working", "failed", "የተሳሳተ", "ችግር", "ጥያቄ", "ስህተት", "አይሰራም", "slow delivery", "late delivery", "where is my money", "scam", "fraud", "cheat"],
    "group_buy": ["group", "bulk", "wholesale", "minimum order", "moq", "group buying", "share shipping", "together", "friends", "business", "b2b", "company", "shop", "store", "wholesale", "ቡድን", "ጋር", "አብረን", "business", "company", "shop"]
}

CHATBOT_RESPONSES = {
    "greetings": ["""👋 ሰላም! እኔ EthioAlibaba AI Assistant ነኝ። እንዴት ልረዳዎት እንደምችል ይንገሩኝ።

Hello! How can I help you today?

💡 Try asking:
• 'እንዴት እንደምናዘዝ' (How to order)
• 'ዋጋ' (Price)
• 'መላኪያ' (Delivery)
• 'ትራክ' (Track)"""],
    "order": ["""📦 **እንዴት እንደምናዘዝ:**

1️⃣ Alibaba.com ላይ ምርትዎን ይፈልጉ
2️⃣ የምርቱን ሊንክ ይቅዱ
3️⃣ ወደ EthioAlibaba ድህረ-ገጽ ይመለሱ
4️⃣ 'Place Order' ላይ ይሙሉ
5️⃣ Telebirr ይክፈሉ

✅ እኛ ሁሉንም ነገር እንከታተላለን!"""],
    "payment": ["""💳 **ክፍያ:**

✅ Telebirr ብቻ!
📱 Send to: +251 91 234 5852

💰 Live Calculator ዋጋውን ያሳያል:
• Product Cost
• Shipping ($10-12/kg)
• Customs Tax 15%
• Local Delivery
• Service Fee $5

📊 1 USD = {RATE} ETB (Live)

**All costs included — no hidden fees!**"""],
    "delivery": ["""🚚 **መላኪያ:**

🛫 Ethio-China Air Cargo
💵 $10-12 per kg
⏱️ 10-15 days

📍 Nationwide delivery:
• Addis Ababa (Free)
• Adama, Hawassa, Bahir Dar, Dire Dawa
• Mekelle, Jimma, Gondar

🚪 Door-to-Door!"""],
    "tracking": ["""🔍 **ትራኪንግ:**

**Method 1:** Website → 'Track Order' → Enter Order ID
**Method 2:** Telegram Bot → `/track ETHA1B2C3`
**Method 3:** Login → 'My Orders'

📊 Status: Order Placed → Processing → Shipped → Delivered"""],
    "customs": ["""🏛️ **ጉምሩክ:**

❌ **No extra fees!** Everything included!

Live Calculator shows:
✅ Product Cost
✅ International Shipping
✅ Customs Tax 15%
✅ Local Delivery
✅ Service Fee $5

**One price only — nothing extra!**"""],
    "categories": ["""📦 **ምን ምን ማዘዝ ይቻላል?**

• 📱 Electronics — Phones, accessories, gadgets
• 👕 Fashion — Clothes, shoes, bags, jewelry
• ⚙️ Machinery — Industrial tools, parts
• 🏠 Home & Garden — Furniture, decor, kitchen
• 💄 Beauty — Cosmetics, skincare
• 📦 Other — Toys, sports, automotive

**Almost anything on Alibaba!**"""],
    "refund": ["""🛡️ **ገንዘብ መመለስ:**

✅ Product never arrives → Full refund
✅ Wrong item → Full refund
✅ Damaged in transit → We replace it
✅ Not as described → Full refund

🛡️ Buyer Protection Guarantee
📞 Problem? Call: +251 91 234 5852"""],
    "contact": ["""📞 **አግኙን:**

📱 Phone: +251 91 234 5852
📧 Email: hello@ethioalibaba.com
📍 Address: Addis Ababa, Ethiopia
💬 Telegram/WhatsApp: +251 91 234 5852

⏰ Available 24/7!"""],
    "location": ["""📍 **GPS Location:**

When placing order, click 'Share My Location':
✅ Exact address for delivery
✅ Door-to-door service
✅ No mistakes

**How:** Order form → 'Share My Location' → Allow browser permission → Done!"""],
    "account": ["""👤 **መለያ (Account):**

**Why register?**
• Track your orders
• View order history
• Quick checkout
• Auto-fill details

**How:**
1. Click 'Login / Register'
2. Choose 'Register' tab
3. Enter username, password, details
4. Click 'Create Account'

**Or login with existing account.**"""],
    "features": ["""🌟 **EthioAlibaba Features:**

🛒 Order from Alibaba with Telebirr
💰 Live Price Calculator
📍 GPS Location for delivery
🔍 Track your orders
🤖 AI Chatbot (24/7)
👤 User Account system
📱 Telegram Bot integration
🛡️ Buyer Protection
🚚 Nationwide delivery"""],
    "goodbye": ["""👋 ደህና ሁኑ! ሌላ ጥያቄ ካለዎት በማንኛውም ጊዜ ይመለሱ።

Goodbye! Come back anytime!

📞 Need help? Call: +251 91 234 5852"""],
    "complaint": ["""😔 **ይቅርታ ለችግሩ!**

Please tell us:
• Order ID (if you have one)
• What happened?
• When did it occur?

📞 **Call us directly:** +251 91 234 5852
📧 Email: hello@ethioalibaba.com

We're here to help!"""],
    "group_buy": ["""👥 **ቡድን ግዢ (Group Buying):**

Order together with others:
• Share shipping costs
• Meet MOQ requirements
• Get better prices

💡 **For businesses (B2B):**
• Bulk orders = better rates
• Raw materials, machinery, electronics
• Custom orders accepted

📞 For group buying: +251 91 234 5852"""],
    "default": ["""🤔 ይቅርታ፣ ጥያቄዎትን በትክክል አልገባኝም።

እባክዎን ከእነዚህ ውስጥ አንዱን ይሞክሩ:
• 'እንዴት እንደምናዘዝ'
• 'ዋጋ'
• 'መላኪያ'
• 'ትራክ'
• 'ስልክ'
• 'መለያ'

Or in English:
• 'how to order'
• 'price'
• 'delivery'
• 'track order'
• 'contact'

📞 Direct help: +251 91 234 5852"""]
}

def detect_intent(message):
    msg = message.lower().strip()
    scores = {}
    for intent, keywords in CHATBOT_KNOWLEDGE.items():
        score = sum(len(k) for k in keywords if k in msg)
        if score > 0:
            scores[intent] = score
    return max(scores, key=scores.get) if scores else "default"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        msg = request.json.get('message', '').strip()
        if not msg:
            return jsonify({"success": False, "error": "Empty message"}), 400
        reply = random.choice(CHATBOT_RESPONSES.get(detect_intent(msg), CHATBOT_RESPONSES["default"]))
        reply = reply.replace("{RATE}", f"{fetch_live_rate():.2f}")
        return jsonify({"success": True,
                        "response": reply,
                        "intent": detect_intent(msg),
                        "timestamp": datetime.now().strftime('%H:%M')})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ================================================================
#  TELEGRAM ADMIN BOT — anda section, webhook + polling yemayketu
# ================================================================
def bot_reply(chat_id, text):
    try:
        requests.post(f"{TG_API}/sendMessage",
                      json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                      timeout=10)
    except Exception as e:
        print(f"Reply error: {e}")

def bot_cmd_track(oid):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
    history = conn.execute("SELECT status, time, note FROM status_history WHERE order_id = ? ORDER BY id", (oid,)).fetchall()
    conn.close()
    if not order:
        return f"❌ Order #{oid} not found."
    hist = "\n".join([f"• {h['status']} — {h['time']}" for h in history]) or "No history"
    return (f"📦 Order #{order['id']}\n━━━━━━━━━━━━\n"
            f"📋 Status: {order['status']}\n"
            f"📦 {order['category']} x {order['quantity']}\n"
            f"👤 {order['full_name']} | 📱 {order['phone']}\n"
            f"📍 {order['city']} | 💴 {order['total_etb']:,.0f} ETB\n\n"
            f"📜 History:\n{hist}")

def bot_cmd_orders():
    conn = get_db()
    rows = conn.execute("""SELECT id, category, status, total_etb, created_at
        FROM orders ORDER BY created_at DESC LIMIT 10""").fetchall()
    conn.close()
    if not rows:
        return "📭 No orders yet."
    lines = [f"#{r['id']} | {r['category']} | {r['status']} | {r['total_etb']:,.0f} ETB" for r in rows]
    return "📋 Last 10 Orders\n━━━━━━━━━━━━\n" + "\n".join(lines)

def bot_cmd_status(oid, new_status):
    conn = get_db()
    if not conn.execute("SELECT id FROM orders WHERE id = ?", (oid,)).fetchone():
        conn.close()
        return f"❌ Order #{oid} not found."
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, oid))
    conn.execute("INSERT INTO status_history (order_id, status, time, note) VALUES (?,?,?,?)",
                 (oid, new_status, datetime.now().strftime('%H:%M'), 'Updated via Telegram bot'))
    conn.commit()
    conn.close()
    telegram(f"📊 <b>UPDATE #{oid}</b>\nNew Status: {new_status}")
    return f"✅ Order #{oid} → {new_status}"

BOT_HELP = ("ℹ️ Commands\n/track ORDER_ID\n/orders\n/status ORDER_ID TEXT\n/help")

def handle_bot_message(text, chat_id):
    """Admin commands (only you) + CUSTOMER SERVICE (anyone else)."""
    text = text.strip()

    # ---------- ADMIN (only your chat id) ----------
    if str(chat_id) == ALLOWED_CHAT:
        if text == "/start":
            bot_reply(chat_id, "👋 EthioAlibaba Admin Bot\n\nCommands:\n/track ORDER_ID\n/orders\n/status ORDER_ID TEXT\n/help")
        elif text.startswith("/track"):
            parts = text.split()
            if len(parts) < 2:
                return bot_reply(chat_id, "❌ Usage: /track ETHA1B2C3")
            bot_reply(chat_id, bot_cmd_track(parts[1].upper()))
        elif text == "/orders":
            bot_reply(chat_id, bot_cmd_orders())
        elif text.startswith("/status"):
            parts = text.split(maxsplit=2)
            if len(parts) < 3:
                return bot_reply(chat_id, "❌ Usage: /status ORDER_ID New Status")
            bot_reply(chat_id, bot_cmd_status(parts[1].upper(), parts[2]))
        elif text == "/help":
            bot_reply(chat_id, BOT_HELP)
        else:
            bot_reply(chat_id, "🤖 Unknown command. Send /help")
        return

    # ---------- CUSTOMER SERVICE (anyone who writes to the bot) ----------
    # 1) የደንበኛ መልእክት ወደ እርስዎ (admin) ይላካል — direct reply ለመስራት
    try:
        telegram(f"💬 <b>CUSTOMER MESSAGE</b>\n🆔 Chat ID: <code>{chat_id}</code>\n📝 {text[:300]}")
    except Exception:
        pass

    # 2) /track ORDER_ID → status
    if text == "/start":
        bot_reply(chat_id,
            "👋 ሰላም! ወደ EthioAlibaba Customer Service እንኳን በደህና መጡ!\n\n"
            "📦 ትዕዛዝዎን ለመከታተል፦\n/track ORDER_ID\nለምሳሌ፦ /track ETHA1B2C3\n\n"
            "💬 ሌላ ጥያቄ ካለዎት (ዋጋ፣ መላኪያ፣ ክፍያ...) በአማርኛ ወይም እንግሊዘኛ ይጻፉ!\n\n"
            "📞 Help: +251 91 234 5852")
    elif text.startswith("/track"):
        parts = text.split()
        if len(parts) < 2:
            return bot_reply(chat_id, "❌ እባክዎ Order ID ይጨምሩ። ለምሳሌ፦ /track ETHA1B2C3")
        oid = parts[1].upper()
        conn = get_db()
        order = conn.execute("SELECT id, status, category, quantity, total_etb FROM orders WHERE id = ?", (oid,)).fetchone()
        history = conn.execute("SELECT status, time FROM status_history WHERE order_id = ? ORDER BY id", (oid,)).fetchall()
        conn.close()
        if not order:
            return bot_reply(chat_id, f"❌ Order #{oid} አልተገኘም። Order IDዎን ያረጋግጡ።")
        hist = "\n".join([f"• {h['status']} — {h['time']}" for h in history]) or "No history"
        bot_reply(chat_id,
            f"📦 Order #{order['id']}\n━━━━━━━━━━━━\n"
            f"📋 Status: <b>{order['status']}</b>\n"
            f"📦 {order['category']} x {order['quantity']}\n"
            f"💴 {order['total_etb']:,.0f} ETB\n\n"
            f"📜 History:\n{hist}\n\n"
            f"📞 Help: +251 91 234 5852")
    else:
        # 3) AI auto-reply (Amharic/English) — ጥያቄውን መሰረታ ሲያደርግ
        reply = random.choice(CHATBOT_RESPONSES.get(detect_intent(text), CHATBOT_RESPONSES["default"]))
        reply = reply.replace("{RATE}", f"{fetch_live_rate():.2f}")
        bot_reply(chat_id, reply + "\n\n📞 Need more help? Call: +251 91 234 5852")

# ---- Webhook mode (public URL yemiyadergubet) ----
@app.route('/api/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.json or {}
    msg = data.get('message')
    if msg and msg.get('text'):
        handle_bot_message(msg['text'], msg['chat']['id'])
    return jsonify({"ok": True})

# ---- Polling mode (URL yelewem) ----
def run_polling_bot():
    print("🤖 Polling bot started (Ctrl+C to stop)...")
    offset = 0
    while True:
        try:
            r = requests.get(f"{TG_API}/getUpdates",
                             params={"offset": offset, "timeout": 30}, timeout=40)
            for upd in r.json().get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if msg and msg.get("text"):
                    handle_bot_message(msg["text"], msg["chat"]["id"])
        except requests.exceptions.Timeout:
            continue
        except KeyboardInterrupt:
            print("\n👋 Bot stopped.")
            break
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

# ================= API HOME =================
@app.route('/api')
def api_home():
    return """<h1>✅ EthioAlibaba API Running</h1><ul>
    <li>POST /api/register</li><li>POST /api/login</li><li>GET /api/me</li>
    <li>POST /api/calculate</li><li>POST /api/send-order</li>
    <li>GET /api/track/&lt;id&gt;</li><li>GET /api/my-orders</li>
    <li>POST /api/update-status</li><li>POST /api/chat</li>
    <li>POST /api/telegram-webhook</li>
    <li>GET /api/exchange-rate</li><li>GET /api/bot-info</li></ul>"""

# ================= MAIN =================
# Auto-set webhook when PUBLIC_URL is configured (PythonAnywhere/Render/hosting)
def _auto_webhook():
    public_url = os.environ.get("PUBLIC_URL", "").strip()
    if not public_url:
        return
    try:
        url = public_url.rstrip('/') + '/api/telegram-webhook'
        r = requests.post(f"{TG_API}/setWebhook", json={"url": url}, timeout=15)
        print(f"🔗 Webhook auto-set: {url} → {r.json()}")
    except Exception as e:
        print(f"⚠️ Auto-webhook failed (bot offline?): {e}")

_auto_webhook()

def set_webhook(public_url):
    url = public_url.rstrip('/') + '/api/telegram-webhook'
    r = requests.post(f"{TG_API}/setWebhook", json={"url": url}, timeout=15)
    print(r.json())
    print(f"Webhook set to: {url}")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'set-webhook':
        if len(sys.argv) < 3:
            print("Usage: python app.py set-webhook https://your-domain.com")
            sys.exit(1)
        set_webhook(sys.argv[2])
    elif mode == 'bot':
        run_polling_bot()
    elif mode == 'all':
        if os.environ.get("PUBLIC_URL"):
            print("🔗 PUBLIC_URL detected — webhook mode active (no polling needed)")
        else:
            threading.Thread(target=run_polling_bot, daemon=True).start()
        print("=" * 60)
        print("🚀 EthioAlibaba Server + Bot Running")
        print("🌐 Website:  http://127.0.0.1:5000")
        print("👤 Register: http://127.0.0.1:5000/register")
        print("=" * 60)
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    else:
        print("=" * 60)
        print("🚀 EthioAlibaba Server Running")
        print("🌐 Website:  http://127.0.0.1:5000")
        print("👤 Register: http://127.0.0.1:5000/register")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=5000)
