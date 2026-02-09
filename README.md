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
| 2 | Data Preprocessing & Feature Engineering | 🔄 In Progress | Cleaning, normalization, feature creation |
| 3 | Model Development with MLflow | ⏳ Pending | Recommendation algorithm, experiment tracking |
| 4 | FastAPI Backend | ⏳ Pending | REST API endpoints for recommendations |
| 5 | React Frontend | ⏳ Pending | User interface with filtering and results display |
| 6 | Docker & Integration | ⏳ Pending | Containerization and full stack integration |
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
code/
├── scrape_tunisianet_smartphones.py   # Tunisianet scraper
├── scrape_mytek_smartphones.py        # Mytek scraper (Selenium)
├── scrape_spacenet_smartphones.py     # SpaceNet scraper
├── scrape_bestphone_smartphones.py    # BestPhone scraper
├── fill_missing_specs.py              # GSMArena-based filling
├── fill_specs_from_existing.py        # Cross-source matching
├── fill_bestphone_specs.py            # BestPhone enrichment
├── fill_bestphone_enhanced.py         # Improved fuzzy matching
├── fill_known_specs.py                # Known specs database
└── eda_analysis.py                    # Comprehensive EDA script

dataset/
├── tunisianet_smartphones.csv         # Raw data
├── tunisianet_smartphones_filled.csv  # Enriched data
├── mytek_smartphones.csv
├── mytek_smartphones_filled.csv
├── spacenet_smartphones.csv
├── spacenet_smartphones_filled.csv
├── bestphone_smartphones.csv
├── bestphone_smartphones_filled.csv
└── unified_smartphones.csv            # Combined dataset

EDA_REPORT.md                          # EDA findings summary
```

---

## 🔜 Upcoming Work

### Week 2: Data Preprocessing & Feature Engineering
- [ ] Standardize all spec formats (RAM, storage units)
- [ ] Handle outliers and anomalies
- [ ] Create derived features (value score, price per spec)
- [ ] Encode categorical variables for ML
- [ ] Final cleaned dataset ready for modeling

### Week 3: Model Development with MLflow
- [ ] Content-based recommendation algorithm
- [ ] Similarity scoring (cosine, euclidean)
- [ ] MLflow experiment tracking setup
- [ ] Model versioning and comparison
- [ ] Hyperparameter tuning

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

### Week 6: Docker & Integration
- [ ] Dockerfile for backend
- [ ] Dockerfile for frontend
- [ ] Docker Compose orchestration
- [ ] Environment configuration

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
python code/scrape_tunisianet_smartphones.py
python code/scrape_spacenet_smartphones.py
python code/scrape_mytek_smartphones.py
python code/scrape_bestphone_smartphones.py

# Fill missing specs
python code/fill_specs_from_existing.py

# Run EDA
python code/eda_analysis.py
```

---

## 🔧 Technologies

### Current (Week 1)
- **Python 3.13** - Core language
- **BeautifulSoup4** - HTML parsing
- **Selenium** - Dynamic page scraping
- **Pandas** - Data manipulation
- **Requests** - HTTP requests

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
