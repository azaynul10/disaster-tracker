import json
import boto3
import logging
from datetime import datetime
import math

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Intelligent resource allocation with cost optimization and deployment strategies
    """
    try:
        # Parse optimization request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        incident_id = body.get('incident_id')
        incident_data = body.get('incident_data', {})
        
        # Get available resources
        available_resources = get_available_resources(incident_data.get('affected_countries', []))
        
        # Optimize resource allocation
        optimization = optimize_resources(incident_data, available_resources)
        
        # Calculate deployment strategy
        deployment_strategy = calculate_deployment_strategy(optimization)
        
        # Store optimization results
        store_optimization_results(incident_id, optimization, deployment_strategy)
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'optimization_id': f"OPT-{incident_id}",
                'resource_allocation': optimization,
                'deployment_strategy': deployment_strategy,
                'estimated_cost': calculate_total_cost(optimization),
                'estimated_response_time': calculate_response_time(deployment_strategy)
            }, default=str)
        }
        
    except Exception as e:
        logger.error(f"Resource optimization error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def get_available_resources(countries):
    """Get available response teams and equipment"""
    
    # Sample resource database
    resources = {
        'Bangladesh': [
            {'team_id': 'BD-HAZMAT-01', 'specialization': 'Chemical Response', 'status': 'AVAILABLE', 'capability': 9},
            {'team_id': 'BD-FLOOD-02', 'specialization': 'Flood Response', 'status': 'AVAILABLE', 'capability': 8}
        ],
        'India': [
            {'team_id': 'IN-BORDER-01', 'specialization': 'Cross-Border Ops', 'status': 'AVAILABLE', 'capability': 9},
            {'team_id': 'IN-ENV-02', 'specialization': 'Environmental', 'status': 'DEPLOYED', 'capability': 7}
        ],
        'United States': [
            {'team_id': 'US-HAZMAT-01', 'specialization': 'Chemical Response', 'status': 'AVAILABLE', 'capability': 10},
            {'team_id': 'US-FLOOD-02', 'specialization': 'Flood Response', 'status': 'AVAILABLE', 'capability': 9}
        ],
        'Canada': [
            {'team_id': 'CA-COORD-01', 'specialization': 'Coordination', 'status': 'AVAILABLE', 'capability': 8},
            {'team_id': 'CA-ENV-02', 'specialization': 'Environmental', 'status': 'AVAILABLE', 'capability': 8}
        ],
        'Germany': [
            {'team_id': 'DE-IND-01', 'specialization': 'Industrial Cleanup', 'status': 'AVAILABLE', 'capability': 9},
            {'team_id': 'DE-CHEM-02', 'specialization': 'Chemical Response', 'status': 'AVAILABLE', 'capability': 9}
        ],
        'Netherlands': [
            {'team_id': 'NL-ENV-01', 'specialization': 'Environmental', 'status': 'AVAILABLE', 'capability': 8},
            {'team_id': 'NL-WATER-02', 'specialization': 'Water Management', 'status': 'AVAILABLE', 'capability': 10}
        ]
    }
    
    available = []
    for country in countries:
        if country in resources:
            available.extend([team for team in resources[country] if team['status'] == 'AVAILABLE'])
    
    return available

def optimize_resources(incident_data, available_resources):
    """Optimize resource allocation based on incident requirements"""
    
    waste_type = incident_data.get('waste_classification', {}).get('primary_type', 'Unknown')
    priority = incident_data.get('priority', 'MEDIUM')
    hazard_level = incident_data.get('waste_classification', {}).get('hazard_level', 3)
    
    # Determine required specializations
    required_specializations = determine_required_specializations(waste_type, hazard_level)
    
    # Select optimal teams
    selected_teams = select_optimal_teams(available_resources, required_specializations, priority)
    
    # Calculate resource requirements
    resource_requirements = calculate_resource_requirements(incident_data, selected_teams)
    
    return {
        'selected_teams': selected_teams,
        'resource_requirements': resource_requirements,
        'specializations_covered': required_specializations,
        'optimization_score': calculate_optimization_score(selected_teams, required_specializations)
    }

def determine_required_specializations(waste_type, hazard_level):
    """Determine required team specializations"""
    
    specialization_map = {
        'Chemical Hazardous': ['Chemical Response', 'Environmental'],
        'Medical Biological': ['Medical Response', 'Environmental'],
        'Industrial Waste': ['Industrial Cleanup', 'Environmental'],
        'Disaster Debris': ['Flood Response', 'Construction'],
        'Radioactive': ['Radiation Response', 'Environmental']
    }
    
    base_specializations = specialization_map.get(waste_type, ['Environmental'])
    
    # Add coordination for high-priority incidents
    if hazard_level >= 4:
        base_specializations.append('Coordination')
    
    return base_specializations

def select_optimal_teams(available_resources, required_specializations, priority):
    """Select optimal teams based on requirements"""
    
    selected = []
    covered_specializations = set()
    
    # Sort teams by capability score
    sorted_teams = sorted(available_resources, key=lambda x: x['capability'], reverse=True)
    
    for specialization in required_specializations:
        best_team = None
        best_score = 0
        
        for team in sorted_teams:
            if team['team_id'] not in [t['team_id'] for t in selected]:
                if specialization.lower() in team['specialization'].lower():
                    score = team['capability']
                    if score > best_score:
                        best_score = score
                        best_team = team
        
        if best_team:
            selected.append(best_team)
            covered_specializations.add(specialization)
    
    # Add coordination team for critical incidents
    if priority == 'CRITICAL' and 'Coordination' not in covered_specializations:
        coord_teams = [t for t in sorted_teams if 'coord' in t['specialization'].lower()]
        if coord_teams and coord_teams[0]['team_id'] not in [t['team_id'] for t in selected]:
            selected.append(coord_teams[0])
    
    return selected

def calculate_resource_requirements(incident_data, selected_teams):
    """Calculate detailed resource requirements"""
    
    base_equipment = ['Communication Systems', 'Safety Equipment', 'Transportation']
    
    waste_type = incident_data.get('waste_classification', {}).get('primary_type', 'Unknown')
    
    specialized_equipment = {
        'Chemical Hazardous': ['Chemical Suits', 'Neutralization Agents', 'Containment Systems'],
        'Medical Biological': ['Biohazard Suits', 'Sterilization Equipment', 'Medical Waste Containers'],
        'Industrial Waste': ['Heavy Machinery', 'Industrial Containers', 'Filtration Systems'],
        'Disaster Debris': ['Heavy Machinery', 'Sorting Equipment', 'Disposal Trucks']
    }
    
    equipment = base_equipment + specialized_equipment.get(waste_type, [])
    
    return {
        'personnel': len(selected_teams) * 5,  # Assume 5 people per team
        'equipment': equipment,
        'vehicles': len(selected_teams) * 2,   # 2 vehicles per team
        'estimated_duration_hours': calculate_estimated_duration(incident_data)
    }

def calculate_deployment_strategy(optimization):
    """Calculate optimal deployment strategy"""
    
    teams = optimization['selected_teams']
    
    # Group teams by country for coordination
    country_groups = {}
    for team in teams:
        country = team['team_id'].split('-')[0]
        if country not in country_groups:
            country_groups[country] = []
        country_groups[country].append(team)
    
    deployment_phases = []
    
    # Phase 1: Immediate response (highest capability teams)
    immediate_teams = sorted(teams, key=lambda x: x['capability'], reverse=True)[:2]
    deployment_phases.append({
        'phase': 'IMMEDIATE',
        'teams': immediate_teams,
        'deployment_time_hours': 2,
        'objective': 'Initial assessment and containment'
    })
    
    # Phase 2: Full deployment
    remaining_teams = [t for t in teams if t not in immediate_teams]
    if remaining_teams:
        deployment_phases.append({
            'phase': 'FULL_DEPLOYMENT',
            'teams': remaining_teams,
            'deployment_time_hours': 6,
            'objective': 'Complete response and cleanup'
        })
    
    return {
        'deployment_phases': deployment_phases,
        'coordination_centers': list(country_groups.keys()),
        'total_deployment_time': max([p['deployment_time_hours'] for p in deployment_phases])
    }

def calculate_optimization_score(selected_teams, required_specializations):
    """Calculate optimization effectiveness score"""
    
    if not selected_teams:
        return 0
    
    # Base score from team capabilities
    capability_score = sum(team['capability'] for team in selected_teams) / len(selected_teams)
    
    # Coverage score (how many required specializations are covered)
    covered = sum(1 for spec in required_specializations 
                 if any(spec.lower() in team['specialization'].lower() for team in selected_teams))
    coverage_score = (covered / len(required_specializations)) * 100 if required_specializations else 100
    
    # Combined score
    return (capability_score * 0.6 + coverage_score * 0.4)

def calculate_total_cost(optimization):
    """Calculate estimated total cost"""
    
    teams = optimization['selected_teams']
    requirements = optimization['resource_requirements']
    
    # Cost estimates (in USD)
    team_cost_per_hour = 500
    equipment_base_cost = 10000
    vehicle_cost_per_hour = 100
    
    personnel_cost = len(teams) * team_cost_per_hour * requirements['estimated_duration_hours']
    equipment_cost = equipment_base_cost
    vehicle_cost = requirements['vehicles'] * vehicle_cost_per_hour * requirements['estimated_duration_hours']
    
    return personnel_cost + equipment_cost + vehicle_cost

def calculate_response_time(deployment_strategy):
    """Calculate estimated response time"""
    
    if deployment_strategy['deployment_phases']:
        return deployment_strategy['deployment_phases'][0]['deployment_time_hours']
    return 6  # Default 6 hours

def calculate_estimated_duration(incident_data):
    """Calculate estimated incident duration"""
    
    priority = incident_data.get('priority', 'MEDIUM')
    hazard_level = incident_data.get('waste_classification', {}).get('hazard_level', 3)
    
    base_duration = {
        'CRITICAL': 48,
        'HIGH': 24,
        'MEDIUM': 12,
        'LOW': 6
    }
    
    duration = base_duration.get(priority, 12)
    
    # Adjust for hazard level
    duration *= (hazard_level / 3)
    
    return int(duration)

def store_optimization_results(incident_id, optimization, deployment_strategy):
    """Store optimization results in DynamoDB"""
    try:
        table = dynamodb.Table('ResourceOptimization')
        table.put_item(Item={
            'incident_id': incident_id,
            'optimization_timestamp': datetime.now().isoformat(),
            'selected_teams': optimization['selected_teams'],
            'deployment_strategy': deployment_strategy,
            'optimization_score': optimization['optimization_score']
        })
    except Exception as e:
        logger.error(f"Failed to store optimization results: {str(e)}")
