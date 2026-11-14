
import os
import json
import re
from urllib.parse import urlparse

from dotenv import load_dotenv
from google import genai
from roadmap_model import Roadmap


# --------------------------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------------------------


# --------------------------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------------------------

import streamlit as st

load_dotenv()

# First read local .env, then Streamlit Cloud Secrets
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not API_KEY:
    try:
        API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        API_KEY = ""

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)



# --------------------------------------------------
# JSON EXTRACTION
# --------------------------------------------------

def extract_json(text):
    """
    Extract JSON even if Gemini adds Markdown code fences
    or explanatory text around the response.
    """

    if not text:
        raise ValueError("Gemini returned an empty response.")

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    # Try direct JSON parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the first JSON object in the response
    decoder = json.JSONDecoder()

    for index, character in enumerate(text):
        if character == "{":
            try:
                data, _ = decoder.raw_decode(text[index:])
                return data
            except json.JSONDecodeError:
                continue

    raise ValueError("Gemini did not return valid JSON.")


# --------------------------------------------------
# ROADMAP DATA VALIDATION
# --------------------------------------------------

def validate_roadmap_data(data):
    """
    Check the basic structure and normalize roadmap fields.
    """

    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object.")

    if not data.get("title"):
        raise ValueError("Roadmap title is missing.")

    # Keep compatibility with the existing PDF and dashboard.
    if not data.get("description"):
        data["description"] = data.get(
            "summary",
            "Your personalized learning roadmap."
        )

    if not data.get("summary"):
        data["summary"] = data["description"]

    weeks = data.get("weeks")

    if not isinstance(weeks, list):
        raise ValueError("Roadmap weeks are missing or invalid.")

    if len(weeks) != 8:
        raise ValueError(
            f"Expected 8 weeks, but AI generated {len(weeks)} weeks."
        )

    for index, week in enumerate(weeks, start=1):

        if not isinstance(week, dict):
            raise ValueError(f"Week {index} has an invalid format.")

        week["week_number"] = index

        week.setdefault("theme", f"Learning Week {index}")
        week.setdefault("learning_objectives", [])
        week.setdefault("topics", [])
        week.setdefault("practical_assignment", "")
        week.setdefault("mini_project", "")
        week.setdefault("resources", [])
        week.setdefault("career_tip", "")

        if not isinstance(week["topics"], list):
            raise ValueError(f"Topics in Week {index} must be a list.")

        if not week["topics"]:
            raise ValueError(f"No learning topics found in Week {index}.")

        if not isinstance(week["resources"], list):
            week["resources"] = []

        # Check resource URL format
        for resource in week["resources"]:
            if not isinstance(resource, dict):
                raise ValueError(
                    f"Invalid resource format in Week {index}."
                )

            url = resource.get("url", "")

            if url:
                parsed_url = urlparse(url)

                if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
                    resource["url"] = ""

            resource.setdefault("title", "Learning Resource")
            resource.setdefault("type", "Website")

    data["estimated_duration_weeks"] = 8

    return data


# --------------------------------------------------
# AI PROMPT
# --------------------------------------------------

def create_prompt(user_input):

    return f"""
You are an expert career mentor, professional educator,
and personalized learning roadmap planner.

Create a detailed and practical 8-week learning roadmap.

STUDENT INFORMATION:

Name: {user_input.get("full_name", "Student")}
Career Goal: {user_input.get("career_goal", "Not specified")}
Current Skill Level: {user_input.get("skill_level", "Beginner")}
Daily Study Time: {user_input.get("daily_time", "1 hour")}
Budget: {user_input.get("budget", "Free")}
Preferred Language: {user_input.get("preferred_language", "English")}

IMPORTANT INSTRUCTIONS:

1. Create exactly 8 weeks.
2. Customize the roadmap according to the student's career goal.
3. Start from the appropriate skill level.
4. Make every week progressively more advanced.
5. Include clear weekly learning objectives.
6. Include 3 to 5 learning topics per week.
7. Include one practical assignment per week.
8. Include one realistic mini-project per week.
9. Include useful learning resources.
10. Prefer official websites and trusted learning platforms.
11. Never invent URLs. If you are unsure of a URL, use an empty string.
12. Respect the student's budget. Prefer free resources for a free budget.
13. Make the plan realistic for the available daily study time.
14. Include one useful career tip per week.
15. Use the student's preferred language.
16. Avoid repeating the same topics across multiple weeks.
17. Make assignments practical, not just theoretical.

RETURN ONLY VALID JSON.

Use this exact structure:

{{
    "title": "Personalized Roadmap Title",
    "description": "Detailed roadmap overview",
    "summary": "Short roadmap summary",
    "estimated_duration_weeks": 8,
    "weeks": [
        {{
            "week_number": 1,
            "theme": "Weekly theme",
            "learning_objectives": [
                "Learning objective 1",
                "Learning objective 2"
            ],
            "topics": [
                "Topic 1",
                "Topic 2",
                "Topic 3"
            ],
            "practical_assignment": "Detailed practical assignment",
            "mini_project": "A practical mini project",
            "resources": [
                {{
                    "title": "Resource title",
                    "url": "https://example.com",
                    "type": "Course"
                }}
            ],
            "career_tip": "Useful career advice"
        }}
    ]
}}

The weeks array must contain exactly 8 week objects.
Do not include Markdown, explanations, or text outside the JSON.
"""


# --------------------------------------------------
# MAIN GEMINI AI FUNCTION
# --------------------------------------------------

def generate_roadmap(user_input: dict) -> dict:
    """
    Generate and validate a personalized roadmap using Gemini AI.
    """

    if not API_KEY:
        raise ValueError(
            "Gemini API key is missing. "
            "Please check GEMINI_API_KEY in your .env file."
        )

    if not isinstance(user_input, dict):
        raise ValueError("Invalid student information.")

    required_fields = [
        "career_goal",
        "skill_level",
        "daily_time",
        "budget"
    ]

    for field in required_fields:
        if not user_input.get(field):
            raise ValueError(
                f"Please provide the student's {field.replace('_', ' ')}."
            )

    client = genai.Client(api_key=API_KEY)

    prompt = create_prompt(user_input)

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            raise ValueError(
                "Gemini returned an empty response. Please try again."
            )

        # Extract JSON
        roadmap_data = extract_json(response.text)

        # Validate roadmap structure
        roadmap_data = validate_roadmap_data(roadmap_data)

        # Validate using the existing Pydantic model
        validated_roadmap = Roadmap.model_validate(roadmap_data)

        result = validated_roadmap.model_dump()

        # Preserve compatibility with the existing app and PDF.
        if not result.get("description"):
            result["description"] = roadmap_data["description"]

        if not result.get("summary"):
            result["summary"] = roadmap_data["summary"]

        result["estimated_duration_weeks"] = 8

        return result

    except json.JSONDecodeError as error:
        raise ValueError(
            "AI returned invalid JSON. Please try again."
        ) from error

    except ValueError:
        raise

    except Exception as error:

        error_message = str(error)
        error_lower = error_message.lower()

        if "503" in error_message or "unavailable" in error_lower:
            raise RuntimeError(
                "Gemini AI is temporarily busy. "
                "Please wait a little and try again."
            ) from error

        if "429" in error_message or "quota" in error_lower:
            raise RuntimeError(
                "Gemini API quota or rate limit reached. "
                "Please check your API usage and try again later."
            ) from error

        if "404" in error_message or "not found" in error_lower:
            raise RuntimeError(
                f"Gemini model '{MODEL_NAME}' was not found. "
                "Check the model name in your .env configuration."
            ) from error

        raise RuntimeError(
            f"Roadmap generation failed: {error_message}"
        ) from error
