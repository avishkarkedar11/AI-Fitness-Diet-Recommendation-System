"""
Train Diet Recommendation Model

Cleans the raw diet dataset, classifies foods into dietary preferences (vegan, vegetarian, 
eggetarian, non-vegetarian) and meal categories (breakfast, lunch/dinner, snack), and fits 
a MinMaxScaler for content-based similarity matching.
"""

from pathlib import Path
import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from app.ml.preprocessing import DataPreprocessor


class DietModelTrainer:
    """
    Handles diet recommendation data preprocessing and model setup.
    """

    PROCESSED_NAME = "diet_processed.csv"
    SCALER_NAME = "diet_scaler.pkl"

    @classmethod
    def classify_diet_type(cls, name: str) -> str:
        name_lower = name.lower()
        
        non_veg = [
            "chicken", "beef", "pork", "fish", "lamb", "turkey", "shrimp", "seafood", 
            "duck", "bacon", "crab", "lobster", "salmon", "tuna", "steak", "meat", 
            "sausage", "pepperoni", "gelatin", "veal", "anchovy", "sardine", "oyster", 
            "mussel", "mutton", "ham", "prawn", "venison", "salami"
        ]
        for nv in non_veg:
            if nv in name_lower:
                return "non-vegetarian"
                
        # Check for egg, excluding eggplant and eggnog (eggnog has dairy/egg, which fits eggetarian)
        if "egg" in name_lower and "eggplant" not in name_lower:
            return "eggetarian"
            
        dairy_honey = [
            "cheese", "milk", "butter", "cream", "yogurt", "whey", "honey", "ghee", 
            "paneer", "curd", "mayonnaise", "custard", "pudding"
        ]
        for d in dairy_honey:
            if d in name_lower:
                return "vegetarian"
                
        return "vegan"

    @classmethod
    def classify_meal_time(cls, name: str) -> str:
        name_lower = name.lower()
        
        breakfast_kw = [
            "cereal", "oats", "oatmeal", "porridge", "toast", "egg", "pancake", "waffle", 
            "muffin", "yogurt", "milk", "fruit", "juice", "cornstarch", "pecan", "nut", 
            "berry", "banana", "apple", "orange", "grape", "honey", "syrup", "bread",
            "flakes", "muesli", "granola", "smoothie", "croissant"
        ]
        
        dinner_kw = [
            "beef", "steak", "pork", "lamb", "mutton", "fish", "salmon", "tuna", "shrimp",
            "crab", "lobster", "veal", "chicken", "turkey", "duck", "curry", "rice", 
            "pasta", "spaghetti", "noodle", "potato", "stew", "soup", "lentil", "bean",
            "tofu", "tempeh", "paneer", "vegetables", "salad", "roast", "baked", "grilled",
            "steak", "burger", "pizza", "taco", "tortilla", "chili", "sauce"
        ]
        
        if any(kw in name_lower for kw in breakfast_kw):
            return "breakfast"
        elif any(kw in name_lower for kw in dinner_kw):
            return "lunch/dinner"
        else:
            return "snack"

    @classmethod
    def train(cls):
        print("=" * 60)
        print("Preprocessing raw diet dataset...")
        print("=" * 60)

        # Apply basic preprocessing
        DataPreprocessor.preprocess("diet.csv", "diet_processed_temp.csv")
        
        processed_dir = Path(__file__).resolve().parent.parent / "datasets" / "processed"
        df = pd.read_csv(processed_dir / "diet_processed_temp.csv")

        # Clean nutritional columns with units
        # Stripping trailing/leading whitespaces and removing 'g'
        def clean_nutrient(val):
            if pd.isna(val):
                return 0.0
            val_str = str(val).lower().replace("g", "").replace(" ", "").strip()
            try:
                return float(val_str)
            except ValueError:
                return 0.0

        for col in ["total_fat", "protein", "carbohydrate"]:
            df[col] = df[col].apply(clean_nutrient)

        # Convert calories to float
        df["calories"] = pd.to_numeric(df["calories"], errors="coerce").fillna(0.0)

        # Categorize foods
        df["diet_type"] = df["name"].apply(cls.classify_diet_type)
        df["meal_time"] = df["name"].apply(cls.classify_meal_time)

        # Root vegetable categorization for Jain diets
        root_veggies = [
            "potato", "onion", "garlic", "carrot", "radish", "turnip", "beet", 
            "sweet potato", "ginger", "yam", "tapioca", "cassava", "taro"
        ]
        df["is_root_veg"] = df["name"].apply(
            lambda name: any(rv in str(name).lower() for rv in root_veggies)
        )
        df["is_jain"] = (df["diet_type"].isin(["vegetarian", "vegan"])) & (~df["is_root_veg"])

        # Fit a scaler on calories, protein, carbs, fat
        scaler = MinMaxScaler()
        features = df[["calories", "protein", "carbohydrate", "total_fat"]]
        scaler.fit(features)

        # Save the scaler and preprocessed dataset
        model_dir = Path(__file__).resolve().parent.parent / "trained_models"
        model_dir.mkdir(exist_ok=True)
        joblib.dump(scaler, model_dir / cls.SCALER_NAME)
        print("Saved MinMaxScaler for diet items.")

        output_path = processed_dir / cls.PROCESSED_NAME
        df.to_csv(output_path, index=False)
        print(f"Saved processed diet dataset at: {output_path}")

        # Clean up temp file
        temp_file = processed_dir / "diet_processed_temp.csv"
        if temp_file.exists():
            temp_file.unlink()

        print("=" * 60)


if __name__ == "__main__":
    DietModelTrainer.train()
