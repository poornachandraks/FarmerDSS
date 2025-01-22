# Farmer Decision Support System

## Overview

The Farmer Decision Support System (FDSS) is a web application designed to assist farmers in making informed decisions regarding crop selection, market trends, and weather conditions. The application utilizes machine learning models to predict suitable crops based on soil parameters and provides insights into market trends.

## Project Structure

```
/your_project
│
├── /data
│   ├── Best_Values.csv
│   └── market_trends.csv
│
├── app.py
├── config.py
├── database.py
├── generate_market_data.py
├── requirements.txt
├── README.md
├── .gitignore
├── utils/
│   └── weather.py
├── verify_model.py
├── train_model.py
└── templates/
    ├── base.html
    ├── crop_prediction.html
    └── dashboard.html
```

## Setup Instructions

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a configuration file**:
   - Create a `config.py` file in the root directory with your API credentials and other settings:
   ```python
   METEOMATICS_USERNAME = "your_username"
   METEOMATICS_PASSWORD = "your_password"
   METEOMATICS_BASE_URL = "https://api.meteomatics.com"
   ```
   - Head over to https://www.meteomatics.com/en/weather-api/weather-api-free/ to sign up for a Meteomatics account.

4. **Set up the database**:
   - Run the `database.py` script to create the database and populate it with initial data:
   ```bash
   python database.py
   ```

5. **Generate market trends data** (optional):
   - If you want to generate or refresh the market trends data, run the `generate_market_data.py` script:
   ```bash
   python generate_market_data.py
   ```

6. **Run the application**:
   - Start the Flask web server by running the `app.py` script:
   ```bash
   python app.py
   ```

7. **Access the application**:
   - Open your web browser and navigate to `http://127.0.0.1:8080` to access the application.

## Features

- **Crop Prediction**: Input soil parameters to receive crop recommendations.
- **Market Trends**: View historical market trends for various crops.
- **Weather Data**: Fetch and display current weather conditions based on location.
- **User Management**: Admin functionality for managing user accounts and crop data.

## File Descriptions

- **`data/`**: Contains CSV files for crop data and market trends.
- **`app.py`**: Main application file that runs the Flask server.
- **`config.py`**: Configuration settings for the application, including API credentials for weather data.
- **`database.py`**: Initializes the SQLite database and populates it with data.
- **`generate_market_data.py`**: Generates market trends data and saves it to a CSV file.
- **`requirements.txt`**: Lists the required Python packages for the project.
- **`.gitignore`**: Specifies files and directories that should be ignored by Git.
- **`utils/weather.py`**: Utility functions for fetching weather data.
- **`verify_model.py`**: Script for verifying machine learning models.
- **`train_model.py`**: Script for training machine learning models.
- **`templates/`**: Contains HTML templates for the web application, including:
  - **`base.html`**: Base template for the application layout.
  - **`crop_prediction.html`**: Template for the crop prediction page.
  - **`dashboard.html`**: Template for the dashboard displaying market trends and crop information.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
