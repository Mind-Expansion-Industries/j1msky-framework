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
