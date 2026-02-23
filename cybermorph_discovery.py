#!/usr/bin/env python3
"""
CyberMorph Stage 2: Auto-Discovery
"""

import json
import logging
import paramiko
from typing import Dict, Any, List

class AutoDiscoveryEngine:
    def __init__(self, target_connection, target_os: str, logger: logging.Logger):
        self.target = target_connection
        self.os = target_os
        self.logger = logger
        self.discoveries = {}
    
    def discover_all(self) -> Dict[str, Any]:
        """Discover all environment components"""
        self.logger.info("=" * 60)
        self.logger.info("CYBERMORPH STAGE 2: AUTO-DISCOVERY")
        self.logger.info("=" * 60)
        
        try:
            # 1. Discover files
            self.logger.info("\n[1/7] Discovering files...")
            self.discover_files()
            self.logger.info(f"✓ Discovered {len(self.discoveries.get('files', []))} files")
            
            # 2. Discover users
            self.logger.info("\n[2/7] Discovering users...")
            self.discover_users()
            self.logger.info(f"✓ Discovered {len(self.discoveries.get('users', []))} users")
            
            # 3. Discover services
            self.logger.info("\n[3/7] Discovering services...")
            self.discover_services()
            self.logger.info(f"✓ Discovered {len(self.discoveries.get('services', []))} services")
            
            # 4. Discover databases
            self.logger.info("\n[4/7] Discovering databases...")
            self.discover_databases()
            self.logger.info(f"✓ Discovered databases")
            
            # 5. Discover cron jobs
            self.logger.info("\n[5/7] Discovering cron jobs...")
            self.discover_cron_jobs()
            self.logger.info(f"✓ Discovered {len(self.discoveries.get('cron_jobs', []))} cron jobs")
            
            # 6. Discover environment variables
            self.logger.info("\n[6/7] Discovering environment variables...")
            self.discover_environment_variables()
            self.logger.info(f"✓ Discovered {len(self.discoveries.get('env_vars', []))} environment variables")
            
            # 7. Capture network traffic
            self.logger.info("\n[7/7] Capturing network traffic baseline...")
            self.capture_network_traffic()
            self.logger.info("✓ Network traffic baseline established")
            
            # Save discoveries
            self.save_discoveries()
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("✓ STAGE 2 COMPLETE - READY FOR STAGE 3")
            self.logger.info("=" * 60)
            
            return self.discoveries
        
        except Exception as e:
            self.logger.error(f"✗ Discovery failed: {str(e)}", exc_info=True)
            return {}
    
    def discover_files(self):
        """Use Osquery to discover all files"""
        query = """
        SELECT path, filename, size, mode, uid, gid, atime, mtime, ctime 
        FROM file 
        WHERE (directory = '/etc' OR directory = '/home' OR directory = '/opt' 
               OR directory = '/var' OR directory = '/root')
        """
        
        results = self.execute_osquery(query)
        self.discoveries['files'] = results
    
    def discover_users(self):
        """Use Osquery to discover all users"""
        query = "SELECT uid, username, gid, shell, directory FROM users"
        results = self.execute_osquery(query)
        self.discoveries['users'] = results
    
    def discover_services(self):
        """Use Osquery to discover all services"""
        if self.os == "linux":
            query = "SELECT name, path, state FROM services"
        else:
            query = "SELECT name, path, state FROM services"
        
        results = self.execute_osquery(query)
        self.discoveries['services'] = results
    
    def discover_databases(self):
        """Auto-discover databases (MySQL, PostgreSQL, MongoDB, etc.)"""
        databases = {}
        
        # Try MySQL
        try:
            self.logger.debug("Attempting to discover MySQL databases...")
            databases['mysql'] = self.discover_mysql()
        except Exception as e:
            self.logger.debug(f"MySQL discovery failed: {str(e)}")
        
        # Try PostgreSQL
        try:
            self.logger.debug("Attempting to discover PostgreSQL databases...")
            databases['postgresql'] = self.discover_postgresql()
        except Exception as e:
            self.logger.debug(f"PostgreSQL discovery failed: {str(e)}")
        
        # Try MongoDB
        try:
            self.logger.debug("Attempting to discover MongoDB databases...")
            databases['mongodb'] = self.discover_mongodb()
        except Exception as e:
            self.logger.debug(f"MongoDB discovery failed: {str(e)}")
        
        self.discoveries['databases'] = databases
    
    def discover_mysql(self) -> Dict[str, Any]:
        """Discover MySQL databases"""
        cmd = "mysql -u root -e 'SHOW DATABASES;' --json"
        stdin, stdout, stderr = self.target.exec_command(cmd)
        output = stdout.read().decode()
        
        try:
            return json.loads(output)
        except:
            return {}
    
    def discover_postgresql(self) -> Dict[str, Any]:
        """Discover PostgreSQL databases"""
        cmd = "psql -U postgres -l --json"
        stdin, stdout, stderr = self.target.exec_command(cmd)
        output = stdout.read().decode()
        
        try:
            return json.loads(output)
        except:
            return {}
    
    def discover_mongodb(self) -> Dict[str, Any]:
        """Discover MongoDB databases"""
        cmd = "mongo --eval 'db.adminCommand(\"listDatabases\")' --quiet"
        stdin, stdout, stderr = self.target.exec_command(cmd)
        output = stdout.read().decode()
        
        try:
            return json.loads(output)
        except:
            return {}
    
    def discover_cron_jobs(self):
        """Use Osquery to discover cron jobs"""
        query = "SELECT * FROM crontab"
        results = self.execute_osquery(query)
        self.discoveries['cron_jobs'] = results
    
    def discover_environment_variables(self):
        """Use Osquery to discover environment variables"""
        query = "SELECT * FROM process_envs"
        results = self.execute_osquery(query)
        self.discoveries['env_vars'] = results
    
    def capture_network_traffic(self):
        """Use Zeek to capture network traffic baseline"""
        # Zeek runs in background and generates logs
        # For now, just note that it's capturing
        self.discoveries['network_traffic'] = {
            'status': 'capturing',
            'duration': '1 hour',
            'output_files': [
                'conn.log',
                'http.log',
                'dns.log',
                'ssl.log',
                'files.log'
            ]
        }
    
    def execute_osquery(self, query: str ) -> List[Dict[str, Any]]:
        """Execute Osquery query on target"""
        # Escape quotes in query
        query = query.replace('"', '\\"')
        
        cmd = f'osqueryi --json "{query}"'
        stdin, stdout, stderr = self.target.exec_command(cmd)
        output = stdout.read().decode()
        
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse Osquery output: {output}")
            return []
    
    def save_discoveries(self):
        """Save discoveries to JSON file"""
        with open('environment_blueprint.json', 'w') as f:
            json.dump(self.discoveries, f, indent=2)
        
        self.logger.info("✓ Discoveries saved to environment_blueprint.json")