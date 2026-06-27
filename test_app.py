import json
import pytest
from pydantic import ValidationError
from app import MindMateResponse, IndianMeals

def test_mindmate_response_parsing_valid():
    """
    Test that MindMateResponse correctly parses a valid mock JSON payload.
    """
    mock_payload = {
        "emotion": "Hopeful",
        "empathy_validation": "It is completely normal to feel exam pressure, but you are handling it well.",
        "emotion_insight": "You are feeling positive because of syllabus milestones achieved.",
        "academic_anxiety_pct": 40,
        "fatigue_burnout_pct": 30,
        "domestic_pressure_pct": 30,
        "coping_plan": [
            "1. Do a 2-minute box breathing cycle.",
            "2. Stand up and stretch.",
            "3. Revise one key chemistry formula."
        ],
        "meals": {
            "breakfast": "Poha with a handful of almonds for slow-release brain carbs",
            "lunch": "Dal Tadka with brown rice for high protein concentration",
            "dinner": "Khichdi with a dash of ghee for easy nighttime digestion",
            "snack": "Roasted makhana with green tea for antioxidant alertness",
            "avoid": "Over-sweetened milk coffee which causes blood sugar crashes"
        },
        "walk_prompt": "Walk to your local park and search for 3 yellow flowers to ground your visual awareness.",
        "youtube_music_query": "Calm Lo-Fi Rain Sounds for UPSC Prep",
        "youtube_strategy_query": "IIT JEE organic chemistry key equation summary sheets",
        "parent_guardrail": "Hi Mom and Dad, I am studying hard but need some quiet focus time today. Love you.",
        "friend_nudge": "Send a text to a friend asking them what their favorite lunch was today.",
        "burnout_score": 5,
        "dynamic_reset_exercise": "Take five deep physiological sighs to activate your parasympathetic nervous system.",
        "motivational_nudge": "Keep going! UPSC prep is a marathon, and you have exactly 45 days left to cross the finish line."
    }
    
    # Validation passes without error
    try:
        response = MindMateResponse(**mock_payload)
        assert response.emotion == "Hopeful"
        assert response.burnout_score == 5
        assert response.meals.breakfast == "Poha with a handful of almonds for slow-release brain carbs"
        assert response.academic_anxiety_pct + response.fatigue_burnout_pct + response.domestic_pressure_pct == 100
    except ValidationError as e:
        pytest.fail(f"ValidationError raised on valid mock payload: {e}")

def test_mindmate_response_parsing_invalid():
    """
    Test that MindMateResponse raises a ValidationError when invalid payloads are supplied.
    """
    # Missing required field 'meals'
    invalid_payload = {
        "emotion": "Hopeful",
        "empathy_validation": "Validated",
        "emotion_insight": "Insight",
        "academic_anxiety_pct": 40,
        "fatigue_burnout_pct": 30,
        "domestic_pressure_pct": 30,
        "coping_plan": ["Step 1", "Step 2", "Step 3"],
        "walk_prompt": "Walk prompt",
        "youtube_music_query": "Music",
        "youtube_strategy_query": "Strategy",
        "parent_guardrail": "Parent message",
        "friend_nudge": "Friend nudge",
        "burnout_score": 5,
        "dynamic_reset_exercise": "Reset",
        "motivational_nudge": "Motivation"
    }
    
    with pytest.raises(ValidationError):
        MindMateResponse(**invalid_payload)

def test_indian_meals_parsing():
    """
    Test that IndianMeals can be parsed independently.
    """
    meals_payload = {
        "breakfast": "Idli with sambar",
        "lunch": "Roti and paneer dal",
        "dinner": "Khichdi",
        "snack": "Walnuts",
        "avoid": "Excess tea"
    }
    
    meals = IndianMeals(**meals_payload)
    assert meals.breakfast == "Idli with sambar"
