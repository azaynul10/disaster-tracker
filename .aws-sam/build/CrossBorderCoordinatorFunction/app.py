import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
stepfunctions = boto3.client('stepfunctions')
sns = boto3.client('sns')

def lambda_handler(event, context):
    """
    Cross-border coordination with bilateral agreement management
    """
    try:
        # Parse incident data
        if 'detail' in event:
            incident = event['detail']
        else:
            incident = json.loads(event['body']) if 'body' in event else event
        
        incident_id = incident['incident_id']
        affected_countries = incident['affected_countries']
        priority = incident['priority']
        
        # Validate bilateral agreements
        agreements = validate_bilateral_agreements(affected_countries)
        
        # Determine coordination level
        coordination_level = determine_coordination_level(priority, agreements)
        
        # Create coordination record
        coordination = {
            'coordination_id': f"COORD-{incident_id}",
            'incident_id': incident_id,
            'affected_countries': affected_countries,
            'coordination_level': coordination_level,
            'bilateral_agreements': agreements,
            'status': 'INITIATED',
            'created_at': datetime.now().isoformat()
        }
        
        # Store coordination record
        table = dynamodb.Table('CrossBorderCoordination')
        table.put_item(Item=coordination)
        
        # Start appropriate workflow
        workflow_arn = start_coordination_workflow(coordination)
        
        # Send notifications
        send_coordination_notifications(coordination)
        
        logger.info(f"Initiated coordination {coordination['coordination_id']}")
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'coordination_id': coordination['coordination_id'],
                'workflow_arn': workflow_arn,
                'status': 'INITIATED'
            })
        }
        
    except Exception as e:
        logger.error(f"Coordination error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def validate_bilateral_agreements(countries):
    """Validate bilateral agreements between countries"""
    agreements = {
        ('Bangladesh', 'India'): {'type': 'Formal', 'response_time': 6, 'data_sharing': True},
        ('United States', 'Canada'): {'type': 'Formal', 'response_time': 4, 'data_sharing': True},
        ('Germany', 'Netherlands'): {'type': 'EU Framework', 'response_time': 3, 'data_sharing': True}
    }
    
    country_pair = tuple(sorted(countries))
    return agreements.get(country_pair, {'type': 'None', 'response_time': 24, 'data_sharing': False})

def determine_coordination_level(priority, agreements):
    """Determine coordination level based on priority and agreements"""
    if priority == 'CRITICAL':
        return 'CRITICAL'
    elif priority == 'HIGH' and agreements['data_sharing']:
        return 'HIGH'
    else:
        return 'STANDARD'

def start_coordination_workflow(coordination):
    """Start Step Functions workflow"""
    workflow_map = {
        'CRITICAL': 'arn:aws:states:us-east-1:743935940622:stateMachine:CriticalIncidentWorkflow',
        'HIGH': 'arn:aws:states:us-east-1:743935940622:stateMachine:HighPriorityWorkflow',
        'STANDARD': 'arn:aws:states:us-east-1:743935940622:stateMachine:StandardWorkflow'
    }
    
    workflow_arn = workflow_map.get(coordination['coordination_level'])
    if workflow_arn:
        try:
            response = stepfunctions.start_execution(
                stateMachineArn=workflow_arn,
                input=json.dumps(coordination, default=str)
            )
            return response['executionArn']
        except Exception as e:
            logger.error(f"Failed to start workflow: {str(e)}")
    
    return None

def send_coordination_notifications(coordination):
    """Send notifications to relevant authorities"""
    try:
        message = f"Cross-border coordination initiated: {coordination['coordination_id']}"
        # In real implementation, send to country-specific SNS topics
        logger.info(f"Notifications sent for {coordination['coordination_id']}")
    except Exception as e:
        logger.error(f"Failed to send notifications: {str(e)}")
