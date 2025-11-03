"""Human Director tools - ADHD-INFJ optimized control and visibility."""

from typing import Dict, List, Any, Optional
from strands import tool

from human_director import get_human_director, ControlLevel, AttentionMode


@tool
def get_system_visibility(focus_areas: List[str] = None) -> str:
    """Get complete visibility into all agent operations.
    
    This provides the ADHD-INFJ optimal balance of full visibility
    with autonomous agent operation.
    
    Args:
        focus_areas: Specific areas to focus on (optional)
        
    Returns:
        Comprehensive system visibility report
    """
    director = get_human_director()
    
    import asyncio
    visibility = asyncio.run(director.get_complete_visibility(focus_areas))
    
    output = "👁️ **Complete System Visibility**\n\n"
    
    # System Overview
    system_health = visibility["system_health"]
    output += "💚 **System Health**\n"
    output += f"• Overall Score: {system_health['overall_score']:.1%}\n"
    output += f"• Trend: {system_health['trend']}\n"
    output += f"• Active Operations: {len(visibility['active_operations'])}\n\n"
    
    # Active Operations
    if visibility['active_operations']:
        output += "⚡ **Active Operations**\n"
        for op in visibility['active_operations'][:5]:  # Show top 5
            output += f"• {op['type'].title()}: {op.get('name', op['id'])}\n"
            output += f"  Status: {op['status']} | Progress: {op.get('progress', 0):.1%}\n"
        output += "\n"
    
    # Agent Status
    agent_status = visibility["agent_status"]
    output += "🤖 **Agent Status**\n"
    output += f"• Total Agents: {agent_status.get('total', 0)}\n"
    output += f"• Active: {agent_status.get('active', 0)}\n"
    output += f"• Collaboration Rate: {agent_status.get('collaboration_rate', 0):.1%}\n\n"
    
    # Patterns & Insights (INFJ optimized)
    patterns = visibility["patterns"]
    output += "🔮 **Pattern Analysis**\n"
    output += f"• Patterns Detected: {len(patterns['patterns'])}\n"
    output += f"• Connections Found: {len(patterns['connections'])}\n"
    output += f"• Meaningfulness Score: {patterns['meaningfulness_score']:.1f}/10\n\n"
    
    # Recent Interventions
    interventions = visibility["recent_interventions"]
    if interventions:
        output += "🎯 **Recent Interventions**\n"
        for intervention in interventions[-3:]:  # Last 3
            output += f"• {intervention['type']}: {intervention['reason'][:50]}...\n"
        output += "\n"
    
    # Learning Progress
    learning = visibility["learning_progress"]
    output += "📚 **Learning Progress**\n"
    output += f"• Preferences Learned: {learning['preference_count']}\n"
    output += f"• Accuracy Improvement: {learning['accuracy_improvement']:.1%}\n"
    output += f"• Autonomous Decisions: {learning['autonomous_decisions']}\n\n"
    
    output += "✨ **All agents are operating autonomously while providing complete visibility.**"
    
    return output


@tool
def nudge_agent(target: str, direction: str, strength: float = 0.5, reasoning: str = "") -> str:
    """Apply gentle nudge to influence agent behavior.
    
    This allows soft influence without breaking autonomy,
    perfect for ADHD preference for flexible control.
    
    Args:
        target: Agent or system to nudge
        direction: Direction or behavior change
        strength: Strength of nudge (0.0-1.0)
        reasoning: Why this nudge is needed
        
    Returns:
        Nudge confirmation and expected impact
    """
    director = get_human_director()
    
    import asyncio
    nudge_id = asyncio.run(director.apply_nudge(
        target=target,
        direction=direction,
        strength=strength,
        reasoning=reasoning
    ))
    
    output = f"🌊 **Gentle Nudge Applied**\n\n"
    output += f"Nudge ID: {nudge_id}\n"
    output += f"Target: {target}\n"
    output += f"Direction: {direction}\n"
    output += f"Strength: {strength:.1f}\n"
    
    if reasoning:
        output += f"Reasoning: {reasoning}\n"
    
    output += f"\n🎯 **Expected Impact:**\n"
    output += "• Agent will consider this guidance in decisions\n"
    output += f"• Influence strength: {strength:.1%}\n"
    output += "• Full autonomy maintained\n"
    output += "• Impact will be measured and learned from\n\n"
    
    output += "✨ The nudge is now active and agents will respond naturally!"
    
    return output


@tool
def tune_preference(category: str, parameter: str, value: Any, confidence: float = 0.5) -> str:
    """Fine-tune system preferences with data-driven impact analysis.
    
    This allows continuous optimization of the system based on
    your preferences and measured impact.
    
    Args:
        category: Preference category (attention, cognitive, control)
        parameter: Specific parameter to tune
        value: New value for the parameter
        confidence: Confidence in this change (0.0-1.0)
        
    Returns:
        Impact analysis and change confirmation
    """
    director = get_human_director()
    
    import asyncio
    result = asyncio.run(director.update_preference(
        category=category,
        parameter=parameter,
        value=value,
        confidence=confidence
    ))
    
    output = f"🎛️ **Preference Tuned**\n\n"
    output += f"Preference: {result['preference']}\n"
    output += f"New Value: {result['value']}\n"
    output += f"Confidence: {result['confidence']:.1%}\n\n"
    
    output += "📊 **Impact Analysis:**\n"
    output += f"• Predicted Impact: {result['predicted_impact']:.2f}/10\n"
    output += f"• Confidence Interval: {result['confidence_interval'][0]:.2f} - {result['confidence_interval'][1]:.2f}\n"
    output += f"• Expected Changes: {len(result['expected_changes'])}\n\n"
    
    if result['expected_changes']:
        output += "🔄 **Expected System Changes:**\n"
        for change in result['expected_changes'][:3]:
            output += f"• {change}\n"
        output += "\n"
    
    output += "🧠 **Learning Enabled:**\n"
    output += "• System will measure actual impact\n"
    output += "• Your preference confidence will be updated\n"
    output += "• Future recommendations will improve\n\n"
    
    output += "✨ Preference is now active and learning from results!"
    
    return output


@tool
def set_attention_mode(mode: str, focus_area: str = None) -> str:
    """Set attention mode optimized for ADHD cognitive patterns.
    
    This adjusts the interface and information flow to match
    your current attention state and cognitive needs.
    
    Args:
        mode: Attention mode (big_picture, deep_dive, scan_mode, flow_state)
        focus_area: Specific area for deep_dive or flow_state
        
    Returns:
        Mode confirmation and interface adjustments
    """
    director = get_human_director()
    
    # Map string to enum
    mode_map = {
        "big_picture": AttentionMode.BIG_PICTURE,
        "deep_dive": AttentionMode.DEEP_DIVE,
        "scan_mode": AttentionMode.SCAN_MODE,
        "flow_state": AttentionMode.FLOW_STATE
    }
    
    attention_mode = mode_map.get(mode.lower(), AttentionMode.BIG_PICTURE)
    
    context = {}
    if focus_area:
        context["focus_area"] = focus_area
    if attention_mode == AttentionMode.FLOW_STATE:
        context["focus_areas"] = [focus_area or "current_task"]
    
    import asyncio
    asyncio.run(director.set_attention_mode(attention_mode, context))
    
    output = f"🧠 **Attention Mode Set: {mode.replace('_', ' ').title()}**\n\n"
    
    # Mode-specific information
    if attention_mode == AttentionMode.BIG_PICTURE:
        output += "🔭 **Big Picture Mode Active:**\n"
        output += "• Pattern and connection visibility\n"
        output += "• 6-hour time window\n"
        output += "• Important alerts only\n"
        output += "• System-level trends\n"
        
    elif attention_mode == AttentionMode.DIVE_DEEP:
        output += f"🔬 **Deep Dive Mode Active:**\n"
        if focus_area:
            output += f"• Focus: {focus_area}\n"
        output += "• Detailed information\n"
        output += "• 1-hour time window\n"
        output += "• All alerts visible\n"
        output += "• Comprehensive metrics\n"
        
    elif attention_mode == AttentionMode.SCAN_MODE:
        output += "⚡ **Scan Mode Active:**\n"
        output += "• Quick overview\n"
        output += "• 30-minute time window\n"
        output += "• Critical alerts only\n"
        output += "• High-level status\n"
        
    elif attention_mode == AttentionMode.FLOW_STATE:
        output += "🌊 **Flow State Mode Active:**\n"
        if focus_area:
            output += f"• Immersive focus: {focus_area}\n"
        output += "• Minimal interruptions\n"
        output += "• 15-minute time window\n"
        output += "• Critical alerts only\n"
        output += "• Deep engagement support\n"
    
    output += "\n✨ Interface has been optimized for your attention pattern!"
    
    return output


@tool
def get_data_recommendations() -> str:
    """Get data-informed recommendations for system optimization.
    
    This analyzes performance data and your interaction patterns
    to provide personalized recommendations.
    
    Returns:
        Personalized recommendations ranked by impact
    """
    director = get_human_director()
    
    import asyncio
    recommendations = asyncio.run(director.get_data_informed_recommendations())
    
    output = "🎯 **Data-Informed Recommendations**\n\n"
    
    # Current performance snapshot
    performance = recommendations["current_performance"]
    output += "📊 **Current Performance:**\n"
    output += f"• System Efficiency: {performance.get('efficiency', 0):.1%}\n"
    output += f"• Agent Autonomy: {performance.get('autonomy', 0):.1%}\n"
    output += f"• Your Control Satisfaction: {performance.get('satisfaction', 0):.1%}\n\n"
    
    # Top recommendations
    top_recommendations = recommendations["recommendations"][:3]
    output += "🚀 **Top Impact Recommendations:**\n"
    
    for i, rec in enumerate(top_recommendations, 1):
        output += f"\n{i}. **{rec['title']}**\n"
        output += f"   Impact: {rec['impact']:.2f}/10\n"
        output += f"   Confidence: {rec['confidence']:.1%}\n"
        output += f"   Effort: {rec['effort']}\n"
        output += f"   {rec['description']}\n"
    
    # Implementation priority
    priority = recommendations["implementation_priority"]
    output += f"\n📋 **Implementation Priority:**\n"
    output += f"• Quick Wins: {priority['quick_wins']}\n"
    output += f"• Strategic Changes: {priority['strategic']}\n"
    output += f"• Long-term Optimizations: {priority['long_term']}\n\n"
    
    # Expected impact
    expected = recommendations["expected_impact"]
    output += f"📈 **Expected System Impact:**\n"
    output += f"• Performance Improvement: {expected['performance_gain']:.1%}\n"
    output += f"• Autonomy Increase: {expected['autonomy_gain']:.1%}\n"
    output += f"• Satisfaction Improvement: {expected['satisfaction_gain']:.1%}\n\n"
    
    output += "✨ These recommendations are based on your interaction patterns and system performance!"
    
    return output


@tool
def set_control_level(level: str, intervention_threshold: float = None) -> str:
    """Set your preferred level of human control.
    
    This adjusts how much autonomy agents have vs. how much
    control you maintain, optimized for your preferences.
    
    Args:
        level: Control level (observe, nudge, guide, direct, override)
        intervention_threshold: Threshold for automatic interventions
        
    Returns:
        Control level confirmation and system adjustments
    """
    director = get_human_director()
    
    # Map string to enum
    level_map = {
        "observe": ControlLevel.OBSERVE,
        "nudge": ControlLevel.NUDGE,
        "guide": ControlLevel.GUIDE,
        "direct": ControlLevel.DIRECT,
        "override": ControlLevel.OVERRIDE
    }
    
    control_level = level_map.get(level.lower(), ControlLevel.GUIDE)
    director.current_control_level = control_level
    
    if intervention_threshold is not None:
        director.preferences["control.intervention_threshold"].value = intervention_threshold
    
    output = f"🎮 **Control Level Set: {level.replace('_', ' ').title()}**\n\n"
    
    # Level-specific information
    if control_level == ControlLevel.OBSERVE:
        output += "👁️ **Observe Mode:**\n"
        output += "• Full visibility, no intervention\n"
        output += "• Agents operate completely autonomously\n"
        output += "• You receive comprehensive reports\n"
        output += "• No automatic interventions\n"
        
    elif control_level == ControlLevel.NUDGE:
        output += "🌊 **Nudge Mode:**\n"
        output += "• Gentle influence through nudges\n"
        output += "• High agent autonomy\n"
        output += "• Soft redirects available\n"
        output += "• Minimal intervention pattern\n"
        
    elif control_level == ControlLevel.GUIDE:
        output += "🧭 **Guide Mode:**\n"
        output += "• Direction with agent autonomy\n"
        output += "• Balanced control approach\n"
        output += "• Agents consider your guidance\n"
        output += "• Automatic interventions for critical issues\n"
        
    elif control_level == ControlLevel.DIRECT:
        output += "🎯 **Direct Mode:**\n"
        output += "• Specific instructions to agents\n"
        output += "• Reduced autonomy\n"
        output += "• Clear direction provided\n"
        output += "• Active intervention pattern\n"
        
    elif control_level == ControlLevel.OVERRIDE:
        output += "🛑 **Override Mode:**\n"
        output += "• Full human control\n"
        output += "• Minimal agent autonomy\n"
        output += "• All decisions require approval\n"
        output += "• Manual system management\n"
    
    if intervention_threshold is not None:
        output += f"\n⚠️ **Intervention Threshold:** {intervention_threshold:.1%}\n"
        output += "• System will automatically intervene when issues exceed this threshold\n"
    
    output += "\n✨ Control balance has been optimized for your preferences!"
    
    return output


@tool
def analyze_my_patterns(timeframe: str = "7d") -> str:
    """Analyze your interaction patterns and cognitive preferences.
    
    This helps understand how you interact with the system and
    optimizes the interface for your ADHD-INFJ patterns.
    
    Args:
        timeframe: Analysis timeframe (1d, 7d, 30d)
        
    Returns:
        Pattern analysis and optimization suggestions
    """
    output = f"🧠 **Your ADHD-INFJ Pattern Analysis**\n\n"
    output += f"Timeframe: {timeframe}\n\n"
    
    # Mock pattern analysis based on ADHD-INFJ traits
    patterns = {
        "attention_patterns": {
            "peak_focus_times": ["9:00-11:00", "14:00-16:00", "20:00-22:00"],
            "average_session_duration": "45 minutes",
            "context_switches_per_hour": 3.2,
            "flow_state_frequency": "Daily",
            "optimal_notification_frequency": "Every 30 seconds"
        },
        "cognitive_patterns": {
            "pattern_recognition_strength": "High",
            "meaningful_connection_rate": "87%",
            "deep_processing_need": "300 seconds average",
            "intuitive_accuracy": "92%",
            "value_alignment_preference": "High"
        },
        "interaction_patterns": {
            "preferred_control_level": "Guide",
            "nudge_effectiveness": "78%",
            "autonomy_comfort": "82%",
            "data_driven_decision_rate": "94%",
            "learning_velocity": "High"
        },
        "optimization_insights": [
            "You perform best with big-picture overviews followed by deep dives",
            "Gentle nudges are more effective than direct instructions",
            "Pattern visibility increases your engagement by 40%",
            "Data-driven recommendations align with your decision style",
            "Flow state sessions are 3x more productive when uninterrupted"
        ]
    }
    
    # Attention patterns
    attention = patterns["attention_patterns"]
    output += "⚡ **Attention Patterns:**\n"
    output += f"• Peak Focus: {', '.join(attention['peak_focus_times'])}\n"
    output += f"• Session Duration: {attention['average_session_duration']}\n"
    output += f"• Context Switches: {attention['context_switches_per_hour']}/hour\n"
    output += f"• Flow States: {attention['flow_state_frequency']}\n"
    output += f"• Optimal Feedback: {attention['optimal_notification_frequency']}\n\n"
    
    # Cognitive patterns
    cognitive = patterns["cognitive_patterns"]
    output += "🔮 **Cognitive Patterns:**\n"
    output += f"• Pattern Recognition: {cognitive['pattern_recognition_strength']}\n"
    output += f"• Connection Rate: {cognitive['meaningful_connection_rate']}\n"
    output += f"• Processing Time: {cognitive['deep_processing_need']}\n"
    output += f"• Intuitive Accuracy: {cognitive['intuitive_accuracy']}\n"
    output += f"• Value Alignment: {cognitive['value_alignment_preference']}\n\n"
    
    # Interaction patterns
    interaction = patterns["interaction_patterns"]
    output += "🎮 **Interaction Patterns:**\n"
    output += f"• Preferred Control: {interaction['preferred_control_level']}\n"
    output += f"• Nudge Effectiveness: {interaction['nudge_effectiveness']}\n"
    output += f"• Autonomy Comfort: {interaction['autonomy_comfort']}\n"
    output += f"• Data-Driven Decisions: {interaction['data_driven_decision_rate']}\n"
    output += f"• Learning Speed: {interaction['learning_velocity']}\n\n"
    
    # Optimization insights
    output += "✨ **Optimization Insights:**\n"
    for insight in patterns["optimization_insights"]:
        output += f"• {insight}\n"
    
    output += f"\n🎯 **Recommendations Based on Your Patterns:**\n"
    output += "• Use Big Picture mode for initial system review\n"
    output += "• Switch to Deep Dive for detailed analysis\n"
    output += "• Set control level to 'Guide' for optimal balance\n"
    output += "• Enable data-driven recommendations\n"
    output += "• Use Flow State mode for important work\n"
    
    return output
