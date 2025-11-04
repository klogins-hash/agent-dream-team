"""Neurotype Discovery Tools - Adaptive evaluation and personalized AI interaction."""

from typing import Dict, List, Any, Optional
from strands import tool

from neurotype_discovery import get_neurotype_discovery, DiscoveryPhase
from neurotype_profiles import ADHDType, MBTIType, CognitiveStyle


@tool
def start_neurotype_discovery(adhd_type: str = None, mbti_type: str = None, 
                             cognitive_style: str = None) -> str:
    """Start personalized neurotype discovery session.
    
    If you know your types, provide them for instant setup.
    If not, we'll guide you through a gentle evaluation process.
    
    Args:
        adhd_type: Your ADHD type if known (inattentive, hyperactive_impulsive, combined, none)
        mbti_type: Your MBTI type if known (INTJ, INFP, INFJ, etc.)
        cognitive_style: Your cognitive style if known (analytical, intuitive, creative, etc.)
        
    Returns:
        Session ID and next steps
    """
    discovery = get_neurotype_discovery()
    
    # Check if user knows their types
    known_types = {}
    if adhd_type:
        known_types["adhd_type"] = adhd_type
    if mbti_type:
        known_types["mbti_type"] = mbti_type
    if cognitive_style:
        known_types["cognitive_style"] = cognitive_style
    
    import asyncio
    session_id = asyncio.run(discovery.start_discovery_session("user", known_types))
    
    output = "🧠 **Neurotype Discovery Started**\n\n"
    output += f"Session ID: {session_id}\n\n"
    
    if known_types:
        output += "✅ **Known Types Detected:**\n"
        if adhd_type:
            output += f"• ADHD Type: {adhd_type}\n"
        if mbti_type:
            output += f"• MBTI Type: {mbti_type}\n"
        if cognitive_style:
            output += f"• Cognitive Style: {cognitive_style}\n"
        
        output += "\n🎯 **Next Steps:**\n"
        output += "• We'll fine-tune your preferences\n"
        output += "• Ask a few behavioral questions\n"
        output += "• Create your personalized profile\n"
    else:
        output += "🔍 **Discovery Mode:** Full Evaluation\n\n"
        output += "We'll gently guide you through:\n"
        output += "• ADHD screening (6 questions)\n"
        output += "• MBTI assessment (6 questions)\n"
        output += "• Cognitive style analysis (3 questions)\n"
        output += "• Behavioral preferences (3 questions)\n\n"
        output += "🎯 **This will help us:**\n"
        output += "• Optimize feedback timing for your attention\n"
        output += "• Match control levels to your autonomy preference\n"
        output += "• Adjust information density to your processing style\n"
        output += "• Personalize notifications and interactions\n"
    
    output += f"\n📝 Use: `get_next_discovery_question('{session_id}')` to continue"
    
    return output


@tool
def get_next_discovery_question(session_id: str) -> str:
    """Get the next question in your neurotype discovery.
    
    Args:
        session_id: Your discovery session ID
        
    Returns:
        Next question or completion status
    """
    discovery = get_neurotype_discovery()
    
    import asyncio
    question = asyncio.run(discovery.get_next_question(session_id))
    
    if not question:
        # Check if assessment is complete
        progress = asyncio.run(discovery.get_discovery_progress(session_id))
        
        if progress["phase"] == "preference_tuning":
            output = "🎉 **Initial Assessment Complete!**\n\n"
            output += "Based on your answers, we've generated your estimated profile.\n\n"
            
            if progress.get("profile_summary"):
                summary = progress["profile_summary"]
                output += "🧠 **Your Estimated Profile:**\n"
                output += f"• ADHD Type: {summary['adhd_type']}\n"
                output += f"• MBTI Type: {summary['mbti_type']}\n"
                output += f"• Cognitive Style: {summary['cognitive_style']}\n"
                output += f"• Confidence: {summary['confidence']:.1%}\n\n"
            
            output += "📝 Use: `submit_discovery_answer('{session_id}', 'confirm', 'yes')` to confirm\n"
            output += "📝 Or: `submit_discovery_answer('{session_id}', 'adjust', 'your adjustments')` to modify"
            
            return output
        else:
            return "✅ **Discovery Complete!** Your personalized AI interface is now active."
    
    # Format question for display
    output = f"📝 **Question {question.get('progress', '')}**\n\n"
    output += f"**{question['question']}**\n\n"
    
    output += "**Options:**\n"
    for i, option in enumerate(question['options'], 1):
        output += f"{i}. {option}\n"
    
    output += f"\n📝 Use: `submit_discovery_answer('{session_id}', '{question['question_id']}', 'your choice')`"
    
    return output


@tool
def submit_discovery_answer(session_id: str, question_id: str, answer: str) -> str:
    """Submit your answer to a discovery question.
    
    Args:
        session_id: Your discovery session ID
        question_id: The question you're answering
        answer: Your answer (can be option number or text)
        
    Returns:
        Confirmation and next question
    """
    discovery = get_neurotype_discovery()
    
    # Handle special answers
    if question_id == "confirm" and answer.lower() in ["yes", "confirm", "true"]:
        import asyncio
        result = asyncio.run(discovery.confirm_profile(session_id, True))
        
        if result.get("profile_confirmed"):
            output = "🎉 **Profile Confirmed!**\n\n"
            output += "✨ Your personalized AI interface is now active!\n\n"
            output += "🎯 **What's been optimized for you:**\n"
            output += "• Feedback timing matched to your attention span\n"
            output += "• Control levels balanced with your autonomy preference\n"
            output += "• Information density optimized for your processing style\n"
            output += "• Notifications personalized to your needs\n"
            output += "• Learning mode adapted to your cognitive style\n\n"
            
            output += "🧠 The system will continue learning and adapting to you!"
            
            return output
    
    elif question_id == "adjust":
        output = "🔧 **Profile Adjustment Mode**\n\n"
        output += "Tell me what you'd like to adjust:\n\n"
        output += "Examples:\n"
        output += "• 'Change ADHD type to combined'\n"
        output += "• 'Set MBTI to INTJ'\n"
        output += "• 'Make cognitive style analytical'\n"
        output += "• 'Increase feedback frequency'\n"
        output += "• 'Less control, more autonomy'\n\n"
        output += "📝 Use: `submit_discovery_answer('{session_id}', 'adjustment', 'your changes')`"
        
        return output
    
    elif question_id == "adjustment":
        # Process adjustment request
        return process_profile_adjustment(session_id, answer)
    
    # Get the question to validate answer
    question = discovery.questions.get(question_id)
    if not question:
        return f"❌ Question '{question_id}' not found"
    
    # Convert numeric answers to text
    if answer.isdigit():
        answer_index = int(answer) - 1
        if 0 <= answer_index < len(question.options):
            answer = question.options[answer_index]
        else:
            return f"❌ Invalid option number. Please choose 1-{len(question.options)}"
    
    # Validate answer
    if answer not in question.options:
        return f"❌ Invalid answer. Please choose from: {', '.join(question.options)}"
    
    # Submit answer
    import asyncio
    result = asyncio.run(discovery.submit_answer(session_id, question_id, answer))
    
    if result.get("error"):
        return f"❌ {result['error']}"
    
    output = "✅ **Answer Recorded**\n\n"
    
    # Show confidence progress
    confidence = result.get("confidence_scores", {})
    if confidence:
        output += "🧠 **Current Confidence Scores:**\n"
        for key, value in confidence.items():
            output += f"• {key.replace('_', ' ').title()}: {value:.1%}\n"
        output += "\n"
    
    # Get next question
    next_question = result.get("next_question")
    if next_question:
        output += "📝 **Next Question:**\n\n"
        output += f"**{next_question['question']}**\n\n"
        
        output += "**Options:**\n"
        for i, option in enumerate(next_question['options'], 1):
            output += f"{i}. {option}\n"
        
        output += f"\n📝 Use: `submit_discovery_answer('{session_id}', '{next_question['question_id']}', 'your choice')`"
    else:
        # Assessment complete
        progress = asyncio.run(discovery.get_discovery_progress(session_id))
        if progress.get("profile_summary"):
            summary = progress["profile_summary"]
            output += "🎉 **Assessment Complete!**\n\n"
            output += "🧠 **Your Estimated Profile:**\n"
            output += f"• ADHD Type: {summary['adhd_type']}\n"
            output += f"• MBTI Type: {summary['mbti_type']}\n"
            output += f"• Cognitive Style: {summary['cognitive_style']}\n"
            output += f"• Confidence: {summary['confidence']:.1%}\n\n"
            
            output += "📝 Use: `submit_discovery_answer('{session_id}', 'confirm', 'yes')` to confirm\n"
            output += "📝 Or: `submit_discovery_answer('{session_id}', 'adjust', 'your changes')` to modify"
    
    return output


def process_profile_adjustment(session_id: str, adjustment_text: str) -> str:
    """Process profile adjustment request."""
    adjustments = {}
    
    # Parse adjustment text
    text = adjustment_text.lower()
    
    # ADHD type adjustments
    if "combined" in text:
        adjustments["adhd_type"] = "combined"
    elif "inattentive" in text:
        adjustments["adhd_type"] = "inattentive"
    elif "hyperactive" in text:
        adjustments["adhd_type"] = "hyperactive_impulsive"
    elif "none" in text or "no adhd" in text:
        adjustments["adhd_type"] = "none"
    
    # MBTI type adjustments
    mbti_types = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
                  "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
    for mbti in mbti_types:
        if mbti.lower() in text:
            adjustments["mbti_type"] = mbti
            break
    
    # Cognitive style adjustments
    if "analytical" in text:
        adjustments["cognitive_style"] = "analytical"
    elif "intuitive" in text:
        adjustments["cognitive_style"] = "intuitive"
    elif "creative" in text:
        adjustments["cognitive_style"] = "creative"
    elif "logical" in text:
        adjustments["cognitive_style"] = "logical"
    elif "systematic" in text:
        adjustments["cognitive_style"] = "systematic"
    elif "holistic" in text:
        adjustments["cognitive_style"] = "holistic"
    
    if not adjustments:
        output = "❓ **Adjustment Not Recognized**\n\n"
        output += "Please specify what you'd like to adjust:\n\n"
        output += "• ADHD type: combined, inattentive, hyperactive_impulsive, none\n"
        output += "• MBTI type: INTJ, INFP, INFJ, ENTP, etc.\n"
        output += "• Cognitive style: analytical, intuitive, creative, etc.\n\n"
        output += "Example: 'Change ADHD type to combined and set MBTI to INTJ'"
        
        return output
    
    # Apply adjustments
    discovery = get_neurotype_discovery()
    import asyncio
    result = asyncio.run(discovery.confirm_profile(session_id, False, adjustments))
    
    output = "🔧 **Profile Adjusted**\n\n"
    output += "Changes applied:\n"
    for key, value in adjustments.items():
        output += f"• {key.replace('_', ' ').title()}: {value}\n"
    
    output += f"\n{result.get('next_steps', 'System will continue learning from your interactions.')}"
    
    return output


@tool
def get_discovery_progress(session_id: str) -> str:
    """Check your neurotype discovery progress.
    
    Args:
        session_id: Your discovery session ID
        
    Returns:
        Current progress and confidence scores
    """
    discovery = get_neurotype_discovery()
    
    import asyncio
    progress = asyncio.run(discovery.get_discovery_progress(session_id))
    
    if progress.get("error"):
        return f"❌ {progress['error']}"
    
    output = "📊 **Discovery Progress**\n\n"
    output += f"Session: {session_id}\n"
    output += f"Phase: {progress['phase'].replace('_', ' ').title()}\n"
    output += f"Questions Answered: {progress['questions_answered']}\n"
    output += f"Learning Iterations: {progress['learning_iterations']}\n\n"
    
    # Confidence scores
    confidence = progress.get("confidence_scores", {})
    if confidence:
        output += "🧠 **Confidence Scores:**\n"
        for key, value in confidence.items():
            output += f"• {key.replace('_', ' ').title()}: {value:.1%}\n"
        output += "\n"
    
    # Profile summary
    if progress.get("profile_summary"):
        summary = progress["profile_summary"]
        output += "👤 **Current Profile Estimate:**\n"
        output += f"• ADHD Type: {summary['adhd_type']}\n"
        output += f"• MBTI Type: {summary['mbti_type']}\n"
        output += f"• Cognitive Style: {summary['cognitive_style']}\n"
        output += f"• Overall Confidence: {summary['confidence']:.1%}\n\n"
        
        if summary['confidence'] >= 0.8:
            output += "🎯 **High Confidence!** Ready to confirm your profile."
        elif summary['confidence'] >= 0.6:
            output += "⚡ **Good Confidence!** A few more questions will help."
        else:
            output += "🔍 **Building Confidence!** Continue with evaluation questions."
    
    return output


@tool
def quick_neurotype_assessment() -> str:
    """Quick 3-question assessment for immediate optimization.
    
    Returns:
        Rapid assessment and basic optimization
    """
    output = "⚡ **Quick Neurotype Assessment**\n\n"
    output += "Answer these 3 questions for immediate optimization:\n\n"
    
    output += "**1. Attention Style:**\n"
    output += "How would you describe your attention?\n"
    output += "a) I focus best in short bursts\n"
    output += "b) I can hyperfocus when interested\n"
    output += "c) I prefer long, deep work sessions\n"
    output += "d) It varies depending on the task\n\n"
    
    output += "**2. Interaction Preference:**\n"
    output += "When working with AI, you prefer:\n"
    output += "a) Full control over decisions\n"
    output += "b) Guidance with AI autonomy\n"
    output += "c) Mostly autonomous AI\n"
    output += "d) Fully autonomous AI\n\n"
    
    output += "**3. Information Style:**\n"
    output += "You prefer information that is:\n"
    output += "a) Detailed and step-by-step\n"
    output += "b) Pattern-focused and intuitive\n"
    output += "c) Creative and exploratory\n"
    output += "d) Big picture and meaningful\n\n"
    
    output += "📝 Use: `submit_quick_assessment('1a', '2b', '3d')` format\n\n"
    
    output += "This will give you instant basic optimization while you decide\n"
    output += "if you want to do the full detailed assessment."
    
    return output


@tool
def submit_quick_assessment(q1: str, q2: str, q3: str) -> str:
    """Submit quick assessment answers for immediate optimization.
    
    Args:
        q1: Answer to question 1 (1a, 1b, 1c, or 1d)
        q2: Answer to question 2 (2a, 2b, 2c, or 2d)
        q3: Answer to question 3 (3a, 3b, 3c, or 3d)
        
    Returns:
        Quick optimization recommendations
    """
    # Parse answers
    attention = q1[-1] if q1.startswith('1') else 'a'
    interaction = q2[-1] if q2.startswith('2') else 'b'
    information = q3[-1] if q3.startswith('3') else 'd'
    
    # Generate quick profile
    quick_profile = {
        "attention_style": attention,
        "interaction_preference": interaction,
        "information_style": information
    }
    
    output = "⚡ **Quick Assessment Results**\n\n"
    
    # Attention optimization
    output += "🧠 **Attention Optimization:**\n"
    if attention == 'a':
        output += "• Short feedback intervals (30 seconds)\n"
        output += "• Task breakdown for quick wins\n"
        output += "• High notification frequency\n"
    elif attention == 'b':
        output += "• Variable feedback timing\n"
        output += "• Hyperfocus protection mode\n"
        output += "• Context switching support\n"
    elif attention == 'c':
        output += "• Long feedback intervals (5 minutes)\n"
        output += "• Deep work preservation\n"
        output += "• Minimal interruptions\n"
    else:
        output += "• Adaptive feedback timing\n"
        output += "• Multiple attention modes\n"
        output += "• Flexible notification system\n"
    
    output += "\n🎮 **Interaction Optimization:**\n"
    if interaction == 'a':
        output += "• High control level (80% human)\n"
        output += "• Decision approval required\n"
        output += "• Detailed option presentation\n"
    elif interaction == 'b':
        output += "• Balanced control (50% human)\n"
        output += "• Guidance with autonomy\n"
        output += "• Nudge-based influence\n"
    elif interaction == 'c':
        output += "• Low control level (30% human)\n"
        output += "• Mostly autonomous AI\n"
        output += "• Occasional human direction\n"
    else:
        output += "• Autonomous AI (10% human)\n"
        output += "• Minimal intervention\n"
        output += "• Automatic optimization\n"
    
    output += "\n📚 **Information Optimization:**\n"
    if information == 'a':
        output += "• Detailed, step-by-step information\n"
        output += "• High information density\n"
        output += "• Analytical presentation style\n"
    elif information == 'b':
        output += "• Pattern-focused information\n"
        output += "• Intuitive connections highlighted\n"
        output += "• Medium information density\n"
    elif information == 'c':
        output += "• Creative, exploratory information\n"
        output += "• Multiple perspectives shown\n"
        output += "• Variable information density\n"
    else:
        output += "• Big picture, meaningful information\n"
        output += "• Value and purpose emphasized\n"
        output += "• Context-rich presentation\n"
    
    output += f"\n✨ **Quick Optimization Applied!**\n\n"
    output += "🎯 For even better personalization, try the full assessment:\n"
    output += "📝 Use: `start_neurotype_discovery()` for complete evaluation"
    
    return output


@tool
def get_neurotype_recommendations() -> str:
    """Get personalized recommendations based on your neurotype.
    
    Returns:
        Tailored recommendations for optimal AI interaction
    """
    output = "🎯 **Personalized Neurotype Recommendations**\n\n"
    
    output += "Based on your neurotype, here are optimal strategies:\n\n"
    
    output += "🧠 **Cognitive Optimization:**\n"
    output += "• Work during your peak focus hours\n"
    output += "• Use attention mode switching (big picture → deep dive)\n"
    output += "• Leverage your natural pattern recognition\n"
    output += "• Match information density to your energy levels\n\n"
    
    output += "🤖 **AI Interaction Strategies:**\n"
    output += "• Start with 'Guide' control level for balance\n"
    output += "• Use gentle nudges instead of direct commands\n"
    output += "• Enable dopamine loops for motivation\n"
    output += "• Set feedback frequency to match your attention span\n\n"
    
    output += "🎨 **Interface Personalization:**\n"
    output += "• Visual notifications for immediate attention\n"
    output += "• Pattern visibility for intuitive understanding\n"
    output += "• Context preservation for task switching\n"
    output += "• Deep processing time for complex decisions\n\n"
    
    output += "📈 **Performance Enhancement:**\n"
    output += "• Monitor your optimization score regularly\n"
    output += "• Adjust preferences based on current context\n"
    output += "• Use flow state mode for important work\n"
    output += "• Enable continuous learning for adaptation\n\n"
    
    output += "🔄 **Evolution Strategy:**\n"
    output += "• Review neurotype fit monthly\n"
    output += "• Create context-specific profiles\n"
    output += "• Share feedback to improve recommendations\n"
    output += "• Experiment with different optimization approaches"
    
    return output
