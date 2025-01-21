import pickle

try:
    # Load the model
    with open('model/crop_pred.pkl', 'rb') as f:
        model_data = pickle.load(f)
        
    print("Model loaded successfully!")
    if isinstance(model_data, dict):
        print("Available model components:", model_data.keys())
    else:
        print("Model type:", type(model_data))
        
except FileNotFoundError:
    print("Error: crop_prediction_model.pkl not found in the model directory")
except Exception as e:
    print(f"Error loading model: {e}") 