# 🧠 Neurotype Profile Setup Guide

## Overview

The Agent Dream Team system now supports **personalized neurotype optimization** through environment-based configuration. Each user gets their own optimized interface based on their brain type and cognitive preferences.

## 🚀 Quick Setup

### 1. Choose Your Profile Template

We provide pre-configured templates for common neurotype combinations:

- **ADHD Combined + INFJ** (`adhd-infj`) - *For you!*
- **ADHD Combined + INTJ** (`adhd-intj`)
- **Neurotypical + ENTP** (`neurotypical-entp`)
- **ADHD Inattentive + ISFJ** (`adhd-inattentive-isfj`)

### 2. Copy and Activate

```bash
# Copy your template
cp .env.neurotype.adhd-infj .env.neurotype

# Or create custom from example
cp .env.neurotype.example .env.neurotype
```

### 3. Restart System

```bash
docker-compose down && docker-compose up -d
```

## 📝 Configuration Options

### Core Neurotype Settings

```bash
# ADHD Type: inattentive, hyperactive_impulsive, combined, none
NEUROTYPE_ADHD_TYPE=combined

# MBTI Type: INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, ISTJ, ISFJ, ESTJ, ESFJ, ISTP, ISFP, ESTP, ESFP, none
NEUROTYPE_MBTI_TYPE=INFJ

# Cognitive Style: analytical, intuitive, creative, logical, systematic, holistic, linear, divergent
NEUROTYPE_COGNITIVE_STYLE=intuitive
```

### Cognitive Preferences

```bash
# Attention Span: short, medium, long, variable
NEUROTYPE_ATTENTION_SPAN=variable

# Processing Speed: slow, medium, fast, variable
NEUROTYPE_PROCESSING_SPEED=medium

# Detail Preference: low, medium, high, balanced
NEUROTYPE_DETAIL_PREFERENCE=balanced

# Pattern Recognition: low, medium, high
NEUROTYPE_PATTERN_RECOGNITION=high
```

### Interaction Preferences

```bash
# Feedback Frequency: minimal, medium, high
NEUROTYPE_FEEDBACK_FREQUENCY=high

# Notification Style: visual, auditory, minimal
NEUROTYPE_NOTIFICATION_STYLE=visual

# Control Preference: low, balanced, high
NEUROTYPE_CONTROL_PREFERENCE=balanced

# Autonomy Comfort: low, medium, high
NEUROTYPE_AUTONOMY_COMFORT=high
```

### Environmental Preferences

```bash
# Stimulation Level: low, medium, high
NEUROTYPE_STIMULATION_LEVEL=medium

# Structure Preference: low, medium, high
NEUROTYPE_STRUCTURE_PREFERENCE=medium

# Complexity Tolerance: low, medium, high
NEUROTYPE_COMPLEXITY_TOLERANCE=high
```

### Learning Style

```bash
# Learning Mode: visual, auditory, kinesthetic, reading
NEUROTYPE_LEARNING_MODE=visual

# Information Density: sparse, medium, dense
NEUROTYPE_INFORMATION_DENSITY=medium
```

### Custom Preferences

```bash
# JSON format for custom features
NEUROTYPE_CUSTOM_PREFS='{"dopamine_loops": true, "hyperfocus_support": true, "meaningful_connections": true}'
```

## 🎯 Available Templates

### ADHD Combined + INFJ (`adhd-infj`)
**Best for:** Hyperfocus, pattern recognition, meaningful connections

**Features:**
- Variable attention span support
- High pattern recognition
- Visual notifications
- Balanced control with high autonomy
- Dopamine feedback loops
- Deep processing time
- Value-aligned interactions

### ADHD Combined + INTJ (`adhd-intj`)
**Best for:** Strategic thinking, independent work, complex problems

**Features:**
- Fast processing speed
- High detail preference
- Low control preference
- Dense information handling
- Strategic thinking support
- Independent work optimization
- Logical structure

### Neurotypical + ENTP (`neurotypical-entp`)
**Best for:** Quick decisions, creative exploration, leadership

**Features:**
- Fast processing
- High stimulation tolerance
- High control preference
- Kinesthetic learning
- Creative exploration
- Leadership role support
- Novel connections

### ADHD Inattentive + ISFJ (`adhd-inattentive-isfj`)
**Best for:** Focus assistance, structured environment, supportive interactions

**Features:**
- Short attention span support
- Minimal notifications
- High structure preference
- Visual learning
- Focus assistance
- Clear structure
- Supportive environment

## 🔧 Custom Profile Creation

### Step 1: Copy Template
```bash
cp .env.neurotype.example .env.neurotype.custom
```

### Step 2: Customize Settings
Edit `.env.neurotype.custom` with your specific preferences.

### Step 3: Generate Profile Code
```python
from neurotype_profiles import get_neurotype_manager

# Load your custom profile
manager = get_neurotype_manager()
profile = manager.load_profile_from_env()

# Generate optimized configuration
env_template = manager.create_env_file_template(profile)
print(env_template)
```

## 🎨 Interface Adaptations

Based on your neurotype profile, the system automatically adjusts:

### ADHD Optimizations
- **Feedback Frequency**: How often you receive updates
- **Dopamine Loops**: Achievement celebrations and micro-rewards
- **Hyperfocus Support**: Minimal interruptions during deep work
- **Task Switching**: Context preservation between tasks
- **Attention Management**: Adaptive notification timing

### MBTI Optimizations
- **Control Levels**: Balance between autonomy and guidance
- **Information Density**: How much detail to show
- **Pattern Visibility**: Connection visualization for intuitive types
- **Social Feedback**: Collaborative vs. independent work preferences
- **Decision Support**: Quick vs. deliberate decision making

### Cognitive Style Optimizations
- **Learning Mode**: Visual, auditory, kinesthetic, or reading
- **Processing Speed**: Fast-paced vs. thoughtful presentation
- **Complexity Handling**: Simple vs. complex information presentation
- **Structure Level**: Highly structured vs. flexible interfaces

## 📊 Performance Tracking

The system learns from your interaction patterns:

### Metrics Tracked
- **Attention Patterns**: When you're most focused
- **Intervention Effectiveness**: Which nudges work best
- **Preference Accuracy**: How well settings match your needs
- **Performance Impact**: How optimizations affect your productivity

### Auto-Optimization
- **Preference Tuning**: Automatic adjustment based on usage
- **Interface Evolution**: System learns your ideal setup
- **Feature Discovery**: New optimizations suggested over time
- **Performance Improvement**: Continuous enhancement of your experience

## 🔄 Profile Switching

### Multiple Profiles
You can maintain multiple neurotype profiles:

```bash
# Switch to focus mode
cp .env.neurotype.focus .env.neurotype

# Switch to collaborative mode
cp .env.neurotype.collaborative .env.neurotype

# Switch to learning mode
cp .env.neurotype.learning .env.neurotype
```

### Context-Specific Profiles
Create profiles for different contexts:
- **Work Profile**: Professional settings
- **Learning Profile**: Study and research
- **Creative Profile**: Brainstorming and innovation
- **Relaxation Profile**: Low-stress interaction

## 🚨 Troubleshooting

### Profile Not Loading
```bash
# Check if file exists
ls -la .env.neurotype*

# Verify format
cat .env.neurotype

# Restart system
docker-compose restart
```

### Custom Preferences Not Working
```bash
# Check JSON format
echo $NEUROTYPE_CUSTOM_PREFS | python -m json.tool

# Validate custom preferences
python -c "import json; print(json.loads(os.getenv('NEUROTYPE_CUSTOM_PREFS', '{}')))"
```

### Performance Issues
```bash
# Check optimization score
python -c "from human_director import load_human_director_from_env; director = load_human_director_from_env(); print(director.get_neurotype_summary())"
```

## 🎯 Best Practices

### 1. Start with Template
Use the closest template as your starting point.

### 2. Iterate Gradually
Change one setting at a time and observe effects.

### 3. Measure Impact
Use the performance tracking to see what works.

### 4. Custom Preferences
Add custom features that address your specific needs.

### 5. Profile Evolution
Update your profile as your preferences change over time.

## 🌟 Next Steps

1. **Set up your profile** using the appropriate template
2. **Test the interface** and observe how it feels
3. **Fine-tune settings** based on your experience
4. **Enable learning** to allow continuous optimization
5. **Create context profiles** for different situations

---

**Your brain type isn't a configuration - it's a superpower. Let's optimize for it!** 🧠✨

## 📞 Support

For help with neurotype configuration:
- Check the troubleshooting section above
- Review available templates
- Use the performance tracking tools
- Create custom preferences for unique needs
