"""
CLI Script to train all AI models for the Fitness & Diet Recommendation System.
"""

import sys
from app import create_app
from app.ml.recommendation_engine import RecommendationEngine

def main():
    # Load Flask app context so extensions/database connection is available if needed
    app = create_app()
    with app.app_context():
        try:
            RecommendationEngine.train_all_models()
        except Exception as e:
            print(f"\n❌ Error during model training: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
