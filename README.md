# Farmer Decision Support System

A web application to help farmers make informed decisions about crop selection based on soil parameters and weather conditions.

## Features

- Crop prediction based on soil parameters and weather conditions
- Real-time weather data integration
- Interactive map interface
- User authentication system
- Dashboard with weather updates and crop information

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

1. Clone the repository:

2. Create and activate a virtual environment

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `config.py` file in the root directory with your API credentials:
```python
METEOMATICS_USERNAME = "your_username"
METEOMATICS_PASSWORD = "your_password"
METEOMATICS_BASE_URL = "https://api.meteomatics.com"
```


## Running the Application

1. Ensure your virtual environment is activated

2. Start the Flask application:
```bash
python app.py
```

3. Access the application in your web browser:
```
http://localhost:8080
```

## Project Structure

```
farmer-dss/
├── app.py              # Main Flask application
├── config.py           # Configuration file (not in version control)
├── requirements.txt    # Python dependencies
├── model/
│   └── crop_pred.pkl  # Trained model file
├── templates/         # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── crop_prediction.html
└── utils/
    └── weather.py    # Weather data utilities
```

## Usage

1. Log in to the system
2. Navigate to the Crop Prediction tool
3. Enter soil parameters:
   - Nitrogen content (0-140)
   - Phosphorus content (0-145)
   - Potassium content (0-205)
   - pH value (0-14)
4. Select location on the map
5. Submit for crop recommendations

## Notes

- The model expects specific ranges for input parameters
- Weather data is fetched in real-time for the selected location
- Ensure you have valid API credentials in config.py

## Troubleshooting

If you encounter any issues:

1. Verify your Python version:
```bash
python --version
```

2. Check if all requirements are installed:
```bash
pip list
```

3. Ensure the model file exists in the correct location
4. Verify your API credentials in config.py
```

This README provides:
1. Clear installation instructions
2. Project structure overview
3. Usage guidelines
4. Troubleshooting steps
5. All necessary prerequisites

Let me know if you need any clarification or additional sections in the README!
