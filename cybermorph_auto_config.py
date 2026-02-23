#!/usr/bin/env python3
"""
CyberMorph: Auto Configuration Generator - FIXED
"""

import logging
import tempfile
import yaml
from typing import Dict, Any
from pathlib import Path

class AutoConfigGenerator:
    """Auto-generates CyberMorph configuration"""
    
    def __init__(self, target_host: str, target_user: str, 
                 target_password: str = None, target_key: str = None,
                 logger: logging.Logger = None):
        self.target_host = target_host
        self.target_user = target_user
        self.target_password = target_password
        self.target_key = target_key
        self.logger = logger or logging.getLogger('AutoConfig')
    
    def generate_config(self) -> Dict[str, Any]:
        """Generate complete configuration automatically"""
        
        config = {
            'target': {
                'type': 'linux',
                'connection': {
                    'method': 'ssh',
                    'host': self.target_host,
                    'port': 22,
                    'username': self.target_user,
                    'timeout': 30
                }
            },
            'replica': {
                'type': 'docker',
                'cloud': {  # ← KEY FIX: 'cloud' not 'docker'
                    'provider': 'docker',
                    'docker': {
                        'network': 'cybermorph_replica',
                        'subnet': '10.0.1.0/24',
                        'image_base': 'ubuntu:22.04'
                    }
                }
            },
            'discovery': {
                'scan_files': True,
                'scan_users': True,
                'scan_services': True,
                'scan_databases': True,
                'scan_network_traffic': True,
                'traffic_capture_duration': 3600
            },
            'dlp': {
                'enabled': True,
                'detect_credentials': True,
                'detect_pii': True,
                'detect_financial_data': True,
                'detect_custom_patterns': True
            },
            'sanitization': {
                'enabled': True,
                'replace_credentials': True,
                'replace_pii': True,
                'replace_financial_data': True,
                'keep_data_structure': True,
                'keep_relationships': True,
                'synthetic': {
                    'locale': 'en_US',
                    'seed': 12345
                }
            },
            'deployment': {
                'auto_deploy': True,
                'validate_after_deploy': True,
                'generate_report': True,
                'output_format': 'json'
            },
            'logging': {
                'level': 'INFO',
                'console': True
            }
        }
        
        # Add SSH credentials
        if self.target_key:
            config['target']['connection']['key_file'] = self.target_key
        elif self.target_password:
            config['target']['connection']['password'] = self.target_password
        else:
            raise ValueError("Either --key or --password must be provided")
        
        self.logger.debug(f"Auto-generated configuration: {config}")
        return config
    
    def save_temp_config(self, config: Dict[str, Any]) -> str:
        """Save config to temporary file for compatibility"""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            delete=False
        )
        
        yaml.dump(config, temp_file)
        temp_file.close()
        
        self.logger.debug(f"Temporary config saved to: {temp_file.name}")
        return temp_file.name
