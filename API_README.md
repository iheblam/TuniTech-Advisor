# 🚀 FastAPI Backend - TuniTech Advisor

## 📋 Overview

This is the FastAPI backend for the TuniTech Advisor smartphone recommendation system. It provides RESTful API endpoints for:

- **Price Predictions**: Predict smartphone prices based on specifications using trained ML models
- **Smart Recommendations**: Get personalized smartphone recommendations based on budget and requirements
- **Data Queries**: Search and compare smartphones from multiple Tunisian e-commerce stores

## 🏗️ Project Structure

```
api/
├── __init__.py           # Package initialization
├── main.py              # FastAPI application entry point
├── config.py            # Application configuration
├── models/              # Pydantic models
│   ├── __init__.py
│   └── schemas.py       # Request/Response schemas
├── routers/             # API endpoints
│   ├── __init__.py
│   ├── health.py        # Health check endpoints
│   ├── predictions.py   # Price prediction endpoints
│   └── recommendations.py  # Recommendation endpoints
└── services/            # Business logic
    ├── __init__.py
    ├── ml_service.py    # ML model operations
    └── data_service.py  # Data operations
```

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to customize settings if needed.

### 3. Ensure Data and Models are Ready

Make sure you have:
- ✅ Smartphone data in `dataset/unified_smartphones_filled.csv`
- ✅ Trained ML models in `mlruns/` directory (from Week 2)

## 🚀 Running the API

### Option 1: Using the run script

```bash
python run_api.py
```

### Option 2: Using uvicorn directly

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using Python module

```bash
python -m api.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Endpoints

### Health & Status

- `GET /api/v1/health/` - Health check
- `GET /api/v1/health/model-info` - ML model information
- `GET /api/v1/health/data-stats` - Dataset statistics
- `GET /api/v1/health/brands` - List of all brands

### Price Predictions

- `POST /api/v1/predict/price` - Predict price for a smartphone
- `POST /api/v1/predict/batch-price` - Predict prices for multiple smartphones

### Recommendations

- `POST /api/v1/recommendations/` - Get smartphone recommendations
- `GET /api/v1/recommendations/search` - Search smartphones
- `GET /api/v1/recommendations/compare` - Compare multiple smartphones

## 💡 API Usage Examples

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

### 2. Predict Smartphone Price

```bash
curl -X POST http://localhost:8000/api/v1/predict/price \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "ram": 8,
      "storage": 128,
      "battery": 5000,
      "screen_size": 6.5,
      "main_camera": 64,
      "front_camera": 16,
      "processor_cores": 8,
      "is_5g": true,
      "has_nfc": true
    },
    "brand": "Samsung"
  }'
```

### 3. Get Recommendations

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/ \
  -H "Content-Type: application/json" \
  -d '{
    "budget_min": 800,
    "budget_max": 1500,
    "min_ram": 6,
    "min_storage": 128,
    "min_battery": 4000,
    "brand": "Samsung",
    "requires_5g": true,
    "limit": 10
  }'
```

### 4. Search Smartphones

```bash
curl "http://localhost:8000/api/v1/recommendations/search?query=Samsung&min_price=500&max_price=2000&limit=10"
```

## 🔍 Interactive Documentation

Visit http://localhost:8000/docs to access the interactive Swagger UI where you can:
- 📝 View all endpoints
- 🧪 Test API calls directly
- 📄 See request/response schemas
- 💾 Download OpenAPI specification

## 🛠️ Development

### Running in Debug Mode

Set `DEBUG=True` in your `.env` file to enable:
- Auto-reload on code changes
- Detailed error messages
- CORS for local development

### Testing the API

You can test endpoints using:
- **Swagger UI**: http://localhost:8000/docs
- **curl**: Command line HTTP client
- **Postman**: API testing tool
- **Python requests library**:

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health/")
print(response.json())

# Get recommendations
response = requests.post(
    "http://localhost:8000/api/v1/recommendations/",
    json={
        "budget_min": 800,
        "budget_max": 1500,
        "min_ram": 6,
        "limit": 5
    }
)
print(response.json())
```

## 📊 Configuration

Key settings in `api/config.py`:

- `API_PREFIX`: API route prefix (default: `/api/v1`)
- `MLFLOW_TRACKING_URI`: Path to MLflow runs
- `DATA_PATH`: Path to smartphone data
- `CORS_ORIGINS`: Allowed CORS origins

## 🔒 Security Notes

⚠️ This is a development setup. For production:

- [ ] Add authentication (JWT tokens)
- [ ] Enable HTTPS
- [ ] Configure proper CORS origins
- [ ] Add rate limiting
- [ ] Set up logging and monitoring
- [ ] Use environment variables for sensitive data

## 🐛 Troubleshooting

### Model not loading
- Ensure MLflow runs exist in `mlruns/` directory
- Check that models were trained in Week 2
- Verify `MLFLOW_TRACKING_URI` setting

### Data not loading
- Verify `unified_smartphones_filled.csv` exists in `dataset/`
- Check file permissions
- Ensure CSV is properly formatted

### Port already in use
- Change the port: `uvicorn api.main:app --port 8001`
- Or kill the process using port 8000

## 📚 Next Steps

- Week 4: Build React frontend to consume this API
- Week 5: Dockerize the application
- Week 6: Add tests and optimize performance
- Week 7: Deploy to production

## 📞 Support

For issues or questions:
- Check the main project README
- Review API documentation at `/docs`
- Examine logs for error details

---

**Happy Coding! 🚀**
