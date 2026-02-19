#!/usr/bin/env python3
"""
j1msky-init - Custom Init System for J1MSKY Framework
Replaces systemd for agent management - lightweight and autonomous
"""

import os
import sys
import json
import time
import signal
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/j1msky/init.log')
    ]
)
logger = logging.getLogger('j1msky-init')

@dataclass
class AgentConfig:
    """Configuration for an autonomous agent"""
    name: str
    command: str
    working_dir: str
    auto_start: bool = True
    restart_on_crash: bool = True
    max_restarts: int = 5
    restart_window: int = 60  # seconds
    env_vars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}

class AgentProcess:
    """Manages a single agent process"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.status = "STOPPED"
        self.start_time: Optional[datetime] = None
        self.restart_count = 0
        self.last_restart = 0
        self.log_file = Path(f"/var/log/j1msky/agents/{config.name}.log")
        self.pid_file = Path(f"/run/j1msky/{config.name}.pid")
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        
    def start(self) -> bool:
        """Start the agent process"""
        try:
            if self.process and self.process.poll() is None:
                logger.warning(f"Agent {self.config.name} already running (PID: {self.process.pid})")
                return False
                
            # Check restart limits
            current_time = time.time()
            if current_time - self.last_restart < self.config.restart_window:
                self.restart_count += 1
                if self.restart_count > self.config.max_restarts:
                    logger.error(f"Agent {self.config.name} exceeded max restarts")
                    self.status = "FAILED"
                    return False
            else:
                self.restart_count = 0
                
            # Prepare environment
            env = os.environ.copy()
            env.update(self.config.env_vars)
            env['J1MSKY_AGENT_NAME'] = self.config.name
            env['J1MSKY_AGENT_VERSION'] = '1.0'
            
            # Open log file
            log_fp = open(self.log_file, 'a')
            
            # Start process
            self.process = subprocess.Popen(
                self.config.command,
                shell=True,
                cwd=self.config.working_dir,
                env=env,
                stdout=log_fp,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid  # Create new process group
            )
            
            self.pid = self.process.pid
            self.start_time = datetime.now()
            self.status = "RUNNING"
            self.last_restart = current_time
            
            # Write PID file
            self.pid_file.write_text(str(self.pid))
            
            logger.info(f"Started agent {self.config.name} (PID: {self.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.config.name}: {e}")
            self.status = "ERROR"
            return False
            
    def stop(self, timeout: int = 10) -> bool:
        """Stop the agent process gracefully"""
        try:
            if not self.process or self.process.poll() is not None:
                self.status = "STOPPED"
                return True
                
            logger.info(f"Stopping agent {self.config.name} (PID: {self.pid})")
            self.status = "STOPPING"
            
            # Try graceful termination first
            self.process.terminate()
            
            # Wait for process to exit
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Force kill if necessary
                logger.warning(f"Force killing agent {self.config.name}")
                self.process.kill()
                self.process.wait()
                
            # Cleanup
            self.process = None
            self.pid = None
            self.status = "STOPPED"
            
            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
                
            logger.info(f"Agent {self.config.name} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping agent {self.config.name}: {e}")
            return False
            
    def restart(self) -> bool:
        """Restart the agent"""
        self.stop()
        time.sleep(1)
        return self.start()
        
    def is_running(self) -> bool:
        """Check if agent is running"""
        if self.process is None:
            return False
        return self.process.poll() is None
        
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'name': self.config.name,
            'status': self.status,
            'pid': self.pid,
            'running': self.is_running(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'restart_count': self.restart_count,
            'uptime': self._get_uptime()
        }
        
    def _get_uptime(self) -> Optional[str]:
        """Calculate uptime"""
        if not self.start_time or not self.is_running():
            return None
        delta = datetime.now() - self.start_time
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"

class J1MSKYInit:
    """Main init system for J1MSKY Framework"""
    
    def __init__(self, config_path: str = "/etc/j1msky/init.conf"):
        self.config_path = Path(config_path)
        self.agents: Dict[str, AgentProcess] = {}
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Ensure directories exist
        Path("/var/log/j1msky").mkdir(parents=True, exist_ok=True)
        Path("/run/j1msky").mkdir(parents=True, exist_ok=True)
        Path("/etc/j1msky").mkdir(parents=True, exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGHUP, self._handle_reload)
        
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown()
        
    def _handle_reload(self, signum, frame):
        """Handle config reload"""
        logger.info("Received SIGHUP, reloading configuration...")
        self.reload_config()
        
    def load_config(self) -> List[AgentConfig]:
        """Load agent configurations"""
        configs = []
        
        if not self.config_path.exists():
            # Create default config
            self._create_default_config()
            
        try:
            with open(self.config_path) as f:
                data = json.load(f)
                
            for agent_data in data.get('agents', []):
                configs.append(AgentConfig(**agent_data))
                
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Use default configs
            configs = self._get_default_agents()
            
        return configs
        
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            'agents': [
                {
                    'name': 'scout',
                    'command': 'python3 /home/m1ndb0t/Desktop/J1MSKY/agents/scout.py',
                    'working_dir': '/home/m1ndb0t/Desktop/J1MSKY',
                    'auto_start': True,
                    'restart_on_crash': True
                },
                {
                    'name': 'vitals',
                    'command': 'python3 /home/m1ndb0t/Desktop/J1MSKY/agents/vitals.py',
                    'working_dir': '/home/m1ndb0t/Desktop/J1MSKY',
                    'auto_start': True,
                    'restart_on_crash': True
                },
                {
                    'name': 'archivist',
                    'command': 'python3 /home/m1ndb0t/Desktop/J1MSKY/agents/archivist.py',
                    'working_dir': '/home/m1ndb0t/Desktop/J1MSKY',
                    'auto_start': True,
                    'restart_on_crash': True
                }
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        logger.info(f"Created default config at {self.config_path}")
        
    def _get_default_agents(self) -> List[AgentConfig]:
        """Get default agent configurations"""
        return [
            AgentConfig(
                name='scout',
                command='python3 /home/m1ndb0t/Desktop/J1MSKY/agents/scout.py',
                working_dir='/home/m1ndb0t/Desktop/J1MSKY'
            ),
            AgentConfig(
                name='vitals',
                command='python3 /home/m1ndb0t/Desktop/J1MSKY/agents/vitals.py',
                working_dir='/home/m1ndb0t/Desktop/J1MSKY'
            ),
            AgentConfig(
                name='archivist',
                command='python3 /home/m1ndb0t/Desktop/J1MSKY/agents/archivist.py',
                working_dir='/home/m1ndb0t/Desktop/J1MSKY'
            )
        ]
        
    def start(self):
        """Start the init system"""
        logger.info("◈ J1MSKY Init System Starting ◈")
        
        # Load configurations
        configs = self.load_config()
        
        # Create agent processes
        for config in configs:
            self.agents[config.name] = AgentProcess(config)
            
        # Start auto-start agents
        for name, agent in self.agents.items():
            if agent.config.auto_start:
                agent.start()
                time.sleep(0.5)  # Stagger starts
                
        self.running = True
        logger.info(f"Started {len(self.agents)} agents")
        
        # Main loop
        self._monitor_loop()
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Check agent health
                for name, agent in self.agents.items():
                    if agent.config.restart_on_crash and not agent.is_running():
                        if agent.status == "RUNNING":
                            logger.warning(f"Agent {name} crashed, restarting...")
                            agent.restart()
                            
                # Wait with interrupt handling
                self.shutdown_event.wait(timeout=5)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                
    def reload_config(self):
        """Reload configuration without stopping running agents"""
        configs = self.load_config()
        
        # Add new agents
        for config in configs:
            if config.name not in self.agents:
                self.agents[config.name] = AgentProcess(config)
                if config.auto_start:
                    self.agents[config.name].start()
                    
        logger.info("Configuration reloaded")
        
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down J1MSKY Init...")
        self.running = False
        self.shutdown_event.set()
        
        # Stop all agents
        for name, agent in self.agents.items():
            agent.stop()
            
        logger.info("Shutdown complete")
        
    def get_status(self) -> Dict:
        """Get status of all agents"""
        return {
            'running': self.running,
            'agents': {name: agent.get_status() for name, agent in self.agents.items()}
        }

def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='J1MSKY Init System')
    parser.add_argument('--config', '-c', default='/etc/j1msky/init.conf',
                       help='Configuration file path')
    parser.add_argument('--daemon', '-d', action='store_true',
                       help='Run as daemon')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'],
                       default='start', nargs='?')
    
    args = parser.parse_args()
    
    init = J1MSKYInit(config_path=args.config)
    
    if args.action == 'start':
        if args.daemon:
            # Daemonize
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
            os.setsid()
            
        init.start()
        
    elif args.action == 'stop':
        # Send signal to running init
        pid_file = Path('/run/j1msky/init.pid')
        if pid_file.exists():
            pid = int(pid_file.read_text())
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent stop signal to init (PID: {pid})")
        else:
            logger.error("Init not running")
            
    elif args.action == 'restart':
        # Stop then start
        pass
        
    elif args.action == 'status':
        import pprint
        status = init.get_status()
        pprint.pprint(status)

if __name__ == '__main__':
    main()
