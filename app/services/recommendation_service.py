"""
Recommendation Service

Generates personalized fitness and diet recommendations.
"""

from app.extensions import db
from app.models.recommendation import SavedRecommendation
from app.services.profile_service import ProfileService
from app.services.bmi_service import BMIService
from app.services.calorie_service import CalorieService
from app.services.progress_service import ProgressService

from app.ml.predictors.workout_predictor import WorkoutPredictor
from app.ml.predictors.diet_predictor import DietPredictor

# Lazy initialization of ML predictors
_workout_predictor = None
_diet_predictor = None


def get_workout_predictor():
    global _workout_predictor
    if _workout_predictor is None:
        try:
            _workout_predictor = WorkoutPredictor()
        except Exception:
            _workout_predictor = None
    return _workout_predictor


def get_diet_predictor():
    global _diet_predictor
    if _diet_predictor is None:
        try:
            _diet_predictor = DietPredictor()
        except Exception:
            _diet_predictor = None
    return _diet_predictor


class RecommendationService:
    """
    Generates personalized workout and diet recommendations.
    """

    # =====================================================
    # Generate Recommendation
    # =====================================================

    @staticmethod
    def generate_ai_recommendation(profile, nutrition, bmi):
        import os
        import urllib.request
        import json

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.5-flash:generateContent?key={api_key}"

        prompt = f"""
        You are an expert AI fitness coach and clinical nutritionist.
        Generate a personalized fitness recommendation for a user with the following profile:
        - Age: {profile.age}
        - Gender: {profile.gender.value if hasattr(profile.gender, 'value') else profile.gender}
        - Height: {profile.height_cm} cm
        - Weight: {profile.weight_kg} kg (BMI: {bmi})
        - Fitness Goal: {profile.goal.value if hasattr(profile.goal, 'value') else profile.goal}
        - Activity Level: {profile.activity_level.value if hasattr(profile.activity_level, 'value') else profile.activity_level}
        - Workout Hours: {profile.workout_hours} hrs/day
        - Sleep Hours: {profile.sleep_hours} hrs/day
        - Daily Steps: {profile.daily_steps}
        - Dietary Preference: {profile.dietary_preference}
        - Medical Conditions: {profile.medical_conditions}

        Provide:
        1. A realistic and medically safe program duration (in weeks/months).
        2. A structured workout schedule and frequency details.
        3. A Personalized Workout Plan (list of strings representing specific exercises, target muscle groups, sets/reps).
        4. A Personalized Meal Plan categorized into breakfast, lunch, and dinner. For each category, suggest healthy, realistic food items with serving size, calories, protein, carbs, and fats.
        5. A flat list of general fitness/nutrition tips.
        6. A motivational note or advice.

        Ensure the duration and recommendations are realistic and medically safe. Do not recommend extreme weight loss or unsafe diets. If the user has any medical conditions, modify the duration and recommendations accordingly.

        You must respond ONLY with a raw JSON object containing these keys:
        {{
          "program_duration": {{
            "duration": "8 weeks",
            "review_after": "2 weeks",
            "reason": "An 8-week program provides enough time for gradual, sustainable progress.",
            "expected_result": "Lose approximately 4–6 kg while improving overall fitness."
          }},
          "plan_schedule": {{
            "total_duration": "8 weeks",
            "workout_frequency": "4 days per week",
            "diet_frequency": "7 days per week",
            "rest_days": "3 days per week",
            "review_after": "Every 2 weeks",
            "expected_result": "Lose 4-6 kg safely while maintaining muscle mass.",
            "note": "Results may vary depending on consistency and individual metabolic factors."
          }},
          "workout_plan": [
            "Cardio: 30 min brisk walk (General)",
            "Strength: Push-ups - 3 sets x 10 reps (Chest)",
            "Strength: Bodyweight Squats - 3 sets x 15 reps (Legs)"
          ],
          "diet_plan": {{
            "breakfast": [
              {{
                "name": "Oatmeal with banana & almond butter",
                "serving": "1 bowl",
                "calories": 350,
                "protein": 10.0,
                "carbs": 55.0,
                "fat": 8.0
              }}
            ],
            "lunch": [
              {{
                "name": "Grilled chicken breast with brown rice & broccoli",
                "serving": "150g chicken, 1 cup rice",
                "calories": 500,
                "protein": 40.0,
                "carbs": 50.0,
                "fat": 6.0
              }}
            ],
            "dinner": [
              {{
                "name": "Baked salmon with quinoa & mixed greens",
                "serving": "150g salmon, 1 cup quinoa",
                "calories": 450,
                "protein": 35.0,
                "carbs": 40.0,
                "fat": 12.0
              }}
            ],
            "plan": [
              "Drink at least 3.0 L water daily.",
              "Limit added sugar intake."
            ]
          }},
          "tips": [
            "Drink at least 3.0 L water daily.",
            "Prioritize protein source in every meal."
          ],
          "motivation": "Keep pushing forward! Consistency is the bridge between goals and accomplishment."
        }}
        """

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        import urllib.error
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                text_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
                cleaned_text = text_response.strip()
                if cleaned_text.startswith("```"):
                    lines = cleaned_text.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    cleaned_text = "\n".join(lines).strip()
                return json.loads(cleaned_text)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", error_body)
            except Exception:
                error_msg = error_body
            raise ValueError(f"Gemini API returned an error ({e.code}): {error_msg}")
        except Exception as e:
            raise ValueError(f"Failed to communicate with Gemini API: {e}")

    @classmethod
    def generate(cls, user_id):
        """
        Generate recommendation for a user.
        """

        profile = ProfileService.get_profile(user_id)

        if not profile:
            return None

        latest_progress = ProgressService.latest(user_id)

        current_weight = (
            latest_progress.weight_kg
            if latest_progress
            else profile.weight_kg
        )

        # ---------------------------------------------
        # BMI
        # ---------------------------------------------

        bmi = BMIService.calculate(
            current_weight,
            profile.height_cm
        )

        # ---------------------------------------------
        # Nutrition Report
        # ---------------------------------------------

        nutrition = CalorieService.nutrition_report(
            profile
        )

        # ---------------------------------------------
        # Generate Recommendations via Gemini AI Only
        # ---------------------------------------------
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from your .env file. "
                "Please add GEMINI_API_KEY=your_api_key to enable AI recommendations."
            )

        ai_rec = cls.generate_ai_recommendation(profile, nutrition, bmi)

        if not ai_rec:
            raise ValueError(
                "Gemini AI API failed to generate recommendations. "
                "Please check your network connection and verify that your GEMINI_API_KEY is valid."
            )

        workout = ai_rec.get("workout_plan", [])
        diet = ai_rec.get("diet_plan", {"plan": []})
        program_duration = ai_rec.get("program_duration", {})
        plan_schedule = ai_rec.get("plan_schedule", {})
        tips = ai_rec.get("tips", [])
        motivation = ai_rec.get("motivation", "")

        # Backward compatibility for tips
        if "plan" not in diet or not diet["plan"]:
            diet["plan"] = tips if tips else []

        # ---------------------------------------------
        # Save Recommendation
        # ---------------------------------------------

        recommendation = SavedRecommendation(

            user_id=user_id,

            workout_plan={
                "plan": workout,
                "program_duration": program_duration,
                "plan_schedule": plan_schedule,
                "tips": tips,
                "motivation": motivation
            },

            diet_plan=diet,  # diet is already structured as a dictionary

            daily_calories=nutrition["target_calories"],

            protein_g=nutrition["protein_g"],

            carbs_g=nutrition["carbs_g"],

            fats_g=nutrition["fat_g"]

        )

        db.session.add(recommendation)
        db.session.commit()

        return recommendation

    # =====================================================
    # Workout Recommendation
    # =====================================================

    @staticmethod
    def workout_plan(profile, bmi):
        """
        Generate personalized workout plan.
        """

        workout = []
        goal = profile.goal.value.lower()

        # ---------------------------------------------
        # Goal Based Workout (Rule-based Guidelines)
        # ---------------------------------------------

        if "lose" in goal:

            workout.extend([
                "45 min Cardio",
                "30 min Strength Training",
                "10,000 Daily Steps"
            ])

        elif "gain" in goal:

            workout.extend([
                "60 min Weight Training",
                "Compound Exercises",
                "Progressive Overload"
            ])

        else:

            workout.extend([
                "30 min Mixed Workout",
                "Strength + Cardio",
                "Flexibility Training"
            ])

        # ---------------------------------------------
        # BMI Recommendation
        # ---------------------------------------------

        if bmi >= 30:

            workout.append(
                "Prefer Low Impact Exercises (Walking/Cycling)"
            )

        elif bmi < 18.5:

            workout.append(
                "Focus on Muscle Building Exercises"
            )

        # ---------------------------------------------
        # Workout Hours
        # ---------------------------------------------

        if profile.workout_hours < 1:

            workout.append(
                "Increase workout duration gradually."
            )

        elif profile.workout_hours > 2:

            workout.append(
                "Ensure adequate recovery between sessions."
            )

        # ---------------------------------------------
        # Daily Steps
        # ---------------------------------------------

        if profile.daily_steps < 5000:

            workout.append(
                "Increase daily walking activity."
            )

        elif profile.daily_steps >= 10000:

            workout.append(
                "Excellent daily activity level."
            )

        # ---------------------------------------------
        # Sleep
        # ---------------------------------------------

        if profile.sleep_hours < 7:

            workout.append(
                "Improve sleep to support muscle recovery."
            )

        # ---------------------------------------------
        # Medical Conditions
        # ---------------------------------------------

        if (
            profile.medical_conditions
            and profile.medical_conditions.lower() != "none"
        ):

            workout.append(
                f"Exercise with caution due to: {profile.medical_conditions}."
            )

        # ---------------------------------------------
        # ML Recommended Specific Exercises
        # ---------------------------------------------
        wp = get_workout_predictor()
        if wp is not None:
            try:
                ml_workouts = wp.recommend_workouts(profile, limit=4)
                if ml_workouts:
                    workout.append("--- ML Recommended Specific Workouts ---")
                    workout.extend(ml_workouts)
            except Exception as e:
                print(f"ML workout recommendation failed: {e}")

        return workout

    # =====================================================
    # Diet Recommendation
    # =====================================================

    @staticmethod
    def diet_plan(profile, nutrition):
        """
        Generate personalized diet plan.
        """

        # Try to use ML Predictor
        dp = get_diet_predictor()
        if dp is not None:
            try:
                ml_diet = dp.recommend_meals(profile, nutrition, limit=3)
                
                # Add general tips to the flat plan list
                pref_text = f"Dietary Preference: {profile.dietary_preference}"
                water_text = f"Drink at least {nutrition['water_liters']} L water daily."
                ml_diet["plan"] = [pref_text, water_text] + ml_diet["plan"]
                
                if (
                    profile.medical_conditions
                    and profile.medical_conditions.lower() != "none"
                ):
                    ml_diet["plan"].append(
                        f"Consult your healthcare provider regarding your diet because of: {profile.medical_conditions}."
                    )
                return ml_diet
            except Exception as e:
                print(f"ML diet recommendation failed: {e}")

        # Fallback to Rule-based Diet Plan
        diet = []
        goal = profile.goal.value.lower()

        # ---------------------------------------------
        # Goal Based Diet
        # ---------------------------------------------

        if "lose" in goal:

            diet.extend([
                "High Protein Meals",
                "Low Sugar Intake",
                "High Fiber Vegetables",
                "Healthy Fats"
            ])

        elif "gain" in goal:

            diet.extend([
                "High Protein Meals",
                "Complex Carbohydrates",
                "Calorie Surplus Diet",
                "Healthy Snacks"
            ])

        else:

            diet.extend([
                "Balanced Diet",
                "Whole Grains",
                "Lean Protein",
                "Fresh Fruits & Vegetables"
            ])

        # ---------------------------------------------
        # Dietary Preference
        # ---------------------------------------------

        preference = profile.dietary_preference.lower()

        if preference == "vegetarian":

            diet.append(
                "Protein Sources: Paneer, Milk, Soybean, Lentils"
            )

        elif preference == "non-vegetarian":

            diet.append(
                "Protein Sources: Chicken, Eggs, Fish"
            )

        elif preference == "vegan":

            diet.append(
                "Protein Sources: Tofu, Soy Milk, Chickpeas"
            )

        elif preference == "eggetarian":

            diet.append(
                "Protein Sources: Eggs, Paneer, Lentils"
            )

        elif preference == "jain":

            diet.append(
                "Follow Jain dietary guidelines with high-protein alternatives."
            )

        # ---------------------------------------------
        # Water Intake
        # ---------------------------------------------

        diet.append(
            f"Drink at least {nutrition['water_liters']} L water daily."
        )

        # ---------------------------------------------
        # Calories
        # ---------------------------------------------

        diet.append(
            f"Daily Calories: {nutrition['target_calories']} kcal"
        )

        # ---------------------------------------------
        # Macronutrients
        # ---------------------------------------------

        diet.append(
            f"Protein: {nutrition['protein_g']} g/day"
        )

        diet.append(
            f"Carbohydrates: {nutrition['carbs_g']} g/day"
        )

        diet.append(
            f"Healthy Fats: {nutrition['fat_g']} g/day"
        )

        # ---------------------------------------------
        # Medical Conditions
        # ---------------------------------------------

        if (
            profile.medical_conditions
            and profile.medical_conditions.lower() != "none"
        ):

            diet.append(
                f"Consult your healthcare provider regarding your diet because of: {profile.medical_conditions}."
            )

        return {"plan": diet}

    # =====================================================
    # Latest Recommendation
    # =====================================================

    @staticmethod
    def latest(user_id):
        """
        Return the latest recommendation for a user.
        """

        return (
            SavedRecommendation.query
            .filter_by(user_id=user_id)
            .order_by(
                SavedRecommendation.generated_at.desc()
            )
            .first()
        )