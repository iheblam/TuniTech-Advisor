# 📱 TuniTech Advisor - Smart Phone Recommendation System

> **An AI-powered smartphone recommendation system for Tunisian e-commerce**

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB.svg)](https://reactjs.org/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-orange.svg)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178C6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Styling-38B2AC.svg)](https://tailwindcss.com/)

---

## 🎯 Project Overview

**TuniTech Advisor** is an intelligent smartphone recommendation system designed specifically for the Tunisian market. It aggregates data from multiple local e-commerce platforms, analyzes specifications, and provides personalized phone recommendations based on user preferences - including price comparisons across different stores.

### 🌟 Key Features

- **Multi-source Data Aggregation**: Scrapes smartphones from Tunisianet, Mytek, SpaceNet, and BestPhone
- **Smart Recommendations**: AI-powered matching based on user requirements (budget, RAM, storage, camera, etc.)
- **Price Prediction**: ML model (KNN, R²=0.9998) predicts fair market prices in TND
- **Price Comparison**: Shows the same phone across different stores with price differences
- **Store Availability**: Indicates which stores have the phone in stock
- **Real-time Search**: Fast filtering by brand, price range, and specifications
- **User Authentication**: JWT-based auth with registration, login, and profile management
- **Full-stack Docker**: One-command deployment with Docker Compose
- **Interactive UI**: React + TypeScript + Tailwind CSS frontend with dedicated pages for search, recommendations, predictions, and comparisons

---

## 🗓️ Project Timeline (7 Weeks)

| Week | Phase | Status | Description |
|------|-------|--------|-------------|
| 1 | Setup, Scraping & EDA | ✅ Complete | Project structure, web scrapers, data exploration |
| 2 | ML Pipeline & Experiment Tracking | ✅ Complete | Preprocessing, feature engineering, model training, MLflow |
| 3 | FastAPI Backend | ✅ Complete | Full REST API with auth, predictions, recommendations, search |
| 4 | React Frontend | ✅ Complete | Multi-page TypeScript/Tailwind UI |
| 5 | Docker & Integration | ✅ Complete | Dockerized frontend + backend with Docker Compose |
| 6 | Testing & Optimization | ⏳ Pending | Performance testing, bug fixes, optimization |
| 7 | Deployment & Presentation | ⏳ Pending | Cloud deployment and final presentation |

---

## 📊 Week 1 Progress: Setup, Scraping & EDA

### ✅ What We Accomplished

#### 1. Project Setup
- [x] Git repository initialized and organized
- [x] Virtual environment configured (Python 3.13)
- [x] Dependencies managed via `requirements.txt`
- [x] Folder structure: `code/`, `dataset/`, documentation

#### 2. Web Scraping (4 Sources)
| Source | Products | Method | Notes |
|--------|----------|--------|-------|
| Tunisianet | 357 | BeautifulSoup + Requests | Direct HTML parsing |
| SpaceNet | 320 | BeautifulSoup + Requests | 8 pages scraped |
| Mytek | 281 | Selenium | JavaScript rendering required |
| BestPhone | 138 | BeautifulSoup + Requests | Simpler structure |
| **Total** | **1,096** | | |

#### 3. Data Enrichment
- Cross-source matching to fill missing specifications
- Known specs database for 50+ popular phone models
- Enhanced fuzzy matching algorithms
- **Result**: 85-97% spec coverage across all datasets

#### 4. Exploratory Data Analysis (EDA)
- Created unified dataset combining all sources
- Price analysis across stores and brands
- Specification distribution analysis (RAM, Storage, Battery)
- Data quality assessment and validation
- Generated comprehensive EDA report

### 📁 Week 1 Deliverables
```
├── notebooks/
│   └── 01_EDA.ipynb                   # Exploratory Data Analysis notebook
│
├── scrapers/
│   ├── scrape_tunisianet_smartphones.py
│   ├── scrape_mytek_smartphones.py
│   ├── scrape_spacenet_smartphones.py
│   ├── scrape_bestphone_smartphones.py
│   ├── fill_missing_specs.py
│   ├── fill_specs_from_existing.py
│   ├── fill_bestphone_specs.py
│   ├── fill_bestphone_enhanced.py
│   └── fill_known_specs.py
│
├── dataset/
│   ├── tunisianet_smartphones.csv
│   ├── tunisianet_smartphones_filled.csv
│   ├── mytek_smartphones.csv
│   ├── mytek_smartphones_filled.csv
│   ├── spacenet_smartphones.csv
│   ├── spacenet_smartphones_filled.csv
│   ├── bestphone_smartphones.csv
│   ├── bestphone_smartphones_filled.csv
│   └── unified_smartphones.csv
│
├── requirements.txt
└── README.md
```

---

## � Week 2 Progress: ML Pipeline & Experiment Tracking

### ✅ What We Accomplished

#### 1. Complete ML Pipeline (5 Steps)
- [x] **Step 1: Data Preprocessing** - KNNImputer + StandardScaler pipeline
- [x] **Step 2: Feature Engineering** - Created 14 new features (value_score, price_tier, etc.)
- [x] **Step 3: Feature Selection** - Reduced to 7 optimal features using correlation + RF importance
- [x] **Step 4: Model Training** - Trained KNN, Random Forest, XGBoost
- [x] **Step 5: MLflow Integration** - Complete experiment tracking setup

#### 2. Model Performance
| Model | MAE (TND) | RMSE | R² Score | Training Time | Status |
|-------|-----------|------|----------|---------------|--------|
| **KNN (n=10)** | **4.42** | 19.07 | **0.9998** | 0.004s | 🏆 Best |
| KNN (n=5) | 7.97 | 52.06 | 0.9988 | 0.006s | Baseline |
| XGBoost | 12.3 | 68.4 | 0.9971 | 2.1s | Alternative |
- ✅ Production-ready model pipeline saved

#### 4. Deliverables
- `notebooks/02_ML_Pipeline.ipynb` - Complete ML pipeline
- `models/knn_model.pkl` - Best performing model
- `models/preprocessor_pipeline.pkl` - Feature preprocessing pipeline
- `models/mlflow_model_comparison.png` - Performance visualizations
- `WEEK2_SUMMARY.md` - Comprehensive technical documentation

📖 **[Read Full Week 2 Documentation](WEEK2_SUMMARY.md)**

---

## � Week 3 Progress: FastAPI Backend

### ✅ What We Accomplished

#### 1. REST API Architecture
- [x] **FastAPI** app with versioned routers and Swagger/OpenAPI docs at `/docs`
- [x] CORS middleware configured for frontend integration
- [x] Request-timing middleware and structured JSON error handlers

#### 2. API Endpoints
| Router | Prefix | Highlights |
|--------|--------|-----------|
| Health | `/api/v1/health` | Liveness, readiness, version info |
| Auth | `/api/v1/auth` | Register, login (JWT), token refresh |
| Predictions | `/api/v1/predictions` | Price prediction, batch prediction |
| Recommendations | `/api/v1/recommendations` | Similar phones, personalized suggestions |
| Admin | `/api/v1/admin` | Dataset stats, model info, data reload |

#### 3. Services Layer
- `ml_service.py` – loads trained KNN model + preprocessor pipeline, serves real-time inference
- `data_service.py` – reads unified CSV dataset, provides filtering/search utilities
- `auth_service.py` – JWT token creation & validation
- `user_service.py` – in-memory user store with hashed passwords

#### 4. Deliverables
- `api/` – full production-ready FastAPI application
- `run_api.py` / `start_api.bat` – convenient launch scripts
- `API_README.md` – complete API reference documentation

📖 **[Read Full API Documentation](API_README.md)**

---

## 🖥️ Week 4 Progress: React Frontend

### ✅ What We Accomplished

#### 1. Technology Stack
- **React 18** + **TypeScript** + **Vite** for fast builds
- **Tailwind CSS** for utility-first responsive styling
- Axios-based typed API client (`frontend/src/api/client.ts`)

#### 2. Pages Built
| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Landing page with feature highlights |
| Search | `/search` | Filter phones by brand, price, specs |
| Recommendations | `/recommend` | AI-powered personalised phone picks |
| Price Prediction | `/predict` | Estimate fair price from specs |
| Compare | `/compare` | Side-by-side phone comparison |
| Login / Register | `/login`, `/register` | JWT auth forms |
| User Profile | `/profile` | Account details and history |
| Admin | `/admin` | Dataset & model management panel |

#### 3. Context & State
- React Context API for global auth state
- Protected routes redirecting unauthenticated users

#### 4. Deliverables
- `frontend/` – complete Vite + React TypeScript app
- `frontend/nginx.conf` – Nginx config for production static serving
- `frontend/Dockerfile` – containerised frontend image

---

## 🐳 Week 5 Progress: Docker & Full-Stack Integration

### ✅ What We Accomplished

#### 1. Containerisation
- [x] **Backend Dockerfile** – Python 3.13 slim image, installs deps, runs Uvicorn
- [x] **Frontend Dockerfile** – multi-stage build (Node build → Nginx serve)
- [x] **`docker-compose.yml`** – single-command spin-up of both services

#### 2. Service Architecture
```
┌─────────────────────┐        ┌──────────────────────────┐
│  Frontend (Nginx)   │  HTTP  │  Backend (FastAPI/Uvicorn)│
│  Port 3000          │◄──────►│  Port 8000                │
└─────────────────────┘        └──────────────────────────┘
```

#### 3. Quick Start with Docker
```bash
# Build & start everything
docker-compose up --build

# Frontend → http://localhost:3000
# Backend API → http://localhost:8000
# Swagger docs → http://localhost:8000/docs
```

#### 4. Deliverables
- `Dockerfile` – backend image
- `frontend/Dockerfile` – frontend image
- `docker-compose.yml` – full-stack orchestration
- `QUICKSTART.md` – step-by-step startup guide

📖 **[Read Quick Start Guide](QUICKSTART.md)**

---

## 🔜 Upcoming Work

### Week 6: Testing & Optimization
- [ ] Integration tests with pytest + httpx
- [ ] Frontend unit tests (Vitest)
- [ ] Performance profiling and API response optimisation
- [ ] Security audit (rate limiting, input validation)

### Week 7: Deployment & Presentation
- [ ] Cloud deployment (Azure / AWS / Render)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Final documentation polish
- [ ] Project presentation

---

## 📊 Dataset Schema

| Column | Description | Example |
|--------|-------------|---------|
| `name` | Product name | iPhone 15 Pro Max 256GB |
| `brand` | Manufacturer | Apple, Samsung, Xiaomi |
| `ram_gb` | RAM in GB | 8 |
| `storage_gb` | Storage in GB | 256 |
| `battery_mah` | Battery capacity | 5000 |
| `screen_inches` | Screen size | 6.7 |
| `camera_rear_mp` | Rear camera | 48 |
| `camera_front_mp` | Front camera | 12 |
| `network` | Connectivity | 5G |
| `os` | Operating system | Android 14, iOS 17 |
| `processor_type` | CPU | Snapdragon 8 Gen 3 |
| `price` | Price in TND | 1499 |
| `source` | Store name | Tunisianet, Mytek, etc. |
| `url` | Product link | https://... |

---

## 🛠️ Installation & Running

### Option 1 – Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/iheblam/TuniTech-Advisor.git
cd TuniTech-Advisor

# Build & start all services
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

---

### Option 2 – Manual Setup

#### Prerequisites
- Python 3.13+
- Node.js 18+
- Chrome/Chromium (for Selenium scrapers)

#### Backend

```bash
# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start API server
python run_api.py
# → http://localhost:8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Running Scrapers

```bash
python scrapers/scrape_tunisianet_smartphones.py
python scrapers/scrape_spacenet_smartphones.py
python scrapers/scrape_mytek_smartphones.py
python scrapers/scrape_bestphone_smartphones.py

# Fill missing specs
python scrapers/fill_specs_from_existing.py
```

### Running EDA Notebook

```bash
jupyter notebook notebooks/01_EDA.ipynb
```

---

## 🔧 Technologies

### Backend
- **Python 3.13** – core language
- **FastAPI** – REST API framework with automatic OpenAPI docs
- **Uvicorn** – ASGI server
- **Scikit-learn** – ML pipelines, KNN, Random Forest
- **XGBoost** – Gradient boosting
- **MLflow** – Experiment tracking and model versioning
- **JWT (python-jose)** – Authentication tokens
- **Pandas / NumPy** – Data processing

### Frontend
- **React 18** – UI library
- **TypeScript** – Type-safe JavaScript
- **Vite** – Build tool and dev server
- **Tailwind CSS** – Utility-first CSS framework
- **Axios** – HTTP client

### Infrastructure
- **Docker** – Containerisation
- **Docker Compose** – Multi-service orchestration
- **Nginx** – Frontend static file serving
- **BeautifulSoup / Selenium** – Web scraping

---

## 👥 Team

| Name | Role | Contact |
|------|------|---------|
| **Iheb Lamouchi** | Developer | [GitHub](https://github.com/iheblam) |
| **Yassine Nemri** | Developer | |

---

## 📄 License

This project is developed as part of an academic course.

---

## 🙏 Acknowledgments

- Tunisianet, Mytek, SpaceNet, and BestPhone for their public product data
- Course instructors for guidance and feedback

---

<p align="center">
  <b>TuniTech Advisor</b> - Making smartphone shopping smarter in Tunisia 🇹🇳
</p>
