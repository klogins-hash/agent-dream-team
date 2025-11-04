"""Neurotype-optimized tools for personalized human-agent interaction."""

from typing import Dict, List, Any, Optional
from strands import tool

from neurotype_profiles import get_neurotype_manager, ADHDType, MBTIType, CognitiveStyle
from human_director import load_human_director_from_env


@tool
def get_my_neurotype_profile() -> str:
    """Get your current neurotype profile and optimizations.
    
    Returns:
        Detailed profile information and current optimizations
    """
    director = load_human_director_from_env()
    summary = director.get_neurotype_summary()
    
    output = "🧠 **Your Neurotype Profile**\n\n"
    
    # Core type
    output += f"🎯 **Core Type:** {summary['core_type']}\n"
    output += f"🔮 **Cognitive Style:** {summary['cognitive_style']}\n\n"
    
    # Attention characteristics
    attention = summary["attention_characteristics"]
    output += "⚡ **Attention Characteristics:**\n"
    output += f"• Span: {attention['span']}\n"
    output += f"• Processing: {attention['processing']}\n"
    output += f"• Feedback: {attention['feedback']}\n\n"
    
    # Interaction style
    interaction = summary["interaction_style"]
    output += "🎮 **Interaction Style:**\n"
    output += f"• Control Preference: {interaction['control']}\n"
    output += f"• Autonomy Comfort: {interaction['autonomy']}\n"
    output += f"• Notifications: {interaction['notifications']}\n\n"
    
    # Custom features
    if summary["custom_features"]:
        output += "✨ **Custom Optimizations:**\n"
        for feature in summary["custom_features"]:
            output += f"• {feature.replace('_', ' ').title()}\n"
        output += "\n"
    
    # Optimization score
    output += f"📊 **System Optimization:** {summary['optimization_score']:.1%}\n\n"
    
    output += "🎯 The interface is optimized for your unique cognitive patterns!"
    
    return output


@tool
def list_neurotype_templates() -> str:
    """List all available neurotype profile templates.
    
    Returns:
        Available templates with descriptions
    """
    manager = get_neurotype_manager()
    templates = manager.list_available_templates()
    
    output = "📚 **Available Neurotype Templates**\n\n"
    
    template_descriptions = {
        "adhd_infj": "ADHD Combined + INFJ - Hyperfocus, pattern recognition, meaningful connections",
        "adhd_intj": "ADHD Combined + INTJ - Strategic thinking, independent work, complex problems",
        "neurotypical_entp": "Neurotypical + ENTP - Quick decisions, creative exploration, leadership",
        "adhd_inattentive_isfj": "ADHD Inattentive + ISFJ - Focus assistance, structured environment"
    }
    
    for template in templates:
        description = template_descriptions.get(template, "Custom neurotype configuration")
        output += f"• **{template}**: {description}\n"
    
    output += f"\n🎯 **Total Templates:** {len(templates)}\n\n"
    output += "Use: `activate_neurotype_template(template_name)` to switch profiles"
    
    return output


@tool
def activate_neurotype_template(template_name: str) -> str:
    """Activate a neurotype profile template.
    
    Args:
        template_name: Name of the template to activate
        
    Returns:
        Activation confirmation and profile summary
    """
    manager = get_neurotype_manager()
    template = manager.get_profile_template(template_name)
    
    if not template:
        return f"❌ Template '{template_name}' not found. Use `list_neurotype_templates()` to see available options."
    
    # Generate environment file content
    env_content = manager.create_env_file_template(template)
    
    output = f"✅ **Neurotype Template Activated: {template_name}**\n\n"
    
    # Profile summary
    output += f"🧠 **Profile:** {template.adhd_type.value} + {template.mbti_type.value}\n"
    output += f"🔮 **Cognitive Style:** {template.cognitive_style.value}\n\n"
    
    # Key optimizations
    output += "🎯 **Key Optimizations:**\n"
    output += f"• Feedback Frequency: {template.feedback_frequency}\n"
    output += f"• Control Preference: {template.control_preference}\n"
    output += f"• Pattern Recognition: {template.pattern_recognition}\n"
    output += f"• Learning Mode: {template.learning_mode}\n\n"
    
    # Custom features
    if template.custom_preferences:
        output += "✨ **Special Features:**\n"
        for feature, value in template.custom_preferences.items():
            if value:
                output += f"• {feature.replace('_', ' ').title()}\n"
        output += "\n"
    
    output += "📝 **To apply permanently:**\n"
    output += f"1. Copy the template content to your `.env.neurotype` file\n"
    output += f"2. Restart the system\n\n"
    
    output += "🎨 Your interface will now be optimized for this neurotype!"
    
    return output


@tool
def create_custom_neurotype(adhd_type: str, mbti_type: str, cognitive_style: str, 
                           attention_span: str = "medium", processing_speed: str = "medium",
                           feedback_frequency: str = "medium", control_preference: str = "balanced") -> str:
    """Create a custom neurotype profile.
    
    Args:
        adhd_type: ADHD type (inattentive, hyperactive_impulsive, combined, none)
        mbti_type: MBTI type (INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, etc.)
        cognitive_style: Cognitive style (analytical, intuitive, creative, logical, etc.)
        attention_span: Attention span (short, medium, long, variable)
        processing_speed: Processing speed (slow, medium, fast, variable)
        feedback_frequency: Feedback frequency (minimal, medium, high)
        control_preference: Control preference (low, balanced, high)
        
    Returns:
        Custom profile configuration
    """
    # Validate inputs
    adhd_types = ["inattentive", "hyperactive_impulsive", "combined", "none"]
    mbti_types = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
                  "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP", "none"]
    cognitive_styles = ["analytical", "intuitive", "creative", "logical", "systematic", "holistic", "linear", "divergent"]
    
    if adhd_type not in adhd_types:
        return f"❌ Invalid ADHD type. Choose from: {', '.join(adhd_types)}"
    
    if mbti_type not in mbti_types:
        return f"❌ Invalid MBTI type. Choose from: {', '.join(mbti_types)}"
    
    if cognitive_style not in cognitive_styles:
        return f"❌ Invalid cognitive style. Choose from: {', '.join(cognitive_styles)}"
    
    # Create custom profile
    from neurotype_profiles import NeurotypeProfile, ADHDType, MBTIType, CognitiveStyle
    
    profile = NeurotypeProfile(
        user_id="custom",
        adhd_type=ADHDType(adhd_type),
        mbti_type=MBTIType(mbti_type),
        cognitive_style=CognitiveStyle(cognitive_style),
        attention_span=attention_span,
        processing_speed=processing_speed,
        feedback_frequency=feedback_frequency,
        control_preference=control_preference
    )
    
    # Generate environment configuration
    manager = get_neurotype_manager()
    env_content = manager.create_env_file_template(profile)
    
    output = f"🎨 **Custom Neurotype Profile Created**\n\n"
    output += f"🧠 **Core Configuration:**\n"
    output += f"• ADHD Type: {profile.adhd_type.value}\n"
    output += f"• MBTI Type: {profile.mbti_type.value}\n"
    output += f"• Cognitive Style: {profile.cognitive_style.value}\n\n"
    
    output += f"⚡ **Cognitive Settings:**\n"
    output += f"• Attention Span: {profile.attention_span}\n"
    output += f"• Processing Speed: {profile.processing_speed}\n"
    output += f"• Feedback Frequency: {profile.feedback_frequency}\n\n"
    
    output += f"🎮 **Interaction Settings:**\n"
    output += f"• Control Preference: {profile.control_preference}\n"
    output += f"• Autonomy Comfort: {profile.autonomy_comfort}\n"
    output += f"• Notification Style: {profile.notification_style}\n\n"
    
    output += "📝 **Environment Configuration:**\n"
    output += "```\n" + env_content + "```\n\n"
    
    output += "✅ Save this to `.env.neurotype` and restart to apply!"
    
    return output


@tool
def analyze_neurotype_fit() -> str:
    """Analyze how well the current system fits your neurotype.
    
    Returns:
        Fit analysis and optimization recommendations
    """
    director = load_human_director_from_env()
    summary = director.get_neurotype_summary()
    
    optimization_score = summary["optimization_score"]
    
    output = "🔍 **Neurotype Fit Analysis**\n\n"
    
    # Overall score
    output += f"📊 **Overall Fit Score:** {optimization_score:.1%}\n"
    
    if optimization_score >= 0.9:
        output += "🎉 Excellent fit! The system is highly optimized for you.\n"
    elif optimization_score >= 0.7:
        output += "✅ Good fit! The system is well-optimized for your needs.\n"
    elif optimization_score >= 0.5:
        output += "⚠️ Moderate fit. Some optimizations could improve your experience.\n"
    else:
        output += "❌ Poor fit. Consider adjusting your neurotype configuration.\n"
    
    output += "\n🎯 **Optimization Opportunities:**\n"
    
    # Analyze specific areas
    profile = director.neurotype_profile
    
    if profile.adhd_type.value != "none" and profile.feedback_frequency == "minimal":
        output += "• Consider increasing feedback frequency for ADHD support\n"
    
    if profile.mbti_type.value in ["INFJ", "INFP"] and profile.pattern_recognition == "low":
        output += "• Enable higher pattern recognition for intuitive types\n"
    
    if profile.control_preference == "high" and summary["interaction_style"]["autonomy"] == "high":
        output += "• Balance control preference with autonomy for better flow\n"
    
    if profile.attention_span == "variable" and profile.notification_style == "minimal":
        output += "• Consider visual notifications for variable attention spans\n"
    
    output += "\n✨ **Recommendations:**\n"
    output += "• Use `get_my_neurotype_profile()` to review current settings\n"
    output += "• Try `activate_neurotype_template()` to test different configurations\n"
    output += "• Create a custom profile for perfect personalization\n"
    output += "• Monitor your optimization score over time\n"
    
    return output


@tool
def get_neurotype_insights() -> str:
    """Get insights about your neurotype and how it affects your interaction with AI agents.
    
    Returns:
        Personalized insights and recommendations
    """
    director = load_human_director_from_env()
    profile = director.neurotype_profile
    
    output = f"🧠 **Neurotype Insights: {profile.adhd_type.value} + {profile.mbti_type.value}**\n\n"
    
    # ADHD-specific insights
    if profile.adhd_type.value != "none":
        output += "⚡ **ADHD Strengths in AI Interaction:**\n"
        
        if profile.adhd_type.value == "combined":
            output += "• Hyperfocus allows deep exploration of AI capabilities\n"
            output += "• Rapid task switching enables managing multiple agents\n"
            output += "• Creative problem solving with AI collaboration\n"
            output += "• High energy for intensive AI interactions\n\n"
            
        elif profile.adhd_type.value == "inattentive":
            output += "• Deep focus on interesting AI topics\n"
            output += "• Ability to see patterns others miss\n"
            output += "• Creative connections between AI capabilities\n"
            output += "• Reduced distraction when properly engaged\n\n"
            
        elif profile.adhd_type.value == "hyperactive_impulsive":
            output += "• Quick decision making with AI assistance\n"
            output += "• Energetic exploration of AI possibilities\n"
            output += "• Spontaneous creative insights\n"
            output += "• Engaging interaction style\n\n"
    
    # MBTI-specific insights
    mbti_insights = {
        "INTJ": "Strategic planning with AI systems, long-term vision, independent work",
        "INTP": "Deep analysis of AI capabilities, theoretical exploration, logical frameworks",
        "ENTJ": "Leadership in AI implementation, strategic deployment, efficient systems",
        "ENTP": "Innovative AI applications, creative problem solving, exploring possibilities",
        "INFJ": "Meaningful AI collaboration, pattern recognition, value-aligned systems",
        "INFP": "Creative AI partnerships, ethical considerations, personalized interactions",
        "ENFJ": "AI team coordination, human-centered design, collaborative systems",
        "ENFP": "Creative AI brainstorming, enthusiastic exploration, connecting ideas",
    }
    
    if profile.mbti_type.value in mbti_insights:
        output += f"🔮 **{profile.mbti_type.value} Strengths with AI:**\n"
        insight = mbti_insights[profile.mbti_type.value]
        for point in insight.split(", "):
            output += f"• {point}\n"
        output += "\n"
    
    # Cognitive style insights
    style_insights = {
        "analytical": "Data-driven decisions, systematic AI optimization, detailed analysis",
        "intuitive": "Pattern recognition, holistic AI understanding, insights generation",
        "creative": "Innovative AI applications, creative problem solving, novel solutions",
        "logical": "Structured AI interactions, logical frameworks, systematic approaches",
        "systematic": "Organized AI workflows, structured learning, methodical progress",
        "holistic": "Big picture AI strategy, integrated systems, comprehensive understanding",
        "linear": "Sequential AI learning, step-by-step progression, structured development",
        "divergent": "Multiple AI approaches, creative exploration, diverse solutions",
    }
    
    if profile.cognitive_style.value in style_insights:
        output += f"🧩 **{profile.cognitive_style.value.title()} Cognitive Style:**\n"
        insight = style_insights[profile.cognitive_style.value]
        for point in insight.split(", "):
            output += f"• {point}\n"
        output += "\n"
    
    output += "🎯 **Optimization Strategy:**\n"
    output += "• Lean into your natural strengths with AI\n"
    output += "• Use the system to compensate for challenges\n"
    output += "• Develop routines that enhance your cognitive style\n"
    output += "• Continuously refine your neurotype configuration\n"
    
    return output
