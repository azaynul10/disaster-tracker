import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Multi-level emergency alerting with specialized team coordination
    """
    try:
        # Parse alert request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        incident_id = body.get('incident_id')
        alert_level = body.get('alert_level', 'MEDIUM')
        affected_countries = body.get('affected_countries', [])
        
        # Generate alerts
        alerts = generate_alerts(incident_id, alert_level, affected_countries)
        
        # Send alerts
        sent_alerts = send_alerts(alerts)
        
        # Log alert activity
        log_alert_activity(incident_id, alerts, sent_alerts)
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'alert_id': f"ALERT-{incident_id}",
                'alerts_generated': len(alerts),
                'alerts_sent': sent_alerts,
                'status': 'COMPLETED'
            })
        }
        
    except Exception as e:
        logger.error(f"Alert generation error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def generate_alerts(incident_id, alert_level, affected_countries):
    """Generate appropriate alerts based on level and countries"""
    
    alert_templates = {
        'CRITICAL': {
            'message': f"🚨 CRITICAL CROSS-BORDER INCIDENT: {incident_id}. Immediate coordination required.",
            'recipients': ['emergency_coordinators', 'border_authorities', 'environmental_agencies'],
            'channels': ['SMS', 'EMAIL', 'PUSH', 'RADIO']
        },
        'HIGH': {
            'message': f"⚠️ HIGH PRIORITY INCIDENT: {incident_id}. Cross-border coordination initiated.",
            'recipients': ['emergency_coordinators', 'environmental_agencies'],
            'channels': ['SMS', 'EMAIL', 'PUSH']
        },
        'MEDIUM': {
            'message': f"📋 INCIDENT ALERT: {incident_id}. Monitoring and coordination in progress.",
            'recipients': ['emergency_coordinators'],
            'channels': ['EMAIL', 'PUSH']
        },
        'LOW': {
            'message': f"ℹ️ INCIDENT NOTIFICATION: {incident_id}. Standard response protocols activated.",
            'recipients': ['emergency_coordinators'],
            'channels': ['EMAIL']
        }
    }
    
    template = alert_templates.get(alert_level, alert_templates['MEDIUM'])
    
    alerts = []
    for country in affected_countries:
        for recipient_type in template['recipients']:
            for channel in template['channels']:
                alerts.append({
                    'country': country,
                    'recipient_type': recipient_type,
                    'channel': channel,
                    'message': template['message'],
                    'priority': alert_level,
                    'timestamp': datetime.now().isoformat()
                })
    
    return alerts

def send_alerts(alerts):
    """Send alerts through various channels"""
    sent_count = 0
    
    for alert in alerts:
        try:
            if alert['channel'] == 'SMS':
                send_sms_alert(alert)
            elif alert['channel'] == 'EMAIL':
                send_email_alert(alert)
            elif alert['channel'] == 'PUSH':
                send_push_alert(alert)
            elif alert['channel'] == 'RADIO':
                send_radio_alert(alert)
            
            sent_count += 1
            logger.info(f"Sent {alert['channel']} alert to {alert['country']} {alert['recipient_type']}")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
    
    return sent_count

def send_sms_alert(alert):
    """Send SMS alert"""
    # In real implementation, use SNS SMS
    logger.info(f"SMS Alert: {alert['message']}")

def send_email_alert(alert):
    """Send email alert"""
    # In real implementation, use SES
    logger.info(f"Email Alert: {alert['message']}")

def send_push_alert(alert):
    """Send push notification"""
    # In real implementation, use SNS mobile push
    logger.info(f"Push Alert: {alert['message']}")

def send_radio_alert(alert):
    """Send radio alert"""
    # In real implementation, integrate with emergency radio systems
    logger.info(f"Radio Alert: {alert['message']}")

def log_alert_activity(incident_id, alerts, sent_count):
    """Log alert activity to DynamoDB"""
    try:
        table = dynamodb.Table('AlertActivity')
        table.put_item(Item={
            'incident_id': incident_id,
            'alert_timestamp': datetime.now().isoformat(),
            'total_alerts': len(alerts),
            'sent_alerts': sent_count,
            'success_rate': (sent_count / len(alerts)) * 100 if alerts else 0
        })
    except Exception as e:
        logger.error(f"Failed to log alert activity: {str(e)}")
