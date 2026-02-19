"""
J1MSKY Agent SDK
Standardized way to build autonomous agents for J1MSKY Framework
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
import logging
import time
import threading

logger = logging.getLogger('j1msky.sdk')

@dataclass
class AgentMetadata:
    """Agent metadata"""
    name: str
    version: str
    description: str
    author: str
    dependencies: list
    config_schema: Dict[str, Any]

class J1MSKYAgent(ABC):
    """Base class for all J1MSKY agents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metadata = self._get_metadata()
        self.running = False
        self.status = "INITIALIZED"
        self.stats = {
            'start_time': None,
            'tasks_completed': 0,
            'errors': 0,
            'last_activity': None
        }
        self._event_handlers: Dict[str, Callable] = {}
        
    @abstractmethod
    def _get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass
        
    @abstractmethod
    def run_cycle(self):
        """Main agent logic - called repeatedly"""
        pass
        
    def start(self):
        """Start the agent"""
        logger.info(f"Starting agent: {self.metadata.name}")
        self.running = True
        self.status = "RUNNING"
        self.stats['start_time'] = datetime.now()
        
        try:
            self.on_start()
            self._main_loop()
        except Exception as e:
            logger.error(f"Agent error: {e}")
            self.status = "ERROR"
            self.on_error(e)
            
    def stop(self):
        """Stop the agent gracefully"""
        logger.info(f"Stopping agent: {self.metadata.name}")
        self.running = False
        self.status = "STOPPED"
        self.on_stop()
        
    def _main_loop(self):
        """Internal main loop"""
        while self.running:
            try:
                self.run_cycle()
                self.stats['last_activity'] = datetime.now()
                time.sleep(self._get_interval())
            except Exception as e:
                logger.error(f"Cycle error: {e}")
                self.stats['errors'] += 1
                self.on_error(e)
                
    def _get_interval(self) -> float:
        """Get cycle interval (can be overridden)"""
        return self.config.get('interval', 5.0)
        
    # Event handlers (override as needed)
    def on_start(self):
        """Called when agent starts"""
        pass
        
    def on_stop(self):
        """Called when agent stops"""
        pass
        
    def on_error(self, error: Exception):
        """Called on error"""
        pass
        
    # Event system
    def emit(self, event: str, data: Dict):
        """Emit an event"""
        if event in self._event_handlers:
            self._event_handlers[event](data)
            
    def on_event(self, event: str, handler: Callable):
        """Register event handler"""
        self._event_handlers[event] = handler
        
    # Utility methods
    def log(self, message: str, level: str = "info"):
        """Log message"""
        getattr(logger, level)(f"[{self.metadata.name}] {message}")
        
    def report_status(self) -> Dict[str, Any]:
        """Get current status report"""
        return {
            'name': self.metadata.name,
            'version': self.metadata.version,
            'status': self.status,
            'stats': self.stats,
            'config': self.config
        }

class AgentBus:
    """Inter-agent communication bus"""
    
    def __init__(self):
        self._agents: Dict[str, J1MSKYAgent] = {}
        self._subscribers: Dict[str, list] = {}
        
    def register(self, agent: J1MSKYAgent):
        """Register an agent"""
        self._agents[agent.metadata.name] = agent
        agent.on_event('broadcast', self._handle_broadcast)
        
    def send(self, target: str, message: Dict):
        """Send message to specific agent"""
        if target in self._agents:
            self._agents[target].emit('message', message)
            
    def broadcast(self, message: Dict, exclude: str = None):
        """Broadcast to all agents"""
        for name, agent in self._agents.items():
            if name != exclude:
                agent.emit('broadcast', message)
                
    def subscribe(self, event: str, callback: Callable):
        """Subscribe to event type"""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)
        
    def _handle_broadcast(self, data):
        """Handle broadcast messages"""
        # Route to subscribers
        pass

# Example agents using SDK
class ExampleScoutAgent(J1MSKYAgent):
    """Example news scouting agent"""
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="scout",
            version="2.0",
            description="Fetches news from RSS feeds",
            author="J1MSKY",
            dependencies=["feedparser", "requests"],
            config_schema={
                "feeds": {"type": "list", "default": []},
                "interval": {"type": "int", "default": 300}
            }
        )
        
    def run_cycle(self):
        """Fetch news"""
        feeds = self.config.get('feeds', [])
        self.log(f"Checking {len(feeds)} feeds")
        # Fetch logic here
        self.stats['tasks_completed'] += 1

# Decorator for quick agent creation
def agent(metadata: AgentMetadata):
    """Decorator to create agent class"""
    def decorator(cls):
        cls._metadata = metadata
        return cls
    return decorator

# Export
__all__ = [
    'J1MSKYAgent',
    'AgentMetadata',
    'AgentBus',
    'agent'
]
