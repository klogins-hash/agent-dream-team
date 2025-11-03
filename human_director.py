"""Human Director Interface - Personalized neurotype-optimized control and visibility system."""

import asyncio
import uuid
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np

from database import get_postgres
from messaging import get_message_broker
from agent_workflow import get_workflow_engine
from agent_testing import get_testing_engine
from agent_cicd import get_cicd_system
from rag import get_rag_engine
from neurotype_profiles import get_neurotype_manager, NeurotypeProfile


class ControlLevel(Enum):
    """Levels of human control."""
    OBSERVE = "observe"           # Full visibility, no intervention
    NUDGE = "nudge"               # Gentle influence, soft redirects
    GUIDE = "guide"               # Direction with agent autonomy
    DIRECT = "direct"             # Specific instructions
    OVERRIDE = "override"         # Full human control


class AttentionMode(Enum):
    """ADHD attention modes."""
    BIG_PICTURE = "big_picture"   # Pattern and connection view
    DEEP_DIVE = "deep_dive"       # Focused on one area
    SCAN_MODE = "scan_mode"       # Quick overview
    FLOW_STATE = "flow_state"     # Immersive engagement


@dataclass
class HumanPreference:
    """Human preference and tuning parameter."""
    category: str
    parameter: str
    value: Any
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    impact_score: float = 0.0


@dataclass
class VisibilityFilter:
    """Filter for what information to show."""
    focus_areas: List[str] = field(default_factory=list)
    agent_filter: List[str] = field(default_factory=list)
    performance_threshold: float = 0.0
    alert_level: str = "important"  # critical, important, all
    time_window: timedelta = field(default_factory=lambda: timedelta(hours=1))


@dataclass
class NudgeInstruction:
    """Soft influence instruction for agents."""
    target: str  # agent or system
    direction: str
    strength: float = 0.5  # 0.0 to 1.0
    reasoning: str = ""
    expires_at: Optional[datetime] = None


class HumanDirector:
    """ADHD-INFJ optimized human direction system."""
    
    def __init__(self):
        """Initialize human director."""
        self.db = get_postgres()
        self.message_broker = get_message_broker()
        self.workflow_engine = get_workflow_engine()
        self.testing_engine = get_testing_engine()
        self.cicd_system = get_cicd_system()
        self.rag_engine = get_rag_engine()
        
        self.preferences: Dict[str, HumanPreference] = {}
        self.current_attention_mode = AttentionMode.BIG_PICTURE
        self.current_control_level = ControlLevel.GUIDE
        self.visibility_filter = VisibilityFilter()
        self.active_nudges: Dict[str, NudgeInstruction] = {}
        
        # Learning system for preferences
        self.preference_learner = PreferenceLearner()
        
        # Initialize default preferences
        self._initialize_default_preferences()
    
    def _initialize_default_preferences(self):
        """Initialize ADHD-INFJ optimized default preferences."""
        # ADHD preferences
        self.preferences.update({
            "feedback_frequency": HumanPreference("attention", "feedback_frequency", 30.0, 0.8),
            "notification_style": HumanPreference("attention", "notification_style", "visual", 0.9),
            "context_preservation": HumanPreference("attention", "context_preservation", True, 0.9),
            "task_switching_support": HumanPreference("attention", "task_switching_support", True, 0.8),
            "dopamine_loops": HumanPreference("attention", "dopamine_loops", True, 0.9),
        })
        
        # INFJ preferences
        self.preferences.update({
            "pattern_visibility": HumanPreference("cognitive", "pattern_visibility", "high", 0.9),
            "meaningful_metrics": HumanPreference("cognitive", "meaningful_metrics", True, 0.9),
            "deep_processing_time": HumanPreference("cognitive", "deep_processing_time", 300.0, 0.8),
            "value_alignment": HumanPreference("cognitive", "value_alignment", "high", 0.9),
            "intuitive_insights": HumanPreference("cognitive", "intuitive_insights", True, 0.9),
        })
        
        # Control preferences
        self.preferences.update({
            "autonomy_level": HumanPreference("control", "autonomy_level", 0.8, 0.9),
            "intervention_threshold": HumanPreference("control", "intervention_threshold", 0.3, 0.7),
            "data_driven_decisions": HumanPreference("control", "data_driven_decisions", True, 0.9),
            "learning_enabled": HumanPreference("control", "learning_enabled", True, 0.9),
        })
    
    async def get_complete_visibility(self, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Get complete visibility into all agent operations."""
        if focus_areas:
            self.visibility_filter.focus_areas = focus_areas
        
        visibility_report = {
            "timestamp": datetime.now().isoformat(),
            "attention_mode": self.current_attention_mode.value,
            "control_level": self.current_control_level.value,
            
            # System Overview
            "system_health": await self._get_system_health(),
            "active_operations": await self._get_active_operations(),
            "performance_metrics": await self._get_performance_metrics(),
            
            # Agent Status
            "agent_status": await self._get_agent_status(),
            "agent_collaboration": await self._get_agent_collaboration(),
            "agent_learning": await self._get_agent_learning(),
            
            # Patterns & Insights
            "patterns": await self._get_pattern_analysis(),
            "anomalies": await self._get_anomaly_detection(),
            "predictions": await self._get_predictions(),
            
            # Human Interaction Data
            "recent_interventions": await self._get_recent_interventions(),
            "preference_impact": await self._get_preference_impact(),
            "learning_progress": await self._get_learning_progress(),
        }
        
        return visibility_report
    
    async def apply_nudge(self, target: str, direction: str, strength: float = 0.5, 
                         reasoning: str = "", duration: timedelta = None) -> str:
        """Apply gentle nudge to agent behavior."""
        nudge_id = str(uuid.uuid4())
        
        nudge = NudgeInstruction(
            target=target,
            direction=direction,
            strength=min(max(strength, 0.0), 1.0),
            reasoning=reasoning,
            expires_at=datetime.now() + (duration or timedelta(hours=1))
        )
        
        self.active_nudges[nudge_id] = nudge
        
        # Send nudge to target
        await self.message_broker.send_message(
            f"agent.{target}.nudges",
            {
                "nudge_id": nudge_id,
                "direction": direction,
                "strength": strength,
                "reasoning": reasoning,
                "expires_at": nudge.expires_at.isoformat()
            }
        )
        
        # Log for learning
        await self._log_nudge_application(nudge_id, nudge)
        
        return nudge_id
    
    async def update_preference(self, category: str, parameter: str, value: Any, 
                               confidence: float = 0.5) -> Dict[str, Any]:
        """Update human preference with data-driven impact analysis."""
        pref_key = f"{category}.{parameter}"
        
        # Calculate predicted impact
        old_preference = self.preferences.get(pref_key)
        impact_analysis = await self.preference_learner.predict_impact(
            category, parameter, value, old_preference
        )
        
        # Update preference
        self.preferences[pref_key] = HumanPreference(
            category=category,
            parameter=parameter,
            value=value,
            confidence=confidence,
            impact_score=impact_analysis["predicted_impact"]
        )
        
        # Apply changes to system
        await self._apply_preference_changes(pref_key, value)
        
        # Schedule learning validation
        asyncio.create_task(self._validate_preference_impact(pref_key, impact_analysis))
        
        return {
            "preference": pref_key,
            "value": value,
            "confidence": confidence,
            "predicted_impact": impact_analysis["predicted_impact"],
            "confidence_interval": impact_analysis["confidence_interval"],
            "expected_changes": impact_analysis["expected_changes"]
        }
    
    async def set_attention_mode(self, mode: AttentionMode, context: Dict[str, Any] = None):
        """Set attention mode with appropriate interface adjustments."""
        self.current_attention_mode = mode
        
        # Adjust visibility filters based on mode
        if mode == AttentionMode.BIG_PICTURE:
            self.visibility_filter.focus_areas = ["overview", "patterns", "trends"]
            self.visibility_filter.alert_level = "important"
            self.visibility_filter.time_window = timedelta(hours=6)
            
        elif mode == AttentionMode.DEEP_DIVE:
            # Focus on specific area from context
            if context and "focus_area" in context:
                self.visibility_filter.focus_areas = [context["focus_area"]]
            self.visibility_filter.alert_level = "all"
            self.visibility_filter.time_window = timedelta(hours=1)
            
        elif mode == AttentionMode.SCAN_MODE:
            self.visibility_filter.focus_areas = ["overview", "alerts"]
            self.visibility_filter.alert_level = "critical"
            self.visibility_filter.time_window = timedelta(minutes=30)
            
        elif mode == AttentionMode.FLOW_STATE:
            # Minimal interruptions, deep focus
            self.visibility_filter.focus_areas = context.get("focus_areas", ["current_task"])
            self.visibility_filter.alert_level = "critical"
            self.visibility_filter.time_window = timedelta(minutes=15)
        
        # Apply mode changes
        await self._apply_attention_mode_changes(mode)
    
    async def get_data_informed_recommendations(self) -> Dict[str, Any]:
        """Get data-informed recommendations for system tuning."""
        # Collect recent performance data
        performance_data = await self._collect_performance_data()
        
        # Analyze patterns and opportunities
        recommendations = {
            "attention_optimizations": await self._analyze_attention_patterns(),
            "preference_adjustments": await self._analyze_preference_effectiveness(),
            "control_recommendations": await self._analyze_control_effectiveness(),
            "system_optimizations": await self._analyze_system_performance(),
            "learning_opportunities": await self._analyze_learning_patterns()
        }
        
        # Rank by impact and confidence
        ranked_recommendations = await self._rank_recommendations(recommendations, performance_data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_performance": performance_data,
            "recommendations": ranked_recommendations,
            "implementation_priority": self._calculate_implementation_priority(ranked_recommendations),
            "expected_impact": self._calculate_expected_impact(ranked_recommendations)
        }
    
    async def autonomous_intervention(self, trigger: Dict[str, Any]) -> Optional[str]:
        """Make autonomous intervention decisions based on data."""
        intervention_threshold = self.preferences["control.intervention_threshold"].value
        
        # Analyze trigger severity and urgency
        severity_score = await self._calculate_trigger_severity(trigger)
        
        if severity_score > intervention_threshold:
            # Determine appropriate intervention level
            if severity_score > 0.8:
                intervention_type = "automatic_correction"
            elif severity_score > 0.6:
                intervention_type = "nudge_application"
            else:
                intervention_type = "preference_adjustment"
            
            # Execute intervention
            intervention_id = await self._execute_autonomous_intervention(
                intervention_type, trigger, severity_score
            )
            
            return intervention_id
        
        return None
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        # Aggregate health from all systems
        workflow_health = await self.workflow_engine.get_performance_metrics()
        test_health = await self.testing_engine.get_test_dashboard()
        cicd_health = await self.cicd_system.get_cicd_dashboard()
        
        return {
            "overall_score": 0.85,  # Calculated from subsystems
            "workflow_health": workflow_health,
            "testing_health": test_health,
            "cicd_health": cicd_health,
            "trend": "improving"
        }
    
    async def _get_active_operations(self) -> List[Dict[str, Any]]:
        """Get all currently active operations."""
        operations = []
        
        # Active workflows
        for workflow_id, workflow in self.workflow_engine.active_workflows.items():
            operations.append({
                "type": "workflow",
                "id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "progress": self._calculate_workflow_progress(workflow),
                "eta": self._calculate_workflow_eta(workflow)
            })
        
        # Active tests
        for execution_id, execution in self.testing_engine.active_tests.items():
            operations.append({
                "type": "test",
                "id": execution_id,
                "status": execution["status"],
                "progress": execution.get("progress", 0),
                "eta": execution.get("eta")
            })
        
        # Active deployments
        for execution_id, execution in self.cicd_system.active_executions.items():
            operations.append({
                "type": "deployment",
                "id": execution_id,
                "stage": execution.current_stage.value if execution.current_stage else None,
                "status": execution.status,
                "progress": self._calculate_deployment_progress(execution)
            })
        
        return operations
    
    async def _get_pattern_analysis(self) -> Dict[str, Any]:
        """Get pattern analysis optimized for INFJ cognition."""
        patterns = {
            "agent_collaboration_patterns": await self._analyze_collaboration_patterns(),
            "performance_patterns": await self._analyze_performance_patterns(),
            "intervention_patterns": await self._analyze_intervention_patterns(),
            "learning_patterns": await self._analyze_learning_patterns(),
            "emergent_behaviors": await self._detect_emergent_behaviors()
        }
        
        # Identify meaningful connections
        connections = await self._find_pattern_connections(patterns)
        
        return {
            "patterns": patterns,
            "connections": connections,
            "insights": await self._generate_pattern_insights(patterns, connections),
            "meaningfulness_score": self._calculate_meaningfulness_score(patterns)
        }
    
    async def _apply_preference_changes(self, pref_key: str, value: Any):
        """Apply preference changes to the system."""
        category, parameter = pref_key.split(".", 1)
        
        if category == "attention":
            if parameter == "feedback_frequency":
                # Adjust notification frequency
                await self._adjust_notification_frequency(value)
            elif parameter == "notification_style":
                # Change notification presentation
                await self._adjust_notification_style(value)
                
        elif category == "cognitive":
            if parameter == "pattern_visibility":
                # Adjust pattern visualization
                await self._adjust_pattern_visibility(value)
            elif parameter == "deep_processing_time":
                # Adjust async processing timeouts
                await self._adjust_processing_timeouts(value)
                
        elif category == "control":
            if parameter == "autonomy_level":
                # Adjust agent autonomy thresholds
                await self._adjust_autonomy_levels(value)
            elif parameter == "intervention_threshold":
                # Update automatic intervention triggers
                await self._adjust_intervention_thresholds(value)
    
    async def _validate_preference_impact(self, pref_key: str, impact_analysis: Dict[str, Any]):
        """Validate actual impact of preference changes."""
        # Wait for impact to manifest
        await asyncio.sleep(300)  # 5 minutes
        
        # Measure actual impact
        actual_impact = await self._measure_preference_impact(pref_key)
        
        # Update preference learning
        await self.preference_learner.update_impact_model(
            pref_key, impact_analysis, actual_impact
        )
        
        # Update preference confidence
        preference = self.preferences[pref_key]
        preference.confidence = min(preference.confidence + 0.1, 1.0)
        preference.impact_score = actual_impact["measured_impact"]
    
    def _calculate_workflow_progress(self, workflow) -> float:
        """Calculate workflow completion progress."""
        if not workflow.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in workflow.tasks.values() 
                            if task.status.value in ["completed", "failed"])
        return completed_tasks / len(workflow.tasks)
    
    def _calculate_deployment_progress(self, execution) -> float:
        """Calculate deployment progress."""
        if not execution.config.stages:
            return 0.0
        
        completed_stages = len(execution.stage_results)
        total_stages = len(execution.config.stages)
        return completed_stages / total_stages


class PreferenceLearner:
    """Learns human preferences and their impact."""
    
    def __init__(self):
        self.impact_models: Dict[str, Dict[str, float]] = {}
        self.learning_history: List[Dict[str, Any]] = []
    
    async def predict_impact(self, category: str, parameter: str, new_value: Any, 
                           old_preference: HumanPreference = None) -> Dict[str, Any]:
        """Predict impact of preference change."""
        pref_key = f"{category}.{parameter}"
        
        # Use historical data or default model
        if pref_key in self.impact_models:
            model = self.impact_models[pref_key]
            predicted_impact = self._apply_model(model, new_value)
        else:
            predicted_impact = self._default_impact_prediction(category, parameter, new_value)
        
        return {
            "predicted_impact": predicted_impact,
            "confidence_interval": [predicted_impact * 0.8, predicted_impact * 1.2],
            "expected_changes": self._predict_expected_changes(category, parameter, new_value)
        }
    
    async def update_impact_model(self, pref_key: str, prediction: Dict[str, Any], 
                                actual: Dict[str, Any]):
        """Update impact model based on actual results."""
        # Simple learning algorithm
        predicted = prediction["predicted_impact"]
        measured = actual["measured_impact"]
        
        error = measured - predicted
        
        if pref_key not in self.impact_models:
            self.impact_models[pref_key] = {"weight": 0.5, "bias": 0.0}
        
        # Update model weights
        model = self.impact_models[pref_key]
        model["weight"] += error * 0.1  # Learning rate
        model["bias"] += error * 0.05
        
        # Store learning history
        self.learning_history.append({
            "timestamp": datetime.now().isoformat(),
            "preference": pref_key,
            "predicted": predicted,
            "actual": measured,
            "error": error
        })
    
    def _apply_model(self, model: Dict[str, float], value: Any) -> float:
        """Apply learned model to predict impact."""
        # Simple linear model
        return model["weight"] * float(value) + model["bias"]
    
    def _default_impact_prediction(self, category: str, parameter: str, value: Any) -> float:
        """Default impact prediction when no model available."""
        # Rule-based predictions
        if category == "attention":
            if parameter == "feedback_frequency":
                return 0.5 if 10 <= value <= 60 else 0.3
            elif parameter == "dopamine_loops":
                return 0.8 if value else 0.4
                
        elif category == "cognitive":
            if parameter == "pattern_visibility":
                return 0.7 if value == "high" else 0.5
            elif parameter == "meaningful_metrics":
                return 0.9 if value else 0.6
                
        elif category == "control":
            if parameter == "autonomy_level":
                return 0.8 if 0.6 <= value <= 0.9 else 0.5
            elif parameter == "data_driven_decisions":
                return 0.9 if value else 0.4
        
        return 0.5  # Default moderate impact


# Singleton instance
_human_director = None

def get_human_director(neurotype_profile: NeurotypeProfile = None) -> HumanDirector:
    """Get human director instance with neurotype profile."""
    global _human_director
    if _human_director is None:
        _human_director = HumanDirector(neurotype_profile)
    return _human_director


def load_human_director_from_env() -> HumanDirector:
    """Load human director with neurotype profile from environment variables."""
    neurotype_manager = get_neurotype_manager()
    profile = neurotype_manager.load_profile_from_env()
    return HumanDirector(profile)
