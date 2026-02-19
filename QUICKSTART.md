# TuniTech Advisor - API Quick Setup Guide

## 🎯 Quick Start (3 Steps)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Setup Environment
```powershell
# Copy environment template
copy .env.example .env
```

### Step 3: Run the API
```powershell
# Option A: Using the batch script (Windows)
.\start_api.bat

# Option B: Using Python directly
python run_api.py

# Option C: Using uvicorn
uvicorn api.main:app --reload
```

## 📍 Access Points

Once running, access:
- **API Root**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## ✅ Prerequisites Checklist

Before running the API, ensure:

- [ ] Python 3.13+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Dataset exists: `dataset/unified_smartphones_filled.csv`
- [ ] ML models trained: `mlruns/` directory with experiment data
- [ ] Port 8000 is available

## 🧪 Test the API

### Using curl:
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Get model info
curl http://localhost:8000/api/v1/health/model-info

# Get data statistics
curl http://localhost:8000/api/v1/health/data-stats
```

### Using Python:
```python
import requests

# Health check
r = requests.get("http://localhost:8000/api/v1/health/")
print(r.json())
```

### Using the Browser:
Simply open http://localhost:8000/docs in your browser for interactive testing!

## 📦 Project Structure
```
projet python sem 2/
├── api/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── config.py          # Configuration
│   ├── models/            # Pydantic schemas
│   ├── routers/           # API endpoints
│   └── services/          # Business logic
├── dataset/               # Smartphone data
├── mlruns/                # MLflow experiments
├── run_api.py             # Run script
├── start_api.bat          # Windows quick start
└── requirements.txt       # Dependencies
```

## 🔧 Troubleshooting

### Issue: "Module not found"
**Solution**: Install dependencies
```powershell
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution**: Use a different port
```powershell
uvicorn api.main:app --reload --port 8001
```

### Issue: "Data not loaded"
**Solution**: Check if dataset exists
```powershell
dir dataset\unified_smartphones_filled.csv
```

### Issue: "Model not loaded"
**Solution**: Ensure ML models are trained (Week 2 notebook)
```powershell
dir mlruns\
```

## 📖 Full Documentation

See [API_README.md](API_README.md) for complete documentation.

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

**Ready to build amazing smartphone recommendations! 🚀**
