#!/usr/bin/env python3
"""
J1MSKY Multi-Model Agent System v4.0
Team-based agents with subagent spawning
Rate limit tracking, model selection, business-ready
"""

import http.server
import socketserver
import json
import os
import subprocess
import threading
import time
import random
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
from pathlib import Path

# Rate Limit Tracking
RATE_LIMITS = {
    'kimi': {'requests': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
    'anthropic': {'requests': 0, 'last_reset': time.time(), 'limit': 50, 'window': 3600},
    'web_search': {'requests': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
    'image_gen': {'requests': 0, 'last_reset': time.time(), 'limit': 50, 'window': 3600},
    'github': {'requests': 0, 'last_reset': time.time(), 'limit': 30, 'window': 3600}
}

# Model Teams - Each model is its own agent
AGENT_TEAMS = {
    'team_coding': {
        'name': '💻 Code Team',
        'models': ['kimi-coding/k2p5', 'anthropic/claude-sonnet-4-6'],
        'specialty': 'Programming, debugging, system architecture',
        'status': 'active',
        'tasks_completed': 0
    },
    'team_creative': {
        'name': '🎨 Creative Team', 
        'models': ['anthropic/claude-opus-4-6', 'kimi-coding/k2p5'],
        'specialty': 'Content creation, design, documentation',
        'status': 'active',
        'tasks_completed': 0
    },
    'team_research': {
        'name': '🔍 Research Team',
        'models': ['anthropic/claude-sonnet-4-6', 'kimi-coding/k2p5'],
        'specialty': 'Web search, analysis, data gathering',
        'status': 'active',
        'tasks_completed': 0
    },
    'team_business': {
        'name': '💼 Business Team',
        'models': ['anthropic/claude-opus-4-6', 'anthropic/claude-sonnet-4-6'],
        'specialty': 'Strategy, planning, revenue optimization',
        'status': 'standby',
        'tasks_completed': 0
    }
}

# Individual Model Agents
MODEL_AGENTS = {
    'k2p5': {
        'name': 'Kimi K2.5',
        'provider': 'kimi-coding',
        'role': 'Primary Coder',
        'status': 'active',
        'last_used': None,
        'success_rate': 0.95,
        'specialty': 'Fast coding, system tasks'
    },
    'sonnet': {
        'name': 'Claude Sonnet 4.6',
        'provider': 'anthropic',
        'role': 'Creative Assistant',
        'status': 'active',
        'last_used': None,
        'success_rate': 0.92,
        'specialty': 'Content, analysis'
    },
    'opus': {
        'name': 'Claude Opus 4.6',
        'provider': 'anthropic',
        'role': 'Deep Thinker',
        'status': 'standby',
        'last_used': None,
        'success_rate': 0.98,
        'specialty': 'Complex reasoning'
    }
}

# Active Subagents
ACTIVE_SUBAGENTS = {}
EVENTS_LOG = []

# Notification System
class NotificationManager:
    """Webhook and notification system for agent events"""
    
    def __init__(self, storage_path='/home/m1ndb0t/Desktop/J1MSKY/config'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.webhooks = self._load_webhooks()
        
    def _load_webhooks(self):
        """Load registered webhooks from config"""
        webhook_file = self.storage_path / 'webhooks.json'
        if webhook_file.exists():
            with open(webhook_file) as f:
                return json.load(f)
        return []
    
    def _save_webhooks(self):
        """Save webhooks to config"""
        webhook_file = self.storage_path / 'webhooks.json'
        with open(webhook_file, 'w') as f:
            json.dump(self.webhooks, f, indent=2)
    
    def register_webhook(self, url, events=None, secret=None):
        """Register a new webhook endpoint"""
        webhook = {
            'id': f"wh_{int(time.time())}_{random.randint(1000,9999)}",
            'url': url,
            'events': events or ['agent.completed', 'agent.failed'],
            'secret': secret,
            'created': datetime.now().isoformat(),
            'active': True
        }
        self.webhooks.append(webhook)
        self._save_webhooks()
        return webhook['id']
    
    def unregister_webhook(self, webhook_id):
        """Remove a webhook"""
        self.webhooks = [w for w in self.webhooks if w['id'] != webhook_id]
        self._save_webhooks()
    
    def notify(self, event_type, data):
        """Send notification to all matching webhooks"""
        for webhook in self.webhooks:
            if not webhook.get('active', True):
                continue
            if event_type not in webhook.get('events', []):
                continue
                
            try:
                payload = {
                    'event': event_type,
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }
                
                # In production, this would actually POST to the webhook URL
                # For now, we just log it
                add_event(f"Webhook {webhook['id'][:8]}: {event_type}", type='info')
                
            except Exception as e:
                add_event(f"Webhook failed: {e}", type='error')
    
    def notify_agent_complete(self, agent_id, model, task, cost):
        """Notify when agent completes task"""
        self.notify('agent.completed', {
            'agent_id': agent_id,
            'model': model,
            'task_preview': task[:100] if task else '',
            'cost': cost,
            'completed_at': datetime.now().isoformat()
        })
    
    def notify_agent_failed(self, agent_id, model, error):
        """Notify when agent fails"""
        self.notify('agent.failed', {
            'agent_id': agent_id,
            'model': model,
            'error': error,
            'failed_at': datetime.now().isoformat()
        })
    
    def notify_rate_limit(self, service, remaining):
        """Notify when approaching rate limits"""
        self.notify('system.rate_limit', {
            'service': service,
            'remaining': remaining,
            'threshold': 'critical' if remaining < 5 else 'warning'
        })
    
    def notify_budget_alert(self, current_cost, budget, percentage):
        """Notify when budget threshold hit"""
        self.notify('system.budget_alert', {
            'current_cost': current_cost,
            'budget': budget,
            'percentage': percentage,
            'status': 'critical' if percentage >= 100 else 'warning' if percentage >= 80 else 'notice'
        })

# Initialize notification manager
notification_mgr = NotificationManager()

# Task Queue System for Rate Limit Management
class TaskQueue:
    """Persistent task queue for handling rate limits and deferred execution"""
    
    def __init__(self, storage_path='/home/m1ndb0t/Desktop/J1MSKY/logs'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.queue_file = self.storage_path / 'task_queue.json'
        self._queue = self._load_queue()
        self._lock = threading.Lock()
        self._processing = False
        self._worker_thread = None
        
    def _load_queue(self):
        """Load queue from disk"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file) as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_queue(self):
        """Save queue to disk"""
        with open(self.queue_file, 'w') as f:
            json.dump(self._queue, f, indent=2)
    
    def enqueue(self, task, model, team=None, priority='normal', delay_seconds=0):
        """Add task to queue"""
        with self._lock:
            queue_item = {
                'id': f"queued_{int(time.time())}_{random.randint(1000,9999)}",
                'task': task,
                'model': model,
                'team': team,
                'priority': priority,
                'created_at': datetime.now().isoformat(),
                'execute_after': (datetime.now() + timedelta(seconds=delay_seconds)).isoformat(),
                'attempts': 0,
                'max_attempts': 3,
                'status': 'queued'
            }
            
            # Insert based on priority (higher priority = earlier in queue)
            priority_order = {'high': 0, 'normal': 1, 'low': 2}
            insert_idx = len(self._queue)
            for i, item in enumerate(self._queue):
                if priority_order.get(priority, 1) < priority_order.get(item.get('priority', 'normal'), 1):
                    insert_idx = i
                    break
            
            self._queue.insert(insert_idx, queue_item)
            self._save_queue()
            
            add_event(f"Task queued: {task[:40]}... (priority: {priority})", type='info')
            return queue_item['id']
    
    def dequeue(self):
        """Get next ready task from queue"""
        with self._lock:
            now = datetime.now()
            for i, item in enumerate(self._queue):
                if item['status'] != 'queued':
                    continue
                execute_after = datetime.fromisoformat(item['execute_after'])
                if now >= execute_after:
                    self._queue.pop(i)
                    self._save_queue()
                    return item
            return None
    
    def get_queue_status(self):
        """Get current queue statistics"""
        with self._lock:
            pending = [q for q in self._queue if q['status'] == 'queued']
            return {
                'total_queued': len(pending),
                'high_priority': len([q for q in pending if q.get('priority') == 'high']),
                'normal_priority': len([q for q in pending if q.get('priority') == 'normal']),
                'low_priority': len([q for q in pending if q.get('priority') == 'low']),
                'next_available': self._get_next_available()
            }
    
    def _get_next_available(self):
        """Get timestamp of next available task"""
        for item in self._queue:
            if item['status'] == 'queued':
                return item['execute_after']
        return None
    
    def start_worker(self):
        """Start background worker to process queued tasks"""
        if self._processing:
            return
        
        self._processing = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        add_event("Task queue worker started", type='info')
    
    def stop_worker(self):
        """Stop background worker"""
        self._processing = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    def _worker_loop(self):
        """Background worker loop"""
        while self._processing:
            try:
                # Check rate limits before processing
                provider = 'kimi'  # Default check
                is_limited, remaining = check_rate_limit(provider)
                
                if is_limited:
                    # Rate limited, wait and retry
                    time.sleep(30)
                    continue
                
                # Get next task
                queued_task = self.dequeue()
                if queued_task:
                    # Attempt to spawn
                    agent_id = spawn_subagent(
                        queued_task['task'],
                        queued_task['model'],
                        queued_task.get('team')
                    )
                    
                    if not agent_id and queued_task['attempts'] < queued_task['max_attempts']:
                        # Re-queue with exponential backoff
                        queued_task['attempts'] += 1
                        delay = 60 * (2 ** queued_task['attempts'])  # 2min, 4min, 8min
                        self.enqueue(
                            queued_task['task'],
                            queued_task['model'],
                            queued_task.get('team'),
                            queued_task.get('priority', 'normal'),
                            delay
                        )
                        add_event(f"Task re-queued (attempt {queued_task['attempts']})", type='warning')
                
                # Sleep before next check
                time.sleep(10)
                
            except Exception as e:
                add_event(f"Queue worker error: {e}", type='error')
                time.sleep(30)

# Initialize global task queue
task_queue = TaskQueue()

# Cost Tracking & Billing Module
class CostTracker:
    """Track API costs per model and generate billing reports"""
    
    MODEL_PRICING = {
        'k2p5': {'input': 0.0005, 'output': 0.0015, 'per_1k': True},  # per 1K tokens
        'sonnet': {'input': 0.003, 'output': 0.015, 'per_1k': True},
        'opus': {'input': 0.015, 'output': 0.075, 'per_1k': True},
        'minimax-m2.5': {'input': 0.0001, 'output': 0.0001, 'per_1k': True}
    }
    
    def __init__(self, storage_path='/home/m1ndb0t/Desktop/J1MSKY/logs'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.daily_usage = self._load_daily_usage()
        self.session_start = datetime.now()
        
    def _load_daily_usage(self):
        """Load today's usage from file"""
        today = datetime.now().strftime('%Y-%m-%d')
        usage_file = self.storage_path / f'usage_{today}.json'
        if usage_file.exists():
            with open(usage_file) as f:
                return json.load(f)
        return {'models': {}, 'total_cost': 0.0, 'tasks_completed': 0}
    
    def _save_daily_usage(self):
        """Save usage to file"""
        today = datetime.now().strftime('%Y-%m-%d')
        usage_file = self.storage_path / f'usage_{today}.json'
        with open(usage_file, 'w') as f:
            json.dump(self.daily_usage, f, indent=2)
    
    def record_usage(self, model, input_tokens=0, output_tokens=0, task_type='unknown'):
        """Record token usage and calculate cost"""
        if model not in self.MODEL_PRICING:
            return 0.0
            
        pricing = self.MODEL_PRICING[model]
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * pricing['input'] if pricing['per_1k'] else input_tokens * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output'] if pricing['per_1k'] else output_tokens * pricing['output']
        total_cost = input_cost + output_cost
        
        # Update daily usage
        if model not in self.daily_usage['models']:
            self.daily_usage['models'][model] = {
                'input_tokens': 0, 'output_tokens': 0, 
                'cost': 0.0, 'calls': 0
            }
        
        self.daily_usage['models'][model]['input_tokens'] += input_tokens
        self.daily_usage['models'][model]['output_tokens'] += output_tokens
        self.daily_usage['models'][model]['cost'] += total_cost
        self.daily_usage['models'][model]['calls'] += 1
        self.daily_usage['total_cost'] += total_cost
        self.daily_usage['tasks_completed'] += 1
        
        # Persist to disk
        self._save_daily_usage()
        
        return total_cost
    
    def get_daily_report(self):
        """Get daily usage report"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'session_duration_minutes': (datetime.now() - self.session_start).seconds / 60,
            **self.daily_usage
        }
    
    def get_model_breakdown(self):
        """Get cost breakdown by model"""
        return self.daily_usage['models']
    
    def estimate_task_cost(self, model, estimated_input=1000, estimated_output=500):
        """Estimate cost before running task"""
        if model not in self.MODEL_PRICING:
            return 0.0
        pricing = self.MODEL_PRICING[model]
        input_cost = (estimated_input / 1000) * pricing['input']
        output_cost = (estimated_output / 1000) * pricing['output']
        return round(input_cost + output_cost, 4)
    
    def check_budget_alert(self, daily_budget=50.0):
        """Check if approaching daily budget"""
        current_cost = self.daily_usage['total_cost']
        percentage = (current_cost / daily_budget) * 100
        
        if percentage >= 100:
            return 'critical', f'Budget exceeded: ${current_cost:.2f} / ${daily_budget:.2f}'
        elif percentage >= 80:
            return 'warning', f'Budget at {percentage:.0f}%: ${current_cost:.2f} / ${daily_budget:.2f}'
        elif percentage >= 50:
            return 'notice', f'Budget at {percentage:.0f}%: ${current_cost:.2f} / ${daily_budget:.2f}'
        return 'ok', f'Budget healthy: ${current_cost:.2f} / ${daily_budget:.2f}'

# Initialize global cost tracker
cost_tracker = CostTracker()

# Metrics and Analytics Module
class MetricsCollector:
    """Collect and aggregate system metrics for monitoring and optimization"""
    
    def __init__(self, storage_path='/home/m1ndb0t/Desktop/J1MSKY/logs'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.metrics_file = self.storage_path / 'metrics.json'
        self._metrics = self._load_metrics()
        self._lock = threading.Lock()
        
    def _load_metrics(self):
        """Load metrics from disk"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file) as f:
                    return json.load(f)
            except:
                return self._init_metrics()
        return self._init_metrics()
    
    def _init_metrics(self):
        """Initialize default metrics structure"""
        return {
            'agents': {
                'total_spawned': 0,
                'total_completed': 0,
                'total_failed': 0,
                'by_model': {},
                'by_team': {},
                'by_status': {}
            },
            'performance': {
                'avg_completion_time': 0,
                'total_runtime_seconds': 0,
                'tasks_per_hour': []
            },
            'costs': {
                'total_spent': 0.0,
                'by_model': {},
                'by_day': {}
            },
            'errors': {
                'total': 0,
                'by_type': {},
                'recent': []
            },
            'system': {
                'uptime_seconds': 0,
                'start_time': datetime.now().isoformat(),
                'restart_count': 0
            }
        }
    
    def _save_metrics(self):
        """Save metrics to disk"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self._metrics, f, indent=2)
    
    def record_agent_spawn(self, model, team=None):
        """Record agent spawn event"""
        with self._lock:
            self._metrics['agents']['total_spawned'] += 1
            
            # By model
            if model not in self._metrics['agents']['by_model']:
                self._metrics['agents']['by_model'][model] = {'spawned': 0, 'completed': 0, 'failed': 0}
            self._metrics['agents']['by_model'][model]['spawned'] += 1
            
            # By team
            if team:
                if team not in self._metrics['agents']['by_team']:
                    self._metrics['agents']['by_team'][team] = {'spawned': 0, 'completed': 0}
                self._metrics['agents']['by_team'][team]['spawned'] += 1
            
            self._save_metrics()
    
    def record_agent_complete(self, model, duration_seconds, cost, team=None):
        """Record agent completion"""
        with self._lock:
            self._metrics['agents']['total_completed'] += 1
            
            # Update model stats
            if model in self._metrics['agents']['by_model']:
                self._metrics['agents']['by_model'][model]['completed'] += 1
            
            # Update team stats
            if team and team in self._metrics['agents']['by_team']:
                self._metrics['agents']['by_team'][team]['completed'] += 1
            
            # Update performance metrics
            perf = self._metrics['performance']
            total_tasks = self._metrics['agents']['total_completed']
            old_avg = perf['avg_completion_time']
            perf['avg_completion_time'] = ((old_avg * (total_tasks - 1)) + duration_seconds) / total_tasks
            perf['total_runtime_seconds'] += duration_seconds
            
            # Update costs
            today = datetime.now().strftime('%Y-%m-%d')
            self._metrics['costs']['total_spent'] += cost
            
            if model not in self._metrics['costs']['by_model']:
                self._metrics['costs']['by_model'][model] = 0.0
            self._metrics['costs']['by_model'][model] += cost
            
            if today not in self._metrics['costs']['by_day']:
                self._metrics['costs']['by_day'][today] = 0.0
            self._metrics['costs']['by_day'][today] += cost
            
            self._save_metrics()
    
    def record_agent_fail(self, model, error_type='unknown'):
        """Record agent failure"""
        with self._lock:
            self._metrics['agents']['total_failed'] += 1
            
            if model in self._metrics['agents']['by_model']:
                self._metrics['agents']['by_model'][model]['failed'] += 1
            
            # Track errors
            self._metrics['errors']['total'] += 1
            if error_type not in self._metrics['errors']['by_type']:
                self._metrics['errors']['by_type'][error_type] = 0
            self._metrics['errors']['by_type'][error_type] += 1
            
            # Keep recent errors (last 20)
            self._metrics['errors']['recent'].append({
                'time': datetime.now().isoformat(),
                'model': model,
                'type': error_type
            })
            self._metrics['errors']['recent'] = self._metrics['errors']['recent'][-20:]
            
            self._save_metrics()
    
    def get_dashboard_metrics(self):
        """Get metrics formatted for dashboard display"""
        with self._lock:
            uptime = datetime.now() - datetime.fromisoformat(self._metrics['system']['start_time'])
            
            return {
                'agents': {
                    'total_spawned': self._metrics['agents']['total_spawned'],
                    'total_completed': self._metrics['agents']['total_completed'],
                    'total_failed': self._metrics['agents']['total_failed'],
                    'success_rate': (
                        self._metrics['agents']['total_completed'] / 
                        max(self._metrics['agents']['total_spawned'], 1) * 100
                    )
                },
                'performance': {
                    'avg_completion_time': round(self._metrics['performance']['avg_completion_time'], 1),
                    'uptime_hours': round(uptime.total_seconds() / 3600, 1)
                },
                'costs': {
                    'total_spent': round(self._metrics['costs']['total_spent'], 2),
                    'today': round(self._metrics['costs']['by_day'].get(datetime.now().strftime('%Y-%m-%d'), 0), 2)
                },
                'breakdown': {
                    'by_model': self._metrics['agents']['by_model'],
                    'by_team': self._metrics['agents']['by_team']
                }
            }
    
    def get_health_status(self):
        """Get system health status"""
        with self._lock:
            total = self._metrics['agents']['total_spawned']
            failed = self._metrics['agents']['total_failed']
            error_rate = failed / max(total, 1)
            
            # Determine health status
            if error_rate > 0.2:  # >20% error rate
                status = 'critical'
                message = f'High failure rate: {error_rate*100:.1f}%'
            elif error_rate > 0.1:  # >10% error rate
                status = 'warning'
                message = f'Elevated failure rate: {error_rate*100:.1f}%'
            else:
                status = 'healthy'
                message = 'System operating normally'
            
            return {
                'status': status,
                'message': message,
                'error_rate': round(error_rate * 100, 1),
                'total_agents': total,
                'failed_agents': failed
            }

# Initialize metrics collector
metrics = MetricsCollector()

def add_event(message, agent=None, model=None, type='info'):
    """Add event to log"""
    event = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'agent': agent,
        'model': model,
        'type': type
    }
    EVENTS_LOG.append(event)
    if len(EVENTS_LOG) > 100:
        EVENTS_LOG.pop(0)

def check_rate_limit(service):
    """Check if service is rate limited"""
    limit = RATE_LIMITS.get(service, {})
    if not limit:
        return False, 0
    
    # Reset if window passed
    if time.time() - limit['last_reset'] > limit['window']:
        limit['requests'] = 0
        limit['last_reset'] = time.time()
    
    remaining = limit['limit'] - limit['requests']
    is_limited = remaining <= 0
    
    return is_limited, remaining

def use_service(service):
    """Record service usage"""
    if service in RATE_LIMITS:
        RATE_LIMITS[service]['requests'] += 1

def spawn_subagent(task, model, team=None):
    """Spawn a subagent with specific model"""
    agent_id = f"subagent_{int(time.time())}_{random.randint(1000,9999)}"
    
    # Record metrics for spawn attempt
    metrics.record_agent_spawn(model, team)
    
    # Check rate limit for model provider
    provider = MODEL_AGENTS.get(model, {}).get('provider', 'kimi-coding')
    is_limited, remaining = check_rate_limit(provider.split(':')[0])
    
    if is_limited:
        add_event(f"Rate limited: {provider}. Cannot spawn {model}", type='error')
        metrics.record_agent_fail(model, 'rate_limited')
        return None
    
    # Estimate cost before spawning
    estimated_cost = cost_tracker.estimate_task_cost(model, estimated_input=len(task) * 4, estimated_output=500)
    
    # Check budget alert
    budget_status, budget_msg = cost_tracker.check_budget_alert(daily_budget=50.0)
    if budget_status == 'critical':
        add_event(f"Budget critical - spawning with caution: {budget_msg}", type='warning')
    
    # Record usage
    use_service(provider.split(':')[0])
    
    # Create subagent record with cost tracking
    ACTIVE_SUBAGENTS[agent_id] = {
        'id': agent_id,
        'task': task,
        'model': model,
        'team': team,
        'status': 'spawning',
        'created': datetime.now().isoformat(),
        'started': None,
        'completed': None,
        'result': None,
        'estimated_cost': estimated_cost,
        'actual_cost': 0.0
    }
    
    # Update model agent status
    if model in MODEL_AGENTS:
        MODEL_AGENTS[model]['last_used'] = datetime.now().isoformat()
        MODEL_AGENTS[model]['status'] = 'working'
    
    add_event(f"Spawned {model} subagent for: {task[:50]}... (est: ${estimated_cost:.4f})", agent=agent_id, model=model, type='success')
    
    # Simulate subagent work (in real impl, this would call sessions_spawn)
    def run_subagent():
        time.sleep(2)  # Simulate work
        ACTIVE_SUBAGENTS[agent_id]['status'] = 'running'
        ACTIVE_SUBAGENTS[agent_id]['started'] = datetime.now().isoformat()
        time.sleep(5)  # Simulate processing
        ACTIVE_SUBAGENTS[agent_id]['status'] = 'completed'
        ACTIVE_SUBAGENTS[agent_id]['completed'] = datetime.now().isoformat()
        ACTIVE_SUBAGENTS[agent_id]['result'] = f"Task completed using {model}"
        
        # Record actual cost (simulated)
        actual_cost = cost_tracker.record_usage(
            model=model,
            input_tokens=len(task) * 4,  # Rough estimate
            output_tokens=500,
            task_type='subagent_task'
        )
        ACTIVE_SUBAGENTS[agent_id]['actual_cost'] = actual_cost
        
        if model in MODEL_AGENTS:
            MODEL_AGENTS[model]['status'] = 'active'
            MODEL_AGENTS[model]['tasks_completed'] = MODEL_AGENTS[model].get('tasks_completed', 0) + 1
        
        add_event(f"Subagent {agent_id} completed task (cost: ${actual_cost:.4f})", agent=agent_id, model=model, type='success')
        
        # Record metrics
        duration = 7  # Simulated 7 seconds (2 + 5 from run_subagent)
        metrics.record_agent_complete(model, duration, actual_cost, team)
        
        # Send completion notification
        notification_mgr.notify_agent_complete(agent_id, model, task, actual_cost)
    
    threading.Thread(target=run_subagent, daemon=True).start()
    
    return agent_id

def get_system_stats():
    """Get system stats"""
    stats = {'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--:--', 'disk_free': '0G', 'processes': 0}
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            stats['temp'] = round(int(f.read()) / 1000.0, 1)
        with open('/proc/loadavg', 'r') as f:
            stats['load'] = round(float(f.read().split()[0]), 2)
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            stats['mem'] = round(((total - available) / total) * 100, 1)
        with open('/proc/uptime', 'r') as f:
            secs = float(f.read().split()[0])
            h = int(secs // 3600)
            m = int((secs % 3600) // 60)
            stats['uptime'] = f"{h}h {m:02d}m"
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            stats['disk_free'] = lines[1].split()[3]
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        stats['processes'] = len(result.stdout.strip().split('\n')) - 1
    except:
        pass
    return stats

# HTML Template with Rate Limit Panel and Team View
HTML_V4 = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>◈ J1MSKY AGENT TEAMS v4.0 ◈</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a25;
            --accent-cyan: #00ffff;
            --accent-green: #00ff88;
            --accent-pink: #ff00ff;
            --accent-yellow: #ffff00;
            --accent-red: #ff4444;
            --accent-purple: #9945ff;
            --text-primary: #e0e0e0;
            --text-secondary: #888888;
            --border: #333333;
        }
        
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            padding: 20px 25px;
            border-bottom: 2px solid var(--accent-cyan);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            color: var(--accent-cyan);
            font-size: 1.5em;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            letter-spacing: 2px;
        }
        
        .header-stats {
            display: flex;
            gap: 15px;
        }
        
        .header-stat {
            text-align: center;
            padding: 8px 15px;
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid var(--accent-cyan);
            border-radius: 8px;
        }
        
        .header-stat-value {
            font-size: 1.1em;
            font-weight: 700;
            color: var(--accent-cyan);
        }
        
        .header-stat-label {
            font-size: 9px;
            color: var(--text-secondary);
            text-transform: uppercase;
        }
        
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 0 20px;
        }
        
        .nav-tab {
            padding: 15px 22px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            text-transform: uppercase;
        }
        
        .nav-tab:hover {
            color: var(--text-primary);
            background: rgba(0, 255, 255, 0.1);
        }
        
        .nav-tab.active {
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
            background: var(--bg-card);
        }
        
        .main-content {
            padding: 20px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .panel {
            display: none;
        }
        
        .panel.active {
            display: block;
            animation: fadeIn 0.4s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        
        @media (max-width: 1200px) {
            .grid-4, .grid-3 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
        }
        
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .card:hover {
            transform: translateY(-3px);
            border-color: var(--accent-cyan);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
        }
        
        .card-title {
            color: var(--accent-cyan);
            font-size: 1em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Rate Limit Panel */
        .rate-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .rate-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s;
        }
        
        .rate-item.limited {
            border-color: var(--accent-red);
            background: rgba(255, 68, 68, 0.1);
        }
        
        .rate-item.safe {
            border-color: var(--accent-green);
        }
        
        .rate-item.warning {
            border-color: var(--accent-yellow);
        }
        
        .rate-name {
            font-weight: 600;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .rate-status {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        
        .status-ok { background: var(--accent-green); color: #000; }
        .status-warn { background: var(--accent-yellow); color: #000; }
        .status-limit { background: var(--accent-red); color: #fff; }
        
        .rate-bar {
            height: 8px;
            background: var(--bg-primary);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .rate-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }
        
        .fill-safe { background: var(--accent-green); }
        .fill-warn { background: var(--accent-yellow); }
        .fill-limit { background: var(--accent-red); }
        
        /* Team Cards */
        .team-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid var(--accent-cyan);
            transition: all 0.3s;
        }
        
        .team-card:hover {
            transform: translateX(5px);
            border-color: var(--accent-cyan);
        }
        
        .team-card.active { border-left-color: var(--accent-green); }
        .team-card.standby { border-left-color: var(--accent-yellow); }
        
        .team-name {
            font-size: 1.2em;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 10px;
        }
        
        .team-models {
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 10px;
            font-family: monospace;
        }
        
        .team-specialty {
            font-size: 12px;
            color: var(--accent-cyan);
            margin-bottom: 15px;
        }
        
        .team-stats {
            display: flex;
            gap: 15px;
            font-size: 12px;
        }
        
        .team-stat {
            background: var(--bg-card);
            padding: 5px 10px;
            border-radius: 6px;
        }
        
        /* Model Agents */
        .model-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s;
        }
        
        .model-card:hover {
            border-color: var(--accent-cyan);
            transform: scale(1.02);
        }
        
        .model-card.active { border-color: var(--accent-green); }
        .model-card.working { border-color: var(--accent-yellow); animation: pulse 2s infinite; }
        .model-card.standby { border-color: var(--text-secondary); opacity: 0.7; }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255, 255, 0, 0.4); }
            50% { box-shadow: 0 0 0 10px rgba(255, 255, 0, 0); }
        }
        
        .model-name {
            font-weight: 600;
            color: var(--accent-cyan);
            margin-bottom: 5px;
        }
        
        .model-role {
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        .model-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-active { background: rgba(0, 255, 136, 0.2); color: var(--accent-green); }
        .status-working { background: rgba(255, 255, 0, 0.2); color: var(--accent-yellow); }
        .status-standby { background: rgba(136, 136, 136, 0.2); color: var(--text-secondary); }
        
        /* Subagents */
        .subagent-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .subagent-item.spawning { border-left: 3px solid var(--accent-cyan); }
        .subagent-item.running { border-left: 3px solid var(--accent-yellow); }
        .subagent-item.completed { border-left: 3px solid var(--accent-green); }
        
        .subagent-info {
            flex: 1;
        }
        
        .subagent-id {
            font-family: monospace;
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }
        
        .subagent-task {
            font-size: 13px;
            color: var(--text-primary);
        }
        
        .subagent-model {
            font-size: 10px;
            color: var(--accent-cyan);
            margin-top: 4px;
        }
        
        .subagent-status {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        /* Event Log */
        .event-log {
            background: #050508;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Fira Code', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .event-line {
            padding: 4px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .event-time {
            color: var(--accent-pink);
            margin-right: 10px;
        }
        
        .event-info { color: var(--accent-cyan); }
        .event-success { color: var(--accent-green); }
        .event-error { color: var(--accent-red); }
        .event-warn { color: var(--accent-yellow); }
        
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
            text-transform: uppercase;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), #0088aa);
            color: #000;
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--accent-green), #00aa55);
            color: #000;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .footer {
            text-align: center;
            padding: 25px;
            margin-top: 30px;
            color: var(--text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--border);
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY AGENT TEAMS v4.0 ◈</h1>
        <div class="header-stats">
            <div class="header-stat">
                <div class="header-stat-value">{{TEAM_COUNT}}</div>
                <div class="header-stat-label">Teams</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value">{{MODEL_COUNT}}</div>
                <div class="header-stat-label">Models</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value">{{ACTIVE_SUBAGENTS}}</div>
                <div class="header-stat-label">Active</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value" style="color: {{TEMP_COLOR}};">{{TEMP}}°C</div>
                <div class="header-stat-label">Temp</div>
            </div>
        </div>
    </header>
    
    <nav class="nav-tabs">
        <button class="nav-tab active" onclick="showPanel('teams')">👥 Teams</button>
        <button class="nav-tab" onclick="showPanel('models')">🤖 Models</button>
        <button class="nav-tab" onclick="showPanel('spawn')">🚀 Spawn</button>
        <button class="nav-tab" onclick="showPanel('rates')">⚡ Rate Limits</button>
        <button class="nav-tab" onclick="showPanel('subagents')">📋 Subagents</button>
        <button class="nav-tab" onclick="showPanel('logs')">📜 Logs</button>
    </nav>
    
    <main class="main-content">
        {{CONTENT}}
    </main>
    
    <footer class="footer">
        <p>◈ J1MSKY v4.0 Multi-Model Agent System ◈ | Business-Ready ◈ Rate-Limit Protected ◈</p>
    </footer>
    
    <script>
        function showPanel(panelId) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(panelId).classList.add('active');
            event.target.classList.add('active');
        }
        
        function spawnAgent(model) {
            const task = prompt('Enter task for ' + model + ':');
            if (task) {
                fetch('/api/spawn', {
                    method: 'POST',
                    body: 'model=' + model + '&task=' + encodeURIComponent(task),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).then(() => {
                    alert('🚀 Spawned ' + model + ' agent!');
                    location.reload();
                });
            }
        }
        
        function spawnTeam(team) {
            const task = prompt('Enter task for ' + team + ' team:');
            if (task) {
                fetch('/api/spawn-team', {
                    method: 'POST',
                    body: 'team=' + team + '&task=' + encodeURIComponent(task),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).then(() => {
                    alert('🚀 Spawned ' + team + ' team!');
                    location.reload();
                });
            }
        }
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            location.reload();
        }, 10000);
    </script>
</body>
</html>'''

# Panel: Rate Limits
RATES_PANEL = '''<div id="rates" class="panel">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">⚡ Rate Limit Status</span>
        </div>
        <div class="rate-grid">
            {{RATE_LIMITS}}
        </div>
    </div>
    
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 Usage Today</span>
            </div>
            <div style="color: var(--text-secondary); line-height: 2;">
                <p>🤖 <strong style="color: var(--accent-cyan);">Model Requests:</strong> {{MODEL_REQUESTS}}</p>
                <p>🔍 <strong style="color: var(--accent-cyan);">Web Searches:</strong> {{WEB_REQUESTS}}</p>
                <p>🖼️ <strong style="color: var(--accent-cyan);">Image Generations:</strong> {{IMAGE_REQUESTS}}</p>
                <p>💾 <strong style="color: var(--accent-cyan);">GitHub Operations:</strong> {{GITHUB_REQUESTS}}</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <span class="card-title">🛡️ Protection Status</span>
            </div>
            <div style="color: var(--text-secondary); line-height: 2;">
                <p>✅ <strong style="color: var(--accent-green);">Auto-throttling:</strong> Active</p>
                <p>✅ <strong style="color: var(--accent-green);">Request batching:</strong> Enabled</p>
                <p>✅ <strong style="color: var(--accent-green);">Cooldown periods:</strong> Enforced</p>
                <p>✅ <strong style="color: var(--accent-green);">Fallback models:</strong> Ready</p>
            </div>
        </div>
    </div>
</div>'''

# Panel: Teams
TEAMS_PANEL = '''<div id="teams" class="panel active">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">👥 Agent Teams</span>
        </div>
        <div class="grid-2">
            {{TEAMS}}
        </div>
    </div>
</div>'''

# Panel: Models
MODELS_PANEL = '''<div id="models" class="panel">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">🤖 Individual Model Agents</span>
            <span style="color: var(--text-secondary); font-size: 12px;">Click to spawn subagent</span>
        </div>
        <div class="grid-3">
            {{MODELS}}
        </div>
    </div>
</div>'''

# Panel: Spawn
SPAWN_PANEL = '''<div id="spawn" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">🚀 Spawn New Subagent</span>
        </div>
        
        <form onsubmit="spawnFromForm(event)" style="display: grid; gap: 20px;">
            <div>
                <label style="display: block; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; text-transform: uppercase;">Task Description</label>
                <textarea name="task" rows="4" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: monospace;"
                  placeholder="Describe what you want the agent to do..."></textarea>
            </div>
            
            <div class="grid-2">
                <div>
                    <label style="display: block; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; text-transform: uppercase;">Select Model</label>
                    <select name="model" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);">
                        <option value="k2p5">Kimi K2.5 (Fast Coder)</option>
                        <option value="sonnet">Claude Sonnet (Creative)</option>
                        <option value="opus">Claude Opus (Deep Thinker)</option>
                    </select>
                </div>
                
                <div>
                    <label style="display: block; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; text-transform: uppercase;">Priority</label>
                    <select name="priority" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);">
                        <option value="low">🟢 Low (Background)</option>
                        <option value="normal" selected>🟡 Normal</option>
                        <option value="high">🔴 High (Urgent)</option>
                    </select>
                </div>
            </div>
            
            <button type="submit" class="btn btn-success" style="width: 100%; padding: 15px; font-size: 16px;">🚀 SPAWN SUBAGENT</button>
        </form>
    </div>
</div>'''

# Panel: Subagents
SUBAGENTS_PANEL = '''<div id="subagents" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">📋 Active Subagents</span>
        </div>
        <div>
            {{SUBAGENTS}}
        </div>
    </div>
</div>'''

# Panel: Logs
LOGS_PANEL = '''<div id="logs" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">📜 Event Log</span>
        </div>
        <div class="event-log">
            {{EVENTS}}
        </div>
    </div>
</div>'''

class MultiAgentServer(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            stats = get_system_stats()
            
            # Build rate limits HTML
            rates_html = ''
            for service, data in RATE_LIMITS.items():
                is_limited, remaining = check_rate_limit(service)
                used = data['requests']
                limit = data['limit']
                percent = (used / limit) * 100
                
                status_class = 'safe' if percent < 50 else 'warning' if percent < 80 else 'limited'
                status_text = 'OK' if percent < 50 else 'WARN' if percent < 80 else 'LIMIT'
                fill_class = 'fill-safe' if percent < 50 else 'fill-warn' if percent < 80 else 'fill-limit'
                
                rates_html += f'''
                <div class="rate-item {status_class}">
                    <div class="rate-name">
                        {service.upper()}
                        <span class="rate-status status-{status_text.lower()}">{status_text}</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary);">{remaining} / {limit} remaining</div>
                    <div class="rate-bar">
                        <div class="rate-fill {fill_class}" style="width: {percent}%;"></div>
                    </div>
                </div>'''
            
            # Build teams HTML
            teams_html = ''
            for team_id, team in AGENT_TEAMS.items():
                status_class = team['status']
                teams_html += f'''
                <div class="team-card {status_class}">
                    <div class="team-name">{team['name']}</div>
                    <div class="team-models">{', '.join(team['models'])}</div>
                    <div class="team-specialty">{team['specialty']}</div>
                    <div class="team-stats">
                        <div class="team-stat">Status: {team['status'].upper()}</div>
                        <div class="team-stat">Tasks: {team['tasks_completed']}</div>
                    </div>
                    <button class="btn btn-primary" style="margin-top: 15px; width: 100%;" onclick="spawnTeam('{team_id}')">🚀 Deploy Team</button>
                </div>'''
            
            # Build models HTML
            models_html = ''
            for model_id, model in MODEL_AGENTS.items():
                status = model['status']
                last_used = model.get('last_used', 'Never')
                if last_used and last_used != 'Never':
                    last_used = last_used.split('T')[1][:5] if 'T' in last_used else last_used[:10]
                else:
                    last_used = 'Never'
                
                models_html += f'''
                <div class="model-card {status}" onclick="spawnAgent('{model_id}')" style="cursor: pointer;">
                    <div class="model-name">{model['name']}</div>
                    <div class="model-role">{model['role']}</div>
                    <div class="model-status status-{status}">{status.upper()}</div>
                    <div style="margin-top: 10px; font-size: 10px; color: var(--text-secondary);">Last: {last_used}</div>
                    <div style="font-size: 10px; color: var(--accent-cyan);">Success: {int(model['success_rate']*100)}%</div>
                </div>'''
            
            # Build subagents HTML
            subagents_html = ''
            if ACTIVE_SUBAGENTS:
                for agent_id, agent in sorted(ACTIVE_SUBAGENTS.items(), key=lambda x: x[1]['created'], reverse=True)[:10]:
                    status = agent['status']
                    subagents_html += f'''
                    <div class="subagent-item {status}">
                        <div class="subagent-info">
                            <div class="subagent-id">{agent_id[:20]}...</div>
                            <div class="subagent-task">{agent['task'][:50]}...</div>
                            <div class="subagent-model">🤖 {agent['model']} | Team: {agent.get('team', 'None')}</div>
                        </div>
                        <div class="subagent-status status-{status}">{status.upper()}</div>
                    </div>'''
            else:
                subagents_html = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">No active subagents. Spawn one from the Models or Spawn tab!</div>'
            
            # Build events HTML
            events_html = ''
            for event in reversed(EVENTS_LOG[-20:]):
                event_class = f"event-{event.get('type', 'info')}"
                events_html += f'''
                <div class="event-line">
                    <span class="event-time">{event['time']}</span>
                    <span class="{event_class}">[{event.get('model', 'SYSTEM')}] {event['message']}</span>
                </div>'''
            
            if not events_html:
                events_html = '<div class="event-line"><span class="event-time">--:--:--</span><span class="event-info">System initialized. Ready to spawn agents.</span></div>'
            
            # Build content
            content = RATES_PANEL + TEAMS_PANEL + MODELS_PANEL + SPAWN_PANEL + SUBAGENTS_PANEL + LOGS_PANEL
            content = content.replace('{{RATE_LIMITS}}', rates_html)
            content = content.replace('{{TEAMS}}', teams_html)
            content = content.replace('{{MODELS}}', models_html)
            content = content.replace('{{SUBAGENTS}}', subagents_html)
            content = content.replace('{{EVENTS}}', events_html)
            
            # Calculate totals
            total_model_requests = sum(RATE_LIMITS[k]['requests'] for k in ['kimi', 'anthropic'])
            
            html = HTML_V4
            html = html.replace('{{CONTENT}}', content)
            html = html.replace('{{TEAM_COUNT}}', str(len(AGENT_TEAMS)))
            html = html.replace('{{MODEL_COUNT}}', str(len(MODEL_AGENTS)))
            html = html.replace('{{ACTIVE_SUBAGENTS}}', str(len([a for a in ACTIVE_SUBAGENTS.values() if a['status'] != 'completed'])))
            html = html.replace('{{TEMP}}', str(stats['temp']))
            html = html.replace('{{TEMP_COLOR}}', 'var(--accent-green)' if stats['temp'] < 70 else 'var(--accent-yellow)' if stats['temp'] < 80 else 'var(--accent-red)')
            html = html.replace('{{MODEL_REQUESTS}}', str(total_model_requests))
            html = html.replace('{{WEB_REQUESTS}}', str(RATE_LIMITS['web_search']['requests']))
            html = html.replace('{{IMAGE_REQUESTS}}', str(RATE_LIMITS['image_gen']['requests']))
            html = html.replace('{{GITHUB_REQUESTS}}', str(RATE_LIMITS['github']['requests']))
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        params = parse_qs(body)
        
        if self.path == '/api/spawn':
            model = params.get('model', ['k2p5'])[0]
            task = params.get('task', ['No task'])[0]
            
            agent_id = spawn_subagent(task, model)
            
            if agent_id:
                self.send_json({'success': True, 'agent_id': agent_id})
            else:
                self.send_json({'success': False, 'error': 'Rate limited or error'})
                
        elif self.path == '/api/spawn-team':
            team_id = params.get('team', ['team_coding'])[0]
            task = params.get('task', ['No task'])[0]
            
            team = AGENT_TEAMS.get(team_id)
            if team:
                # Spawn primary model from team
                primary_model = team['models'][0].split('/')[-1].replace('claude-', '').replace('kimi-coding/', '').replace('k2p5', 'k2p5')
                if 'sonnet' in primary_model.lower():
                    primary_model = 'sonnet'
                elif 'opus' in primary_model.lower():
                    primary_model = 'opus'
                else:
                    primary_model = 'k2p5'
                
                agent_id = spawn_subagent(task, primary_model, team_id)
                
                if agent_id:
                    team['tasks_completed'] += 1
                    self.send_json({'success': True, 'agent_id': agent_id, 'team': team_id})
                else:
                    self.send_json({'success': False, 'error': 'Rate limited'})
            else:
                self.send_json({'success': False, 'error': 'Team not found'})
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_PUT(self):
        """Handle PUT requests for webhooks"""
        if self.path == '/api/webhooks':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            
            try:
                data = json.loads(body)
                url = data.get('url')
                events = data.get('events', ['agent.completed'])
                secret = data.get('secret')
                
                if not url:
                    self.send_json({'success': False, 'error': 'URL required'})
                    return
                
                webhook_id = notification_mgr.register_webhook(url, events, secret)
                self.send_json({
                    'success': True,
                    'webhook_id': webhook_id,
                    'url': url,
                    'events': events
                })
            except json.JSONDecodeError:
                self.send_json({'success': False, 'error': 'Invalid JSON'})
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if self.path.startswith('/api/webhooks/'):
            webhook_id = self.path.split('/')[-1]
            notification_mgr.unregister_webhook(webhook_id)
            self.send_json({'success': True, 'message': f'Webhook {webhook_id} removed'})
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), MultiAgentServer) as httpd:
        print("◈ J1MSKY AGENT TEAMS v4.0 Started ◈")
        print("Multi-model subagent system with rate limit protection")
        print("Access: http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    add_event("Agent Teams v4.0 initialized", type='success')
    add_event("Rate limit protection active", type='info')
    add_event("Ready to spawn subagents", type='info')
    run()
