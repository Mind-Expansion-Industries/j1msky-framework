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

    def recommend_task_quote(self, model, estimated_input=1000, estimated_output=500, complexity='medium'):
        """Generate a customer-facing quote recommendation from model cost estimates."""
        complexity_markup = {'low': 3.0, 'medium': 4.0, 'high': 5.0}
        markup = complexity_markup.get(complexity, 4.0)

        internal_cost = self.estimate_task_cost(model, estimated_input, estimated_output)
        minimum_price = 0.50
        recommended_price = round(max(internal_cost * markup, minimum_price), 2)
        margin_pct = round(((recommended_price - internal_cost) / recommended_price) * 100, 2) if recommended_price else 0.0

        if margin_pct >= 70:
            margin_band = 'strong'
        elif margin_pct >= 55:
            margin_band = 'healthy'
        else:
            margin_band = 'at_risk'

        return {
            'model': model,
            'complexity': complexity,
            'estimated_input_tokens': int(estimated_input),
            'estimated_output_tokens': int(estimated_output),
            'internal_cost': round(internal_cost, 4),
            'markup': markup,
            'recommended_price': recommended_price,
            'gross_margin_pct': margin_pct,
            'margin_band': margin_band
        }

    def evaluate_margin_guardrail(self, quote, delivery_type='task'):
        """Evaluate quote against minimum margin thresholds."""
        thresholds = {'task': 55.0, 'subscription': 50.0, 'enterprise': 45.0}
        threshold = thresholds.get(delivery_type, 55.0)
        margin = quote.get('gross_margin_pct', 0.0)
        compliant = margin >= threshold

        return {
            'delivery_type': delivery_type,
            'minimum_margin_pct': threshold,
            'actual_margin_pct': margin,
            'is_compliant': compliant,
            'action': 'approve_quote' if compliant else 'escalate_deal_desk'
        }

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

# Workflow Engine for Multi-Agent Pipelines
class WorkflowEngine:
    """
    Define and execute multi-step agent workflows.
    Allows chaining multiple agents with conditional logic.
    """
    
    def __init__(self, storage_path='/home/m1ndb0t/Desktop/J1MSKY/workflows'):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.active_workflows = {}
        self._lock = threading.Lock()
        
    def create_workflow(self, name, steps, description=''):
        """
        Create a reusable workflow definition.
        
        Steps format:
        [
            {
                'name': 'research',
                'model': 'sonnet',
                'task_template': 'Research: {topic}',
                'output_var': 'research_result',
                'condition': None  # Optional: only run if condition met
            },
            {
                'name': 'write',
                'model': 'k2p5',
                'task_template': 'Write based on: {research_result}',
                'input_vars': ['research_result'],
                'output_var': 'final_output'
            }
        ]
        """
        workflow = {
            'id': f"wf_{int(time.time())}_{random.randint(1000,9999)}",
            'name': name,
            'description': description,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        # Save workflow definition
        wf_file = self.storage_path / f"{workflow['id']}.json"
        with open(wf_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        return workflow['id']
    
    def execute_workflow(self, workflow_id, inputs, callback=None):
        """
        Execute a workflow with given inputs.
        Returns execution ID for tracking.
        """
        # Load workflow
        wf_file = self.storage_path / f"{workflow_id}.json"
        if not wf_file.exists():
            return None, f"Workflow {workflow_id} not found"
        
        with open(wf_file) as f:
            workflow = json.load(f)
        
        execution_id = f"exec_{int(time.time())}_{random.randint(1000,9999)}"
        
        execution = {
            'id': execution_id,
            'workflow_id': workflow_id,
            'workflow_name': workflow['name'],
            'status': 'running',
            'inputs': inputs,
            'outputs': {},
            'step_results': [],
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'total_cost': 0.0
        }
        
        with self._lock:
            self.active_workflows[execution_id] = execution
        
        # Start execution in background
        threading.Thread(
            target=self._run_workflow,
            args=(execution, workflow, callback),
            daemon=True
        ).start()
        
        return execution_id, None
    
    def _run_workflow(self, execution, workflow, callback=None):
        """Internal method to run workflow steps"""
        try:
            context = execution['inputs'].copy()
            
            for i, step in enumerate(workflow['steps']):
                step_name = step['name']
                add_event(f"Workflow {execution['id'][:8]}: Starting step '{step_name}'", type='info')
                
                # Check condition if present
                if 'condition' in step and step['condition']:
                    if not self._evaluate_condition(step['condition'], context):
                        add_event(f"Step {step_name} skipped (condition not met)", type='info')
                        continue
                
                # Build task from template
                task_template = step['task_template']
                try:
                    task = task_template.format(**context)
                except KeyError as e:
                    error = f"Missing variable {e} for step {step_name}"
                    add_event(error, type='error')
                    execution['status'] = 'failed'
                    execution['error'] = error
                    if callback:
                        callback(execution)
                    return
                
                # Spawn agent for this step
                model = step.get('model', 'k2p5')
                agent_id = spawn_subagent(task, model)
                
                if not agent_id:
                    error = f"Failed to spawn agent for step {step_name}"
                    add_event(error, type='error')
                    execution['status'] = 'failed'
                    execution['error'] = error
                    if callback:
                        callback(execution)
                    return
                
                # Wait for completion (in real impl, this would be async)
                # For now, we simulate waiting
                max_wait = 300  # 5 minutes
                waited = 0
                while waited < max_wait:
                    if agent_id in ACTIVE_SUBAGENTS:
                        agent = ACTIVE_SUBAGENTS[agent_id]
                        if agent['status'] == 'completed':
                            break
                        elif agent['status'] == 'failed':
                            error = f"Step {step_name} failed"
                            add_event(error, type='error')
                            execution['status'] = 'failed'
                            execution['error'] = error
                            if callback:
                                callback(execution)
                            return
                    time.sleep(1)
                    waited += 1
                
                # Get result and add to context
                result = ACTIVE_SUBAGENTS.get(agent_id, {}).get('result', 'No result')
                output_var = step.get('output_var', f'step_{i}_output')
                context[output_var] = result
                
                # Track cost
                step_cost = ACTIVE_SUBAGENTS.get(agent_id, {}).get('actual_cost', 0)
                execution['total_cost'] += step_cost
                
                execution['step_results'].append({
                    'step': step_name,
                    'agent_id': agent_id,
                    'output': result,
                    'cost': step_cost
                })
                
                add_event(f"Step {step_name} completed (${step_cost:.4f})", type='success')
            
            # Workflow complete
            execution['status'] = 'completed'
            execution['completed_at'] = datetime.now().isoformat()
            execution['outputs'] = {k: v for k, v in context.items() 
                                   if k not in execution['inputs']}
            
            # Update workflow usage count
            workflow['usage_count'] = workflow.get('usage_count', 0) + 1
            wf_file = self.storage_path / f"{workflow['id']}.json"
            with open(wf_file, 'w') as f:
                json.dump(workflow, f, indent=2)
            
            add_event(f"Workflow {execution['id'][:8]} completed (${execution['total_cost']:.4f})", type='success')
            
        except Exception as e:
            execution['status'] = 'failed'
            execution['error'] = str(e)
            add_event(f"Workflow error: {e}", type='error')
        
        finally:
            if callback:
                callback(execution)
    
    def _evaluate_condition(self, condition, context):
        """Evaluate a simple condition against context"""
        # Simple condition evaluation: "variable == value" or "variable != value"
        try:
            if '==' in condition:
                var, val = condition.split('==')
                return context.get(var.strip()) == val.strip().strip('"\'')
            elif '!=' in condition:
                var, val = condition.split('!=')
                return context.get(var.strip()) != val.strip().strip('"\'')
        except:
            pass
        return True
    
    def get_execution_status(self, execution_id):
        """Get status of a workflow execution"""
        with self._lock:
            return self.active_workflows.get(execution_id)
    
    def list_workflows(self):
        """List all available workflow definitions"""
        workflows = []
        for wf_file in self.storage_path.glob('*.json'):
            try:
                with open(wf_file) as f:
                    wf = json.load(f)
                    workflows.append({
                        'id': wf['id'],
                        'name': wf['name'],
                        'description': wf.get('description', ''),
                        'steps': len(wf['steps']),
                        'usage_count': wf.get('usage_count', 0)
                    })
            except:
                pass
        return workflows

# Initialize workflow engine
workflow_engine = WorkflowEngine()

# Plugin System for Extensibility
class PluginManager:
    """
    Plugin system for extending J1MSKY functionality.
    Allows third-party extensions and custom integrations.
    """
    
    def __init__(self, plugins_path='/home/m1ndb0t/Desktop/J1MSKY/plugins'):
        self.plugins_path = Path(plugins_path)
        self.plugins_path.mkdir(exist_ok=True)
        self.loaded_plugins = {}
        self.hooks = {
            'pre_spawn': [],
            'post_complete': [],
            'on_error': [],
            'on_startup': [],
            'on_shutdown': []
        }
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Discover and register available plugins"""
        for plugin_dir in self.plugins_path.iterdir():
            if plugin_dir.is_dir():
                manifest_file = plugin_dir / 'manifest.json'
                if manifest_file.exists():
                    try:
                        with open(manifest_file) as f:
                            manifest = json.load(f)
                        self.loaded_plugins[manifest['id']] = {
                            'manifest': manifest,
                            'path': plugin_dir,
                            'enabled': False,
                            'instance': None
                        }
                    except Exception as e:
                        add_event(f"Plugin discovery error: {e}", type='error')
    
    def load_plugin(self, plugin_id):
        """Load and initialize a plugin"""
        if plugin_id not in self.loaded_plugins:
            return False, "Plugin not found"
        
        plugin = self.loaded_plugins[plugin_id]
        if plugin['enabled']:
            return True, "Already loaded"
        
        try:
            manifest = plugin['manifest']
            
            # Validate manifest
            required_fields = ['id', 'name', 'version', 'entry_point']
            for field in required_fields:
                if field not in manifest:
                    return False, f"Missing required field: {field}"
            
            # Check compatibility
            if 'min_j1msky_version' in manifest:
                # Version check logic here
                pass
            
            # Register hooks
            for hook in manifest.get('hooks', []):
                if hook in self.hooks:
                    self.hooks[hook].append(plugin_id)
            
            plugin['enabled'] = True
            add_event(f"Plugin loaded: {manifest['name']} v{manifest['version']}", type='success')
            
            # Trigger on_startup hook
            self.execute_hook('on_startup', {'plugin_id': plugin_id})
            
            return True, "Loaded successfully"
            
        except Exception as e:
            return False, str(e)
    
    def unload_plugin(self, plugin_id):
        """Unload a plugin"""
        if plugin_id not in self.loaded_plugins:
            return False
        
        plugin = self.loaded_plugins[plugin_id]
        if not plugin['enabled']:
            return True
        
        # Trigger on_shutdown hook
        self.execute_hook('on_shutdown', {'plugin_id': plugin_id})
        
        # Unregister hooks
        for hook_name in self.hooks:
            self.hooks[hook_name] = [p for p in self.hooks[hook_name] if p != plugin_id]
        
        plugin['enabled'] = False
        plugin['instance'] = None
        
        add_event(f"Plugin unloaded: {plugin_id}", type='info')
        return True
    
    def execute_hook(self, hook_name, context):
        """Execute all plugins registered for a hook"""
        if hook_name not in self.hooks:
            return context
        
        for plugin_id in self.hooks[hook_name]:
            plugin = self.loaded_plugins.get(plugin_id)
            if plugin and plugin['enabled']:
                try:
                    # Execute plugin hook (simplified)
                    add_event(f"Hook {hook_name} executed by {plugin_id}", type='debug')
                except Exception as e:
                    add_event(f"Plugin hook error: {e}", type='error')
        
        return context
    
    def list_plugins(self):
        """List all discovered plugins"""
        return [
            {
                'id': pid,
                'name': p['manifest']['name'],
                'version': p['manifest']['version'],
                'enabled': p['enabled'],
                'description': p['manifest'].get('description', '')
            }
            for pid, p in self.loaded_plugins.items()
        ]
    
    def create_plugin_template(self, plugin_id, name):
        """Create a new plugin template"""
        plugin_dir = self.plugins_path / plugin_id
        plugin_dir.mkdir(exist_ok=True)
        
        manifest = {
            "id": plugin_id,
            "name": name,
            "version": "1.0.0",
            "description": f"{name} plugin for J1MSKY",
            "author": "Your Name",
            "entry_point": "plugin.py",
            "min_j1msky_version": "4.0.0",
            "hooks": ["post_complete"],
            "config": {}
        }
        
        with open(plugin_dir / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        plugin_code = '''#!/usr/bin/env python3
"""
J1MSKY Plugin: {name}
"""

def initialize(config):
    """Called when plugin is loaded"""
    pass

def on_agent_complete(agent_data):
    """Called when an agent completes a task"""
    pass

def on_agent_error(error_data):
    """Called when an agent fails"""
    pass
'''.format(name=name)
        
        with open(plugin_dir / 'plugin.py', 'w') as f:
            f.write(plugin_code)
        
        return plugin_dir

# Initialize plugin manager
plugin_mgr = PluginManager()

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


def validate_model(model):
    """Validate requested model against supported model agents."""
    return model in MODEL_AGENTS


def sanitize_task(task, max_len=2000):
    """Normalize and constrain incoming task text."""
    if not isinstance(task, str):
        return ""
    cleaned = " ".join(task.strip().split())
    return cleaned[:max_len]


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
        if self.path == '/api/pricing/status':
            sample_quote = cost_tracker.recommend_task_quote('k2p5', estimated_input=1200, estimated_output=600, complexity='medium')
            guardrail = cost_tracker.evaluate_margin_guardrail(sample_quote, delivery_type='task')
            self.send_json({
                'success': True,
                'pricing_policy': {
                    'complexity_markup': {'low': 3.0, 'medium': 4.0, 'high': 5.0},
                    'minimum_price': 0.50,
                    'margin_thresholds': {'task': 55.0, 'subscription': 50.0, 'enterprise': 45.0}
                },
                'example_quote': sample_quote,
                'guardrail_check': guardrail
            })
        elif self.path == '/':
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
        
        if self.path == '/api/pricing/decision':
            model = params.get('model', ['k2p5'])[0]
            complexity = params.get('complexity', ['medium'])[0]
            delivery_type = params.get('delivery_type', ['task'])[0]
            approver = params.get('approver', ['ops-auto'])[0]

            try:
                estimated_input = int(params.get('estimated_input', ['1000'])[0])
                estimated_output = int(params.get('estimated_output', ['500'])[0])
            except ValueError:
                self.send_json({'success': False, 'error': 'estimated_input and estimated_output must be integers'})
                return

            if model not in cost_tracker.MODEL_PRICING:
                self.send_json({'success': False, 'error': f'Unsupported model: {model}'})
                return
            if complexity not in {'low', 'medium', 'high'}:
                self.send_json({'success': False, 'error': 'complexity must be low|medium|high'})
                return

            quote = cost_tracker.recommend_task_quote(
                model,
                estimated_input=estimated_input,
                estimated_output=estimated_output,
                complexity=complexity
            )
            guardrail = cost_tracker.evaluate_margin_guardrail(quote, delivery_type=delivery_type)
            decision_status = 'approved' if guardrail.get('is_compliant') else 'escalated'

            self.send_json({
                'success': True,
                'decision': {
                    'decision_status': decision_status,
                    'approver': approver,
                    'delivery_type': delivery_type,
                    'next_step': 'send_quote' if decision_status == 'approved' else 'route_to_deal_desk',
                    'generated_at': datetime.now().isoformat()
                },
                'quote': quote,
                'guardrail_check': guardrail
            })

        elif self.path == '/api/pricing/scenario':
            delivery_type = params.get('delivery_type', ['task'])[0]
            raw_scenarios = params.get('scenarios', ['[]'])[0]

            try:
                scenarios = json.loads(raw_scenarios)
                if not isinstance(scenarios, list) or not scenarios:
                    raise ValueError('scenarios must be a non-empty JSON array')
            except Exception as e:
                self.send_json({'success': False, 'error': f'Invalid scenarios payload: {e}'})
                return

            evaluated = []
            for idx, item in enumerate(scenarios):
                model = item.get('model', 'k2p5')
                complexity = item.get('complexity', 'medium')
                try:
                    estimated_input = int(item.get('estimated_input', 1000))
                    estimated_output = int(item.get('estimated_output', 500))
                except (TypeError, ValueError):
                    self.send_json({'success': False, 'error': f'Invalid token estimates in scenario {idx}'})
                    return

                if model not in cost_tracker.MODEL_PRICING:
                    self.send_json({'success': False, 'error': f'Unsupported model in scenario {idx}: {model}'})
                    return
                if complexity not in {'low', 'medium', 'high'}:
                    self.send_json({'success': False, 'error': f'Invalid complexity in scenario {idx}: {complexity}'})
                    return

                quote = cost_tracker.recommend_task_quote(
                    model,
                    estimated_input=estimated_input,
                    estimated_output=estimated_output,
                    complexity=complexity
                )
                guardrail = cost_tracker.evaluate_margin_guardrail(quote, delivery_type=delivery_type)
                evaluated.append({'quote': quote, 'guardrail_check': guardrail})

            compliant_count = sum(1 for e in evaluated if e['guardrail_check'].get('is_compliant'))
            avg_margin = round(sum(e['quote'].get('gross_margin_pct', 0.0) for e in evaluated) / len(evaluated), 2)
            compliance_ratio = round(compliant_count / len(evaluated), 2)

            self.send_json({
                'success': True,
                'delivery_type': delivery_type,
                'scenario_count': len(evaluated),
                'compliant_count': compliant_count,
                'compliance_ratio': compliance_ratio,
                'needs_escalation': compliant_count < len(evaluated),
                'requires_executive_review': compliance_ratio < 0.67,
                'average_margin_pct': avg_margin,
                'results': evaluated
            })

        elif self.path == '/api/pricing/exception-alert':
            try:
                open_exceptions = int(params.get('open_exceptions', ['0'])[0])
                oldest_days = int(params.get('oldest_days', ['0'])[0])
                at_risk_count = int(params.get('at_risk_count', ['0'])[0])
            except ValueError:
                self.send_json({'success': False, 'error': 'open_exceptions, oldest_days, at_risk_count must be integers'})
                return

            requires_exec = oldest_days >= 30 or at_risk_count >= 2
            if open_exceptions <= 0:
                level = 'none'
                summary = 'No open quote exceptions'
                next_action = 'no_action'
            elif requires_exec:
                level = 'critical'
                summary = f'Critical exception risk: {open_exceptions} open, oldest {oldest_days}d'
                next_action = 'schedule_executive_review'
            elif at_risk_count >= 1:
                level = 'warning'
                summary = f'Warning exception risk: {open_exceptions} open, oldest {oldest_days}d'
                next_action = 'manager_followup'
            else:
                level = 'ok'
                summary = f'Exceptions under control: {open_exceptions} open'
                next_action = 'continue_recovery_plan'

            self.send_json({
                'success': True,
                'exception_aging': {
                    'open_exceptions': open_exceptions,
                    'oldest_days': oldest_days,
                    'at_risk_count': at_risk_count,
                    'requires_exec_followup': requires_exec,
                    'risk_level': level,
                    'next_action': next_action
                },
                'exception_alert': {
                    'level': level,
                    'summary': summary,
                    'recommended_action': next_action
                }
            })

        elif self.path == '/api/pricing/portfolio-alert':
            try:
                scenario_count = int(params.get('scenario_count', ['0'])[0])
                compliant_count = int(params.get('compliant_count', ['0'])[0])
                avg_margin = float(params.get('average_margin_pct', ['0.0'])[0])
            except ValueError:
                self.send_json({'success': False, 'error': 'scenario_count and compliant_count must be integers, average_margin_pct must be float'})
                return

            if scenario_count <= 0:
                level = 'ok'
                summary = 'No portfolio scenarios to evaluate'
                action = 'no_action'
            else:
                ratio = round(compliant_count / scenario_count, 2)
                requires_exec = ratio < 0.67

                if requires_exec:
                    level = 'critical'
                    summary = f'Portfolio executive review required: {compliant_count}/{scenario_count} compliant, ratio {ratio}'
                    action = 'route_to_executive_review'
                elif ratio < 1.0:
                    level = 'warning'
                    summary = f'Portfolio needs attention: {compliant_count}/{scenario_count} compliant'
                    action = 'proceed_with_caution'
                else:
                    level = 'ok'
                    summary = f'Portfolio healthy: {compliant_count}/{scenario_count} compliant, margin {avg_margin}%'
                    action = 'send_proposal'

            self.send_json({
                'success': True,
                'portfolio_summary': {
                    'scenario_count': scenario_count,
                    'compliant_count': compliant_count,
                    'compliance_ratio': round(compliant_count / max(scenario_count, 1), 2),
                    'requires_executive_review': scenario_count > 0 and compliant_count < scenario_count * 0.67,
                    'average_margin_pct': avg_margin
                },
                'portfolio_alert': {
                    'level': level,
                    'summary': summary,
                    'recommended_action': action
                }
            })

        elif self.path == '/api/pricing/weekly-metrics':
            raw_quotes = params.get('quotes', ['[]'])[0]
            try:
                quotes = json.loads(raw_quotes)
                if not isinstance(quotes, list):
                    raise ValueError('quotes must be a JSON array')
            except Exception as e:
                self.send_json({'success': False, 'error': f'Invalid quotes payload: {e}'})
                return

            total = len(quotes)
            approved = sum(1 for q in quotes if q.get('decision_status') == 'approved')
            escalated = total - approved
            avg_margin = round(sum(q.get('gross_margin_pct', 0.0) for q in quotes) / max(total, 1), 2) if total else 0.0
            exceptions_created = sum(1 for q in quotes if q.get('exception_created'))
            exceptions_closed = sum(1 for q in quotes if q.get('exception_closed'))

            self.send_json({
                'success': True,
                'weekly_metrics': {
                    'total_quotes': total,
                    'approved_count': approved,
                    'escalated_count': escalated,
                    'approval_rate': round(approved / max(total, 1), 2),
                    'avg_margin_pct': avg_margin,
                    'exceptions_created': exceptions_created,
                    'exceptions_closed': exceptions_closed
                }
            })

        elif self.path == '/api/pricing/quote':
            model = params.get('model', ['k2p5'])[0]
            complexity = params.get('complexity', ['medium'])[0]
            delivery_type = params.get('delivery_type', ['task'])[0]

            try:
                estimated_input = int(params.get('estimated_input', ['1000'])[0])
                estimated_output = int(params.get('estimated_output', ['500'])[0])
            except ValueError:
                self.send_json({'success': False, 'error': 'estimated_input and estimated_output must be integers'})
                return

            if model not in cost_tracker.MODEL_PRICING:
                self.send_json({'success': False, 'error': f'Unsupported model: {model}'})
                return
            if complexity not in {'low', 'medium', 'high'}:
                self.send_json({'success': False, 'error': 'complexity must be low|medium|high'})
                return

            quote = cost_tracker.recommend_task_quote(
                model,
                estimated_input=estimated_input,
                estimated_output=estimated_output,
                complexity=complexity
            )
            guardrail = cost_tracker.evaluate_margin_guardrail(quote, delivery_type=delivery_type)

            self.send_json({'success': True, 'quote': quote, 'guardrail_check': guardrail})

        elif self.path == '/api/spawn':
            model = params.get('model', ['k2p5'])[0]
            task = sanitize_task(params.get('task', ['No task'])[0])

            if not validate_model(model):
                self.send_json({'success': False, 'error': f'Unsupported model: {model}'})
                return
            if not task:
                self.send_json({'success': False, 'error': 'Task cannot be empty'})
                return
            
            agent_id = spawn_subagent(task, model)
            
            if agent_id:
                self.send_json({'success': True, 'agent_id': agent_id})
            else:
                self.send_json({'success': False, 'error': 'Rate limited or error'})
                
        elif self.path == '/api/spawn-team':
            team_id = params.get('team', ['team_coding'])[0]
            task = sanitize_task(params.get('task', ['No task'])[0])
            
            if not task:
                self.send_json({'success': False, 'error': 'Task cannot be empty'})
                return

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
