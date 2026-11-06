"""
Image Analysis Service Layer
This module handles the integration with the YOLOv8 object detection model.
In our MVC architecture, this service acts as a bridge between the Controller (which handles the image upload)
and the deep learning model. I chose the Singleton pattern for the model loading so that we don't reload 
the heavy PyTorch weights into memory every time a user uploads a photo, which would be very slow.
"""
import os
import json
from flask import current_app
from PIL import Image

# Global variables to cache the model and database (Singleton-like behavior)
_classifier = None
_nutrition_db = None

class ImageAnalysisService:
    @staticmethod
    def _load_resources():
        """
        Lazy-loads the YOLO model and the nutrition JSON database.
        We only load them the first time an image is analyzed to save startup time.
        """
        global _classifier, _nutrition_db
        
        # Load the custom YOLOv8 model if not already in memory
        if _classifier is None:
            print("Loading custom YOLOv8 Vision Model...")
            from ultralytics import YOLO
            
            # Construct the absolute path to our trained weights (best.pt)
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runs', 'detect', 'runs', 'detect', 'food_model_merged', 'weights', 'best.pt')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Custom YOLO model not found at {model_path}. Please train it first.")
                
            _classifier = YOLO(model_path)
            print("YOLO Model loaded successfully.")
            
        # Load the nutrition database JSON file
        if _nutrition_db is None:
            db_path = os.path.join(current_app.root_path, 'data', 'nutrition_db.json')
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    _nutrition_db = json.load(f)
            except Exception as e:
                print(f"Error loading nutrition DB: {e}")
                _nutrition_db = {} # Fallback to empty dict to prevent app crashes

    @staticmethod
    def analyze_meal_image(image_path):
        """
        Takes the relative path of an uploaded image, passes it through YOLOv8,
        and calculates the total calories and macronutrients by mapping detected classes
        to our nutrition database.
        
        Returns:
            tuple: (success_boolean, result_dictionary_or_error_message)
        """
        try:
            # Resolve the absolute path of the uploaded file
            absolute_path = os.path.join(current_app.static_folder, image_path)
            if not os.path.exists(absolute_path):
                return False, f"Image not found at {absolute_path}"

            # Ensure model and DB are loaded
            ImageAnalysisService._load_resources()
            
            # Execute inference (forward pass through the neural network)
            results = _classifier(absolute_path)
            
            predictions = []
            # Extract bounding boxes, class names, and confidence scores
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = r.names[cls_id]
                    predictions.append({"label": class_name, "score": conf})

            # If YOLO didn't detect any food objects above the confidence threshold
            if not predictions:
                return False, "Could not classify image. No food detected."
                
            detected_names = []
            total_cals = 0.0
            total_protein = 0.0
            total_carbs = 0.0
            total_fat = 0.0
            
            # Loop through all detected food items and aggregate their nutritional values
            for p in predictions:
                # Format the label to match our JSON keys (e.g., "Greek Salad" -> "greek_salad")
                label = p['label'].lower().replace(' ', '_')
                
                # Fetch nutritional data, using a default fallback (250 kcal) if the food is not in the DB
                db_entry = _nutrition_db.get(label, {
                    "calories": 250.0,
                    "protein": 10.0,
                    "carbs": 30.0,
                    "fat": 10.0,
                    "friendly_name": p['label'].capitalize()
                })
                
                detected_names.append(db_entry.get("friendly_name", p['label'].capitalize()))
                total_cals += db_entry.get("calories", 250.0)
                total_protein += db_entry.get("protein", 10.0)
                total_carbs += db_entry.get("carbs", 30.0)
                total_fat += db_entry.get("fat", 10.0)
            
            # Group identical items for a cleaner UI display (e.g., "Apple, Apple" -> "Apple x2")
            from collections import Counter
            name_counts = Counter(detected_names)
            final_name_parts = []
            
            for name, count in name_counts.items():
                if count > 1:
                    final_name_parts.append(f"{name} x{count}")
                else:
                    final_name_parts.append(name)
                    
            final_name = ", ".join(final_name_parts)
            
            # Construct the final result dictionary to return to the Controller
            result = {
                "detected_food_name": final_name,
                "estimated_calories": total_cals,
                "protein": total_protein,
                "carbs": total_carbs,
                "fat": total_fat,
                "confidence": round(predictions[0]['score'], 2), # Using the confidence of the first object
                "explanation": f"Custom YOLO model detected: {final_name}."
            }
            
            return True, result

        except Exception as e:
            # Catch and log any exceptions (e.g., out of memory errors) to prevent server crashes
            import traceback
            traceback.print_exc()
            return False, str(e)

