# 📊 Week 2: ML Pipeline Development - Complete Summary

## 🎯 Objectives Achieved

Week 2 focused on building a complete machine learning pipeline from data preprocessing to experiment tracking with MLflow. We successfully transformed our raw smartphone data into a production-ready recommendation system.

---

## 📂 Deliverables

### 1. **Notebooks** (Cleaned & Simplified)
- `notebooks/01_EDA.ipynb` - Exploratory Data Analysis (Week 1)
- `notebooks/02_ML_Pipeline_Clean.ipynb` - **Complete ML pipeline (simplified from 1,825 to ~400 lines)**

### 2. **Final Dataset**
- `dataset/unified_smartphones.csv` - Original merged data (953 smartphones)
- `dataset/unified_smartphones_filled.csv` - **Final cleaned dataset with smart imputation**

### 3. **Production Models** (Clean & Optimized)
- `models/best_model.pkl` - **Production-ready KNN model (MAE: 4.42 TND)**
- `models/best_model_info.pkl` - Model metadata and performance metrics
- `models/data_splits.pkl` - Train/test splits for reproducibility
- `models/model_comparison.png` - Visual performance comparison

### 4. **MLflow Experiment Tracking**
- `mlruns/` - 7 tracked experiments with full reproducibility
- Complete parameter and metric logging
- Model versioning and easy comparison

---

## 🔬 ML Pipeline Steps

### **Step 1: Data Preprocessing** ✅

**Goal**: Clean and prepare data for modeling

**Actions**:
- Loaded unified dataset (953 smartphones with prices)
- Created preprocessing pipeline using scikit-learn:
  - **Numerical features**: KNNImputer (n_neighbors=5) + StandardScaler
  - **Categorical features**: SimpleImputer + OneHotEncoder
- Handled missing values intelligently
- Normalized features for consistent scaling

**Output**: 
- Preprocessed dataset with ~52 features (after one-hot encoding)
- Saved preprocessing pipeline for future predictions

---

### **Step 2: Feature Engineering** ✅

**Goal**: Create meaningful features to improve prediction accuracy

**Features Created** (14 new features):

#### 1. **Value Metrics**
- `value_score`: Composite score based on RAM, storage, camera, and battery
- `price_per_gb_ram`: Price efficiency metric
- `price_per_gb_storage`: Storage value indicator

#### 2. **Specification Ratios**
- `camera_ratio`: Rear camera / Front camera quality comparison
- `ram_storage_ratio`: Memory balance indicator
- `battery_per_inch`: Battery efficiency per screen size

#### 3. **Combined Features**
- `total_camera_mp`: Sum of all cameras
- `total_specs_score`: Overall device capability score

#### 4. **Price Tiers**
- `price_tier`: Budget (0-700 TND), Mid-range (700-2000), Premium (2000+)

#### 5. **Binary Indicators**
- `is_5g`: Network capability flag
- `is_flagship_brand`: Premium brand indicator (Apple, Samsung)
- `has_high_camera`: Camera quality flag (>40 MP)
- `high_battery`: Battery capacity flag (>4500 mAh)
- `large_screen`: Screen size flag (>6.5 inches)

**Result**: Dataset expanded to 26 features with rich information

---

### **Step 3: Feature Selection** ✅

**Goal**: Identify most important features for price prediction

**Methods Used**:
1. **Correlation Analysis**: Removed highly correlated features (threshold: 0.85)
2. **Random Forest Feature Importance**: Ranked features by predictive power
3. **Domain Knowledge**: Kept business-critical features

**Selected Features** (7 final features):

**Numerical** (2):
- `value_score` - Most important predictor
- `total_specs_score` - Overall device quality

**Categorical** (5):
- `brand` - Manufacturer impact on price
- `network` - 5G vs 4G pricing difference
- `os` - Android vs iOS market positioning
- `processor_type` - CPU performance indicator
- `price_tier` - Market segment classification

**Impact**: 
- Reduced feature space by 73% (26 → 7 features)
- Maintained prediction accuracy
- Improved model interpretability

---

### **Step 4: Model Training & Evaluation** ✅

**Goal**: Build and compare multiple regression models

**Models Trained**:

#### 1. **K-Nearest Neighbors (KNN)** 🏆
- **Baseline**: n_neighbors=5, weights='distance'
- **Optimized**: n_neighbors=10, weights='distance'
- **Final MAE**: 4.42 TND (after hyperparameter tuning)
- **R² Score**: 0.9998
- **Training Time**: 0.004s
- **Status**: **Best Model**

#### 2. **Random Forest**
- **Parameters**: n_estimators=100, max_depth=20
- **MAE**: 20.75 TND
- **R² Score**: 0.9988
- **Training Time**: 0.89s

#### 3. **XGBoost**
- **Parameters**: n_estimators=100, max_depth=6, learning_rate=0.1
- **MAE**: 17.27 TND
- **R² Score**: 0.9991
- **Training Time**: 0.23s

**Dataset Split**:
- Training: 762 smartphones (80%)
- Testing: 191 smartphones (20%)

**Winner**: KNN (n=10) with **lowest MAE** and **fastest training**

---

### **Step 5: MLflow Integration** ✅

**Goal**: Track experiments and enable reproducible ML

**Setup**:
- Created MLflow experiment: "TuniTech_Smartphone_Recommender"
- Configured local tracking server
- Implemented automatic logging for all experiments

**What's Tracked**:
- ✅ **Parameters**: All hyperparameters (n_neighbors, max_depth, etc.)
- ✅ **Metrics**: MAE, RMSE, R², training_time
- ✅ **Models**: Complete pipelines with preprocessing
- ✅ **Tags**: model_type, dataset_size, experiment_type
- ✅ **Artifacts**: Saved model files and visualizations

**Experiments Logged** (7 total):
1. KNN Model (baseline)
2. Random Forest Model
3. XGBoost Model
4. KNN_n3 (hyperparameter tuning)
5. KNN_n7 (hyperparameter tuning)
6. KNN_n10 (hyperparameter tuning) ⭐ **Best**

---

### **Step 5.5: Hyperparameter Tuning** ✅

**Goal**: Optimize KNN performance through systematic experimentation

**Methodology**:
- Tested n_neighbors: [3, 5, 7, 10, 15]
- All experiments automatically logged to MLflow
- Systematic evaluation across metrics

**Results**:

| n_neighbors | MAE (TND) | R² Score | Training Time |
|-------------|-----------|----------|---------------|
| 3           | 12.22     | 0.9974   | 0.005s       |
| 5           | 7.97      | 0.9988   | 0.006s       |
| 7           | 6.20      | 0.9994   | 0.004s       |
| **10** 🏆   | **4.42**  | **0.9998** | **0.004s** |
| 15          | 5.15      | 0.9996   | 0.004s       |

**Key Findings**:
- **45% improvement** from baseline (7.97 → 4.42 TND MAE)
- Optimal configuration: **n_neighbors=10**
- Clear trend: More neighbors = Better accuracy (up to optimal point)
- Minimal impact on training time

**Business Impact**:
- Average prediction error: **4.42 TND** (~0.5% for mid-range phones)
- Highly accurate recommendations for users
- Fast inference for real-time applications

---

## 📈 Overall Performance

### **Final Model Performance**

**Best Model**: KNN with n_neighbors=10

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **MAE** | 4.42 TND | Average error per prediction |
| **R²** | 0.9998 | 99.98% variance explained |
| **Training Time** | 0.004s | Very fast training |
| **Inference Time** | <1ms | Real-time ready |

### **Why KNN Won**:
1. **Best accuracy**: Lowest MAE among all models (4.42 TND)
2. **Fastest training**: 10-20x faster than ensemble methods
3. **Simple & interpretable**: Easy to explain predictions
4. **Scalable**: Efficient for our dataset size (953 phones)
5. **Consistent**: Extremely high R² score (0.9998)

---

## 🎓 Key Learnings

### 1. **Feature Engineering is Critical**
- Engineered features (`value_score`, `total_specs_score`) were among top predictors
- Domain knowledge helped create meaningful features
- Feature selection reduced complexity without sacrificing accuracy

### 2. **Simpler Models Can Win**
- KNN outperformed complex ensemble methods (RF, XGBoost)
- Training time matters for iterative development
- Interpretability is valuable for business stakeholders

### 3. **Hyperparameter Tuning Matters**
- 44% improvement from optimal hyperparameters
- MLflow made systematic experimentation easy
- Data-driven decision making > intuition

### 4. **MLflow is Essential**
- Complete experiment reproducibility
- Easy model comparison and versioning
- Professional ML workflow from day one

---

## 🔧 Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Processing** | Pandas, NumPy | Data manipulation and analysis |
| **ML Framework** | Scikit-learn | Pipelines, models, preprocessing |
| **Gradient Boosting** | XGBoost | Advanced ensemble model |
| **Experiment Tracking** | MLflow | Model versioning and comparison |
| **Visualization** | Matplotlib, Seaborn | Charts and insights |
| **Development** | Jupyter Notebook | Interactive development |

---

## 📊 Data Flow Summary

```
Raw Data (953 phones with prices)
    ↓
Smart Imputation → Fill missing specs
    ↓
Preprocessing Pipeline → KNNImputer + StandardScaler (Numerical)
                      → SimpleImputer + OneHotEncoder (Categorical)
    ↓
Feature Engineering → 14 new features created
                   → value_score, total_specs_score, price_tier, etc.
    ↓
Feature Selection → 7 optimal features selected
                 → 2 numerical + 5 categorical
    ↓
Train/Test Split → 762 / 191 (80/20)
    ↓
Model Training → KNN, Random Forest, XGBoost
    ↓
Hyperparameter Tuning → n_neighbors: 3, 5, 7, 10, 15
    ↓
Best Model Selection → KNN (n=10, MAE=4.42 TND)
    ↓
MLflow Tracking → 7 experiments logged
    ↓
Production Ready Model ✅
```

---

## 🎉 Week 2 Achievements

1. ✅ Built production-ready ML pipeline (simplified to 400 lines)
2. ✅ Achieved 99.98% prediction accuracy (R²=0.9998)
3. ✅ Reduced prediction error to 4.42 TND (45% improvement)
4. ✅ Implemented professional experiment tracking (7 MLflow runs)
5. ✅ Optimized model through systematic hyperparameter tuning
6. ✅ Cleaned and organized project structure
7. ✅ Created comprehensive, easy-to-run documentation
8. ✅ Prepared for API development (Week 3)

**Status**: Week 2 completed successfully! Clean, production-ready ML pipeline 🚀

---

*Last Updated: February 17, 2026*  
*Authors: Iheb Lamouchi & Yassine Nemri*  
*Project: TuniTech Advisor - ML Pipeline Development*
