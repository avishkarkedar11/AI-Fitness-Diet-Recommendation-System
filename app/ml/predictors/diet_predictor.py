"""
Diet Predictor

Loads preprocessed diet data and the min-max scaler, and recommends 
breakfast, lunch, and dinner options using content-based filtering (cosine similarity).
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class DietPredictor:
    """
    Content-Based filtering diet recommender using Cosine Similarity.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_DIR = BASE_DIR / "trained_models"
    SCALER_PATH = MODEL_DIR / "diet_scaler.pkl"
    DATA_PATH = BASE_DIR / "datasets" / "processed" / "diet_processed.csv"

    def __init__(self):
        # Load scaler
        self.scaler = joblib.load(self.SCALER_PATH)
        
        # Load processed diet database
        if self.DATA_PATH.exists():
            self.diet_df = pd.read_csv(self.DATA_PATH)
        else:
            self.diet_df = None

    def recommend_meals(self, profile, nutrition_targets, limit=3) -> dict:
        """
        Recommend customized breakfast, lunch, and dinner options.
        """
        if self.diet_df is None:
            return {
                "breakfast": ["No diet database available."],
                "lunch": ["No diet database available."],
                "dinner": ["No diet database available."],
                "plan": ["No diet database available."]
            }

        pref = profile.dietary_preference.lower()

        # ---------------------------------------------
        # Step 1: Filter by dietary preference
        # ---------------------------------------------
        candidates = self.diet_df.copy()

        if pref == "vegan":
            candidates = candidates[candidates["diet_type"] == "vegan"]
        elif pref == "vegetarian":
            candidates = candidates[candidates["diet_type"].isin(["vegetarian", "vegan"])]
        elif pref == "eggetarian":
            candidates = candidates[candidates["diet_type"].isin(["eggetarian", "vegetarian", "vegan"])]
        elif pref == "jain":
            candidates = candidates[candidates["is_jain"] == True]
        # 'non-vegetarian' accepts all items

        if candidates.empty:
            candidates = self.diet_df.copy()

        # ---------------------------------------------
        # Step 2: Separate by meal time categories
        # ---------------------------------------------
        breakfast_candidates = candidates[candidates["meal_time"] == "breakfast"].copy()
        lunch_dinner_candidates = candidates[candidates["meal_time"] == "lunch/dinner"].copy()
        
        # Fallbacks if a category is empty
        if breakfast_candidates.empty:
            breakfast_candidates = candidates.copy()
        if lunch_dinner_candidates.empty:
            lunch_dinner_candidates = candidates.copy()

        # ---------------------------------------------
        # Step 3: Set macro/calorie target splits
        # ---------------------------------------------
        total_cal = nutrition_targets["target_calories"]
        total_prot = nutrition_targets["protein_g"]
        total_carb = nutrition_targets["carbs_g"]
        total_fat = nutrition_targets["fat_g"]

        # Meal targets: Breakfast (30%), Lunch (40%), Dinner (30%)
        meal_targets = {
            "breakfast": (breakfast_candidates, [total_cal * 0.3, total_prot * 0.3, total_carb * 0.3, total_fat * 0.3]),
            "lunch": (lunch_dinner_candidates, [total_cal * 0.4, total_prot * 0.4, total_carb * 0.4, total_fat * 0.4]),
            "dinner": (lunch_dinner_candidates, [total_cal * 0.3, total_prot * 0.3, total_carb * 0.3, total_fat * 0.3])
        }

        recommendations = {}

        # ---------------------------------------------
        # Step 4: Calculate cosine similarity for each meal type
        # ---------------------------------------------
        for meal_name, (meal_df, target_vector) in meal_targets.items():
            features = meal_df[["calories", "protein", "carbohydrate", "total_fat"]]
            
            # Scale features and target
            scaled_features = self.scaler.transform(features)
            scaled_target = self.scaler.transform([target_vector])

            # Calculate cosine similarities
            similarities = cosine_similarity(scaled_features, scaled_target).flatten()
            
            # Add similarity scores to temp column
            meal_df = meal_df.copy()
            meal_df["similarity"] = similarities

            # Sort and take top items
            top_items = meal_df.sort_values(by="similarity", ascending=False).head(limit)

            meal_list = []
            for _, row in top_items.iterrows():
                serving = row["serving_size"] if pd.notna(row["serving_size"]) else "100 g"
                cals = int(row["calories"])
                p = float(row["protein"])
                c = float(row["carbohydrate"])
                f = float(row["total_fat"])
                
                meal_list.append({
                    "name": str(row["name"]),
                    "serving": str(serving),
                    "calories": cals,
                    "protein": p,
                    "carbs": c,
                    "fat": f
                })

            recommendations[meal_name] = meal_list

        # Flat plan format for backward compatibility
        flat_plan = [
            f"Breakfast: {recommendations['breakfast'][0]['name']} & {recommendations['breakfast'][1]['name']}",
            f"Lunch: {recommendations['lunch'][0]['name']} & {recommendations['lunch'][1]['name']}",
            f"Dinner: {recommendations['dinner'][0]['name']} & {recommendations['dinner'][1]['name']}"
        ]
        
        recommendations["plan"] = flat_plan

        return recommendations
