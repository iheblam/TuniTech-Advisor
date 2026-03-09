# 📱 TuniTech Advisor — Smart Phone Recommendation System

> **An AI-powered smartphone recommendation system for the Tunisian market**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB.svg)](https://reactjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248.svg)](https://www.mongodb.com/atlas)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178C6.svg)](https://www.typescriptlang.org/)

---

## 🎯 Project Overview

**TuniTech Advisor** aggregates smartphone data from 5 Tunisian e-commerce platforms, applies a machine-learning pipeline for price prediction, and exposes a full-stack web app so users can search, compare, and get personalised phone recommendations — all with persistent community features (reviews, trending, price history).

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-source Scraping** | 1 236 phones from Tunisianet, Mytek, SpaceNet, BestPhone, BestBuyTunisie |
| **Price Prediction** | KNN model — R² = 0.9998, MAE ≈ 4–33 TND |
| **Smart Recommendations** | Filter by budget, RAM, storage, camera, brand, 5G |
| **Use-case Profiles** | Gaming · Photography · Student · Work · Battery · 5G |
| **Budget Optimizer** | Price range presets + advanced filters |
| **Community Reviews** | 1–5 ⭐ ratings + comments, one review per user per phone |
| **Trending Phones** | View/search event tracking, weighted score ranking |
| **Price History** | 90-day rolling price snapshots per store |
| **Brand Analytics** | Average price + phone count per brand (Recharts) |
| **Market Dashboard** | Spec distributions, price heatmap, Groq AI summary |
| **Scraper Scheduler** | Weekly auto-scrape, additive merge, per-store timeout |
| **JWT Auth** | Registration, login, protected routes, admin panel |

---

## 🗓️ Project Timeline

| Week | Phase | Status |
|------|-------|--------|
| 1 | Setup, Web Scraping & EDA | ✅ Complete |
| 2 | ML Pipeline & MLflow Experiment Tracking | ✅ Complete |
| 3 | FastAPI Backend (REST API + Auth) | ✅ Complete |
| 4 | React + TypeScript Frontend | ✅ Complete |
| 5 | Docker & Full-stack Integration | ✅ Complete |
| 6 | Community Features, Analytics & Scheduler | ✅ Complete |
| 7 | Cloud Deployment (Render + Vercel + MongoDB Atlas) | ✅ Complete |

---

## 🚀 Live Deployment

| Service | URL |
|---------|-----|
| **Frontend** | https://tuni-tech-advisor.vercel.app |
| **Backend API** | https://tunitech-backend.onrender.com |
| **API Docs** | https://tunitech-backend.onrender.com/docs |

### Architecture

```
User Browser
     │
     ▼
Vercel (React Frontend)
     │  HTTPS API calls
     ▼
Render (FastAPI Backend — Docker container)
     │
     ▼
MongoDB Atlas (Persistent Database — free M0 cluster)
```

- **CI/CD**: every `git push` to `main` → GitHub Actions runs tests → deploys backend (Render) + frontend (Vercel) automatically
- **Data persistence**: all users, reviews, trending events and price history live in MongoDB Atlas — never lost on redeploy

---

## 🔧 Technology Stack

### Backend
| Tech | Purpose |
|------|---------|
| Python 3.11 | Core language |
| FastAPI + Uvicorn | REST API, OpenAPI docs at `/docs` |
| Scikit-learn | KNN price prediction, preprocessing pipeline |
| MLflow | Experiment tracking & model registry |
| pymongo | MongoDB Atlas driver |
| python-jose + passlib | JWT auth, bcrypt password hashing |
| APScheduler | Weekly scraper scheduler |
| Pandas / NumPy | Data processing |

### Frontend
| Tech | Purpose |
|------|---------|
| React 18 + TypeScript | UI library |
| Vite | Build tool & dev server |
| Tailwind CSS | Utility-first styling |
| Recharts | Data visualisation |
| Axios | HTTP client |

### Infrastructure
| Tech | Purpose |
|------|---------|
| Docker | Backend containerisation |
| Render | Backend cloud hosting (free tier) |
| Vercel | Frontend cloud hosting (free tier) |
| MongoDB Atlas | Cloud database (free M0 tier, never resets) |
| GitHub Actions | CI/CD pipeline |
| Nginx | Frontend static file serving |

---

## 📊 ML Model

| Model | MAE (TND) | R² | Training Time |
|-------|-----------|-----|---------------|
| **KNN n=10** | **4.42** | **0.9998** | 0.004 s |
| KNN n=5 | 7.97 | 0.9988 | 0.006 s |
| XGBoost | 12.3 | 0.9971 | 2.1 s |

Features used: `ram`, `storage`, `battery`, `screen_size`, `main_camera`, `front_camera`, `brand` (encoded)

---

## 📊 Dataset

| Column | Description |
|--------|-------------|
| `name` | Product name |
| `brand` | Manufacturer |
| `ram` / `storage` | GB |
| `battery` | mAh |
| `screen_size` | inches |
| `main_camera` / `front_camera` | MP |
| `network` | 4G / 5G |
| `price` | TND |
| `store` | Source store |

**1 236 phones** across 5 stores · 85–97 % spec coverage after enrichment

---

## 🗄️ Database Collections (MongoDB Atlas)

| Collection | Content |
|------------|---------|
| `users` | Registered user profiles + bcrypt hashed passwords |
| `reviews` | Phone ratings and comments per user |
| `trending` | View / search event counts + weighted score |
| `price_history` | 90-day rolling price snapshots per phone per store |
| `scheduler_status` | Last/next run time, per-store results, logs |

---

## 🛠️ Local Development

### Prerequisites
- Python 3.11+, Node.js 20+, Docker Desktop

### Quick start with Docker Compose

```bash
git clone https://github.com/iheblam/TuniTech-Advisor.git
cd TuniTech-Advisor

# copy and edit env vars
cp .env.example .env   # set MONGODB_URI, GROQ_API_KEY, etc.

docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

### Manual setup (without Docker)

```bash
# Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_api.py          # → http://localhost:8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev               # → http://localhost:3000
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `JWT_SECRET` | Random secret for signing tokens |
| `ADMIN_USERNAME` | Admin panel login |
| `ADMIN_PASSWORD` | Admin panel password |
| `GROQ_API_KEY` | Groq AI key for market summary |

---

## 👥 Team

| Name | Role |
|------|------|
| **Iheb Lamouchi** | Full-stack Developer |
| **Yassine Nemri** | Full-stack Developer |

---

## 📄 License

Developed as part of an academic course project.

---

<p align="center">
  <b>TuniTech Advisor</b> — Making smartphone shopping smarter in Tunisia 🇹🇳
</p>

