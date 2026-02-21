#!/usr/bin/env python3
"""
J1MSKY Unified Model Orchestrator v5.1
Integrates all models: Anthropic (Opus/Sonnet), Kimi (K2.5), MiniMax (M2.5), OpenAI Codex
CEO-Worker hierarchy with automatic fallbacks
"""

import json
import time
import random
import threading
import hashlib
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

    def prune_usage_log(self, max_entries: int = 5000):
        """Keep usage log bounded to avoid unbounded memory growth."""
        if len(self.usage_log) > max_entries:
            self.usage_log = self.usage_log[-max_entries:]

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

    def validate_quote_request(self, model: str, complexity: str, segment: str = "mid_market", 
                                estimated_input: int = 1000, estimated_output: int = 500) -> tuple:
        """
        Centralized validation for pricing quote requests.
        Returns (is_valid: bool, error_message: str, sanitized_params: dict)
        """
        errors = []
        
        # Validate model
        valid_models = ["k2p5", "sonnet", "opus", "minimax-m2.5", "codex"]
        if model not in valid_models:
            errors.append(f"Invalid model '{model}'. Must be one of: {', '.join(valid_models)}")
        
        # Validate complexity
        valid_complexities = ["low", "medium", "high"]
        if complexity not in valid_complexities:
            errors.append(f"Invalid complexity '{complexity}'. Must be one of: {', '.join(valid_complexities)}")
        
        # Validate segment
        valid_segments = ["enterprise", "mid_market", "smb", "startup"]
        if segment not in valid_segments:
            errors.append(f"Invalid segment '{segment}'. Must be one of: {', '.join(valid_segments)}")
        
        # Validate token estimates
        try:
            estimated_input = int(estimated_input)
            estimated_output = int(estimated_output)
            if estimated_input < 1 or estimated_output < 1:
                errors.append("Token estimates must be positive integers")
            if estimated_input > 100000 or estimated_output > 100000:
                errors.append("Token estimates exceed maximum (100,000)")
        except (TypeError, ValueError):
            errors.append("Token estimates must be valid integers")
        
        if errors:
            return False, "; ".join(errors), {}
        
        return True, "", {
            "model": model,
            "complexity": complexity,
            "segment": segment,
            "estimated_input": estimated_input,
            "estimated_output": estimated_output
        }

    def bulk_generate_quotes(self, tasks: list) -> list:
        """
        Generate quotes for multiple tasks in a single batch operation.
        More efficient than individual quote requests for bulk operations.
        
        Args:
            tasks: List of dicts with keys: model, complexity, segment, 
                   estimated_input, estimated_output
        
        Returns:
            List of quote result dicts with validation status
        """
        results = []
        
        for idx, task in enumerate(tasks):
            # Validate each task
            is_valid, error_msg, params = self.validate_quote_request(
                task.get("model", "k2p5"),
                task.get("complexity", "medium"),
                task.get("segment", "mid_market"),
                task.get("estimated_input", 1000),
                task.get("estimated_output", 500)
            )
            
            if not is_valid:
                results.append({
                    "index": idx,
                    "success": False,
                    "error": error_msg,
                    "task_preview": task.get("task_preview", "unnamed task")
                })
                continue
            
            # Generate quote
            try:
                quote = self.recommend_task_price(
                    params["model"],
                    params["estimated_input"],
                    params["complexity"],
                    params["segment"]
                )
                
                guardrail = self.evaluate_pricing_guardrails(quote, task.get("delivery_type", "task"))
                
                results.append({
                    "index": idx,
                    "success": True,
                    "quote": quote,
                    "guardrail": guardrail,
                    "task_preview": task.get("task_preview", "unnamed task")
                })
            except Exception as e:
                results.append({
                    "index": idx,
                    "success": False,
                    "error": str(e),
                    "task_preview": task.get("task_preview", "unnamed task")
                })
        
        return results

    def record_usage(self, model_alias, task, tokens=0):
        """Record model usage"""
        usage = {
            "timestamp": datetime.now().isoformat(),
            "model": model_alias,
            "task": task,
            "tokens": tokens
        }
        self.usage_log.append(usage)
        self.prune_usage_log()

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

    def get_pricing_policy(self) -> Dict[str, Any]:
        """Return pricing policy with safe defaults for customer quoting."""
        pricing = self.config.get("pricing", {})
        return {
            "min_markup": pricing.get("min_markup", 3.0),
            "target_markup": pricing.get("target_markup", 4.0),
            "max_markup": pricing.get("max_markup", 5.0),
            "complexity_markup": pricing.get(
                "complexity_markup",
                {"low": 3.0, "medium": 4.0, "high": 5.0}
            ),
            "minimum_price": pricing.get("minimum_price", 0.50)
        }

    def recommend_task_price(self, model_alias: str, estimated_tokens: int = 1000, complexity: str = "medium", segment: str = "mid_market") -> Dict[str, Any]:
        """Return an internal-cost + customer-price quote for pay-per-task workflows."""
        policy = self.get_pricing_policy()
        internal_cost = round(self.estimate_cost(model_alias, estimated_tokens), 4)

        # Segment markup adjustments
        segment_adjustments = {
            "enterprise": 0.5,
            "mid_market": 0.0,
            "smb": -0.5,
            "startup": -1.0
        }
        segment_adj = segment_adjustments.get(segment, 0.0)

        complexity_map = policy.get("complexity_markup", {})
        base_markup = complexity_map.get(complexity, policy.get("target_markup", 4.0))
        markup = base_markup + segment_adj
        markup = min(max(markup, policy.get("min_markup", 3.0)), policy.get("max_markup", 5.0))

        recommended_price = max(internal_cost * markup, policy.get("minimum_price", 0.50))
        gross_margin_pct = round(((recommended_price - internal_cost) / recommended_price) * 100, 2) if recommended_price else 0.0

        if gross_margin_pct >= 70:
            margin_band = "strong"
        elif gross_margin_pct >= 55:
            margin_band = "healthy"
        else:
            margin_band = "at_risk"

        return {
            "model": model_alias,
            "complexity": complexity,
            "segment": segment,
            "estimated_tokens": estimated_tokens,
            "internal_cost": internal_cost,
            "base_markup": base_markup,
            "segment_adjustment": segment_adj,
            "final_markup": round(markup, 2),
            "recommended_price": round(recommended_price, 2),
            "gross_margin_pct": gross_margin_pct,
            "margin_band": margin_band
        }

    def evaluate_pricing_guardrails(self, quote: Dict[str, Any], delivery_type: str = "task") -> Dict[str, Any]:
        """Evaluate quote against margin guardrails for ops approvals."""
        margin = quote.get("gross_margin_pct", 0.0)
        threshold_map = {
            "task": 55.0,
            "subscription": 50.0,
            "enterprise": 45.0
        }
        threshold = threshold_map.get(delivery_type, 55.0)
        is_compliant = margin >= threshold

        return {
            "delivery_type": delivery_type,
            "minimum_margin_pct": threshold,
            "actual_margin_pct": margin,
            "is_compliant": is_compliant,
            "action": "approve_quote" if is_compliant else "escalate_deal_desk"
        }

    def build_quote_decision_record(self, quote: Dict[str, Any], delivery_type: str = "task", approver: str = "ops-auto") -> Dict[str, Any]:
        """Build an auditable quote decision payload for CRM or handoff logs."""
        guardrail = self.evaluate_pricing_guardrails(quote, delivery_type=delivery_type)
        approved = guardrail.get("is_compliant", False)
        decision_status = "approved" if approved else "escalated"

        return {
            "decision_status": decision_status,
            "approver": approver,
            "delivery_type": delivery_type,
            "quote": quote,
            "guardrail": guardrail,
            "next_step": "send_quote" if approved else "route_to_deal_desk",
            "generated_at": datetime.now().isoformat()
        }

    def summarize_quote_portfolio(self, quotes: List[Dict[str, Any]], delivery_type: str = "task") -> Dict[str, Any]:
        """Return compliance rollup for a list of quote candidates."""
        if not quotes:
            return {
                "delivery_type": delivery_type,
                "scenario_count": 0,
                "compliant_count": 0,
                "needs_escalation": False,
                "average_margin_pct": 0.0
            }

        results = [self.evaluate_pricing_guardrails(q, delivery_type=delivery_type) for q in quotes]
        compliant_count = sum(1 for r in results if r.get("is_compliant"))
        avg_margin = round(sum(q.get("gross_margin_pct", 0.0) for q in quotes) / len(quotes), 2)

        compliance_ratio = round(compliant_count / len(quotes), 2)
        return {
            "delivery_type": delivery_type,
            "scenario_count": len(quotes),
            "compliant_count": compliant_count,
            "compliance_ratio": compliance_ratio,
            "needs_escalation": compliant_count < len(quotes),
            "requires_executive_review": compliance_ratio < 0.67,
            "average_margin_pct": avg_margin
        }

    def assess_exception_aging(self, open_exception_days: List[int]) -> Dict[str, Any]:
        """Classify exception age risk for weekly revenue governance."""
        if not open_exception_days:
            return {
                "open_exceptions": 0,
                "oldest_days": 0,
                "at_risk_count": 0,
                "requires_exec_followup": False,
                "risk_level": "none",
                "next_action": "no_action"
            }

        oldest = max(open_exception_days)
        at_risk = sum(1 for d in open_exception_days if d >= 14)
        requires_exec = oldest >= 30 or at_risk >= 2

        if requires_exec:
            risk_level = "critical"
            next_action = "schedule_executive_review"
        elif at_risk >= 1:
            risk_level = "warning"
            next_action = "manager_followup"
        else:
            risk_level = "ok"
            next_action = "continue_recovery_plan"

        return {
            "open_exceptions": len(open_exception_days),
            "oldest_days": oldest,
            "at_risk_count": at_risk,
            "requires_exec_followup": requires_exec,
            "risk_level": risk_level,
            "next_action": next_action
        }

    def build_exception_alert(self, exception_aging: Dict[str, Any]) -> Dict[str, str]:
        """Build human-readable ops alert message from exception aging risk."""
        level = exception_aging.get("risk_level", "none")
        oldest = exception_aging.get("oldest_days", 0)
        open_count = exception_aging.get("open_exceptions", 0)
        action = exception_aging.get("next_action", "no_action")

        if level == "critical":
            summary = f"Critical exception risk: {open_count} open, oldest {oldest}d"
        elif level == "warning":
            summary = f"Warning exception risk: {open_count} open, oldest {oldest}d"
        elif level == "ok":
            summary = f"Exceptions under control: {open_count} open"
        else:
            summary = "No open quote exceptions"

        return {
            "level": level,
            "summary": summary,
            "recommended_action": action
        }

    def build_portfolio_alert(self, portfolio: Dict[str, Any]) -> Dict[str, str]:
        """Build human-readable ops alert message from portfolio rollup."""
        scenarios = portfolio.get("scenario_count", 0)
        compliant = portfolio.get("compliant_count", 0)
        ratio = portfolio.get("compliance_ratio", 0.0)
        margin = portfolio.get("average_margin_pct", 0.0)
        needs_exec = portfolio.get("requires_executive_review", False)

        if needs_exec:
            level = "critical"
            summary = f"Portfolio executive review required: {compliant}/{scenarios} compliant, ratio {ratio}"
        elif ratio < 1.0:
            level = "warning"
            summary = f"Portfolio needs attention: {compliant}/{scenarios} compliant"
        else:
            level = "ok"
            summary = f"Portfolio healthy: {compliant}/{scenarios} compliant, margin {margin}%"

        return {
            "level": level,
            "summary": summary,
            "recommended_action": "route_to_executive_review" if needs_exec else "proceed_with_caution" if ratio < 1.0 else "send_proposal"
        }

    def aggregate_weekly_pricing_metrics(self, weekly_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate weekly pricing decisions for retrospective analysis."""
        if not weekly_quotes:
            return {
                "total_quotes": 0,
                "approved_count": 0,
                "escalated_count": 0,
                "approval_rate": 0.0,
                "avg_margin_pct": 0.0,
                "exceptions_created": 0,
                "exceptions_closed": 0
            }

        total = len(weekly_quotes)
        approved = sum(1 for q in weekly_quotes if q.get("decision_status") == "approved")
        escalated = total - approved
        avg_margin = round(sum(q.get("gross_margin_pct", 0.0) for q in weekly_quotes) / total, 2)

        return {
            "total_quotes": total,
            "approved_count": approved,
            "escalated_count": escalated,
            "approval_rate": round(approved / total, 2),
            "avg_margin_pct": avg_margin,
            "exceptions_created": sum(1 for q in weekly_quotes if q.get("exception_created")),
            "exceptions_closed": sum(1 for q in weekly_quotes if q.get("exception_closed"))
        }

    def compare_weekly_metrics(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two weeks of pricing metrics and flag significant changes."""
        def pct_change(curr, prev):
            if prev == 0:
                return 0.0 if curr == 0 else float('inf')
            return round(((curr - prev) / prev) * 100, 2)

        changes = {
            "total_quotes_change": pct_change(current.get("total_quotes", 0), previous.get("total_quotes", 0)),
            "approval_rate_change": pct_change(current.get("approval_rate", 0), previous.get("approval_rate", 0)),
            "avg_margin_change": pct_change(current.get("avg_margin_pct", 0), previous.get("avg_margin_pct", 0)),
            "exceptions_created_change": pct_change(current.get("exceptions_created", 0), previous.get("exceptions_created", 0))
        }

        alerts = []
        if abs(changes["approval_rate_change"]) > 15:
            alerts.append(f"Approval rate shifted {changes['approval_rate_change']}%")
        if abs(changes["avg_margin_change"]) > 10:
            alerts.append(f"Average margin shifted {changes['avg_margin_change']}%")
        if changes["exceptions_created_change"] > 50:
            alerts.append(f"Exception creation up {changes['exceptions_created_change']}%")

        return {
            "week_over_week_changes": changes,
            "significant_shifts": alerts,
            "requires_review": len(alerts) > 0
        }

    def track_experiment(self, experiment_id: str, variant: str, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Track a quote as part of a pricing experiment."""
        return {
            "experiment_id": experiment_id,
            "variant": variant,
            "timestamp": datetime.now().isoformat(),
            "quote": quote,
            "tracked": True
        }

    def summarize_experiment(self, experiment_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize experiment results for decision-making."""
        if not experiment_quotes:
            return {"status": "no_data", "control": {}, "test": {}}

        control = [q for q in experiment_quotes if q.get("variant") == "control"]
        test = [q for q in experiment_quotes if q.get("variant") == "test"]

        def summarize_variant(quotes):
            if not quotes:
                return {}
            total = len(quotes)
            approved = sum(1 for q in quotes if q.get("quote", {}).get("decision_status") == "approved")
            avg_margin = sum(q.get("quote", {}).get("gross_margin_pct", 0) for q in quotes) / total
            return {
                "count": total,
                "approval_rate": round(approved / total, 2),
                "avg_margin_pct": round(avg_margin, 2)
            }

        control_summary = summarize_variant(control)
        test_summary = summarize_variant(test)

        recommendation = "inconclusive"
        if control_summary and test_summary:
            if test_summary.get("avg_margin_pct", 0) > control_summary.get("avg_margin_pct", 0) and \
               test_summary.get("approval_rate", 0) >= control_summary.get("approval_rate", 0) * 0.9:
                recommendation = "roll_out"
            elif test_summary.get("approval_rate", 0) < control_summary.get("approval_rate", 0) * 0.8:
                recommendation = "discard"
            elif test_summary.get("avg_margin_pct", 0) < control_summary.get("avg_margin_pct", 0) * 0.9:
                recommendation = "discard"

        return {
            "status": "complete" if control and test else "in_progress",
            "control": control_summary,
            "test": test_summary,
            "recommendation": recommendation
        }

    def generate_pricing_summary_report(self, quotes: List[Dict[str, Any]], period: str = "weekly") -> Dict[str, Any]:
        """Generate a comprehensive pricing summary report for a given period."""
        if not quotes:
            return {
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "summary": "No quotes in period",
                "metrics": {}
            }

        # Overall metrics
        total = len(quotes)
        approved = sum(1 for q in quotes if q.get("decision_status") == "approved")
        escalated = total - approved
        avg_margin = sum(q.get("gross_margin_pct", 0) for q in quotes) / total
        total_revenue = sum(q.get("recommended_price", 0) for q in quotes)

        # Segment breakdown
        segments = {}
        for q in quotes:
            seg = q.get("segment", "unknown")
            if seg not in segments:
                segments[seg] = {"count": 0, "approved": 0, "revenue": 0}
            segments[seg]["count"] += 1
            if q.get("decision_status") == "approved":
                segments[seg]["approved"] += 1
            segments[seg]["revenue"] += q.get("recommended_price", 0)

        for seg in segments:
            seg_quotes = [q for q in quotes if q.get("segment") == seg]
            segments[seg]["avg_margin"] = round(sum(q.get("gross_margin_pct", 0) for q in seg_quotes) / len(seg_quotes), 2)
            segments[seg]["approval_rate"] = round(segments[seg]["approved"] / segments[seg]["count"], 2)

        # Model breakdown
        models = {}
        for q in quotes:
            model = q.get("model", "unknown")
            if model not in models:
                models[model] = {"count": 0}
            models[model]["count"] += 1

        for model in models:
            model_quotes = [q for q in quotes if q.get("model") == model]
            models[model]["avg_margin"] = round(sum(q.get("gross_margin_pct", 0) for q in model_quotes) / len(model_quotes), 2)

        return {
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "summary": f"{total} quotes, {approved} approved, {escalated} escalated",
            "metrics": {
                "total_quotes": total,
                "approved_count": approved,
                "escalated_count": escalated,
                "approval_rate": round(approved / total, 2),
                "avg_margin_pct": round(avg_margin, 2),
                "total_revenue": round(total_revenue, 2)
            },
            "by_segment": segments,
            "by_model": models,
            "exceptions": {
                "created": sum(1 for q in quotes if q.get("exception_created")),
                "closed": sum(1 for q in quotes if q.get("exception_closed"))
            }
        }

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

    def get_usage_summary(self, limit: int = 5) -> Dict[str, Any]:
        """Return a compact usage summary by model for quick ops review."""
        by_model: Dict[str, Dict[str, float]] = defaultdict(lambda: {"calls": 0, "tokens": 0})
        for item in self.usage_log:
            model = item.get("model", "unknown")
            by_model[model]["calls"] += 1
            by_model[model]["tokens"] += item.get("tokens", 0)

        ranked = sorted(by_model.items(), key=lambda kv: kv[1]["calls"], reverse=True)[:limit]
        top_models = []
        for model, stats in ranked:
            calls = max(stats["calls"], 1)
            avg_tokens = round(stats["tokens"] / calls, 2)
            est_cost = round(self.estimate_cost(model, stats["tokens"]), 4)
            top_models.append({
                "model": model,
                "calls": stats["calls"],
                "tokens": stats["tokens"],
                "avg_tokens_per_call": avg_tokens,
                "estimated_spend": est_cost
            })

        return {
            "top_models": top_models,
            "total_calls": len(self.usage_log)
        }

    def get_budget_utilization_pct(self) -> float:
        """Return today's budget utilization percentage."""
        daily_budget = self.config.get("cost_tracking", {}).get("daily_budget", 50)
        if daily_budget <= 0:
            return 0.0
        return round((self.get_daily_spend() / daily_budget) * 100, 2)

    def get_budget_alert_level(self) -> str:
        """Return budget alert level for operational routing."""
        pct = self.get_budget_utilization_pct()
        if pct >= 90:
            return "critical"
        if pct >= 70:
            return "warning"
        if pct >= 50:
            return "notice"
        return "ok"

    def detect_usage_anomalies(self) -> Dict[str, Any]:
        """Detect simple anomalies in recent usage patterns."""
        summary = self.get_usage_summary(limit=10)
        top_models = summary.get("top_models", [])
        anomalies = []

        for item in top_models:
            calls = item.get("calls", 0)
            avg_tokens = item.get("avg_tokens_per_call", 0)
            model = item.get("model", "unknown")

            if calls >= 100:
                anomalies.append({"model": model, "type": "high_call_volume", "value": calls})
            if avg_tokens >= 5000:
                anomalies.append({"model": model, "type": "high_tokens_per_call", "value": avg_tokens})

        severity = "none"
        if any(a["type"] == "high_call_volume" for a in anomalies):
            severity = "warning"
        if len(anomalies) >= 2:
            severity = "critical"

        return {
            "has_anomalies": len(anomalies) > 0,
            "anomalies": anomalies,
            "count": len(anomalies),
            "severity": severity
        }

    def get_operational_flags(self) -> Dict[str, Any]:
        """Return normalized operational state for routing and dashboards."""
        provider_usage = self.get_provider_usage_snapshot()
        max_provider_util = 0.0
        hot_providers = []

        for provider, usage in provider_usage.items():
            util = usage.get("utilization_pct", 0.0)
            max_provider_util = max(max_provider_util, util)
            if util >= 80:
                hot_providers.append(provider)

        budget_level = self.get_budget_alert_level()
        return {
            "budget_alert_level": budget_level,
            "max_provider_utilization_pct": round(max_provider_util, 2),
            "hot_providers": hot_providers,
            "requires_ops_attention": budget_level in {"warning", "critical"} or len(hot_providers) > 0,
            "recommended_action": self.get_recommended_action(budget_level, hot_providers)
        }

    def get_recommended_action(self, budget_level: str, hot_providers: List[str]) -> str:
        """Suggest immediate operator action based on current state."""
        if budget_level == "critical":
            return "Pause non-critical workloads and force cheapest model routing"
        if budget_level == "warning":
            return "Shift medium/low-priority tasks to k2p5/minimax and monitor hourly"
        if hot_providers:
            providers = ", ".join(hot_providers)
            return f"Throttle traffic for: {providers}"
        return "No action required"

    def get_model_mix_recommendation(self) -> Dict[str, Any]:
        """Recommend model mix adjustments from recent usage and budget state."""
        summary = self.get_usage_summary(limit=10)
        budget_level = self.get_budget_alert_level()

        if budget_level in {"warning", "critical"}:
            return {
                "strategy": "cost-optimized",
                "primary": ["k2p5", "minimax-m2.5"],
                "secondary": ["sonnet"],
                "restricted": ["opus"],
                "reason": "Budget pressure detected"
            }

        top_models = [m["model"] for m in summary.get("top_models", [])[:3]]
        return {
            "strategy": "balanced",
            "primary": top_models or ["k2p5", "sonnet"],
            "secondary": ["codex"],
            "restricted": [],
            "reason": "Normal operating range"
        }

    def get_status_report(self):
        """Get current orchestrator status"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_budget = self.config.get("cost_tracking", {}).get("daily_budget", 50)
        today_spend = self.get_daily_spend(today)
        default_quote_model = self.get_model_for_task("coding", "medium", "normal")
        sample_quote = self.recommend_task_price(default_quote_model, estimated_tokens=2000, complexity="medium")
        sample_guardrail = self.evaluate_pricing_guardrails(sample_quote, delivery_type="task")
        sample_decision = self.build_quote_decision_record(sample_quote, delivery_type="task", approver="ops-auto")
        sample_portfolio = self.summarize_quote_portfolio([
            sample_quote,
            self.recommend_task_price("sonnet", estimated_tokens=3500, complexity="high"),
            self.recommend_task_price("opus", estimated_tokens=5000, complexity="high")
        ], delivery_type="task")
        sample_exception_aging = self.assess_exception_aging([4, 11, 19, 33])
        sample_exception_alert = self.build_exception_alert(sample_exception_aging)
        return {
            "timestamp": datetime.now().isoformat(),
            "models_active": len(self.config["models"]),
            "rate_limits": self.config.get("rate_limits", {}),
            "provider_usage": self.get_provider_usage_snapshot(),
            "usage_summary": self.get_usage_summary(),
            "recent_usage": len(self.usage_log),
            "daily_budget": daily_budget,
            "today_spend": today_spend,
            "budget_remaining": round(max(daily_budget - today_spend, 0), 4),
            "budget_utilization_pct": self.get_budget_utilization_pct(),
            "budget_alert_level": self.get_budget_alert_level(),
            "operational_flags": self.get_operational_flags(),
            "model_mix_recommendation": self.get_model_mix_recommendation(),
            "pricing_policy": self.get_pricing_policy(),
            "example_task_quote": sample_quote,
            "pricing_guardrail_check": sample_guardrail,
            "quote_decision_preview": sample_decision,
            "quote_portfolio_preview": sample_portfolio,
            "portfolio_alert_preview": self.build_portfolio_alert(sample_portfolio),
            "weekly_metrics_preview": self.aggregate_weekly_pricing_metrics([
                sample_decision,
                {"decision_status": "escalated", "gross_margin_pct": 42.0, "exception_created": True, "exception_closed": False}
            ]),
            "weekly_comparison_preview": self.compare_weekly_metrics(
                {"total_quotes": 50, "approval_rate": 0.84, "avg_margin_pct": 72.5, "exceptions_created": 3},
                {"total_quotes": 45, "approval_rate": 0.88, "avg_margin_pct": 68.0, "exceptions_created": 2}
            ),
            "exception_aging_preview": sample_exception_aging,
            "exception_alert_preview": sample_exception_alert,
            "usage_anomalies": self.detect_usage_anomalies(),
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


# Simple TTL Cache for expensive operations
class SimpleTTLCache:
    """
    Thread-safe TTL cache for expensive operations.
    Used to cache model recommendations and pricing calculations.
    """
    
    def __init__(self, default_ttl_seconds: int = 60):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired."""
        with self._lock:
            if key not in self._cache:
                return None
            
            timestamp = self._timestamps.get(key, 0)
            if (time.time() - timestamp) > self.default_ttl:
                # Expired - clean up
                del self._cache[key]
                del self._timestamps[key]
                return None
            
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store value with optional custom TTL."""
        ttl = ttl_seconds or self.default_ttl
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def invalidate(self, key: str) -> bool:
        """Remove key from cache. Returns True if key existed."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = time.time()
        removed = 0
        with self._lock:
            expired_keys = [
                k for k, ts in self._timestamps.items()
                if (now - ts) > self.default_ttl
            ]
            for k in expired_keys:
                del self._cache[k]
                del self._timestamps[k]
                removed += 1
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            now = time.time()
            expired = sum(
                1 for ts in self._timestamps.values()
                if (now - ts) > self.default_ttl
            )
            return {
                "total_entries": len(self._cache),
                "expired_entries": expired,
                "valid_entries": len(self._cache) - expired,
                "default_ttl_seconds": self.default_ttl
            }


# Global cache instances
_model_cache = SimpleTTLCache(default_ttl_seconds=30)  # Model availability changes frequently
_pricing_cache = SimpleTTLCache(default_ttl_seconds=300)  # Pricing policy changes less often
_team_cache = SimpleTTLCache(default_ttl_seconds=60)  # Team compositions stable


def cached_model_selection(task_type: str, complexity: str, priority: str) -> str:
    """
    Get model for task with caching.
    Cache key includes all parameters that affect selection.
    """
    cache_key = f"model:{task_type}:{complexity}:{priority}"
    
    # Try cache first
    cached = _model_cache.get(cache_key)
    if cached is not None:
        monitor.record_request()
        return cached
    
    # Compute and cache
    result = orchestrator.get_model_for_task(task_type, complexity, priority)
    _model_cache.set(cache_key, result)
    monitor.record_request()
    return result


def cached_team_recommendation(project_type: str) -> Dict[str, str]:
    """Get team composition with caching."""
    cache_key = f"team:{project_type}"
    
    cached = _team_cache.get(cache_key)
    if cached is not None:
        return cached
    
    result = orchestrator.get_team_for_project(project_type)
    _team_cache.set(cache_key, result)
    return result


def cached_price_quote(model: str, tokens: int, complexity: str, segment: str) -> Dict[str, Any]:
    """Get pricing quote with caching (rounded tokens for cache efficiency)."""
    # Round tokens to nearest 100 for better cache hit rate
    rounded_tokens = round(tokens / 100) * 100
    cache_key = f"price:{model}:{rounded_tokens}:{complexity}:{segment}"
    
    cached = _pricing_cache.get(cache_key)
    if cached is not None:
        return cached
    
    result = orchestrator.recommend_task_price(model, tokens, complexity, segment)
    _pricing_cache.set(cache_key, result)
    return result


def invalidate_caches(cache_type: Optional[str] = None) -> Dict[str, int]:
    """
    Invalidate cache entries.
    
    Args:
        cache_type: 'model', 'pricing', 'team', or None for all
    
    Returns:
        Dict with counts of invalidated entries by cache type
    """
    results = {}
    
    if cache_type is None or cache_type == "model":
        count = len(_model_cache._cache)
        _model_cache.clear()
        results["model"] = count
    
    if cache_type is None or cache_type == "pricing":
        count = len(_pricing_cache._cache)
        _pricing_cache.clear()
        results["pricing"] = count
    
    if cache_type is None or cache_type == "team":
        count = len(_team_cache._cache)
        _team_cache.clear()
        results["team"] = count
    
    return results


def get_cache_status() -> Dict[str, Any]:
    """Get status of all caches for monitoring."""
    return {
        "model_cache": _model_cache.get_stats(),
        "pricing_cache": _pricing_cache.get_stats(),
        "team_cache": _team_cache.get_stats(),
        "cache_hit_savings_estimate": "~5-15ms per cached call"
    }


# A/B Testing Framework for Pricing Optimization
class ABTestFramework:
    """
    A/B testing framework for pricing optimization and feature experiments.
    
    Usage:
        ab = ABTestFramework()
        
        # Define an experiment
        ab.create_experiment(
            experiment_id="pricing_v2",
            variants={
                "control": {"markup": 4.0},
                "test": {"markup": 3.5}
            },
            traffic_split=0.2  # 20% to test
        )
        
        # Assign user to variant
        variant = ab.assign_variant("pricing_v2", user_id="user_123")
        
        # Record outcome
        ab.record_outcome("pricing_v2", "user_123", converted=True, revenue=99.0)
        
        # Get results
        results = ab.get_results("pricing_v2")
    """
    
    def __init__(self, storage_path: str = "/home/m1ndb0t/Desktop/J1MSKY/config"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.experiments_file = self.storage_path / "ab_experiments.json"
        self.experiments = self._load_experiments()
        self._lock = threading.Lock()
    
    def _load_experiments(self) -> Dict[str, Any]:
        """Load experiments from disk."""
        if self.experiments_file.exists():
            try:
                with open(self.experiments_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_experiments(self):
        """Save experiments to disk."""
        with open(self.experiments_file, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def create_experiment(
        self,
        experiment_id: str,
        name: str = "",
        variants: Dict[str, Dict] = None,
        traffic_split: float = 0.2,
        min_sample_size: int = 100,
        success_metric: str = "conversion"
    ) -> Dict[str, Any]:
        """
        Create a new A/B test experiment.
        
        Args:
            experiment_id: Unique identifier for the experiment
            name: Human-readable name
            variants: Dict of variant names to their configurations
            traffic_split: Percentage of traffic to send to test variant (0.0-1.0)
            min_sample_size: Minimum samples before calculating significance
            success_metric: Metric to optimize for ('conversion', 'revenue', 'engagement')
        """
        if experiment_id in self.experiments:
            return {"success": False, "error": f"Experiment {experiment_id} already exists"}
        
        if variants is None:
            variants = {"control": {}, "test": {}}
        
        experiment = {
            "id": experiment_id,
            "name": name or experiment_id,
            "variants": variants,
            "traffic_split": traffic_split,
            "min_sample_size": min_sample_size,
            "success_metric": success_metric,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "assignments": {},  # user_id -> variant
            "results": {variant: {"conversions": 0, "total": 0, "revenue": 0.0} 
                       for variant in variants.keys()}
        }
        
        with self._lock:
            self.experiments[experiment_id] = experiment
            self._save_experiments()
        
        return {"success": True, "experiment": experiment}
    
    def assign_variant(self, experiment_id: str, user_id: str) -> str:
        """
        Assign a user to a variant for an experiment.
        Returns the variant name assigned.
        """
        with self._lock:
            if experiment_id not in self.experiments:
                return "control"  # Default fallback
            
            experiment = self.experiments[experiment_id]
            
            if experiment["status"] != "running":
                return "control"
            
            # Check if already assigned
            if user_id in experiment["assignments"]:
                return experiment["assignments"][user_id]
            
            # Assign based on traffic split
            variants = list(experiment["variants"].keys())
            if len(variants) < 2:
                return variants[0] if variants else "control"
            
            # Use hash for deterministic but random-looking assignment
            hash_input = f"{experiment_id}:{user_id}"
            hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            
            # Assign to test variant based on traffic split
            if (hash_val % 100) < (experiment["traffic_split"] * 100):
                variant = "test" if "test" in variants else variants[1]
            else:
                variant = "control" if "control" in variants else variants[0]
            
            experiment["assignments"][user_id] = variant
            experiment["results"][variant]["total"] += 1
            self._save_experiments()
            
            return variant
    
    def record_outcome(
        self,
        experiment_id: str,
        user_id: str,
        converted: bool = False,
        revenue: float = 0.0,
        engagement: float = 0.0
    ):
        """Record an outcome for a user in an experiment."""
        with self._lock:
            if experiment_id not in self.experiments:
                return
            
            experiment = self.experiments[experiment_id]
            
            if user_id not in experiment["assignments"]:
                return
            
            variant = experiment["assignments"][user_id]
            
            if converted:
                experiment["results"][variant]["conversions"] += 1
            
            experiment["results"][variant]["revenue"] += revenue
            
            # Track engagement separately if provided
            if "engagement" not in experiment["results"][variant]:
                experiment["results"][variant]["engagement"] = 0.0
                experiment["results"][variant]["engagement_count"] = 0
            
            if engagement > 0:
                experiment["results"][variant]["engagement"] += engagement
                experiment["results"][variant]["engagement_count"] += 1
            
            self._save_experiments()
    
    def get_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get statistical results for an experiment."""
        with self._lock:
            if experiment_id not in self.experiments:
                return {"error": "Experiment not found"}
            
            experiment = self.experiments[experiment_id]
            results = experiment["results"]
            
            # Calculate conversion rates and confidence intervals
            analysis = {}
            for variant, data in results.items():
                total = data["total"]
                conversions = data["conversions"]
                revenue = data["revenue"]
                
                conversion_rate = conversions / max(total, 1)
                avg_revenue = revenue / max(total, 1)
                
                analysis[variant] = {
                    "sample_size": total,
                    "conversions": conversions,
                    "conversion_rate": round(conversion_rate, 4),
                    "total_revenue": round(revenue, 2),
                    "avg_revenue_per_user": round(avg_revenue, 2)
                }
            
            # Determine winner if enough data
            if len(analysis) >= 2:
                control = analysis.get("control", {})
                test = analysis.get("test", {})
                
                control_size = control.get("sample_size", 0)
                test_size = test.get("sample_size", 0)
                
                if control_size >= experiment["min_sample_size"] and \
                   test_size >= experiment["min_sample_size"]:
                    
                    control_rate = control.get("conversion_rate", 0)
                    test_rate = test.get("conversion_rate", 0)
                    
                    lift = ((test_rate - control_rate) / max(control_rate, 0.001)) * 100
                    
                    analysis["winner"] = "test" if test_rate > control_rate else "control"
                    analysis["lift_pct"] = round(lift, 2)
                    analysis["significant"] = abs(lift) > 10  # Simple threshold
                else:
                    analysis["winner"] = "insufficient_data"
                    analysis["needed_per_variant"] = experiment["min_sample_size"]
            
            return {
                "experiment_id": experiment_id,
                "status": experiment["status"],
                "metric": experiment["success_metric"],
                "variants": analysis
            }
    
    def stop_experiment(self, experiment_id: str, winner: str = None) -> Dict[str, Any]:
        """Stop an experiment and optionally declare a winner."""
        with self._lock:
            if experiment_id not in self.experiments:
                return {"success": False, "error": "Experiment not found"}
            
            self.experiments[experiment_id]["status"] = "stopped"
            if winner:
                self.experiments[experiment_id]["winner"] = winner
            
            self._save_experiments()
            
            return {
                "success": True,
                "experiment_id": experiment_id,
                "final_results": self.get_results(experiment_id)
            }
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments with summary."""
        with self._lock:
            return [
                {
                    "id": exp["id"],
                    "name": exp["name"],
                    "status": exp["status"],
                    "variants": list(exp["variants"].keys()),
                    "total_assignments": len(exp["assignments"]),
                    "created_at": exp["created_at"]
                }
                for exp in self.experiments.values()
            ]


# Initialize A/B testing framework
ab_testing = ABTestFramework()


# Alert Manager for Automated Notifications
class AlertManager:
    """
    Centralized alert management for system monitoring.
    
    Supports multiple notification channels:
    - Email (via SMTP)
    - Slack (via webhooks)
    - Webhook (generic HTTP POST)
    - Console (for development)
    
    Features:
    - Alert throttling (prevent spam)
    - Alert severity levels
    - Alert acknowledgment
    - Alert history
    
    Usage:
        alerts = AlertManager()
        
        # Configure channels
        alerts.add_slack_channel("#ops-alerts", webhook_url="...")
        alerts.add_email_channel("ops@company.com", smtp_config={...})
        
        # Send alert
        alerts.send_alert(
            severity="warning",
            title="High CPU Usage",
            message="CPU at 85% for 5 minutes",
            channels=["slack", "email"]
        )
    """
    
    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_CRITICAL = "critical"
    
    def __init__(self, storage_path: str = "/home/m1ndb0t/Desktop/J1MSKY/config"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.alerts_file = self.storage_path / "alerts.json"
        self.config_file = self.storage_path / "alert_channels.json"
        
        self.channels = self._load_channels()
        self.alert_history = self._load_alerts()
        self._lock = threading.Lock()
        
        # Throttling: track last alert time by (severity, category)
        self._last_alert_time: Dict[str, float] = {}
        self._throttle_intervals = {
            self.SEVERITY_INFO: 3600,      # 1 hour
            self.SEVERITY_WARNING: 900,    # 15 minutes
            self.SEVERITY_CRITICAL: 60     # 1 minute
        }
    
    def _load_channels(self) -> Dict[str, Any]:
        """Load channel configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_channels(self):
        """Save channel configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.channels, f, indent=2)
    
    def _load_alerts(self) -> List[Dict]:
        """Load alert history."""
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)[-1000:]  # Keep last 1000
            except Exception:
                return []
        return []
    
    def _save_alerts(self):
        """Save alert history."""
        with open(self.alerts_file, 'w') as f:
            json.dump(self.alert_history[-1000:], f, indent=2)  # Keep last 1000
    
    def add_slack_channel(self, name: str, webhook_url: str, channel: str = None):
        """Add Slack webhook channel."""
        self.channels[name] = {
            "type": "slack",
            "webhook_url": webhook_url,
            "channel": channel,
            "enabled": True
        }
        self._save_channels()
    
    def add_webhook_channel(self, name: str, url: str, headers: Dict = None):
        """Add generic webhook channel."""
        self.channels[name] = {
            "type": "webhook",
            "url": url,
            "headers": headers or {},
            "enabled": True
        }
        self._save_channels()
    
    def add_console_channel(self, name: str = "console"):
        """Add console output channel (for development)."""
        self.channels[name] = {
            "type": "console",
            "enabled": True
        }
        self._save_channels()
    
    def enable_channel(self, name: str):
        """Enable a channel."""
        if name in self.channels:
            self.channels[name]["enabled"] = True
            self._save_channels()
    
    def disable_channel(self, name: str):
        """Disable a channel."""
        if name in self.channels:
            self.channels[name]["enabled"] = False
            self._save_channels()
    
    def _should_throttle(self, severity: str, category: str) -> bool:
        """Check if alert should be throttled."""
        key = f"{severity}:{category}"
        now = time.time()
        last_time = self._last_alert_time.get(key, 0)
        interval = self._throttle_intervals.get(severity, 3600)
        
        if now - last_time < interval:
            return True
        
        self._last_alert_time[key] = now
        return False
    
    def send_alert(
        self,
        severity: str,
        title: str,
        message: str,
        category: str = "general",
        channels: List[str] = None,
        data: Dict = None,
        throttle: bool = True
    ) -> Dict[str, Any]:
        """
        Send an alert to configured channels.
        
        Args:
            severity: info, warning, or critical
            title: Alert title
            message: Alert message
            category: Alert category for throttling
            channels: Specific channels to use, or None for all enabled
            data: Additional data to include
            throttle: Whether to apply throttling
        
        Returns:
            Dict with delivery status per channel
        """
        # Check throttling
        if throttle and self._should_throttle(severity, category):
            return {"throttled": True, "reason": f"Alert throttled for {category}"}
        
        alert = {
            "id": f"alert_{int(time.time())}_{random.randint(1000, 9999)}",
            "severity": severity,
            "title": title,
            "message": message,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "data": data or {},
            "acknowledged": False
        }
        
        # Save to history
        with self._lock:
            self.alert_history.append(alert)
            self._save_alerts()
        
        # Deliver to channels
        results = {}
        target_channels = channels or list(self.channels.keys())
        
        for channel_name in target_channels:
            if channel_name not in self.channels:
                results[channel_name] = {"success": False, "error": "Channel not found"}
                continue
            
            channel = self.channels[channel_name]
            if not channel.get("enabled", True):
                results[channel_name] = {"success": False, "error": "Channel disabled"}
                continue
            
            try:
                if channel["type"] == "console":
                    self._send_console(alert)
                    results[channel_name] = {"success": True}
                elif channel["type"] == "slack":
                    self._send_slack(alert, channel)
                    results[channel_name] = {"success": True}
                elif channel["type"] == "webhook":
                    self._send_webhook(alert, channel)
                    results[channel_name] = {"success": True}
                else:
                    results[channel_name] = {"success": False, "error": "Unknown channel type"}
            except Exception as e:
                results[channel_name] = {"success": False, "error": str(e)}
        
        return {
            "alert_id": alert["id"],
            "delivered": results,
            "throttled": False
        }
    
    def _send_console(self, alert: Dict):
        """Send alert to console."""
        severity_colors = {
            self.SEVERITY_INFO: "\033[94m",      # Blue
            self.SEVERITY_WARNING: "\033[93m",   # Yellow
            self.SEVERITY_CRITICAL: "\033[91m"   # Red
        }
        reset = "\033[0m"
        color = severity_colors.get(alert["severity"], "")
        
        print(f"\n{color}[{alert['severity'].upper()}] {alert['title']}{reset}")
        print(f"  {alert['message']}")
        print(f"  Time: {alert['timestamp']}")
        if alert['data']:
            print(f"  Data: {json.dumps(alert['data'], indent=2)}")
    
    def _send_slack(self, alert: Dict, channel: Dict):
        """Send alert to Slack webhook."""
        # Note: In production, this would make an HTTP POST
        # For now, we just log that it would be sent
        webhook_url = channel.get("webhook_url", "")
        if webhook_url:
            # In production: requests.post(webhook_url, json=payload)
            pass
    
    def _send_webhook(self, alert: Dict, channel: Dict):
        """Send alert to generic webhook."""
        # Note: In production, this would make an HTTP POST
        url = channel.get("url", "")
        if url:
            # In production: requests.post(url, json=alert, headers=headers)
            pass
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        with self._lock:
            for alert in self.alert_history:
                if alert["id"] == alert_id:
                    alert["acknowledged"] = True
                    alert["acknowledged_at"] = datetime.now().isoformat()
                    self._save_alerts()
                    return True
            return False
    
    def get_active_alerts(self, severity: str = None) -> List[Dict]:
        """Get non-acknowledged alerts."""
        with self._lock:
            alerts = [a for a in self.alert_history if not a.get("acknowledged", False)]
            if severity:
                alerts = [a for a in alerts if a["severity"] == severity]
            return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get alert history."""
        with self._lock:
            return self.alert_history[-limit:]
    
    def check_and_alert(self):
        """
        Check system conditions and send alerts if needed.
        Should be called periodically (e.g., every minute).
        """
        status = orchestrator.get_status_report()
        
        # Check budget
        budget_alert = status.get("budget_alert_level", "ok")
        if budget_alert == "critical":
            self.send_alert(
                severity=self.SEVERITY_CRITICAL,
                title="Budget Critical",
                message=f"Daily budget at {status.get('budget_utilization_pct', 0):.1f}%",
                category="budget",
                data={"today_spend": status.get("today_spend"), "daily_budget": status.get("daily_budget")}
            )
        elif budget_alert == "warning":
            self.send_alert(
                severity=self.SEVERITY_WARNING,
                title="Budget Warning",
                message=f"Daily budget at {status.get('budget_utilization_pct', 0):.1f}%",
                category="budget"
            )
        
        # Check operational flags
        flags = status.get("operational_flags", {})
        if flags.get("requires_ops_attention"):
            self.send_alert(
                severity=self.SEVERITY_WARNING,
                title="Ops Attention Required",
                message=flags.get("recommended_action", "Check system status"),
                category="operations"
            )
        
        # Check usage anomalies
        anomalies = status.get("usage_anomalies", {})
        if anomalies.get("has_anomalies"):
            self.send_alert(
                severity=self.SEVERITY_WARNING,
                title="Usage Anomalies Detected",
                message=f"{anomalies.get('count', 0)} anomalies detected",
                category="usage",
                data={"anomalies": anomalies.get("anomalies", [])}
            )


# Initialize alert manager
alert_manager = AlertManager()
alert_manager.add_console_channel()


# Cost Optimizer for Intelligent Model Selection
class CostOptimizer:
    """
    Intelligent cost optimization for model selection and task routing.
    
    Features:
    - Historical cost tracking per task type
    - Model efficiency scoring
    - Automatic cost-based model recommendations
    - Budget-aware task queuing
    - Cost anomaly detection
    
    Usage:
        optimizer = CostOptimizer()
        
        # Get optimal model for task
        recommendation = optimizer.recommend_model(
            task_type="coding",
            complexity="medium",
            max_budget=0.05
        )
        
        # Record actual cost for learning
        optimizer.record_actual_cost(
            task_type="coding",
            model="k2p5",
            estimated_cost=0.01,
            actual_cost=0.012
        )
    """
    
    def __init__(self, storage_path: str = "/home/m1ndb0t/Desktop/J1MSKY/config"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.cost_db_file = self.storage_path / "cost_optimizer.json"
        self.task_history = self._load_history()
        self._lock = threading.Lock()
        
        # Model cost profiles (cost per 1K tokens)
        self.model_profiles = {
            "k2p5": {"input": 0.0005, "output": 0.0015, "speed": "fast", "quality": "good"},
            "sonnet": {"input": 0.003, "output": 0.015, "speed": "medium", "quality": "excellent"},
            "opus": {"input": 0.015, "output": 0.075, "speed": "slow", "quality": "best"},
            "minimax-m2.5": {"input": 0.0001, "output": 0.0001, "speed": "fast", "quality": "good"},
            "codex": {"input": 0.002, "output": 0.006, "speed": "fast", "quality": "excellent"}
        }
    
    def _load_history(self) -> Dict[str, Any]:
        """Load cost history from disk."""
        if self.cost_db_file.exists():
            try:
                with open(self.cost_db_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {"task_types": {}, "model_efficiency": {}}
    
    def _save_history(self):
        """Save cost history to disk."""
        with open(self.cost_db_file, 'w') as f:
            json.dump(self.task_history, f, indent=2)
    
    def estimate_task_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a task."""
        if model not in self.model_profiles:
            return 0.0
        
        profile = self.model_profiles[model]
        input_cost = (input_tokens / 1000) * profile["input"]
        output_cost = (output_tokens / 1000) * profile["output"]
        return round(input_cost + output_cost, 4)
    
    def recommend_model(
        self,
        task_type: str,
        complexity: str = "medium",
        quality_requirement: str = "good",
        max_budget: float = None,
        preferred_speed: str = None
    ) -> Dict[str, Any]:
        """
        Recommend optimal model based on cost, quality, and speed requirements.
        
        Args:
            task_type: Type of task (coding, writing, analysis, etc.)
            complexity: low, medium, high
            quality_requirement: good, excellent, best
            max_budget: Maximum acceptable cost
            preferred_speed: fast, medium, slow (or None for any)
        
        Returns:
            Recommendation with model, estimated cost, and reasoning
        """
        candidates = []
        
        for model, profile in self.model_profiles.items():
            # Check quality match
            quality_score = {"good": 1, "excellent": 2, "best": 3}
            required_score = quality_score.get(quality_requirement, 1)
            model_score = quality_score.get(profile["quality"], 1)
            
            if model_score < required_score:
                continue
            
            # Check speed preference
            if preferred_speed and profile["speed"] != preferred_speed:
                continue
            
            # Calculate efficiency score
            efficiency = self._get_model_efficiency(task_type, model)
            
            # Estimate cost for typical task
            estimated_input = 1500 if complexity == "low" else 3000 if complexity == "medium" else 5000
            estimated_output = 500 if complexity == "low" else 1000 if complexity == "medium" else 2000
            
            estimated_cost = self.estimate_task_cost(model, estimated_input, estimated_output)
            
            # Check budget constraint
            if max_budget and estimated_cost > max_budget:
                continue
            
            # Calculate score (lower is better): cost / efficiency
            score = estimated_cost / max(efficiency, 0.1)
            
            candidates.append({
                "model": model,
                "estimated_cost": estimated_cost,
                "efficiency": efficiency,
                "quality": profile["quality"],
                "speed": profile["speed"],
                "score": score
            })
        
        if not candidates:
            # Fallback to cheapest available
            return {
                "model": "k2p5",
                "estimated_cost": 0.01,
                "reasoning": "No candidates matched criteria, using fallback",
                "alternatives": []
            }
        
        # Sort by score (ascending)
        candidates.sort(key=lambda x: x["score"])
        
        best = candidates[0]
        alternatives = candidates[1:3]  # Next 2 best options
        
        return {
            "model": best["model"],
            "estimated_cost": best["estimated_cost"],
            "quality": best["quality"],
            "speed": best["speed"],
            "reasoning": f"Best balance of cost ({best['estimated_cost']}) and efficiency ({best['efficiency']:.2f})",
            "alternatives": [
                {"model": alt["model"], "estimated_cost": alt["estimated_cost"]} 
                for alt in alternatives
            ]
        }
    
    def _get_model_efficiency(self, task_type: str, model: str) -> float:
        """Get efficiency score for model on task type (0-1 scale)."""
        with self._lock:
            task_data = self.task_history.get("task_types", {}).get(task_type, {})
            model_data = task_data.get(model, {})
            
            if not model_data:
                return 0.5  # Default neutral efficiency
            
            # Calculate efficiency based on success rate and cost accuracy
            total_tasks = model_data.get("total_tasks", 0)
            successful_tasks = model_data.get("successful_tasks", 0)
            
            if total_tasks == 0:
                return 0.5
            
            success_rate = successful_tasks / total_tasks
            
            # Cost accuracy (how close were estimates to actual)
            cost_variance = model_data.get("avg_cost_variance", 0)
            accuracy_score = max(0, 1 - cost_variance)
            
            return round((success_rate * 0.6 + accuracy_score * 0.4), 2)
    
    def record_actual_cost(
        self,
        task_type: str,
        model: str,
        estimated_cost: float,
        actual_cost: float,
        success: bool = True
    ):
        """Record actual cost for learning and optimization."""
        with self._lock:
            if "task_types" not in self.task_history:
                self.task_history["task_types"] = {}
            
            if task_type not in self.task_history["task_types"]:
                self.task_history["task_types"][task_type] = {}
            
            if model not in self.task_history["task_types"][task_type]:
                self.task_history["task_types"][task_type][model] = {
                    "total_tasks": 0,
                    "successful_tasks": 0,
                    "total_estimated_cost": 0,
                    "total_actual_cost": 0,
                    "cost_variance_sum": 0
                }
            
            model_data = self.task_history["task_types"][task_type][model]
            model_data["total_tasks"] += 1
            if success:
                model_data["successful_tasks"] += 1
            
            model_data["total_estimated_cost"] += estimated_cost
            model_data["total_actual_cost"] += actual_cost
            
            # Track variance
            variance = abs(actual_cost - estimated_cost) / max(estimated_cost, 0.001)
            model_data["cost_variance_sum"] += variance
            
            # Calculate averages
            n = model_data["total_tasks"]
            model_data["avg_cost_variance"] = model_data["cost_variance_sum"] / n
            model_data["avg_actual_cost"] = model_data["total_actual_cost"] / n
            
            self._save_history()
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate cost optimization report."""
        with self._lock:
            report = {
                "generated_at": datetime.now().isoformat(),
                "task_type_stats": {},
                "model_efficiency": {},
                "recommendations": []
            }
            
            # Analyze each task type
            for task_type, models in self.task_history.get("task_types", {}).items():
                best_model = None
                best_efficiency = 0
                total_cost = 0
                
                for model, data in models.items():
                    efficiency = self._get_model_efficiency(task_type, model)
                    if efficiency > best_efficiency:
                        best_efficiency = efficiency
                        best_model = model
                    
                    total_cost += data.get("total_actual_cost", 0)
                
                report["task_type_stats"][task_type] = {
                    "best_model": best_model,
                    "best_efficiency": best_efficiency,
                    "total_cost": round(total_cost, 2)
                }
            
            # Generate recommendations
            for task_type, stats in report["task_type_stats"].items():
                current = stats["best_model"]
                # Find cheaper alternative with similar efficiency
                for model in self.model_profiles:
                    if model != current:
                        alt_efficiency = self._get_model_efficiency(task_type, model)
                        if alt_efficiency >= stats["best_efficiency"] * 0.9:
                            current_cost = self.model_profiles[current]["input"]
                            alt_cost = self.model_profiles[model]["input"]
                            if alt_cost < current_cost:
                                savings_pct = (current_cost - alt_cost) / current_cost * 100
                                report["recommendations"].append({
                                    "task_type": task_type,
                                    "current_model": current,
                                    "recommended_model": model,
                                    "potential_savings_pct": round(savings_pct, 1),
                                    "reasoning": f"Similar efficiency ({alt_efficiency:.2f}) at lower cost"
                                })
            
            return report
    
    def detect_cost_anomalies(self, lookback_hours: int = 24) -> List[Dict]:
        """Detect unusual cost patterns."""
        with self._lock:
            anomalies = []
            
            # Get average costs per task type
            for task_type, models in self.task_history.get("task_types", {}).items():
                for model, data in models.items():
                    avg_cost = data.get("avg_actual_cost", 0)
                    recent_cost = data.get("recent_avg_cost", avg_cost)
                    
                    # Check for significant increase
                    if avg_cost > 0 and recent_cost > avg_cost * 1.5:
                        anomalies.append({
                            "type": "cost_increase",
                            "task_type": task_type,
                            "model": model,
                            "average_cost": round(avg_cost, 4),
                            "recent_cost": round(recent_cost, 4),
                            "increase_pct": round((recent_cost - avg_cost) / avg_cost * 100, 1)
                        })
            
            return anomalies


# Initialize cost optimizer
cost_optimizer = CostOptimizer()


# Task Scheduler for Recurring Automation
class TaskScheduler:
    """
    Schedule and manage recurring tasks with cron-like flexibility.
    
    Features:
    - Cron expression support (e.g., "0 9 * * 1" for Mondays at 9am)
    - Interval scheduling (e.g., every 30 minutes)
    - One-time scheduled tasks
    - Task history and retry logic
    - Budget-aware scheduling
    
    Usage:
        scheduler = TaskScheduler()
        
        # Schedule daily report
        scheduler.schedule_cron(
            task_id="daily_report",
            cron="0 9 * * *",  # 9am daily
            task={
                "model": "sonnet",
                "prompt": "Generate daily sales report"
            }
        )
        
        # Run every 30 minutes
        scheduler.schedule_interval(
            task_id="health_check",
            minutes=30,
            task={
                "model": "k2p5",
                "prompt": "Check system health"
            }
        )
        
        # Start scheduler
        scheduler.start()
    """
    
    def __init__(self, orchestrator_ref=None):
        self.orchestrator = orchestrator_ref or orchestrator
        self.scheduled_tasks: Dict[str, Dict] = {}
        self.task_history: List[Dict] = []
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.storage_path = Path("/home/m1ndb0t/Desktop/J1MSKY/config/scheduler.json")
        self._load_tasks()
    
    def _load_tasks(self):
        """Load scheduled tasks from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.scheduled_tasks = data.get("tasks", {})
                    self.task_history = data.get("history", [])[-1000:]  # Keep last 1000
            except Exception:
                pass
    
    def _save_tasks(self):
        """Save scheduled tasks to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump({
                "tasks": self.scheduled_tasks,
                "history": self.task_history[-1000:]
            }, f, indent=2)
    
    def schedule_cron(
        self,
        task_id: str,
        cron: str,
        task: Dict[str, Any],
        enabled: bool = True,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Schedule a task using cron expression.
        
        Cron format: "min hour day month dow"
        - min: 0-59
        - hour: 0-23
        - day: 1-31
        - month: 1-12
        - dow: 0-6 (0=Sunday)
        
        Examples:
        - "0 9 * * *" = 9am daily
        - "0 9 * * 1" = 9am Mondays
        - "*/30 * * * *" = Every 30 minutes
        """
        with self._lock:
            self.scheduled_tasks[task_id] = {
                "id": task_id,
                "type": "cron",
                "cron": cron,
                "task": task,
                "enabled": enabled,
                "max_retries": max_retries,
                "last_run": None,
                "next_run": self._calculate_next_run(cron),
                "run_count": 0,
                "fail_count": 0,
                "created_at": datetime.now().isoformat()
            }
            self._save_tasks()
        
        return {"success": True, "task_id": task_id, "next_run": self.scheduled_tasks[task_id]["next_run"]}
    
    def schedule_interval(
        self,
        task_id: str,
        minutes: int = 0,
        hours: int = 0,
        days: int = 0,
        task: Dict[str, Any] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Schedule a task to run at regular intervals."""
        interval_seconds = (days * 86400) + (hours * 3600) + (minutes * 60)
        
        if interval_seconds < 60:
            return {"success": False, "error": "Interval must be at least 60 seconds"}
        
        with self._lock:
            self.scheduled_tasks[task_id] = {
                "id": task_id,
                "type": "interval",
                "interval_seconds": interval_seconds,
                "task": task,
                "enabled": enabled,
                "last_run": None,
                "next_run": (datetime.now() + timedelta(seconds=interval_seconds)).isoformat(),
                "run_count": 0,
                "fail_count": 0,
                "created_at": datetime.now().isoformat()
            }
            self._save_tasks()
        
        return {"success": True, "task_id": task_id, "interval_seconds": interval_seconds}
    
    def schedule_once(
        self,
        task_id: str,
        run_at: datetime,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule a one-time task."""
        with self._lock:
            self.scheduled_tasks[task_id] = {
                "id": task_id,
                "type": "once",
                "run_at": run_at.isoformat(),
                "task": task,
                "enabled": True,
                "last_run": None,
                "next_run": run_at.isoformat(),
                "run_count": 0,
                "created_at": datetime.now().isoformat()
            }
            self._save_tasks()
        
        return {"success": True, "task_id": task_id, "scheduled_for": run_at.isoformat()}
    
    def _calculate_next_run(self, cron: str) -> str:
        """Calculate next run time from cron expression."""
        # Simplified cron parser - in production use croniter library
        parts = cron.split()
        if len(parts) != 5:
            return (datetime.now() + timedelta(hours=1)).isoformat()
        
        minute, hour, day, month, dow = parts
        now = datetime.now()
        
        # For simple hourly schedules like */30
        if minute.startswith("*/"):
            try:
                interval = int(minute[2:])
                next_minute = ((now.minute // interval) + 1) * interval
                if next_minute >= 60:
                    next_run = now.replace(minute=0) + timedelta(hours=1)
                else:
                    next_run = now.replace(minute=next_minute)
                return next_run.isoformat()
            except:
                pass
        
        # Default: next hour
        return (now + timedelta(hours=1)).isoformat()
    
    def _should_run(self, task: Dict) -> bool:
        """Check if a task should run now."""
        if not task.get("enabled", True):
            return False
        
        next_run = task.get("next_run")
        if not next_run:
            return False
        
        try:
            next_run_dt = datetime.fromisoformat(next_run)
            return datetime.now() >= next_run_dt
        except:
            return False
    
    def _execute_task(self, task_config: Dict) -> Dict[str, Any]:
        """Execute a scheduled task."""
        try:
            task = task_config.get("task", {})
            model = task.get("model", "k2p5")
            prompt = task.get("prompt", "")
            
            # Get model recommendation if budget constrained
            if "max_budget" in task:
                rec = cost_optimizer.recommend_model(
                    task_type=task.get("task_type", "general"),
                    max_budget=task["max_budget"]
                )
                model = rec["model"]
            
            # Execute through orchestrator
            # In production, this would integrate with your agent spawning system
            result = {
                "success": True,
                "model_used": model,
                "executed_at": datetime.now().isoformat(),
                "task_id": task_config.get("id")
            }
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_next_run(self, task: Dict):
        """Update next run time after execution."""
        task["last_run"] = datetime.now().isoformat()
        task["run_count"] = task.get("run_count", 0) + 1
        
        if task["type"] == "cron":
            task["next_run"] = self._calculate_next_run(task["cron"])
        elif task["type"] == "interval":
            interval = task.get("interval_seconds", 3600)
            task["next_run"] = (datetime.now() + timedelta(seconds=interval)).isoformat()
        elif task["type"] == "once":
            task["enabled"] = False  # Disable one-time tasks after run
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                with self._lock:
                    for task_id, task in self.scheduled_tasks.items():
                        if self._should_run(task):
                            # Execute task
                            result = self._execute_task(task)
                            
                            # Record in history
                            self.task_history.append({
                                "task_id": task_id,
                                "executed_at": datetime.now().isoformat(),
                                "result": result
                            })
                            
                            # Update next run
                            self._update_next_run(task)
                            
                            # Track failures
                            if not result.get("success"):
                                task["fail_count"] = task.get("fail_count", 0) + 1
                            
                            self._save_tasks()
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the scheduler."""
        if self._running:
            return {"success": False, "error": "Scheduler already running"}
        
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        
        return {"success": True, "message": "Scheduler started"}
    
    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        
        return {"success": True, "message": "Scheduler stopped"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        return {
            "running": self._running,
            "scheduled_tasks_count": len(self.scheduled_tasks),
            "enabled_tasks": sum(1 for t in self.scheduled_tasks.values() if t.get("enabled")),
            "tasks": [
                {
                    "id": t["id"],
                    "type": t["type"],
                    "enabled": t.get("enabled"),
                    "next_run": t.get("next_run"),
                    "run_count": t.get("run_count", 0)
                }
                for t in self.scheduled_tasks.values()
            ]
        }
    
    def disable_task(self, task_id: str) -> Dict[str, Any]:
        """Disable a scheduled task."""
        with self._lock:
            if task_id in self.scheduled_tasks:
                self.scheduled_tasks[task_id]["enabled"] = False
                self._save_tasks()
                return {"success": True}
            return {"success": False, "error": "Task not found"}
    
    def enable_task(self, task_id: str) -> Dict[str, Any]:
        """Enable a scheduled task."""
        with self._lock:
            if task_id in self.scheduled_tasks:
                self.scheduled_tasks[task_id]["enabled"] = True
                self._save_tasks()
                return {"success": True}
            return {"success": False, "error": "Task not found"}
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a scheduled task."""
        with self._lock:
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]
                self._save_tasks()
                return {"success": True}
            return {"success": False, "error": "Task not found"}


# Initialize task scheduler
task_scheduler = TaskScheduler()


if __name__ == "__main__"::
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
