"""
Smart Missing Value Filler for Smartphone Dataset
Uses multiple strategies:
1. Fill from same model variants in our dataset
2. Fill from brand averages
3. Use device specs API (fonoapi alternative)
"""

import pandas as pd
import numpy as np
import requests
import time
import re
from collections import defaultdict

# Known specs for popular phone series (manually curated)
PHONE_SPECS_DB = {
    # Samsung Galaxy S series
    'galaxy s24 ultra': {'screen_inches': 6.8, 'camera_rear_mp': 200, 'camera_front_mp': 12, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'galaxy s24+': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 12, 'battery_mah': 4900, 'os': 'Android 14', 'network': '5G'},
    'galaxy s24': {'screen_inches': 6.2, 'camera_rear_mp': 50, 'camera_front_mp': 12, 'battery_mah': 4000, 'os': 'Android 14', 'network': '5G'},
    'galaxy s23 ultra': {'screen_inches': 6.8, 'camera_rear_mp': 200, 'camera_front_mp': 12, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'galaxy s23+': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 12, 'battery_mah': 4700, 'os': 'Android 13', 'network': '5G'},
    'galaxy s23': {'screen_inches': 6.1, 'camera_rear_mp': 50, 'camera_front_mp': 12, 'battery_mah': 3900, 'os': 'Android 13', 'network': '5G'},
    'galaxy s22 ultra': {'screen_inches': 6.8, 'camera_rear_mp': 108, 'camera_front_mp': 40, 'battery_mah': 5000, 'os': 'Android 12', 'network': '5G'},
    'galaxy s22+': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 10, 'battery_mah': 4500, 'os': 'Android 12', 'network': '5G'},
    'galaxy s22': {'screen_inches': 6.1, 'camera_rear_mp': 50, 'camera_front_mp': 10, 'battery_mah': 3700, 'os': 'Android 12', 'network': '5G'},
    'galaxy s21 ultra': {'screen_inches': 6.8, 'camera_rear_mp': 108, 'camera_front_mp': 40, 'battery_mah': 5000, 'os': 'Android 11', 'network': '5G'},
    'galaxy s21+': {'screen_inches': 6.7, 'camera_rear_mp': 64, 'camera_front_mp': 10, 'battery_mah': 4800, 'os': 'Android 11', 'network': '5G'},
    'galaxy s21': {'screen_inches': 6.2, 'camera_rear_mp': 64, 'camera_front_mp': 10, 'battery_mah': 4000, 'os': 'Android 11', 'network': '5G'},
    'galaxy s21 fe': {'screen_inches': 6.4, 'camera_rear_mp': 12, 'camera_front_mp': 32, 'battery_mah': 4500, 'os': 'Android 12', 'network': '5G'},
    
    # Samsung Galaxy A series
    'galaxy a55': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'galaxy a54': {'screen_inches': 6.4, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'galaxy a53': {'screen_inches': 6.5, 'camera_rear_mp': 64, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 12', 'network': '5G'},
    'galaxy a52': {'screen_inches': 6.5, 'camera_rear_mp': 64, 'camera_front_mp': 32, 'battery_mah': 4500, 'os': 'Android 11', 'network': '4G'},
    'galaxy a35': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'galaxy a34': {'screen_inches': 6.6, 'camera_rear_mp': 48, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'galaxy a33': {'screen_inches': 6.4, 'camera_rear_mp': 48, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 12', 'network': '5G'},
    'galaxy a25': {'screen_inches': 6.5, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'galaxy a24': {'screen_inches': 6.5, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'galaxy a23': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    'galaxy a15': {'screen_inches': 6.5, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'galaxy a14': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'galaxy a13': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    'galaxy a05s': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'galaxy a05': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'galaxy a04': {'screen_inches': 6.5, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    'galaxy a04s': {'screen_inches': 6.5, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    
    # Samsung Galaxy M series
    'galaxy m55': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'galaxy m54': {'screen_inches': 6.7, 'camera_rear_mp': 108, 'camera_front_mp': 32, 'battery_mah': 6000, 'os': 'Android 13', 'network': '5G'},
    'galaxy m34': {'screen_inches': 6.5, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 6000, 'os': 'Android 13', 'network': '5G'},
    'galaxy m14': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 6000, 'os': 'Android 13', 'network': '5G'},
    
    # Samsung Galaxy Z series
    'galaxy z fold5': {'screen_inches': 7.6, 'camera_rear_mp': 50, 'camera_front_mp': 10, 'battery_mah': 4400, 'os': 'Android 13', 'network': '5G'},
    'galaxy z fold4': {'screen_inches': 7.6, 'camera_rear_mp': 50, 'camera_front_mp': 10, 'battery_mah': 4400, 'os': 'Android 12', 'network': '5G'},
    'galaxy z fold3': {'screen_inches': 7.6, 'camera_rear_mp': 12, 'camera_front_mp': 10, 'battery_mah': 4400, 'os': 'Android 11', 'network': '5G'},
    'galaxy z flip5': {'screen_inches': 6.7, 'camera_rear_mp': 12, 'camera_front_mp': 10, 'battery_mah': 3700, 'os': 'Android 13', 'network': '5G'},
    'galaxy z flip4': {'screen_inches': 6.7, 'camera_rear_mp': 12, 'camera_front_mp': 10, 'battery_mah': 3700, 'os': 'Android 12', 'network': '5G'},
    
    # Apple iPhone
    'iphone 15 pro max': {'screen_inches': 6.7, 'camera_rear_mp': 48, 'camera_front_mp': 12, 'battery_mah': 4441, 'os': 'iOS 17', 'network': '5G'},
    'iphone 15 pro': {'screen_inches': 6.1, 'camera_rear_mp': 48, 'camera_front_mp': 12, 'battery_mah': 3274, 'os': 'iOS 17', 'network': '5G'},
    'iphone 15 plus': {'screen_inches': 6.7, 'camera_rear_mp': 48, 'camera_front_mp': 12, 'battery_mah': 4383, 'os': 'iOS 17', 'network': '5G'},
    'iphone 15': {'screen_inches': 6.1, 'camera_rear_mp': 48, 'camera_front_mp': 12, 'battery_mah': 3349, 'os': 'iOS 17', 'network': '5G'},
    'iphone 14 pro max': {'screen_inches': 6.7, 'camera_rear_mp': 48, 'camera_front_mp': 12, 'battery_mah': 4323, 'os': 'iOS 16', 'network': '5G'},
    'iphone 14 pro': {'screen_inches': 6.1, 'camera_rear_mp': 48, 'camera_front_mp': 12, 'battery_mah': 3200, 'os': 'iOS 16', 'network': '5G'},
    'iphone 14 plus': {'screen_inches': 6.7, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 4325, 'os': 'iOS 16', 'network': '5G'},
    'iphone 14': {'screen_inches': 6.1, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 3279, 'os': 'iOS 16', 'network': '5G'},
    'iphone 13 pro max': {'screen_inches': 6.7, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 4352, 'os': 'iOS 15', 'network': '5G'},
    'iphone 13 pro': {'screen_inches': 6.1, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 3095, 'os': 'iOS 15', 'network': '5G'},
    'iphone 13': {'screen_inches': 6.1, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 3240, 'os': 'iOS 15', 'network': '5G'},
    'iphone 13 mini': {'screen_inches': 5.4, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 2438, 'os': 'iOS 15', 'network': '5G'},
    'iphone 12 pro max': {'screen_inches': 6.7, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 3687, 'os': 'iOS 14', 'network': '5G'},
    'iphone 12 pro': {'screen_inches': 6.1, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 2815, 'os': 'iOS 14', 'network': '5G'},
    'iphone 12': {'screen_inches': 6.1, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 2815, 'os': 'iOS 14', 'network': '5G'},
    'iphone 12 mini': {'screen_inches': 5.4, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 2227, 'os': 'iOS 14', 'network': '5G'},
    'iphone 11 pro max': {'screen_inches': 6.5, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 3969, 'os': 'iOS 13', 'network': '4G'},
    'iphone 11 pro': {'screen_inches': 5.8, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 3046, 'os': 'iOS 13', 'network': '4G'},
    'iphone 11': {'screen_inches': 6.1, 'camera_rear_mp': 12, 'camera_front_mp': 12, 'battery_mah': 3110, 'os': 'iOS 13', 'network': '4G'},
    'iphone se 2022': {'screen_inches': 4.7, 'camera_rear_mp': 12, 'camera_front_mp': 7, 'battery_mah': 2018, 'os': 'iOS 15', 'network': '5G'},
    'iphone se 2020': {'screen_inches': 4.7, 'camera_rear_mp': 12, 'camera_front_mp': 7, 'battery_mah': 1821, 'os': 'iOS 13', 'network': '4G'},
    
    # Xiaomi series
    'xiaomi 14 ultra': {'screen_inches': 6.73, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'xiaomi 14': {'screen_inches': 6.36, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4610, 'os': 'Android 14', 'network': '5G'},
    'xiaomi 13 ultra': {'screen_inches': 6.73, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'xiaomi 13 pro': {'screen_inches': 6.73, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4820, 'os': 'Android 13', 'network': '5G'},
    'xiaomi 13': {'screen_inches': 6.36, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4500, 'os': 'Android 13', 'network': '5G'},
    'xiaomi 13 lite': {'screen_inches': 6.55, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4500, 'os': 'Android 12', 'network': '5G'},
    'xiaomi 12 pro': {'screen_inches': 6.73, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4600, 'os': 'Android 12', 'network': '5G'},
    'xiaomi 12': {'screen_inches': 6.28, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4500, 'os': 'Android 12', 'network': '5G'},
    'xiaomi 11t pro': {'screen_inches': 6.67, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 11', 'network': '5G'},
    'xiaomi 11t': {'screen_inches': 6.67, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 11', 'network': '5G'},
    'xiaomi 11 lite': {'screen_inches': 6.55, 'camera_rear_mp': 64, 'camera_front_mp': 16, 'battery_mah': 4250, 'os': 'Android 11', 'network': '5G'},
    
    # Redmi series
    'redmi note 13 pro+': {'screen_inches': 6.67, 'camera_rear_mp': 200, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'redmi note 13 pro': {'screen_inches': 6.67, 'camera_rear_mp': 200, 'camera_front_mp': 16, 'battery_mah': 5100, 'os': 'Android 13', 'network': '4G'},
    'redmi note 13': {'screen_inches': 6.67, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'redmi note 12 pro+': {'screen_inches': 6.67, 'camera_rear_mp': 200, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 12', 'network': '5G'},
    'redmi note 12 pro': {'screen_inches': 6.67, 'camera_rear_mp': 50, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 12', 'network': '5G'},
    'redmi note 12': {'screen_inches': 6.67, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    'redmi note 11 pro+': {'screen_inches': 6.67, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 4500, 'os': 'Android 11', 'network': '5G'},
    'redmi note 11 pro': {'screen_inches': 6.67, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 11', 'network': '4G'},
    'redmi note 11': {'screen_inches': 6.43, 'camera_rear_mp': 50, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 11', 'network': '4G'},
    'redmi 13c': {'screen_inches': 6.74, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'redmi 12': {'screen_inches': 6.79, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'redmi a3': {'screen_inches': 6.71, 'camera_rear_mp': 8, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 14', 'network': '4G'},
    'redmi a2': {'screen_inches': 6.52, 'camera_rear_mp': 8, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    
    # POCO series
    'poco f5 pro': {'screen_inches': 6.67, 'camera_rear_mp': 64, 'camera_front_mp': 16, 'battery_mah': 5160, 'os': 'Android 13', 'network': '5G'},
    'poco f5': {'screen_inches': 6.67, 'camera_rear_mp': 64, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'poco x6 pro': {'screen_inches': 6.67, 'camera_rear_mp': 64, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'poco x6': {'screen_inches': 6.67, 'camera_rear_mp': 64, 'camera_front_mp': 16, 'battery_mah': 5100, 'os': 'Android 14', 'network': '5G'},
    'poco x5 pro': {'screen_inches': 6.67, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 12', 'network': '5G'},
    'poco x5': {'screen_inches': 6.67, 'camera_rear_mp': 48, 'camera_front_mp': 13, 'battery_mah': 5000, 'os': 'Android 12', 'network': '5G'},
    'poco m6 pro': {'screen_inches': 6.67, 'camera_rear_mp': 64, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'poco m5': {'screen_inches': 6.58, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    'poco c65': {'screen_inches': 6.74, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    
    # Honor series
    'honor magic6 pro': {'screen_inches': 6.8, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 5600, 'os': 'Android 14', 'network': '5G'},
    'honor magic5 pro': {'screen_inches': 6.81, 'camera_rear_mp': 50, 'camera_front_mp': 12, 'battery_mah': 5100, 'os': 'Android 13', 'network': '5G'},
    'honor 90': {'screen_inches': 6.7, 'camera_rear_mp': 200, 'camera_front_mp': 50, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'honor 90 lite': {'screen_inches': 6.7, 'camera_rear_mp': 100, 'camera_front_mp': 16, 'battery_mah': 4500, 'os': 'Android 13', 'network': '4G'},
    'honor x9b': {'screen_inches': 6.78, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 5800, 'os': 'Android 13', 'network': '5G'},
    'honor x8b': {'screen_inches': 6.7, 'camera_rear_mp': 108, 'camera_front_mp': 50, 'battery_mah': 4500, 'os': 'Android 13', 'network': '4G'},
    'honor x7b': {'screen_inches': 6.8, 'camera_rear_mp': 108, 'camera_front_mp': 8, 'battery_mah': 6000, 'os': 'Android 13', 'network': '4G'},
    'honor x6b': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5200, 'os': 'Android 14', 'network': '4G'},
    'honor x6a': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5200, 'os': 'Android 13', 'network': '4G'},
    'honor x5 plus': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5200, 'os': 'Android 13', 'network': '4G'},
    
    # OPPO series
    'oppo find x7 ultra': {'screen_inches': 6.82, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'oppo find x6 pro': {'screen_inches': 6.82, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'oppo reno11 pro': {'screen_inches': 6.74, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4600, 'os': 'Android 14', 'network': '5G'},
    'oppo reno11': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'oppo reno10 pro+': {'screen_inches': 6.74, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4700, 'os': 'Android 13', 'network': '5G'},
    'oppo reno10 pro': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 4600, 'os': 'Android 13', 'network': '5G'},
    'oppo reno10': {'screen_inches': 6.7, 'camera_rear_mp': 64, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'oppo a79': {'screen_inches': 6.72, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'oppo a78': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'oppo a58': {'screen_inches': 6.72, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'oppo a38': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'oppo a18': {'screen_inches': 6.56, 'camera_rear_mp': 8, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    
    # Vivo series
    'vivo x100 pro': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5400, 'os': 'Android 14', 'network': '5G'},
    'vivo x100': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'vivo v30 pro': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'vivo v30': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'vivo v29': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 4600, 'os': 'Android 13', 'network': '5G'},
    'vivo v27': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 4600, 'os': 'Android 13', 'network': '5G'},
    'vivo y100': {'screen_inches': 6.67, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'vivo y36': {'screen_inches': 6.64, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'vivo y27': {'screen_inches': 6.64, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'vivo y17s': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    
    # Realme series
    'realme gt5 pro': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5400, 'os': 'Android 14', 'network': '5G'},
    'realme 12 pro+': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'realme 12 pro': {'screen_inches': 6.7, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'realme 11 pro+': {'screen_inches': 6.7, 'camera_rear_mp': 200, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'realme 11 pro': {'screen_inches': 6.7, 'camera_rear_mp': 100, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'realme 11': {'screen_inches': 6.43, 'camera_rear_mp': 108, 'camera_front_mp': 16, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'realme c67': {'screen_inches': 6.72, 'camera_rear_mp': 108, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'realme c55': {'screen_inches': 6.72, 'camera_rear_mp': 64, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'realme c53': {'screen_inches': 6.74, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    
    # Infinix series  
    'infinix note 40 pro': {'screen_inches': 6.78, 'camera_rear_mp': 108, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'infinix note 40': {'screen_inches': 6.78, 'camera_rear_mp': 108, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 14', 'network': '4G'},
    'infinix note 30 pro': {'screen_inches': 6.67, 'camera_rear_mp': 108, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    'infinix note 30': {'screen_inches': 6.78, 'camera_rear_mp': 64, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'infinix hot 40 pro': {'screen_inches': 6.78, 'camera_rear_mp': 108, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'infinix hot 40': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'infinix hot 30 play': {'screen_inches': 6.82, 'camera_rear_mp': 16, 'camera_front_mp': 8, 'battery_mah': 6000, 'os': 'Android 13', 'network': '4G'},
    'infinix hot 30': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    'infinix smart 8': {'screen_inches': 6.6, 'camera_rear_mp': 13, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'infinix zero 30': {'screen_inches': 6.78, 'camera_rear_mp': 108, 'camera_front_mp': 50, 'battery_mah': 5000, 'os': 'Android 13', 'network': '5G'},
    
    # Tecno series
    'tecno camon 30 pro': {'screen_inches': 6.77, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 5000, 'os': 'Android 14', 'network': '5G'},
    'tecno camon 30': {'screen_inches': 6.78, 'camera_rear_mp': 50, 'camera_front_mp': 50, 'battery_mah': 5000, 'os': 'Android 14', 'network': '4G'},
    'tecno camon 20 pro': {'screen_inches': 6.67, 'camera_rear_mp': 64, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'tecno camon 20': {'screen_inches': 6.67, 'camera_rear_mp': 64, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'tecno spark 20 pro+': {'screen_inches': 6.78, 'camera_rear_mp': 108, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'tecno spark 20 pro': {'screen_inches': 6.67, 'camera_rear_mp': 50, 'camera_front_mp': 32, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'tecno spark 20': {'screen_inches': 6.56, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'tecno spark go 2024': {'screen_inches': 6.6, 'camera_rear_mp': 13, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'tecno pop 8': {'screen_inches': 6.6, 'camera_rear_mp': 8, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    
    # Itel series
    'itel s24': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'itel s23+': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 12', 'network': '4G'},
    'itel a70': {'screen_inches': 6.6, 'camera_rear_mp': 13, 'camera_front_mp': 5, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
    'itel a60s': {'screen_inches': 6.6, 'camera_rear_mp': 8, 'camera_front_mp': 5, 'battery_mah': 4000, 'os': 'Android 12', 'network': '4G'},
    'itel p55': {'screen_inches': 6.6, 'camera_rear_mp': 50, 'camera_front_mp': 8, 'battery_mah': 5000, 'os': 'Android 13', 'network': '4G'},
}


def clean_name_for_matching(name):
    """Clean a phone name for matching with database."""
    if pd.isna(name):
        return ""
    
    name = str(name).lower()
    
    # Remove common prefixes
    prefixes = ['smartphone ', 'telephone ', 'mobile ', 'téléphone ']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    # Remove brand duplicates at start
    brands = ['samsung', 'apple', 'xiaomi', 'redmi', 'poco', 'oppo', 'realme', 
              'vivo', 'huawei', 'honor', 'infinix', 'tecno', 'itel']
    first_word = name.split()[0] if name.split() else ""
    name_parts = name.split()
    if len(name_parts) > 1 and first_word in brands and name_parts[1].lower() == first_word:
        name_parts = name_parts[1:]
        name = ' '.join(name_parts)
    
    # Remove color and storage info
    name = re.sub(r'\b\d+\s*(go|gb|tb)\b', '', name)
    name = re.sub(r'\b(noir|bleu|vert|blanc|gris|or|rose|violet|rouge|black|blue|green|white|grey|gray|gold|pink|purple|red)\b', '', name)
    
    # Remove special chars except spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def find_matching_specs(name):
    """Find matching specs from our database."""
    clean_name = clean_name_for_matching(name)
    
    # Try exact matches first
    for model, specs in PHONE_SPECS_DB.items():
        if model in clean_name or clean_name in model:
            return specs
    
    # Try fuzzy matching - check if key words match
    for model, specs in PHONE_SPECS_DB.items():
        model_words = set(model.split())
        clean_words = set(clean_name.split())
        # If most words match
        common = model_words.intersection(clean_words)
        if len(common) >= 2 and ('iphone' in common or model.split()[0] in clean_name):
            return specs
    
    return None


def fill_from_brand_stats(df):
    """Fill missing values using brand averages."""
    print("\n📊 Calculating brand statistics...")
    
    brand_stats = {}
    
    for brand in df['brand'].unique():
        if pd.isna(brand):
            continue
        brand_df = df[df['brand'] == brand]
        brand_stats[brand] = {
            'battery_mah': brand_df['battery_mah'].median(),
            'screen_inches': brand_df['screen_inches'].median(),
            'camera_rear_mp': brand_df['camera_rear_mp'].median(),
            'camera_front_mp': brand_df['camera_front_mp'].median(),
            'network': brand_df['network'].mode()[0] if len(brand_df['network'].mode()) > 0 else None,
            'os': brand_df['os'].mode()[0] if len(brand_df['os'].mode()) > 0 else None,
        }
    
    filled_count = 0
    for idx, row in df.iterrows():
        brand = row['brand']
        if brand not in brand_stats:
            continue
            
        stats = brand_stats[brand]
        for col in ['battery_mah', 'screen_inches', 'camera_rear_mp', 'camera_front_mp']:
            if pd.isna(row[col]) and not pd.isna(stats.get(col)):
                df.at[idx, col] = stats[col]
                filled_count += 1
        
        for col in ['network', 'os']:
            if (pd.isna(row[col]) or str(row[col]).strip() == '') and stats.get(col):
                df.at[idx, col] = stats[col]
                filled_count += 1
    
    print(f"  ✓ Filled {filled_count} values from brand averages")
    return df


def main():
    print("=" * 70)
    print("SMART MISSING VALUE FILLER")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv('dataset/unified_smartphones.csv')
    original_missing = df.isna().sum()
    print(f"\n📊 Loaded {len(df)} products")
    
    # Strategy 1: Fill from known specs database
    print("\n🔍 Strategy 1: Matching with known phone specs...")
    filled_from_db = 0
    
    for idx, row in df.iterrows():
        specs = find_matching_specs(row['name'])
        if specs:
            for col, val in specs.items():
                if pd.isna(row[col]) or (col in ['network', 'os'] and str(row[col]).strip() == ''):
                    df.at[idx, col] = val
                    filled_from_db += 1
    
    print(f"  ✓ Filled {filled_from_db} values from specs database")
    
    # Strategy 2: Fill from brand averages
    df = fill_from_brand_stats(df)
    
    # Strategy 3: Fill remaining with global median/mode
    print("\n🔧 Strategy 3: Filling remaining with global statistics...")
    global_filled = 0
    
    for col in ['battery_mah', 'screen_inches', 'camera_rear_mp', 'camera_front_mp', 'ram_gb', 'storage_gb']:
        median = df[col].median()
        missing_count = df[col].isna().sum()
        if missing_count > 0 and not pd.isna(median):
            df[col] = df[col].fillna(median)
            global_filled += missing_count
    
    for col in ['network', 'os']:
        if df[col].notna().any():
            mode = df[col].mode()
            if len(mode) > 0:
                missing_count = df[col].isna().sum() + (df[col].astype(str).str.strip() == '').sum()
                df[col] = df[col].fillna(mode[0])
                df[col] = df[col].replace('', mode[0])
                global_filled += missing_count
    
    print(f"  ✓ Filled {global_filled} values with global statistics")
    
    # Save
    output_file = 'dataset/unified_smartphones_filled.csv'
    df.to_csv(output_file, index=False)
    
    # Report
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    new_missing = df.isna().sum()
    print("\nMissing values comparison:")
    print(f"{'Column':<20} {'Before':<10} {'After':<10} {'Reduced':<10}")
    print("-" * 50)
    for col in ['ram_gb', 'storage_gb', 'battery_mah', 'screen_inches', 
                'camera_rear_mp', 'camera_front_mp', 'network', 'os']:
        before = original_missing[col]
        after = new_missing[col]
        reduced = before - after
        print(f"{col:<20} {before:<10} {after:<10} {reduced:<10}")
    
    print(f"\n✅ Saved to {output_file}")
    print(f"   Total rows: {len(df)}")


if __name__ == "__main__":
    main()
