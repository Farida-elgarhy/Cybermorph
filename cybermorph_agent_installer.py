#!/usr/bin/env python3
"""
CyberMorph Stage 1: Auto-Agent Installation
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
            self.install_wazuh_agent()
            self.logger.info("✓ Wazuh agent installed")
            
            # 2. Install Osquery
            self.logger.info("\n[2/4] Installing Osquery...")
            self.install_osquery()
            self.logger.info("✓ Osquery installed")
            
            # 3. Install Zeek
            self.logger.info("\n[3/4] Installing Zeek...")
            self.install_zeek()
            self.logger.info("✓ Zeek installed")
            
            # 4. Verify all agents running
            self.logger.info("\n[4/4] Verifying agents...")
            self.verify_agents_running()
            self.logger.info("✓ All agents verified running")
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("✓ STAGE 1 COMPLETE - READY FOR STAGE 2")
            self.logger.info("=" * 60)
            
            return True
        
        except Exception as e:
            self.logger.error(f"✗ Agent installation failed: {str(e)}", exc_info=True)
            return False
    
    def install_wazuh_agent(self):
        """Install Wazuh agent based on OS"""
        if self.os == "linux":
            self.install_wazuh_linux()
        elif self.os == "windows":
            self.install_wazuh_windows()
        elif self.os == "macos":
            self.install_wazuh_macos()
        else:
            raise ValueError(f"Unsupported OS: {self.os}")
    
    def install_wazuh_linux(self):
        """Install Wazuh agent on Linux"""
        commands = [
            # Add Wazuh repository
            "curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -",
            "echo 'deb https://packages.wazuh.com/4.x/apt/ stable main' > /etc/apt/sources.list.d/wazuh.list",
            
            # Install Wazuh agent
            "apt-get update",
            "apt-get install -y wazuh-agent",
            
            # Configure Wazuh agent
            "systemctl daemon-reload",
            "systemctl enable wazuh-agent",
            "systemctl start wazuh-agent",
            
            # Verify installation
            "systemctl status wazuh-agent"
        ]
        
        for cmd in commands:
            self.logger.debug(f"Executing: {cmd}" )
            stdin, stdout, stderr = self.target.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if error and "already" not in error.lower():
                self.logger.warning(f"Command output: {error}")
    
    def install_wazuh_windows(self):
        """Install Wazuh agent on Windows"""
        powershell_script = """
        $url = 'https://packages.wazuh.com/4.x/windows/wazuh-agent-4.7.0-1.msi'
        $output = 'C:\\wazuh-agent.msi'
        
        # Download
        (New-Object System.Net.WebClient ).DownloadFile($url, $output)
        
        # Install
        msiexec.exe /i $output /quiet
        
        # Start service
        Start-Service -Name WazuhSvc
        """
        
        self.execute_powershell(powershell_script)
    
    def install_wazuh_macos(self):
        """Install Wazuh agent on macOS"""
        commands = [
            "brew tap wazuh/wazuh",
            "brew install wazuh-agent",
            "sudo launchctl start com.wazuh.agent"
        ]
        
        for cmd in commands:
            self.logger.debug(f"Executing: {cmd}")
            stdin, stdout, stderr = self.target.exec_command(cmd)
            output = stdout.read().decode()
    
    def install_osquery(self):
        """Install Osquery based on OS"""
        if self.os == "linux":
            self.install_osquery_linux()
        elif self.os == "windows":
            self.install_osquery_windows()
        elif self.os == "macos":
            self.install_osquery_macos()
    
    def install_osquery_linux(self):
        """Install Osquery on Linux"""
        commands = [
            "apt-get update",
            "apt-get install -y osquery",
            "systemctl enable osqueryd",
            "systemctl start osqueryd",
            "systemctl status osqueryd"
        ]
        
        for cmd in commands:
            self.logger.debug(f"Executing: {cmd}")
            stdin, stdout, stderr = self.target.exec_command(cmd)
            output = stdout.read().decode()
    
    def install_osquery_windows(self):
        """Install Osquery on Windows"""
        powershell_script = """
        $url = 'https://osquery-packages.s3.amazonaws.com/windows/osquery-5.9.1.msi'
        $output = 'C:\\osquery.msi'
        
        (New-Object System.Net.WebClient ).DownloadFile($url, $output)
        msiexec.exe /i $output /quiet
        
        Start-Service -Name osqueryd
        """
        
        self.execute_powershell(powershell_script)
    
    def install_osquery_macos(self):
        """Install Osquery on macOS"""
        commands = [
            "brew install osquery",
            "sudo launchctl start com.facebook.osqueryd"
        ]
        
        for cmd in commands:
            self.logger.debug(f"Executing: {cmd}")
            stdin, stdout, stderr = self.target.exec_command(cmd)
            output = stdout.read().decode()
    
    def install_zeek(self):
        """Install Zeek based on OS"""
        if self.os == "linux":
            self.install_zeek_linux()
        elif self.os == "windows":
            self.logger.info("Zeek not typically installed on Windows, skipping...")
        elif self.os == "macos":
            self.install_zeek_macos()
    
    def install_zeek_linux(self):
        """Install Zeek on Linux"""
        commands = [
            "apt-get update",
            "apt-get install -y zeek",
            "systemctl enable zeek",
            "systemctl start zeek",
            "systemctl status zeek"
        ]
        
        for cmd in commands:
            self.logger.debug(f"Executing: {cmd}")
            stdin, stdout, stderr = self.target.exec_command(cmd)
            output = stdout.read().decode()
    
    def install_zeek_macos(self):
        """Install Zeek on macOS"""
        commands = [
            "brew install zeek",
            "sudo launchctl start com.zeek.zeek"
        ]
        
        for cmd in commands:
            self.logger.debug(f"Executing: {cmd}")
            stdin, stdout, stderr = self.target.exec_command(cmd)
            output = stdout.read().decode()
    
    def verify_agents_running(self):
        """Verify all agents are running"""
        agents = {
            'wazuh-agent': self.check_wazuh_running,
            'osquery': self.check_osquery_running,
            'zeek': self.check_zeek_running
        }
        
        max_retries = 30  # 5 minutes with 10-second intervals
        retry_count = 0
        
        while retry_count < max_retries:
            all_running = True
            
            for agent_name, check_func in agents.items():
                if not check_func():
                    all_running = False
                    self.logger.debug(f"{agent_name} not running yet, retrying...")
            
            if all_running:
                self.logger.info("✓ All agents verified running")
                return True
            
            retry_count += 1
            time.sleep(10)  # Wait 10 seconds before retrying
        
        raise RuntimeError("Agents failed to start after 5 minutes")
    
    def check_wazuh_running(self) -> bool:
        """Check if Wazuh agent is running"""
        try:
            if self.os == "linux":
                stdin, stdout, stderr = self.target.exec_command(
                    "systemctl is-active wazuh-agent"
                )
                status = stdout.read().decode().strip()
                return status == "active"
            elif self.os == "windows":
                # Check Windows service
                return self.check_windows_service("WazuhSvc")
        except:
            return False
    
    def check_osquery_running(self) -> bool:
        """Check if Osquery is running"""
        try:
            if self.os == "linux":
                stdin, stdout, stderr = self.target.exec_command(
                    "systemctl is-active osqueryd"
                )
                status = stdout.read().decode().strip()
                return status == "active"
            elif self.os == "windows":
                return self.check_windows_service("osqueryd")
        except:
            return False
    
    def check_zeek_running(self) -> bool:
        """Check if Zeek is running"""
        try:
            if self.os == "linux":
                stdin, stdout, stderr = self.target.exec_command(
                    "systemctl is-active zeek"
                )
                status = stdout.read().decode().strip()
                return status == "active"
        except:
            return False
        
        return True  # Skip for Windows/macOS
    
    def check_windows_service(self, service_name: str) -> bool:
        """Check if Windows service is running"""
        powershell_script = f"""
        $service = Get-Service -Name {service_name} -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq 'Running') {{
            Write-Host "running"
        }} else {{
            Write-Host "stopped"
        }}
        """
        
        output = self.execute_powershell(powershell_script)
        return "running" in output.lower()
    
    def execute_powershell(self, script: str) -> str:
        """Execute PowerShell script on Windows target"""
        stdin, stdout, stderr = self.target.exec_command(
            f"powershell -Command \"{script}\""
        )
        return stdout.read().decode()