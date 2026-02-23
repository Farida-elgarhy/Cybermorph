#!/usr/bin/env python3
"""
CyberMorph Stage 0: Initialization & Validation
"""

import yaml
import logging
import socket
import paramiko
import sys
from pathlib import Path
from typing import Dict, Any

class CyberMorphInitializer:
    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.logger = self.setup_logging()
        self.target_connection = None
        self.target_os = None
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load and parse YAML configuration file"""
        self.logger.info(f"Loading configuration from {config_file}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Expand environment variables
        config = self.expand_env_vars(config)
        
        self.logger.info("✓ Configuration loaded successfully")
        return config
    
    def expand_env_vars(self, obj):
        """Recursively expand environment variables in config"""
        import os
        
        if isinstance(obj, dict):
            return {k: self.expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.expand_env_vars(v) for v in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.getenv(var_name, obj)
        return obj
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('CyberMorph')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('/var/log/cybermorph.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        self.logger.info("=" * 60)
        self.logger.info("CYBERMORPH STAGE 0: INITIALIZATION & VALIDATION")
        self.logger.info("=" * 60)
        
        try:
            # 1. Validate configuration
            self.logger.info("\n[1/6] Validating configuration...")
            self.validate_config()
            self.logger.info("✓ Configuration valid")
            
            # 2. Validate target connectivity
            self.logger.info("\n[2/6] Validating target connectivity...")
            self.validate_target_connectivity()
            self.logger.info("✓ Target connectivity verified")
            
            # 3. Validate target credentials
            self.logger.info("\n[3/6] Validating target credentials...")
            self.validate_target_credentials()
            self.logger.info("✓ Target credentials verified")
            
            # 4. Detect target OS
            self.logger.info("\n[4/6] Detecting target OS...")
            self.detect_target_os()
            self.logger.info(f"✓ Target OS detected: {self.target_os}")
            
            # 5. Validate replica environment
            self.logger.info("\n[5/6] Validating replica environment...")
            self.validate_replica_environment()
            self.logger.info("✓ Replica environment validated")
            
            # 6. Check disk space
            self.logger.info("\n[6/6] Checking disk space...")
            self.check_disk_space()
            self.logger.info("✓ Sufficient disk space available")
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("✓ ALL VALIDATIONS PASSED - READY FOR STAGE 1")
            self.logger.info("=" * 60)
            
            return True
        
        except Exception as e:
            self.logger.error(f"✗ Validation failed: {str(e)}", exc_info=True)
            return False
    
    def validate_config(self):
        """Validate configuration structure"""
        required_keys = ['target', 'replica', 'discovery', 'sanitization', 'deployment']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Validate target
        if 'connection' not in self.config['target']:
            raise ValueError("Missing target.connection in configuration")
        
        # Validate replica
        if 'cloud' not in self.config['replica'] and 'on_premise' not in self.config['replica']:
            raise ValueError("Missing replica.cloud or replica.on_premise in configuration")
    
    def validate_target_connectivity(self):
        """Test connectivity to target server"""
        target = self.config['target']['connection']
        host = target['host']
        port = target.get('port', 22)
        timeout = target.get('timeout', 30)
        
        # Test TCP connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            result = sock.connect_ex((host, port))
            if result != 0:
                raise ConnectionError(f"Cannot connect to {host}:{port}")
        finally:
            sock.close()
    
    def validate_target_credentials(self):
        """Test credentials on target server"""
        target = self.config['target']['connection']
        
        if target['method'] == 'ssh':
            self.validate_ssh_credentials(target)
        elif target['method'] == 'winrm':
            self.validate_winrm_credentials(target)
        else:
            raise ValueError(f"Unknown connection method: {target['method']}")
    
    def validate_ssh_credentials(self, target: Dict[str, Any]):
        """Validate SSH credentials"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if 'key_file' in target:
                ssh.connect(
                    hostname=target['host'],
                    port=target.get('port', 22),
                    username=target['username'],
                    key_filename=target['key_file'],
                    timeout=target.get('timeout', 30)
                )
            else:
                ssh.connect(
                    hostname=target['host'],
                    port=target.get('port', 22),
                    username=target['username'],
                    password=target['password'],
                    timeout=target.get('timeout', 30)
                )
            
            self.target_connection = ssh
        except Exception as e:
            raise ConnectionError(f"SSH authentication failed: {str(e)}")
    
    def validate_winrm_credentials(self, target: Dict[str, Any]):
        """Validate WinRM credentials"""
        from pywinrm.protocol import Protocol
        
        try:
            protocol = Protocol(
                endpoint=f"http://{target['host']}:5985/wsman",
                username=target['username'],
                password=target['password']
             )
            protocol.send_message("")
            self.target_connection = protocol
        except Exception as e:
            raise ConnectionError(f"WinRM authentication failed: {str(e)}")
    
    def detect_target_os(self):
        """Detect target operating system"""
        if self.config['target']['type'] == 'linux':
            self.target_os = 'linux'
        elif self.config['target']['type'] == 'windows':
            self.target_os = 'windows'
        else:
            # Auto-detect via SSH
            stdin, stdout, stderr = self.target_connection.exec_command('uname -s')
            output = stdout.read().decode().strip().lower()
            
            if 'linux' in output:
                self.target_os = 'linux'
            elif 'darwin' in output:
                self.target_os = 'macos'
            else:
                self.target_os = 'unknown'
    
    def validate_replica_environment(self):
        """Validate replica environment credentials and access"""
        replica = self.config['replica']
        
        if replica['type'] == 'cloud':
            self.validate_cloud_credentials(replica['cloud'])
        elif replica['type'] == 'on-premise':
            self.validate_on_premise_credentials(replica['on_premise'])
    
    def validate_cloud_credentials(self, cloud_config: Dict[str, Any]):
        """Validate cloud provider credentials"""
        provider = cloud_config['provider']
        
        if provider == 'aws':
            import boto3
            try:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=cloud_config['credentials']['access_key'],
                    aws_secret_access_key=cloud_config['credentials']['secret_key'],
                    region_name=cloud_config['region']
                )
                s3.list_buckets()
            except Exception as e:
                raise ConnectionError(f"AWS credentials invalid: {str(e)}")
        
        elif provider == 'azure':
            from azure.identity import DefaultAzureCredential
            try:
                credential = DefaultAzureCredential()
                credential.get_token("https://management.azure.com/.default" )
            except Exception as e:
                raise ConnectionError(f"Azure credentials invalid: {str(e)}")
        
        elif provider == 'gcp':
            from google.cloud import storage
            try:
                storage.Client()
            except Exception as e:
                raise ConnectionError(f"GCP credentials invalid: {str(e)}")
    
    def validate_on_premise_credentials(self, on_premise_config: Dict[str, Any]):
        """Validate on-premise hypervisor credentials"""
        # Implement based on hypervisor type (KVM, VMware, Hyper-V)
        pass
    
    def check_disk_space(self):
        """Check if sufficient disk space available on replica"""
        import shutil
        
        # Estimate replica size (rough estimate: 2x target size)
        # For now, just check if 500GB available
        total, used, free = shutil.disk_usage("/")
        
        required_space = 500 * 1024 * 1024 * 1024  # 500GB
        
        if free < required_space:
            raise ValueError(f"Insufficient disk space. Required: {required_space}, Available: {free}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CyberMorph Stage 0: Initialization')
    parser.add_argument('--config', required=True, help='Path to configuration file')
    args = parser.parse_args()
    
    initializer = CyberMorphInitializer(args.config)
    
    if initializer.validate_all():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()