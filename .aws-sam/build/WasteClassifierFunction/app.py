import json
import boto3
import logging
from datetime import datetime
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

def lambda_handler(event, context):
    """
    Advanced waste classification with cross-border detection
    """
    try:
        # Parse input data
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract incident data
        location = body.get('location', {})
        waste_type = body.get('waste_type', 'Unknown')
        description = body.get('description', '')
        
        # Generate incident ID
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Classify waste type and determine hazard level
        classification = classify_waste(waste_type, description)
        
        # Check for cross-border implications
        cross_border_info = check_cross_border(location)
        
        # Create incident record
        incident = {
            'incident_id': incident_id,
            'timestamp': datetime.now().isoformat(),
            'location': location,
            'waste_classification': classification,
            'cross_border_coordination': cross_border_info['requires_coordination'],
            'affected_countries': cross_border_info['countries'],
            'status': 'CLASSIFIED',
            'priority': classification['priority'],
            'created_at': datetime.now().isoformat()
        }
        
        # Store in DynamoDB
        table = dynamodb.Table('DisasterIncidents')
        table.put_item(Item=convert_decimals(incident))
        
        # Trigger cross-border coordination if needed
        if cross_border_info['requires_coordination']:
            trigger_coordination_workflow(incident)
        
        logger.info(f"Classified incident {incident_id} with priority {classification['priority']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(incident, default=str)
        }
        
    except Exception as e:
        logger.error(f"Error in waste classification: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def classify_waste(waste_type, description):
    """Classify waste and determine priority"""
    
    # Waste type classifications
    classifications = {
        'chemical_hazardous': {'priority': 'CRITICAL', 'hazard_level': 5, 'special_handling': True},
        'medical_biological': {'priority': 'HIGH', 'hazard_level': 4, 'special_handling': True},
        'radioactive': {'priority': 'CRITICAL', 'hazard_level': 5, 'special_handling': True},
        'industrial_waste': {'priority': 'HIGH', 'hazard_level': 3, 'special_handling': True},
        'disaster_debris': {'priority': 'MEDIUM', 'hazard_level': 2, 'special_handling': False},
        'construction_debris': {'priority': 'LOW', 'hazard_level': 1, 'special_handling': False}
    }
    
    # Default classification
    classification = classifications.get(waste_type.lower().replace(' ', '_'), 
                                       {'priority': 'MEDIUM', 'hazard_level': 2, 'special_handling': False})
    
    # Enhance with description analysis
    if any(keyword in description.lower() for keyword in ['toxic', 'chemical', 'hazardous', 'poison']):
        classification['priority'] = 'CRITICAL'
        classification['hazard_level'] = min(5, classification['hazard_level'] + 1)
    
    return {
        'primary_type': waste_type,
        'priority': classification['priority'],
        'hazard_level': classification['hazard_level'],
        'requires_special_handling': classification['special_handling'],
        'estimated_cleanup_time': calculate_cleanup_time(classification),
        'environmental_risk': determine_environmental_risk(classification)
    }

def check_cross_border(location):
    """Check if incident requires cross-border coordination"""
    
    # Sample border proximity check (in real implementation, use geospatial analysis)
    lat = float(location.get('latitude', 0))
    lng = float(location.get('longitude', 0))
    
    # Define border regions (simplified)
    border_regions = [
        {'countries': ['Bangladesh', 'India'], 'lat_range': (23.0, 26.0), 'lng_range': (88.0, 92.0)},
        {'countries': ['United States', 'Canada'], 'lat_range': (48.0, 50.0), 'lng_range': (-125.0, -95.0)},
        {'countries': ['Germany', 'Netherlands'], 'lat_range': (51.0, 53.0), 'lng_range': (6.0, 8.0)}
    ]
    
    for region in border_regions:
        if (region['lat_range'][0] <= lat <= region['lat_range'][1] and 
            region['lng_range'][0] <= lng <= region['lng_range'][1]):
            return {
                'requires_coordination': True,
                'countries': region['countries'],
                'border_proximity': True
            }
    
    return {
        'requires_coordination': False,
        'countries': [location.get('country', 'Unknown')],
        'border_proximity': False
    }

def calculate_cleanup_time(classification):
    """Calculate estimated cleanup time in hours"""
    base_times = {
        'CRITICAL': 48,
        'HIGH': 24,
        'MEDIUM': 12,
        'LOW': 6
    }
    return base_times.get(classification['priority'], 12)

def determine_environmental_risk(classification):
    """Determine environmental risk level"""
    if classification['hazard_level'] >= 4:
        return 'HIGH'
    elif classification['hazard_level'] >= 2:
        return 'MEDIUM'
    else:
        return 'LOW'

def trigger_coordination_workflow(incident):
    """Trigger Step Functions workflow for cross-border coordination"""
    try:
        eventbridge.put_events(
            Entries=[
                {
                    'Source': 'disaster.waste.tracker',
                    'DetailType': 'Cross-Border Incident Detected',
                    'Detail': json.dumps(incident, default=str),
                    'EventBusName': 'default'
                }
            ]
        )
        logger.info(f"Triggered coordination workflow for incident {incident['incident_id']}")
    except Exception as e:
        logger.error(f"Failed to trigger coordination workflow: {str(e)}")

def convert_decimals(obj):
    """Convert float values to Decimal for DynamoDB"""
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(v) for v in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj
