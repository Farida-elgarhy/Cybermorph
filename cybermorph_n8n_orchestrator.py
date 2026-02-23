#!/usr/bin/env python3
"""
CyberMorph: n8n Orchestrator
Sets up n8n workflows for automated orchestration
"""

import logging
import requests
import json
from typing import Dict, Any

class N8nOrchestrator:
    """Sets up n8n workflows for CyberMorph orchestration"""
    
    def __init__(self, replica_info: Dict[str, Any], logger: logging.Logger = None):
        self.replica_info = replica_info
        self.logger = logger or logging.getLogger('N8nOrchestrator')
        self.n8n_url = 'http://localhost:5678'
    
    def setup_workflows(self ):
        """Setup n8n workflows"""
        self.logger.info("Setting up n8n workflows...")
        
        # 1. Create main orchestration workflow
        self._create_main_workflow()
        
        # 2. Create monitoring workflow
        self._create_monitoring_workflow()
        
        # 3. Create alert workflow
        self._create_alert_workflow()
        
        self.logger.info("✓ n8n workflows configured")
    
    def _create_main_workflow(self):
        """Create main orchestration workflow"""
        workflow = {
            "name": "CyberMorph: Main Orchestration",
            "nodes": [
                {
                    "parameters": {"triggerType": "manual"},
                    "name": "Manual Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "method": "POST",
                        "url": f"http://localhost:8000/api/v1/monitor",
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {"name": "container_id", "value": self.replica_info['container_id']}
                            ]
                        }
                    },
                    "name": "Start Monitoring",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [450, 300]
                }
            ]
        }
        
        self._post_workflow(workflow )
        self.logger.info("✓ Main orchestration workflow created")
    
    def _create_monitoring_workflow(self):
        """Create monitoring workflow"""
        workflow = {
            "name": "CyberMorph: Monitoring",
            "nodes": [
                {
                    "parameters": {"interval": [300]},
                    "name": "Every 5 minutes",
                    "type": "n8n-nodes-base.interval",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "method": "GET",
                        "url": f"http://localhost:8000/api/v1/status",
                    },
                    "name": "Get Status",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [450, 300]
                }
            ]
        }
        
        self._post_workflow(workflow )
        self.logger.info("✓ Monitoring workflow created")
    
    def _create_alert_workflow(self):
        """Create alert workflow"""
        workflow = {
            "name": "CyberMorph: Alerts",
            "nodes": [
                {
                    "parameters": {"triggerType": "manual"},
                    "name": "Alert Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "channel": "#cybermorph",
                        "text": "CyberMorph Alert: {{$json.message}}"
                    },
                    "name": "Slack Notification",
                    "type": "n8n-nodes-base.slack",
                    "typeVersion": 1,
                    "position": [450, 300]
                }
            ]
        }
        
        self._post_workflow(workflow)
        self.logger.info("✓ Alert workflow created")
    
    def _post_workflow(self, workflow: Dict[str, Any]):
        """Post workflow to n8n"""
        try:
            response = requests.post(
                f"{self.n8n_url}/api/v1/workflows",
                json=workflow,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 201:
                self.logger.warning(f"Failed to create workflow: {response.text}")
        
        except Exception as e:
            self.logger.warning(f"Could not connect to n8n: {str(e)}")