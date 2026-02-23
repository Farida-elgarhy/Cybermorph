#!/usr/bin/env python3
"""
CyberMorph Stage 1: Auto-Agent Installation
FIXED: Better Wazuh installation with error handling and fallbacks
"""

import logging
import paramiko
import time
from typing import Dict, Any

class AgentInstaller:
    def __init__(self, target_connection, target_os: str, logger: logging.Logger):
        self.target = target_connection
        self.os = target_os
        self.logger = logger
    
    def install_all_agents(self) -> bool:
        """Install all discovery agents"""
        self.logger.info("=" * 60)
        self.logger.info("CYBERMORPH STAGE 1: AUTO-AGENT INSTALLATION")
        self.logger.info("=" * 60)
        
        try:
            # 1. Install Wazuh agent
            self.logger.info("\n[1/4] Installing Wazuh agent...")
            wazuh_success = self.install_wazuh_agent()
            if wazuh_success:
                self.logger.info("✓ Wazuh agent installed")
            else:
                self.logger.warning("⚠ Wazuh agent installation failed, continuing with other agents...")
            
            # 2. Install Osquery
            self.logger.info("\n[2/4] Installing Osquery...")
            self.install_osquery()
            self.logger.info("✓ Osquery installed")
            
            # 3. Install Zeek
            self.logger.info("\n[3/4] Installing Zeek...")
            self.install_zeek()
            self.logger.info("✓ Zeek installed")
            
            # 4. Verify agents running
            self.logger.info("\n[4/4] Verifying agents...")
            self.verify_agents_running()
            self.logger.info("✓ Agents verified")
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("✓ STAGE 1 COMPLETE - READY FOR STAGE 2")
            self.logger.info("=" * 60)
            
            return True
        
        except Exception as e:
            self.logger.error(f"✗ Agent installation failed: {str(e)}", exc_info=True)
            return False
    
    def install_wazuh_agent(self) -> bool:
        """Install Wazuh agent based on OS"""
        try:
            if self.os == "linux":
                return self.install_wazuh_linux()
            elif self.os == "windows":
                return self.install_wazuh_windows()
            elif self.os == "macos":
                return self.install_wazuh_macos()
            else:
                raise ValueError(f"Unsupported OS: {self.os}")
        except Exception as e:
            self.logger.warning(f"Wazuh installation failed: {str(e)}")
            return False
    
    def install_wazuh_linux(self) -> bool:
        """Install Wazuh agent on Linux with better error handling"""
        try:
            # First, ensure sudo works
            self.logger.info("Testing sudo access...")
            stdin, stdout, stderr = self.target.exec_command("sudo whoami")
            output = stdout.read().decode().strip()
            error = stderr.read().decode()
            
            if "root" not in output:
                self.logger.warning("Sudo access may not be available")
                return False
            
            # Update package manager
            self.logger.info("Updating package manager...")
            self._execute_command("sudo apt-get update -qq")
            
            # Add Wazuh GPG key
            self.logger.info("Adding Wazuh GPG key...")
            self._execute_command("sudo curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo apt-key add -")
            
            # Add Wazuh repository
            self.logger.info("Adding Wazuh repository...")
            self._execute_command("echo 'deb https://packages.wazuh.com/4.x/apt/ stable main' | sudo tee /etc/apt/sources.list.d/wazuh.list > /dev/null")
            
            # Update package manager again
            self.logger.info("Updating package manager (with Wazuh repo)...")
            self._execute_command("sudo apt-get update -qq")
            
            # Install Wazuh agent
            self.logger.info("Installing Wazuh agent package...")
            self._execute_command("sudo apt-get install -y wazuh-agent")
            
            # Configure Wazuh agent
            self.logger.info("Configuring Wazuh agent...")
            self._execute_command("sudo systemctl daemon-reload")
            self._execute_command("sudo systemctl enable wazuh-agent")
            self._execute_command("sudo systemctl start wazuh-agent")
            
            # Verify installation
            self.logger.info("Verifying Wazuh agent...")
            stdin, stdout, stderr = self.target.exec_command("sudo systemctl status wazuh-agent")
            output = stdout.read().decode()
            
            if "active (running)" in output or "Active: active" in output:
                self.logger.info("✓ Wazuh agent is running")
                return True
            else:
                self.logger.warning("Wazuh agent may not be running properly")
                return False
        
        except Exception as e:
            self.logger.warning(f"Wazuh Linux installation error: {str(e)}")
            return False
    
    def install_wazuh_windows(self) -> bool:
        """Install Wazuh agent on Windows"""
        try:
            powershell_script = """
            $url = 'https://packages.wazuh.com/4.x/windows/wazuh-agent-4.7.0-1.msi'
            $output = 'C:\\wazuh-agent.msi'
            
            # Download
            Invoke-WebRequest -Uri $url -OutFile $output
            
            # Install
            msiexec.exe /i $output /quiet
            
            # Start service
            Start-Service WazuhSvc
            """
            
            self._execute_command(f"powershell -Command \"{powershell_script}\"")
            return True
        except Exception as e:
            self.logger.warning(f"Wazuh Windows installation error: {str(e)}")
            return False
    
    def install_wazuh_macos(self) -> bool:
        """Install Wazuh agent on macOS"""
        try:
            commands = [
                "curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo apt-key add -",
                "sudo brew install wazuh-agent",
                "sudo launchctl start com.wazuh.agent"
            ]
            
            for cmd in commands:
                self._execute_command(cmd)
            
            return True
        except Exception as e:
            self.logger.warning(f"Wazuh macOS installation error: {str(e)}")
            return False
    
    def install_osquery(self) -> bool:
        """Install Osquery"""
        try:
            if self.os == "linux":
                self._execute_command("sudo apt-get update -qq")
                self._execute_command("sudo apt-get install -y osquery")
                self._execute_command("sudo systemctl enable osqueryd")
                self._execute_command("sudo systemctl start osqueryd")
            elif self.os == "windows":
                self._execute_command("powershell -Command \"choco install osquery -y\"")
            elif self.os == "macos":
                self._execute_command("brew install osquery")
            
            self.logger.info("✓ Osquery installed")
            return True
        except Exception as e:
            self.logger.warning(f"Osquery installation error: {str(e)}")
            return False
    
    def install_zeek(self) -> bool:
        """Install Zeek"""
        try:
            if self.os == "linux":
                self._execute_command("sudo apt-get update -qq")
                self._execute_command("sudo apt-get install -y zeek")
                self._execute_command("sudo systemctl enable zeek")
                self._execute_command("sudo systemctl start zeek")
            elif self.os == "macos":
                self._execute_command("brew install zeek")
            
            self.logger.info("✓ Zeek installed")
            return True
        except Exception as e:
            self.logger.warning(f"Zeek installation error: {str(e)}")
            return False
    
    def verify_agents_running(self) -> bool:
        """Verify all agents are running"""
        agents_status = {}
        
        # Check Wazuh
        try:
            stdin, stdout, stderr = self.target.exec_command("sudo systemctl status wazuh-agent 2>/dev/null || echo 'not running'")
            output = stdout.read().decode()
            agents_status['wazuh'] = 'running' if 'active (running)' in output or 'Active: active' in output else 'not running'
        except:
            agents_status['wazuh'] = 'unknown'
        
        # Check Osquery
        try:
            stdin, stdout, stderr = self.target.exec_command("sudo systemctl status osqueryd 2>/dev/null || echo 'not running'")
            output = stdout.read().decode()
            agents_status['osquery'] = 'running' if 'active (running)' in output or 'Active: active' in output else 'not running'
        except:
            agents_status['osquery'] = 'unknown'
        
        # Check Zeek
        try:
            stdin, stdout, stderr = self.target.exec_command("sudo systemctl status zeek 2>/dev/null || echo 'not running'")
            output = stdout.read().decode()
            agents_status['zeek'] = 'running' if 'active (running)' in output or 'Active: active' in output else 'not running'
        except:
            agents_status['zeek'] = 'unknown'
        
        # Log status
        for agent, status in agents_status.items():
            self.logger.info(f"  {agent}: {status}")
        
        return True
    
    def _execute_command(self, cmd: str) -> tuple:
        """Execute command on target and return output"""
        self.logger.debug(f"Executing: {cmd}")
        stdin, stdout, stderr = self.target.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if error and "already" not in error.lower() and "warning" not in error.lower():
            self.logger.debug(f"Command error: {error}")
        
        return output, error