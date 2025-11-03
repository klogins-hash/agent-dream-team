"""Neurotype Profile System - Personalized brain context for optimal human-agent interaction."""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ADHDType(Enum):
    """ADHD subtypes."""
    INATTENTIVE = "inattentive"
    HYPERACTIVE_IMPULSIVE = "hyperactive_impulsive"
    COMBINED = "combined"
    NONE = "none"


class MBTIType(Enum):
    """MBTI personality types."""
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"
    NONE = "none"


class CognitiveStyle(Enum):
    """Cognitive processing styles."""
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    CREATIVE = "creative"
    LOGICAL = "logical"
    SYSTEMATIC = "systematic"
    HOLISTIC = "holistic"
    LINEAR = "linear"
    DIVERGENT = "divergent"


@dataclass
class NeurotypeProfile:
    """Complete neurotype and cognitive profile."""
    # Core identifiers
    user_id: str
    adhd_type: ADHDType
    mbti_type: MBTIType
    cognitive_style: CognitiveStyle
    
    # Cognitive preferences
    attention_span: str = "medium"  # short, medium, long, variable
    processing_speed: str = "medium"  # slow, medium, fast, variable
    detail_preference: str = "balanced"  # high, medium, low
    pattern_recognition: str = "medium"  # low, medium, high
    
    # Interaction preferences
    feedback_frequency: str = "medium"  # minimal, medium, high
    notification_style: str = "visual"  # visual, auditory, minimal
    control_preference: str = "balanced"  # high, balanced, low
    autonomy_comfort: str = "medium"  # low, medium, high
    
    # Environmental preferences
    stimulation_level: str = "medium"  # low, medium, high
    structure_preference: str = "medium"  # low, medium, high
    complexity_tolerance: str = "medium"  # low, medium, high
    
    # Learning style
    learning_mode: str = "visual"  # visual, auditory, kinesthetic, reading
    information_density: str = "medium"  # sparse, medium, dense
    
    # Custom preferences
    custom_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_preferences is None:
            self.custom_preferences = {}


class NeurotypeProfileManager:
    """Manages neurotype profiles and environment variable configuration."""
    
    def __init__(self):
        """Initialize profile manager."""
        self.profiles: Dict[str, NeurotypeProfile] = {}
        self.default_profiles = self._create_default_profiles()
        
    def load_profile_from_env(self, user_id: str = "default") -> NeurotypeProfile:
        """Load neurotype profile from environment variables."""
        
        # Core neurotype settings
        adhd_type = ADHDType(os.getenv("NEUROTYPE_ADHD_TYPE", "none").lower())
        mbti_type = MBTIType(os.getenv("NEUROTYPE_MBTI_TYPE", "none").upper())
        cognitive_style = CognitiveStyle(os.getenv("NEUROTYPE_COGNITIVE_STYLE", "analytical").lower())
        
        # Cognitive preferences
        attention_span = os.getenv("NEUROTYPE_ATTENTION_SPAN", "medium")
        processing_speed = os.getenv("NEUROTYPE_PROCESSING_SPEED", "medium")
        detail_preference = os.getenv("NEUROTYPE_DETAIL_PREFERENCE", "balanced")
        pattern_recognition = os.getenv("NEUROTYPE_PATTERN_RECOGNITION", "medium")
        
        # Interaction preferences
        feedback_frequency = os.getenv("NEUROTYPE_FEEDBACK_FREQUENCY", "medium")
        notification_style = os.getenv("NEUROTYPE_NOTIFICATION_STYLE", "visual")
        control_preference = os.getenv("NEUROTYPE_CONTROL_PREFERENCE", "balanced")
        autonomy_comfort = os.getenv("NEUROTYPE_AUTONOMY_COMFORT", "medium")
        
        # Environmental preferences
        stimulation_level = os.getenv("NEUROTYPE_STIMULATION_LEVEL", "medium")
        structure_preference = os.getenv("NEUROTYPE_STRUCTURE_PREFERENCE", "medium")
        complexity_tolerance = os.getenv("NEUROTYPE_COMPLEXITY_TOLERANCE", "medium")
        
        # Learning style
        learning_mode = os.getenv("NEUROTYPE_LEARNING_MODE", "visual")
        information_density = os.getenv("NEUROTYPE_INFORMATION_DENSITY", "medium")
        
        profile = NeurotypeProfile(
            user_id=user_id,
            adhd_type=adhd_type,
            mbti_type=mbti_type,
            cognitive_style=cognitive_style,
            attention_span=attention_span,
            processing_speed=processing_speed,
            detail_preference=detail_preference,
            pattern_recognition=pattern_recognition,
            feedback_frequency=feedback_frequency,
            notification_style=notification_style,
            control_preference=control_preference,
            autonomy_comfort=autonomy_comfort,
            stimulation_level=stimulation_level,
            structure_preference=structure_preference,
            complexity_tolerance=complexity_tolerance,
            learning_mode=learning_mode,
            information_density=information_density
        )
        
        # Apply type-specific optimizations
        profile = self._apply_type_optimizations(profile)
        
        return profile
    
    def _apply_type_optimizations(self, profile: NeurotypeProfile) -> NeurotypeProfile:
        """Apply optimizations based on specific neurotype combinations."""
        
        # ADHD-specific optimizations
        if profile.adhd_type == ADHDType.COMBINED:
            profile.feedback_frequency = "high"
            profile.notification_style = "visual"
            profile.attention_span = "variable"
            profile.custom_preferences.update({
                "dopamine_loops": True,
                "hyperfocus_support": True,
                "task_switching_support": True,
                "immediate_feedback": True
            })
            
        elif profile.adhd_type == ADHDType.INATTENTIVE:
            profile.structure_preference = "high"
            profile.notification_style = "minimal"
            profile.detail_preference = "medium"
            profile.custom_preferences.update({
                "focus_assistance": True,
                "distraction_minimization": True,
                "clear_structure": True
            })
            
        elif profile.adhd_type == ADHDType.HYPERACTIVE_IMPULSIVE:
            profile.stimulation_level = "medium"
            profile.feedback_frequency = "high"
            profile.custom_preferences.update({
                "movement_breaks": True,
                "quick_feedback": True,
                "engagement_variety": True
            })
        
        # MBTI-specific optimizations
        if profile.mbti_type in [MBTI.INTJ, MBTI.INTP]:
            profile.autonomy_comfort = "high"
            profile.control_preference = "low"
            profile.complexity_tolerance = "high"
            profile.custom_preferences.update({
                "independent_work": True,
                "complex_problem_solving": True,
                "minimal_supervision": True
            })
            
        elif profile.mbti_type in [MBTI.INFJ, MBTI.INFP]:
            profile.pattern_recognition = "high"
            profile.learning_mode = "intuitive"
            profile.custom_preferences.update({
                "meaningful_connections": True,
                "value_alignment": True,
                "deep_processing": True,
                "pattern_visibility": "high"
            })
            
        elif profile.mbti_type in [MBTI.ENTJ, MBTI.ENTP]:
            profile.processing_speed = "fast"
            profile.control_preference = "high"
            profile.custom_preferences.update({
                "quick_decisions": True,
                "leadership_role": True,
                "strategic_thinking": True
            })
            
        elif profile.mbti_type in [MBTI.ENFJ, MBTI.ENFP]:
            profile.feedback_frequency = "high"
            profile.custom_preferences.update({
                "collaborative_work": True,
                "social_feedback": True,
                "harmonious_interaction": True
            })
        
        # Cognitive style optimizations
        if profile.cognitive_style == CognitiveStyle.ANALYTICAL:
            profile.detail_preference = "high"
            profile.information_density = "dense"
            profile.custom_preferences.update({
                "detailed_analysis": True,
                "data_driven": True,
                "logical_structure": True
            })
            
        elif profile.cognitive_style == CognitiveStyle.INTUITIVE:
            profile.pattern_recognition = "high"
            profile.custom_preferences.update({
                "pattern_recognition": True,
                "big_picture_thinking": True,
                "insight_generation": True
            })
            
        elif profile.cognitive_style == CognitiveStyle.CREATIVE:
            profile.complexity_tolerance = "high"
            profile.custom_preferences.update({
                "creative_exploration": True,
                "novel_connections": True,
                "divergent_thinking": True
            })
        
        return profile
    
    def _create_default_profiles(self) -> Dict[str, NeurotypeProfile]:
        """Create default profiles for common neurotype combinations."""
        profiles = {}
        
        # ADHD Combined + INFJ (Your profile)
        profiles["adhd_infj"] = NeurotypeProfile(
            user_id="adhd_infj_template",
            adhd_type=ADHDType.COMBINED,
            mbti_type=MBTI.INFJ,
            cognitive_style=CognitiveStyle.INTUITIVE,
            attention_span="variable",
            processing_speed="medium",
            detail_preference="balanced",
            pattern_recognition="high",
            feedback_frequency="high",
            notification_style="visual",
            control_preference="balanced",
            autonomy_comfort="high",
            stimulation_level="medium",
            structure_preference="medium",
            complexity_tolerance="high",
            learning_mode="visual",
            custom_preferences={
                "dopamine_loops": True,
                "hyperfocus_support": True,
                "meaningful_connections": True,
                "pattern_visibility": "high",
                "deep_processing": True,
                "value_alignment": True
            }
        )
        
        # ADHD Combined + INTJ
        profiles["adhd_intj"] = NeurotypeProfile(
            user_id="adhd_intj_template",
            adhd_type=ADHDType.COMBINED,
            mbti_type=MBTI.INTJ,
            cognitive_style=CognitiveStyle.ANALYTICAL,
            attention_span="variable",
            processing_speed="fast",
            detail_preference="high",
            pattern_recognition="medium",
            feedback_frequency="medium",
            notification_style="visual",
            control_preference="low",
            autonomy_comfort="high",
            stimulation_level="low",
            structure_preference="medium",
            complexity_tolerance="high",
            learning_mode="reading",
            custom_preferences={
                "strategic_thinking": True,
                "independent_work": True,
                "complex_problem_solving": True,
                "dopamine_loops": True,
                "hyperfocus_support": True
            }
        )
        
        # Neurotypical + ENTP
        profiles["neurotypical_entp"] = NeurotypeProfile(
            user_id="neurotypical_entp_template",
            adhd_type=ADHDType.NONE,
            mbti_type=MBTI.ENTP,
            cognitive_style=CognitiveStyle.DIVERGENT,
            attention_span="medium",
            processing_speed="fast",
            detail_preference="low",
            pattern_recognition="medium",
            feedback_frequency="medium",
            notification_style="visual",
            control_preference="high",
            autonomy_comfort="medium",
            stimulation_level="high",
            structure_preference="low",
            complexity_tolerance="high",
            learning_mode="kinesthetic",
            custom_preferences={
                "quick_decisions": True,
                "creative_exploration": True,
                "novel_connections": True,
                "strategic_thinking": True
            }
        )
        
        # ADHD Inattentive + ISFJ
        profiles["adhd_inattentive_isfj"] = NeurotypeProfile(
            user_id="adhd_inattentive_isfj_template",
            adhd_type=ADHDType.INATTENTIVE,
            mbti_type=MBTI.ISFJ,
            cognitive_style=CognitiveStyle.SYSTEMATIC,
            attention_span="short",
            processing_speed="medium",
            detail_preference="medium",
            pattern_recognition="low",
            feedback_frequency="medium",
            notification_style="minimal",
            control_preference="balanced",
            autonomy_comfort="low",
            stimulation_level="low",
            structure_preference="high",
            complexity_tolerance="low",
            learning_mode="visual",
            custom_preferences={
                "focus_assistance": True,
                "clear_structure": True,
                "distraction_minimization": True,
                "supportive_environment": True
            }
        )
        
        return profiles
    
    def get_profile_template(self, template_name: str) -> Optional[NeurotypeProfile]:
        """Get a predefined profile template."""
        return self.default_profiles.get(template_name)
    
    def list_available_templates(self) -> List[str]:
        """List all available profile templates."""
        return list(self.default_profiles.keys())
    
    def create_env_file_template(self, profile: NeurotypeProfile) -> str:
        """Create .env file template for a profile."""
        env_template = f"""# Neurotype Profile Configuration
# Generated for: {profile.user_id}

# Core Neurotype Settings
NEUROTYPE_ADHD_TYPE={profile.adhd_type.value}
NEUROTYPE_MBTI_TYPE={profile.mbti_type.value}
NEUROTYPE_COGNITIVE_STYLE={profile.cognitive_style.value}

# Cognitive Preferences
NEUROTYPE_ATTENTION_SPAN={profile.attention_span}
NEUROTYPE_PROCESSING_SPEED={profile.processing_speed}
NEUROTYPE_DETAIL_PREFERENCE={profile.detail_preference}
NEUROTYPE_PATTERN_RECOGNITION={profile.pattern_recognition}

# Interaction Preferences
NEUROTYPE_FEEDBACK_FREQUENCY={profile.feedback_frequency}
NEUROTYPE_NOTIFICATION_STYLE={profile.notification_style}
NEUROTYPE_CONTROL_PREFERENCE={profile.control_preference}
NEUROTYPE_AUTONOMY_COMFORT={profile.autonomy_comfort}

# Environmental Preferences
NEUROTYPE_STIMULATION_LEVEL={profile.stimulation_level}
NEUROTYPE_STRUCTURE_PREFERENCE={profile.structure_preference}
NEUROTYPE_COMPLEXITY_TOLERANCE={profile.complexity_tolerance}

# Learning Style
NEUROTYPE_LEARNING_MODE={profile.learning_mode}
NEUROTYPE_INFORMATION_DENSITY={profile.information_density}

# Custom Preferences (JSON format)
NEUROTYPE_CUSTOM_PREFS='{json.dumps(profile.custom_preferences)}'
"""
        return env_template


# Singleton instance
_profile_manager = None

def get_neurotype_manager() -> NeurotypeProfileManager:
    """Get neurotype profile manager instance."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = NeurotypeProfileManager()
    return _profile_manager
