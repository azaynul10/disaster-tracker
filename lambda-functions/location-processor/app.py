import json
import boto3
import logging
import math
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Comprehensive geospatial analysis and environmental sensitivity assessment
    """
    try:
        # Parse location data
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        location = body.get('location', {})
        incident_id = body.get('incident_id', 'UNKNOWN')
        
        # Perform geospatial analysis
        analysis = {
            'incident_id': incident_id,
            'location_analysis': analyze_location(location),
            'border_proximity': check_border_proximity(location),
            'environmental_sensitivity': assess_environmental_sensitivity(location),
            'accessibility': assess_accessibility(location),
            'weather_impact': assess_weather_impact(location),
            'processed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Processed location for incident {incident_id}")
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(analysis, default=str)
        }
        
    except Exception as e:
        logger.error(f"Location processing error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def analyze_location(location):
    """Analyze location characteristics"""
    lat = float(location.get('latitude', 0))
    lng = float(location.get('longitude', 0))
    
    return {
        'coordinates': {'latitude': lat, 'longitude': lng},
        'country': location.get('country', 'Unknown'),
        'region': location.get('region', 'Unknown'),
        'terrain_type': determine_terrain_type(lat, lng),
        'population_density': estimate_population_density(lat, lng),
        'infrastructure_access': assess_infrastructure_access(lat, lng)
    }

def check_border_proximity(location):
    """Check proximity to international borders"""
    lat = float(location.get('latitude', 0))
    lng = float(location.get('longitude', 0))
    
    # Sample border definitions
    borders = [
        {'countries': ['Bangladesh', 'India'], 'lat': 23.7, 'lng': 90.4, 'threshold': 0.5},
        {'countries': ['United States', 'Canada'], 'lat': 49.0, 'lng': -95.0, 'threshold': 0.5},
        {'countries': ['Germany', 'Netherlands'], 'lat': 51.8, 'lng': 6.2, 'threshold': 0.3}
    ]
    
    nearest_borders = []
    for border in borders:
        distance = calculate_distance(lat, lng, border['lat'], border['lng'])
        if distance <= border['threshold']:
            nearest_borders.append({
                'countries': border['countries'],
                'distance_degrees': distance,
                'type': 'LAND_BORDER'
            })
    
    return {
        'near_border': len(nearest_borders) > 0,
        'nearest_borders': nearest_borders,
        'cross_border_risk': 'HIGH' if nearest_borders else 'LOW'
    }

def assess_environmental_sensitivity(location):
    """Assess environmental sensitivity of the location"""
    lat = float(location.get('latitude', 0))
    lng = float(location.get('longitude', 0))
    
    # Sample environmental zones
    sensitive_zones = [
        {'name': 'Sundarbans Mangroves', 'lat': 22.0, 'lng': 89.0, 'radius': 1.0, 'sensitivity': 'CRITICAL'},
        {'name': 'Great Lakes Region', 'lat': 45.0, 'lng': -85.0, 'radius': 2.0, 'sensitivity': 'HIGH'},
        {'name': 'Rhine Delta', 'lat': 52.0, 'lng': 5.0, 'radius': 0.5, 'sensitivity': 'HIGH'}
    ]
    
    for zone in sensitive_zones:
        distance = calculate_distance(lat, lng, zone['lat'], zone['lng'])
        if distance <= zone['radius']:
            return {
                'sensitivity_level': zone['sensitivity'],
                'protected_area': zone['name'],
                'special_protocols_required': True
            }
    
    return {
        'sensitivity_level': 'STANDARD',
        'protected_area': None,
        'special_protocols_required': False
    }

def assess_accessibility(location):
    """Assess accessibility for response teams"""
    lat = float(location.get('latitude', 0))
    lng = float(location.get('longitude', 0))
    
    # Simplified accessibility assessment
    if abs(lat) > 60:  # Arctic regions
        return 'DIFFICULT'
    elif 'water' in location.get('terrain', '').lower():
        return 'WATER_ACCESS_REQUIRED'
    else:
        return 'ACCESSIBLE'

def assess_weather_impact(location):
    """Assess potential weather impact on response operations"""
    # Simplified weather assessment
    lat = float(location.get('latitude', 0))
    
    if abs(lat) > 50:
        return 'SEVERE_WEATHER_RISK'
    elif 20 <= abs(lat) <= 35:
        return 'MODERATE_WEATHER_RISK'
    else:
        return 'MINIMAL_WEATHER_RISK'

def determine_terrain_type(lat, lng):
    """Determine terrain type based on coordinates"""
    # Simplified terrain classification
    if abs(lat) > 60:
        return 'ARCTIC'
    elif abs(lat) < 23.5:
        return 'TROPICAL'
    else:
        return 'TEMPERATE'

def estimate_population_density(lat, lng):
    """Estimate population density"""
    # Simplified population density estimation
    major_cities = [
        {'lat': 23.8, 'lng': 90.4, 'density': 'HIGH'},  # Dhaka
        {'lat': 45.5, 'lng': -73.6, 'density': 'HIGH'},  # Montreal
        {'lat': 52.5, 'lng': 13.4, 'density': 'HIGH'}   # Berlin
    ]
    
    for city in major_cities:
        distance = calculate_distance(lat, lng, city['lat'], city['lng'])
        if distance < 0.5:
            return city['density']
    
    return 'MEDIUM'

def assess_infrastructure_access(lat, lng):
    """Assess infrastructure access"""
    # Simplified infrastructure assessment
    return 'GOOD'  # Default assumption

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in degrees"""
    return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2)
