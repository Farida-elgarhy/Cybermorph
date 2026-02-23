#!/usr/bin/env python3
"""
CyberMorph: Fully Automated One-Command Execution
No configuration files needed - everything is automatic
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any

from cybermorph_auto_config import AutoConfigGenerator
from cybermorph_init import CyberMorphInitializer
from cybermorph_agent_installer import AgentInstaller
from cybermorph_discovery import AutoDiscoveryEngine
from cybermorph_dlp import AutoDLPEngine
from cybermorph_sanitization import AutoSanitizationEngine
from cybermorph_docker_provisioner import DockerReplicaProvisioner
from cybermorph_n8n_orchestrator import N8nOrchestrator

class CyberMorphAuto:
    """Fully automated CyberMorph with zero configuration"""
    
    def __init__(self, target_host: str, target_user: str, target_password: str = None, 
                 target_key: str = None, log_level: str = 'INFO'):
        """
        Initialize CyberMorph with minimal parameters
        
        Args:
            target_host: IP or hostname of target server
            target_user: SSH username for target
            target_password: SSH password (optional, use key if available)
            target_key: SSH key file path (optional)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.target_host = target_host
        self.target_user = target_user
        self.target_password = target_password
        self.target_key = target_key
        
        # Setup logging
        self.logger = self._setup_logging(log_level)
        
        # Auto-generate configuration
        self.config = None
        self.auto_config_generator = None
        
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('CyberMorph')
        logger.setLevel(getattr(logging, log_level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def run(self) -> int:
        """Execute full CyberMorph pipeline automatically"""
        try:
            self.logger.info("\n" + "=" * 70)
            self.logger.info("CYBERMORPH: FULLY AUTOMATED ENVIRONMENT REPLICATION")
            self.logger.info("=" * 70)
            
            # STAGE 0: Auto-generate configuration
            self.logger.info("\n[STAGE 0] Auto-generating configuration...")
            self._stage_0_auto_config()
            
            # STAGE 1: Initialization & Validation
            self.logger.info("\n[STAGE 1] Initialization & Validation...")
            self._stage_1_init_validation()
            
            # STAGE 2: Agent Installation
            self.logger.info("\n[STAGE 2] Installing discovery agents...")
            self._stage_2_agent_installation()
            
            # STAGE 3: Auto-Discovery
            self.logger.info("\n[STAGE 3] Discovering environment...")
            discoveries = self._stage_3_discovery()
            
            # STAGE 4: DLP Scanning
            self.logger.info("\n[STAGE 4] Scanning for sensitive data...")
            dlp_findings = self._stage_4_dlp_scanning(discoveries)
            
            # STAGE 5: Sanitization
            self.logger.info("\n[STAGE 5] Sanitizing sensitive data...")
            synthetic_data = self._stage_5_sanitization(discoveries, dlp_findings)
            
            # STAGE 6: Docker Replica Provisioning
            self.logger.info("\n[STAGE 6] Provisioning Docker replica environment...")
            replica_info = self._stage_6_docker_provisioning(discoveries, synthetic_data)
            
            # STAGE 7: n8n Orchestration Setup
            self.logger.info("\n[STAGE 7] Setting up n8n orchestration...")
            self._stage_7_n8n_setup(replica_info)
            
            # STAGE 8: Validation
            self.logger.info("\n[STAGE 8] Validating replica environment...")
            self._stage_8_validation(replica_info)
            
            self.logger.info("\n" + "=" * 70)
            self.logger.info("✓ CYBERMORPH EXECUTION COMPLETE")
            self.logger.info("=" * 70)
            self.logger.info("\nReplica Environment Details:")
            self.logger.info(f"  - Docker Container: {replica_info['container_name']}")
            self.logger.info(f"  - IP Address: {replica_info['ip_address']}")
            self.logger.info(f"  - SSH Port: {replica_info['ssh_port']}")
            self.logger.info(f"  - HTTP Port: {replica_info['http_port']}" )
            self.logger.info(f"  - Files: {len(discoveries['files'])} (all sanitized)")
            self.logger.info(f"  - Users: {len(discoveries['users'])} (all synthetic)")
            self.logger.info(f"  - Services: {len(discoveries['services'])} (all configured)")
            self.logger.info(f"\nn8n Orchestration: http://localhost:5678" )
            self.logger.info(f"Kibana Monitoring: http://localhost:5601" )
            
            return 0
        
        except Exception as e:
            self.logger.error(f"✗ CyberMorph failed: {str(e)}", exc_info=True)
            return 1
    
    def _stage_0_auto_config(self):
        """Auto-generate configuration without config file"""
        self.auto_config_generator = AutoConfigGenerator(
            target_host=self.target_host,
            target_user=self.target_user,
            target_password=self.target_password,
            target_key=self.target_key,
            logger=self.logger
        )
        
        self.config = self.auto_config_generator.generate_config()
        self.logger.info("✓ Configuration auto-generated")
    
    def _stage_1_init_validation(self):
        """Initialize and validate"""
        # Create temporary config file from auto-generated config
        config_file = self.auto_config_generator.save_temp_config(self.config)
        
        initializer = CyberMorphInitializer(config_file)
        if not initializer.validate_all():
            raise Exception("Initialization validation failed")
        
        self.initializer = initializer
        self.logger.info("✓ Initialization complete")
    
    def _stage_2_agent_installation(self):
        """Install discovery agents"""
        agent_installer = AgentInstaller(
            self.initializer.target_connection,
            self.initializer.target_os,
            self.logger
        )
        
        if not agent_installer.install_all_agents():
            raise Exception("Agent installation failed")
        
        self.logger.info("✓ All agents installed")
    
    def _stage_3_discovery(self) -> Dict[str, Any]:
        """Auto-discover environment"""
        discovery_engine = AutoDiscoveryEngine(
            self.initializer.target_connection,
            self.initializer.target_os,
            self.logger
        )
        
        discoveries = discovery_engine.discover_all()
        self.logger.info(f"✓ Discovery complete: {len(discoveries['files'])} files, "
                        f"{len(discoveries['users'])} users, "
                        f"{len(discoveries['services'])} services")
        
        return discoveries
    
    def _stage_4_dlp_scanning(self, discoveries: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for sensitive data"""
        dlp_engine = AutoDLPEngine(discoveries, self.logger)
        dlp_findings = dlp_engine.scan_all()
        
        self.logger.info(f"✓ DLP scanning complete: {len(dlp_findings)} findings")
        
        return dlp_findings
    
    def _stage_5_sanitization(self, discoveries: Dict[str, Any], 
                              dlp_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data"""
        sanitization_engine = AutoSanitizationEngine(discoveries, dlp_findings, self.logger)
        synthetic_data = sanitization_engine.sanitize_all()
        
        self.logger.info("✓ Sanitization complete: all sensitive data replaced")
        
        return synthetic_data
    
    def _stage_6_docker_provisioning(self, discoveries: Dict[str, Any], 
                                     synthetic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provision Docker replica environment"""
        provisioner = DockerReplicaProvisioner(
            discoveries=discoveries,
            synthetic_data=synthetic_data,
            logger=self.logger
        )
        
        replica_info = provisioner.provision_replica()
        self.logger.info(f"✓ Docker replica provisioned: {replica_info['container_name']}")
        
        return replica_info
    
    def _stage_7_n8n_setup(self, replica_info: Dict[str, Any]):
        """Setup n8n orchestration"""
        orchestrator = N8nOrchestrator(
            replica_info=replica_info,
            logger=self.logger
        )
        
        orchestrator.setup_workflows()
        self.logger.info("✓ n8n orchestration configured")
    
    def _stage_8_validation(self, replica_info: Dict[str, Any]):
        """Validate replica environment"""
        provisioner = DockerReplicaProvisioner(
            discoveries={},
            synthetic_data={},
            logger=self.logger
        )
        
        if provisioner.validate_replica(replica_info):
            self.logger.info("✓ Replica validation successful")
        else:
            raise Exception("Replica validation failed")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CyberMorph: Fully Automated Environment Replication',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fully automated with SSH key
  cybermorph-auto --host 192.168.1.100 --user admin --key ~/.ssh/id_rsa
  
  # Fully automated with password
  cybermorph-auto --host 192.168.1.100 --user admin --password 'your_password'
  
  # With debug logging
  cybermorph-auto --host 192.168.1.100 --user admin --key ~/.ssh/id_rsa --log-level DEBUG
        """
    )
    
    parser.add_argument('--host', required=True, help='Target server IP or hostname')
    parser.add_argument('--user', required=True, help='SSH username')
    parser.add_argument('--password', help='SSH password (optional, use --key if available)')
    parser.add_argument('--key', help='SSH private key file path')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Run CyberMorph
    cybermorph = CyberMorphAuto(
        target_host=args.host,
        target_user=args.user,
        target_password=args.password,
        target_key=args.key,
        log_level=args.log_level
    )
    
    return cybermorph.run()


if __name__ == '__main__':
    sys.exit(main())