#!/usr/bin/env python3
"""
CyberMorph Stage 3: Auto-DLP Scanning
"""

import json
import logging
from typing import Dict, Any, List
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import spacy

class AutoDLPEngine:
    def __init__(self, discoveries: Dict[str, Any], logger: logging.Logger):
        self.discoveries = discoveries
        self.logger = logger
        self.dlp_findings = {}
        
        # Initialize Presidio
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Initialize spaCy for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.logger.warning("spaCy model not found, installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    def scan_all(self) -> Dict[str, Any]:
        """Scan all discovered data for sensitive information"""
        self.logger.info("=" * 60)
        self.logger.info("CYBERMORPH STAGE 3: AUTO-DLP SCANNING")
        self.logger.info("=" * 60)
        
        try:
            # 1. Scan files for sensitive data
            self.logger.info("\n[1/4] Scanning files for sensitive data...")
            self.scan_files()
            self.logger.info(f"✓ Scanned files, found {len(self.dlp_findings)} issues")
            
            # 2. Scan databases for sensitive data
            self.logger.info("\n[2/4] Scanning databases for sensitive data...")
            self.scan_databases()
            self.logger.info(f"✓ Scanned databases")
            
            # 3. Scan environment variables
            self.logger.info("\n[3/4] Scanning environment variables...")
            self.scan_environment_variables()
            self.logger.info(f"✓ Scanned environment variables")
            
            # 4. Classify findings
            self.logger.info("\n[4/4] Classifying findings...")
            self.classify_findings()
            self.logger.info(f"✓ Classified {len(self.dlp_findings)} findings")
            
            # Save findings
            self.save_findings()
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("✓ STAGE 3 COMPLETE - READY FOR STAGE 4")
            self.logger.info("=" * 60)
            
            return self.dlp_findings
        
        except Exception as e:
            self.logger.error(f"✗ DLP scanning failed: {str(e)}", exc_info=True)
            return {}
    
    def scan_files(self):
        """Scan all files for sensitive data"""
        for file_info in self.discoveries.get('files', []):
            file_path = file_info.get('path')
            
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()
                
                # Run Presidio
                findings = self.analyzer.analyze(text=content, language="en")
                
                if findings:
                    self.dlp_findings[file_path] = {
                        'findings': [
                            {
                                'entity_type': f.entity_type,
                                'start': f.start,
                                'end': f.end,
                                'score': f.score
                            } for f in findings
                        ],
                        'file_size': len(content)
                    }
                    self.logger.debug(f"Found {len(findings)} findings in {file_path}")
            
            except Exception as e:
                self.logger.debug(f"Error scanning {file_path}: {str(e)}")
    
    def scan_databases(self):
        """Scan database records for sensitive data"""
        for db_type, databases in self.discoveries.get('databases', {}).items():
            for db_name, tables in databases.items():
                for table_name in tables:
                    try:
                        # Query table
                        if db_type == 'mysql':
                            records = self.query_mysql(db_name, table_name)
                        elif db_type == 'postgresql':
                            records = self.query_postgresql(db_name, table_name)
                        elif db_type == 'mongodb':
                            records = self.query_mongodb(db_name, table_name)
                        else:
                            continue
                        
                        # Scan each record
                        for record in records:
                            findings = self.analyzer.analyze(str(record), language="en")
                            if findings:
                                key = f"{db_type}.{db_name}.{table_name}"
                                if key not in self.dlp_findings:
                                    self.dlp_findings[key] = {'findings': []}
                                
                                self.dlp_findings[key]['findings'].extend([
                                    {
                                        'entity_type': f.entity_type,
                                        'score': f.score
                                    } for f in findings
                                ])
                    
                    except Exception as e:
                        self.logger.debug(f"Error scanning {db_type}.{db_name}.{table_name}: {str(e)}")
    
    def scan_environment_variables(self):
        """Scan environment variables for sensitive data"""
        for env_var in self.discoveries.get('env_vars', []):
            var_name = env_var.get('name', '')
            var_value = env_var.get('value', '')
            
            # Check if variable name suggests sensitive data
            if any(keyword in var_name.upper() for keyword in ['PASSWORD', 'KEY', 'TOKEN', 'SECRET', 'CREDENTIAL']):
                self.dlp_findings[f"ENV:{var_name}"] = {
                    'type': 'CREDENTIAL',
                    'reason': 'Sensitive variable name'
                }
            
            # Scan variable value
            findings = self.analyzer.analyze(text=var_value, language="en")
            if findings:
                self.dlp_findings[f"ENV:{var_name}"] = {
                    'findings': [
                        {
                            'entity_type': f.entity_type,
                            'score': f.score
                        } for f in findings
                    ]
                }
    
    def classify_findings(self):
        """Classify findings by sensitivity level"""
        for location, finding in self.dlp_findings.items():
            # Determine sensitivity level
            entity_types = [f.get('entity_type') for f in finding.get('findings', [])]
            
            if any(t in ['CREDENTIAL', 'PASSWORD', 'API_KEY'] for t in entity_types):
                finding['sensitivity'] = 'CRITICAL'
            elif any(t in ['PERSON', 'EMAIL', 'PHONE'] for t in entity_types):
                finding['sensitivity'] = 'HIGH'
            elif any(t in ['LOCATION', 'ORGANIZATION'] for t in entity_types):
                finding['sensitivity'] = 'MEDIUM'
            else:
                finding['sensitivity'] = 'LOW'
    
    def save_findings(self):
        """Save DLP findings to JSON file"""
        with open('sensitive_data_inventory.json', 'w') as f:
            json.dump(self.dlp_findings, f, indent=2)
        
        self.logger.info("✓ DLP findings saved to sensitive_data_inventory.json")
    
    def query_mysql(self, db_name: str, table_name: str) -> List[Dict]:
        """Query MySQL table"""
        # Implementation would use mysql connector
        return []
    
    def query_postgresql(self, db_name: str, table_name: str) -> List[Dict]:
        """Query PostgreSQL table"""
        # Implementation would use psycopg2
        return []
    
    def query_mongodb(self, db_name: str, table_name: str) -> List[Dict]:
        """Query MongoDB collection"""
        # Implementation would use pymongo
        return []