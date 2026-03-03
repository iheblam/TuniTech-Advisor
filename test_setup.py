"""
Test script to verify FastAPI setup
Run this after installing dependencies to check if everything is configured correctly
"""

import sys
from pathlib import Path


def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pydantic_settings',
        'pandas',
        'numpy',
        'sklearn',
        'mlflow'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT FOUND")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def check_data():
    """Check if data files exist"""
    print("\n🔍 Checking data files...")
    
    data_file = Path("dataset/unified_smartphones_filled.csv")
    if data_file.exists():
        print(f"  ✓ {data_file}")
        return True
    else:
        print(f"  ✗ {data_file} - NOT FOUND")
        print("   Please ensure data is scraped and preprocessed.")
        return False


def check_models():
    """Check if ML models exist"""
    print("\n🔍 Checking ML models...")
    
    mlruns_dir = Path("mlruns")
    if mlruns_dir.exists():
        # Count experiments
        experiments = [d for d in mlruns_dir.iterdir() if d.is_dir() and d.name != 'models']
        print(f"  ✓ MLflow directory found with {len(experiments)} experiment(s)")
        return True
    else:
        print(f"  ✗ mlruns/ directory - NOT FOUND")
        print("   Please train models first (Week 2 notebook).")
        return False


def check_api_structure():
    """Check if API structure is correct"""
    print("\n🔍 Checking API structure...")
    
    required_files = [
        "api/__init__.py",
        "api/main.py",
        "api/config.py",
        "api/models/__init__.py",
        "api/models/schemas.py",
        "api/routers/__init__.py",
        "api/routers/health.py",
        "api/routers/predictions.py",
        "api/routers/recommendations.py",
        "api/services/__init__.py",
        "api/services/ml_service.py",
        "api/services/data_service.py",
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(file)
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✅ API structure is complete!")
        return True
    else:
        print("\n❌ Some API files are missing!")
        return False


def test_import():
    """Try importing the API module"""
    print("\n🔍 Testing API import...")
    
    try:
        from api.main import app
        from api.config import settings
        print(f"  ✓ API module imported successfully")
        print(f"  ✓ App name: {settings.app_name}")
        print(f"  ✓ App version: {settings.app_version}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to import API: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("TuniTech Advisor - FastAPI Setup Verification")
    print("=" * 60)
    
    results = {
        "Dependencies": check_dependencies(),
        "Data Files": check_data(),
        "ML Models": check_models(),
        "API Structure": check_api_structure(),
        "API Import": test_import()
    }
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check:.<30} {status}")
    
    all_passed = all(results.values())
    
    print("=" * 60)
    if all_passed:
        print("🎉 All checks passed! You're ready to run the API.")
        print("\nNext steps:")
        print("  1. Run: python run_api.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Start building amazing recommendations!")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Missing dependencies: pip install -r requirements.txt")
        print("  • Missing data: Run scrapers and Week 1 notebook")
        print("  • Missing models: Run Week 2 ML pipeline notebook")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
