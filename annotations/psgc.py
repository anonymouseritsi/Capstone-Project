import requests
from typing import List, Dict, Optional
import logging
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

class PSGCApi:
    BASE_URL = "https://psgc.gitlab.io/api"
    CACHE_TIMEOUT = 3600  # 1 hour cache

    @staticmethod
    @lru_cache(maxsize=128)
    def _make_request(url: str) -> List[Dict]:
        """Make a request to the PSGC API with proper error handling and caching"""
        try:
            logger.info(f"Making request to: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received {len(data)} items from API")
            return data if isinstance(data, list) else [data]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return []

    @staticmethod
    def validate_code(code: str, code_type: str) -> bool:
        """Validate if a PSGC code exists"""
        try:
            url = f"{PSGCApi.BASE_URL}/{code_type}/{code}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def get_regions() -> List[Dict]:
        """Get all regions"""
        return PSGCApi._make_request(f"{PSGCApi.BASE_URL}/regions")

    @staticmethod
    def get_provinces(region_code: str = None) -> List[Dict]:
        """Get provinces, optionally filtered by region code"""
        if region_code:
            # Try direct province lookup first
            if PSGCApi.validate_code(region_code, "regions"):
                provinces = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/regions/{region_code}/provinces")
                if provinces:
                    return provinces

            # Fallback to filtering all provinces
            all_provinces = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/provinces")
            return [p for p in all_provinces if p.get('regionCode') == region_code]
        return PSGCApi._make_request(f"{PSGCApi.BASE_URL}/provinces")

    @staticmethod
    def get_cities(province_code: str = None) -> List[Dict]:
        """Get cities, optionally filtered by province code"""
        if province_code:
            # Try direct city lookup first
            if PSGCApi.validate_code(province_code, "provinces"):
                cities = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/provinces/{province_code}/cities")
                if cities:
                    return cities

            # Fallback to filtering all cities
            all_cities = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/cities")
            return [c for c in all_cities if c.get('provinceCode') == province_code]
        return PSGCApi._make_request(f"{PSGCApi.BASE_URL}/cities")

    @staticmethod
    def get_municipalities(province_code: str = None) -> List[Dict]:
        """Get municipalities, optionally filtered by province code"""
        if province_code:
            # Try direct municipality lookup first
            if PSGCApi.validate_code(province_code, "provinces"):
                municipalities = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/provinces/{province_code}/municipalities")
                if municipalities:
                    return municipalities

            # Fallback to filtering all municipalities
            all_municipalities = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/municipalities")
            return [m for m in all_municipalities if m.get('provinceCode') == province_code]
        return PSGCApi._make_request(f"{PSGCApi.BASE_URL}/municipalities")

    @staticmethod
    def get_barangays(city_code: str = None, municipality_code: str = None) -> List[Dict]:
        """Get barangays, optionally filtered by city or municipality code"""
        if city_code or municipality_code:
            code = city_code or municipality_code
            
            # Try direct barangay lookup first
            if city_code and PSGCApi.validate_code(city_code, "cities"):
                barangays = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/cities/{city_code}/barangays")
                if barangays:
                    return barangays
                    
            if municipality_code and PSGCApi.validate_code(municipality_code, "municipalities"):
                barangays = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/municipalities/{municipality_code}/barangays")
                if barangays:
                    return barangays

            # Fallback to filtering all barangays
            all_barangays = PSGCApi._make_request(f"{PSGCApi.BASE_URL}/barangays")
            return [
                b for b in all_barangays 
                if (city_code and b.get('cityCode') == city_code) or 
                   (municipality_code and b.get('municipalityCode') == municipality_code)
            ]
            
        return PSGCApi._make_request(f"{PSGCApi.BASE_URL}/barangays") 