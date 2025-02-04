# Farmer's Decision Support System

A web-based application that helps farmers make informed decisions about crop selection based on soil parameters and local weather conditions.

## Features

- Soil parameter analysis (N, P, K, pH levels)
- Real-time weather data integration
- Interactive map for location selection
- ML-based crop recommendations
- Detailed crop information dashboard
- Historical prediction tracking

## Tech Stack

- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite/PostgreSQL
- **APIs**: OpenWeatherMap, OpenStreetMap
- **ML**: scikit-learn

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/FarmerDSS.git
cd FarmerDSS
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file:
```bash
touch .env
```
Add the following environment variables:
```
WEATHER_API_KEY=your_api_key
DATABASE_URL=your_database_url
FLASK_SECRET_KEY=your_secret_key
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Usage

1. Start the development server:
```bash
flask run
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## API Documentation

### Weather API
- Endpoint: `/update_weather`
- Method: GET
- Parameters: 
  - lat (float): Latitude
  - lon (float): Longitude
- Response: Weather data including temperature, humidity, and rainfall

### Prediction API
- Endpoint: `/crop_prediction/predict`
- Method: POST
- Parameters:
  - nitrogen (float)
  - phosphorus (float)
  - potassium (float)
  - ph (float)
  - latitude (float)
  - longitude (float)
- Response: Top crop recommendations with confidence scores

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security

- API keys and sensitive data are stored in environment variables
- Input validation implemented for all form submissions
- SQL injection prevention through parameterized queries
- XSS protection implemented
- CSRF protection enabled

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

- OpenWeatherMap API for weather data
- OpenStreetMap for map services
- Tailwind CSS for styling
- Flask community for the excellent framework
