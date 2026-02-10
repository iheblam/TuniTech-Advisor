# 📱 TuniTech Advisor - Smart Phone Recommendation System

> **An AI-powered smartphone recommendation system for Tunisian e-commerce**

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB.svg)](https://reactjs.org/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-orange.svg)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)

---

## 🎯 Project Overview

**TuniTech Advisor** is an intelligent smartphone recommendation system designed specifically for the Tunisian market. It aggregates data from multiple local e-commerce platforms, analyzes specifications, and provides personalized phone recommendations based on user preferences - including price comparisons across different stores.

### 🌟 Key Features

- **Multi-source Data Aggregation**: Scrapes smartphones from Tunisianet, Mytek, SpaceNet, and BestPhone
- **Smart Recommendations**: AI-powered matching based on user requirements (budget, RAM, storage, camera, etc.)
- **Price Comparison**: Shows same phone across different stores with price differences
- **Store Availability**: Indicates which stores have the phone in stock
- **Real-time Search**: Fast filtering by brand, price range, and specifications

---

## 🗓️ Project Timeline (7 Weeks)

| Week | Phase | Status | Description |
|------|-------|--------|-------------|
| 1 | Setup, Scraping & EDA | ✅ Complete | Project structure, web scrapers, data exploration |
| 2 | ML Pipeline & Experiment Tracking | ✅ Complete | Preprocessing, feature engineering, model training, MLflow |
| 3 | FastAPI Backend | 🔄 In Progress | REST API endpoints for recommendations |
| 4 | React Frontend | ⏳ Pending | User interface with filtering and results display |
| 5 | Docker & Integration | ⏳ Pending | Containerization and full stack integration |
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
| XGBoost | ow experiments** tracked with full reproducibility
- ✅ Production-ready model pipeline saved

#### 4. Deliverables
- `notebooks/02_ML_Pipeline.ipynb` - Complete ML pipeline
- `models/knn_model.pkl` - Best performing model
- `models/preprocessor_pipeline.pkl` - Feature preprocessing pipeline
- `models/mlflow_model_comparison.png` - Performance visualizations
- `WEEK2_SUMMARY.md` - Comprehensive technical documentation

📖 **[Read Full Week 2 Documentation](WEEK2_SUMMARY.md)**

---

## 🔜 Upcoming Work

### Week 3: FastAPI Backend Development
- [ ] Design REST API architecture
- [ ] Implement price prediction endpoint
- [ ] Create phone recommendation endpoint (similar items)
- [ ] Add search and filter endpoints
- [ ] API documentation with Swagger/OpenAPI
- [ ] Load trained model for real-time inference

### Week 4: FastAPI Backend
- [ ] RESTful API design
- [ ] Recommendation endpoints
- [ ] Search and filter endpoints
- [ ] Store/price comparison endpoints
- [ ] API documentation (Swagger)

### Week 5: React Frontend
- [ ] User preference input form
- [ ] Results display with cards
- [ ] Price comparison view
- [ ] Responsive design

### Week 5: Docker & Integration
- [ ] Dockerfile for backend
- [ ] Dockerfile for frontend
- [ ] Docker Compose orchestration
- [ ] Environment configuration
- [ ] End-to-end testing

### Week 6: Testing & Optimization
- [ ] Performance testing
- [ ] Bug fixes and refinement
- [ ] Security audit
- [ ] Documentation completion

### Week 7: Deployment & Presentation
- [ ] Cloud deployment (Azure/AWS/Heroku)
- [ ] Performance optimization
- [ ] Final documentation
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

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- Chrome/Chromium (for Selenium)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/iheblam/TuniTech-Advisor.git
cd TuniTech-Advisor

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Scrapers

```bash
# Scrape all sources
python scrapers/scrape_tunisianet_smartphones.py
python scrapers/scrape_spacenet_smartphones.py
python scrapers/scrape_mytek_smartphones.py
python scrapers/scrape_bestphone_smartphones.py

# Fill missing specs
python scrapers/fill_specs_from_existing.py
```

### Running EDA Notebook

```bash
# Start Jupyter
jupyter notebook notebooks/01_EDA.ipynb
```

---

## 🔧 Technologies

### Week 2 (Current)
- **Scikit-learn** - ML pipelines, KNN, Random Forest
- **XGBoost** - Gradient boosting
- **MLflow** - Experiment tracking and model versioning
- **Matplotlib/Seaborn** - Visualizations

### Upcoming
- **FastAPI** - Backend API (Week 3)
- **React + Tailwind** - Frontend (Week 4)
- **Docker** - Containerization (Week 5)
- **pytest** - Testing framework

### Upcoming
- **Scikit-learn** - ML algorithms (Week 2-3)
- **MLflow** - Experiment tracking (Week 3)
- **FastAPI** - Backend API (Week 4)
- **React + Tailwind** - Frontend (Week 5)
- **Docker** - Containerization (Week 6)
- **Azure/AWS** - Cloud deployment (Week 7)

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
