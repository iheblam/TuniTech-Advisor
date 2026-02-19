"""
Smartphone recommendation endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd

from ..models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    SmartphoneDetail
)
from ..services.data_service import data_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get smartphone recommendations based on user criteria
    
    This endpoint filters and returns smartphones that match
    the user's budget and specification requirements.
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=503,
            detail="Smartphone data is not loaded."
        )
    
    try:
        # Get recommendations
        recommendations = data_service.get_recommendations(
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            min_ram=request.min_ram,
            min_storage=request.min_storage,
            min_battery=request.min_battery,
            min_camera=request.min_camera,
            brand=request.brand,
            requires_5g=request.requires_5g,
            limit=request.limit
        )
        
        # Convert to SmartphoneDetail objects
        smartphone_details = []
        for rec in recommendations:
            # Map data fields to SmartphoneDetail schema
            detail = SmartphoneDetail(
                name=rec.get('name', 'Unknown'),
                brand=rec.get('brand', 'Unknown'),
                price=rec.get('price', 0),
                store=rec.get('store', 'Unknown'),
                url=rec.get('url'),
                ram=rec.get('ram'),
                storage=rec.get('storage'),
                battery=rec.get('battery'),
                screen_size=rec.get('screen_size'),
                main_camera=rec.get('main_camera'),
                front_camera=rec.get('front_camera'),
                processor=rec.get('processor'),
                is_5g=rec.get('is_5g'),
                has_nfc=rec.get('has_nfc'),
                availability=rec.get('availability', 'In Stock'),
                match_score=rec.get('match_score')
            )
            smartphone_details.append(detail)
        
        # Prepare filters applied
        filters_applied = {
            "budget_min": request.budget_min,
            "budget_max": request.budget_max
        }
        if request.min_ram:
            filters_applied["min_ram"] = request.min_ram
        if request.min_storage:
            filters_applied["min_storage"] = request.min_storage
        if request.min_battery:
            filters_applied["min_battery"] = request.min_battery
        if request.min_camera:
            filters_applied["min_camera"] = request.min_camera
        if request.brand:
            filters_applied["brand"] = request.brand
        if request.requires_5g is not None:
            filters_applied["requires_5g"] = request.requires_5g
        
        return RecommendationResponse(
            total_found=len(smartphone_details),
            recommendations=smartphone_details,
            filters_applied=filters_applied
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/search")
async def search_smartphones(
    query: str = Query(..., description="Search query (name or brand)"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results")
):
    """
    Search for smartphones by name or brand
    
    Simple text search across smartphone names and brands
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=503,
            detail="Smartphone data is not loaded."
        )
    
    try:
        # Get all data
        data = data_service.data.copy()
        
        # Search in name and brand columns
        if 'name' in data.columns:
            mask = data['name'].str.contains(query, case=False, na=False)
        else:
            mask = pd.Series([False] * len(data))
        
        if 'brand' in data.columns:
            mask |= data['brand'].str.contains(query, case=False, na=False)
        
        filtered_data = data[mask]
        
        # Apply price filters if provided
        if min_price is not None and 'price' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['price'] >= min_price]
        
        if max_price is not None and 'price' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['price'] <= max_price]
        
        # Limit results
        filtered_data = filtered_data.head(limit)
        
        # Convert to list of dicts
        results = filtered_data.to_dict('records')
        
        return {
            "query": query,
            "total_found": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during search: {str(e)}"
        )


@router.get("/compare")
async def compare_smartphones(
    ids: str = Query(..., description="Comma-separated smartphone IDs")
):
    """
    Compare multiple smartphones side by side
    
    Provide comma-separated IDs like: ?ids=1,2,3
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=503,
            detail="Smartphone data is not loaded."
        )
    
    try:
        # Parse IDs
        smartphone_ids = [int(id.strip()) for id in ids.split(',')]
        
        if len(smartphone_ids) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 smartphones can be compared at once"
            )
        
        # Get smartphones
        smartphones = []
        for sid in smartphone_ids:
            phone = data_service.get_smartphone_by_id(sid)
            if phone:
                smartphones.append(phone)
        
        if not smartphones:
            raise HTTPException(
                status_code=404,
                detail="No smartphones found with the provided IDs"
            )
        
        return {
            "total": len(smartphones),
            "smartphones": smartphones
        }
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid ID format. Please provide comma-separated integers."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during comparison: {str(e)}"
        )
