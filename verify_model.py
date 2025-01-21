from joblib import load
import os

def verify_model():
    model_path = 'model/crop_pred.pkl'
    
    # Check if directory exists
    if not os.path.exists('model'):
        print("Error: 'model' directory not found")
        return
        
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return
        
    try:
        model = load(model_path)
            
        print(f"Model file loaded successfully")
        print(f"Model type: {type(model)}")
        
        if hasattr(model, 'predict'):
            print("✓ Model has predict method")
            print(f"Model class: {model.__class__.__name__}")
        else:
            print("✗ Model does not have predict method")
            
    except Exception as e:
        print(f"Error loading model: {e}")

if __name__ == "__main__":
    verify_model() 