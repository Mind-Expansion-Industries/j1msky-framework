#!/usr/bin/env python3
"""
J1MSKY Unified Model Orchestrator v5.1
Integrates all models: Anthropic (Opus/Sonnet), Kimi (K2.5), MiniMax (M2.5), OpenAI Codex
CEO-Worker hierarchy with automatic fallbacks
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import defaultdict

class UnifiedOrchestrator:
    def __init__(self):
        self.config_path = Path("/home/m1ndb0t/Desktop/J1MSKY/config/model-stack.json")
        self.config = self.load_config()
        self.usage_log = []
        self.daily_spend = defaultdict(float)
        
    def load_config(self):
        """Load model stack configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()

    def save_config(self):
        """Persist orchestrator config to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_default_config(self):
        """Default configuration if file missing"""
        return {
            "models": {
                "anthropic": {
                    "models": {
                        "claude-opus-4-6": {"alias": "opus", "role": "CEO"},
                        "claude-sonnet-4-6": {"alias": "sonnet", "role": "Operations"}
                    }
                },
                "kimi-coding": {
                    "models": {
                        "k2p5": {"alias": "k2p5", "role": "Lead Dev"}
                    }
                },
                "minimax-portal": {
                    "models": {
                        "MiniMax-M2.5": {"alias": "minimax-m2.5", "role": "Senior Dev"}
                    }
                },
                "openai-codex": {
                    "models": {
                        "codex": {"alias": "codex", "role": "Specialist"}
                    }
                }
            }
        }
    
    def get_model_for_task(self, task_type, complexity="medium", priority="normal"):
        """
        Select best model for task based on type, complexity, and priority
        """
        task_models = {
            "architecture": ["opus", "k2p5"],
            "strategy": ["opus"],
            "complex_reasoning": ["opus"],
            "implementation": ["sonnet", "minimax-m2.5"],
            "documentation": ["sonnet"],
            "coding": ["k2p5", "minimax-m2.5", "codex"],
            "fast_coding": ["minimax-m2.5", "k2p5"],
            "api_integration": ["codex", "k2p5"],
            "specialized_coding": ["codex"],
            "ui_design": ["sonnet", "minimax-m2.5"],
            "business_analysis": ["opus", "sonnet"]
        }
        
        # Get preferred models for task
        preferred = task_models.get(task_type, ["sonnet"])
        
        # Check rate limits and availability
        available = []
        for model in preferred:
            if self.check_model_available(model):
                available.append(model)
        
        # If none available, use fallback chain
        if not available:
            for model in preferred:
                fallback = self.get_fallback(model)
                if self.check_model_available(fallback):
                    available.append(fallback)
        
        # Return best available or default to sonnet
        return available[0] if available else "sonnet"
    
    def _refresh_rate_limit_window(self, provider: str):
        """Reset provider counters when hourly window rolls over."""
        rate_limits = self.config.setdefault("rate_limits", {})
        limits = rate_limits.setdefault(provider, {"hourly": 100, "current": 0})
        last_reset = limits.get("last_reset", time.time())
        window_seconds = limits.get("window", 3600)

        if (time.time() - last_reset) >= window_seconds:
            limits["current"] = 0
            limits["last_reset"] = time.time()

    def check_model_available(self, model_alias):
        """Check if model is within rate limits"""
        # Map alias to provider
        provider_map = {
            "opus": "anthropic",
            "sonnet": "anthropic",
            "k2p5": "kimi-coding",
            "minimax-m2.5": "minimax-portal",
            "codex": "openai-codex"
        }
        
        provider = provider_map.get(model_alias)
        if not provider:
            return True

        self._refresh_rate_limit_window(provider)
        limits = self.config.get("rate_limits", {}).get(provider, {})
        hourly_limit = limits.get("hourly", 100)
        current = limits.get("current", 0)
        
        return current < hourly_limit
    
    def get_fallback(self, model_alias):
        """Get fallback model"""
        fallbacks = self.config.get("orchestration", {}).get("fallback_chain", {})
        return fallbacks.get(model_alias, "sonnet")
    
    def record_usage(self, model_alias, task, tokens=0):
        """Record model usage"""
        usage = {
            "timestamp": datetime.now().isoformat(),
            "model": model_alias,
            "task": task,
            "tokens": tokens
        }
        self.usage_log.append(usage)

        # Track spend by day
        estimated_cost = self.estimate_cost(model_alias, tokens or 1000)
        day_key = datetime.now().strftime("%Y-%m-%d")
        self.daily_spend[day_key] += estimated_cost
        
        # Update rate limit counter
        provider_map = {
            "opus": "anthropic",
            "sonnet": "anthropic",
            "k2p5": "kimi-coding",
            "minimax-m2.5": "minimax-portal",
            "codex": "openai-codex"
        }
        provider = provider_map.get(model_alias)
        if provider:
            if provider not in self.config["rate_limits"]:
                self.config["rate_limits"][provider] = {
                    "hourly": 100,
                    "current": 0,
                    "window": 3600,
                    "last_reset": time.time()
                }
            self._refresh_rate_limit_window(provider)
            self.config["rate_limits"][provider]["current"] += 1

        # Persist counters and budget context
        self.save_config()
    
    def get_team_for_project(self, project_type):
        """Get recommended team composition for project type"""
        teams = {
            "web_app": {
                "lead": "k2p5",
                "frontend": "minimax-m2.5",
                "backend": "codex",
                "review": "sonnet"
            },
            "mobile_app": {
                "lead": "k2p5",
                "ui": "sonnet",
                "implementation": "minimax-m2.5",
                "api": "codex"
            },
            "ai_feature": {
                "architecture": "opus",
                "implementation": "k2p5",
                "integration": "codex",
                "docs": "sonnet"
            },
            "content_platform": {
                "strategy": "opus",
                "content": "sonnet",
                "automation": "minimax-m2.5",
                "seo": "k2p5"
            },
            "business_automation": {
                "analysis": "opus",
                "workflows": "k2p5",
                "integrations": "codex",
                "reporting": "sonnet"
            }
        }
        return teams.get(project_type, {"lead": "sonnet", "support": "minimax-m2.5"})
    
    def estimate_cost(self, model_alias, estimated_tokens=1000):
        """Estimate cost for task"""
        cost_map = {
            "opus": 0.015,
            "sonnet": 0.003,
            "k2p5": 0.001,
            "minimax-m2.5": 0.001,
            "codex": 0.002
        }
        cost_per_1k = cost_map.get(model_alias, 0.003)
        return (estimated_tokens / 1000) * cost_per_1k
    
    def get_daily_spend(self, day: Optional[str] = None) -> float:
        """Get spend for a specific day (YYYY-MM-DD) or today."""
        if not day:
            day = datetime.now().strftime("%Y-%m-%d")
        return round(self.daily_spend.get(day, 0.0), 4)

    def get_provider_usage_snapshot(self) -> Dict[str, Any]:
        """Return normalized provider usage with remaining headroom."""
        snapshot = {}
        rate_limits = self.config.get("rate_limits", {})
        for provider, limits in rate_limits.items():
            self._refresh_rate_limit_window(provider)
            current = limits.get("current", 0)
            hourly = limits.get("hourly", 100)
            remaining = max(hourly - current, 0)
            utilization = round((current / hourly) * 100, 2) if hourly else 0
            snapshot[provider] = {
                "current": current,
                "hourly": hourly,
                "remaining": remaining,
                "utilization_pct": utilization,
                "window": limits.get("window", 3600),
                "last_reset": limits.get("last_reset")
            }
        return snapshot

    def is_budget_available(self, model_alias: str, estimated_tokens: int = 1000) -> bool:
        """Check whether estimated call cost fits remaining daily budget."""
        daily_budget = self.config.get("cost_tracking", {}).get("daily_budget", 50)
        projected_cost = self.estimate_cost(model_alias, estimated_tokens)
        today_spend = self.get_daily_spend()
        return (today_spend + projected_cost) <= daily_budget

    def get_model_for_task_with_budget(self, task_type, complexity="medium", priority="normal", estimated_tokens: int = 1000):
        """
        Select a model while enforcing daily budget constraints.
        Falls back to cheaper available models if preferred model exceeds remaining budget.
        """
        preferred_model = self.get_model_for_task(task_type, complexity, priority)
        if self.is_budget_available(preferred_model, estimated_tokens):
            return preferred_model

        # Budget-aware fallbacks ordered by relative cost efficiency
        cost_ordered = ["k2p5", "minimax-m2.5", "sonnet", "codex", "opus"]
        for model in cost_ordered:
            if self.check_model_available(model) and self.is_budget_available(model, estimated_tokens):
                return model

        # If no model fits budget, return cheapest available to avoid hard failure
        for model in cost_ordered:
            if self.check_model_available(model):
                return model

        return "sonnet"

    def forecast_monthly_spend(self, days: int = 30) -> Dict[str, float]:
        """Forecast monthly spend from recent average usage."""
        today_spend = self.get_daily_spend()
        recent_days = max(min(days, 30), 1)

        # Approximate using current day as baseline if no historical breakdown exists
        projected_monthly = round(today_spend * recent_days, 4)
        daily_budget = self.config.get("cost_tracking", {}).get("daily_budget", 50)
        budget_monthly = round(daily_budget * recent_days, 4)

        return {
            "projected_spend": projected_monthly,
            "budget_ceiling": budget_monthly,
            "delta_to_budget": round(budget_monthly - projected_monthly, 4)
        }

    def get_status_report(self):
        """Get current orchestrator status"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_budget = self.config.get("cost_tracking", {}).get("daily_budget", 50)
        today_spend = self.get_daily_spend(today)
        return {
            "timestamp": datetime.now().isoformat(),
            "models_active": len(self.config["models"]),
            "rate_limits": self.config.get("rate_limits", {}),
            "provider_usage": self.get_provider_usage_snapshot(),
            "recent_usage": len(self.usage_log),
            "daily_budget": daily_budget,
            "today_spend": today_spend,
            "budget_remaining": round(max(daily_budget - today_spend, 0), 4),
            "monthly_forecast": self.forecast_monthly_spend(),
            "orchestration_mode": "unified",
            "ceo_model": "opus",
            "ops_model": "sonnet",
            "dev_models": ["k2p5", "minimax-m2.5", "codex"]
        }

# Global orchestrator instance
orchestrator = UnifiedOrchestrator()

# Health check and monitoring
class OrchestratorMonitor:
    """Monitor orchestrator health and performance"""
    
    def __init__(self, orch: UnifiedOrchestrator):
        self.orch = orch
        self.start_time = datetime.now()
        self.error_count = 0
        self.request_count = 0
        
    def get_health(self) -> Dict[str, Any]:
        """Get health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "status": "healthy" if self.error_count < 10 else "degraded",
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "models_configured": len(self.orch.config.get("models", {})),
        }
    
    def record_request(self):
        """Record successful request"""
        self.request_count += 1
        
    def record_error(self):
        """Record error"""
        self.error_count += 1

# Initialize monitor
monitor = OrchestratorMonitor(orchestrator)

if __name__ == "__main__":
    print("J1MSKY Unified Model Orchestrator v5.1")
    print("=" * 50)
    
    # Test orchestration
    print("\nModel Selection Tests:")
    
    test_tasks = [
        ("architecture", "high"),
        ("coding", "medium"),
        ("fast_coding", "low"),
        ("api_integration", "medium"),
        ("documentation", "medium"),
        ("strategy", "high")
    ]
    
    for task, complexity in test_tasks:
        model = orchestrator.get_model_for_task(task, complexity)
        cost = orchestrator.estimate_cost(model, 1000)
        print(f"  {task:20} -> {model:15} (est: ${cost:.3f})")
    
    print("\nTeam Compositions:")
    projects = ["web_app", "mobile_app", "ai_feature", "content_platform"]
    for project in projects:
        team = orchestrator.get_team_for_project(project)
        print(f"  {project:15} -> {team}")
    
    print("\nStatus Report:")
    status = orchestrator.get_status_report()
    print(f"  Models: {status['models_active']}")
    print(f"  Rate Limits: {status['rate_limits']}")
    print(f"  Daily Budget: ${status['daily_budget']}")
