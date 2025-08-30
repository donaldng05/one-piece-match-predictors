# ⚔️ One Piece Match Predictor

A machine learning-powered web application that predicts fight outcomes between One Piece characters using their combat statistics and abilities.

![One Piece Banner](https://wallpapers.com/images/hd/one-piece-pfp-banner-kodi78blaifijuwv.jpg)

## 🌟 Features

- **⚔️ Fight Prediction**: Predict outcomes between any 2 One Piece characters in the top 100 One Piece Popularity Poll in 2021
- **🤖 ML-Powered**: Uses Support Vector Machine with 96.26% accuracy
- **📊 Character Database**: 100+ One Piece characters with detailed combat stats
- **🎨 Interactive UI**: Streamlit web interface
- **🚀 Real-time API**: FastAPI backend deployed on Railway
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🎯 Live Demo

- **🌐 Web App**: [One Piece Match Predictor](https://one-piece-match-predictors.streamlit.app/)
- **🔗 API Docs**: [FastAPI Documentation](https://one-piece-match-predictors-production.up.railway.app/docs)
- **❤️ Health Check**: [API Status](https://one-piece-match-predictors-production.up.railway.app/health)

## 🏗️ Architecture

```
┌─────────────────┐    HTTP    ┌──────────────────┐    ML Model    ┌─────────────────┐
│   Streamlit     │ ◄────────► │   FastAPI        │ ◄─────────────► │   SVM Model     │
│   Frontend      │            │   Backend        │                │   + Scaler      │
│   (UI/UX)       │            │   (API)          │                │   + Encoder     │
└─────────────────┘            └──────────────────┘                └─────────────────┘
      │                               │                                     │
      │                               │                                     │
   Streamlit                       Railway                              Model Files
   Cloud                          Deployment                           (.pkl format)
```

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Interactive web interface
- **Pandas** - Data manipulation
- **Requests** - API communication
- **PIL** - Image processing

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - Asynchronous Server Gateway Interface server
- **Pydantic** - Data validation
- **CORS Middleware** - Cross-origin requests

### Machine Learning
- **Scikit-learn** - SVM model and preprocessing
- **NumPy** - Numerical computations
- **Pandas** - Data analysis
- **Joblib** - Model serialization

### Deployment
- **Railway** - Backend API hosting
- **Streamlit Cloud** - Frontend hosting
- **GitHub** - Version control and CI/CD

## 🚀 Quick Start

### Option 1: Use the Live App (Recommended)
Simply visit the [live web app](https://one-piece-match-predictors.streamlit.app/) and start predicting fights!

### Option 2: Local Development

#### Prerequisites
- Python 3.8+
- Git

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/one-piece-match-predictors.git
   cd one-piece-match-predictors
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # Full development environment
   pip install -r requirements.txt
   ```

#### Running Locally

1. **Start the FastAPI backend**
   ```bash
   python -m uvicorn src.api.main:app --reload --port 8000
   ```

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run src/frontend/streamlit_app.py
   ```

3. **Open your browser**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📁 Project Structure

```
one-piece-match-predictors/
├── 📁 src/
│   ├── 📁 api/
│   │   └── 📄 main.py              # FastAPI application
│   ├── 📁 frontend/
│   │   └── 📄 streamlit_app.py     # Streamlit web interface
│   ├── 📁 models/
│   │   ├── 📄 svm_fight_predictor.pkl    # Trained ML model
│   │   ├── 📄 feature_scaler.pkl         # Feature scaler
│   │   └── 📄 label_encoder.pkl          # Label encoder
│   ├── 📁 data/
│   │   └── 📁 processed/
│   │       ├── 📄 character_data_cleaned.csv # Character database
│   │       └── 📄 fight_data_cleaned.csv     # Simulated fights database
│   └── 📁 scraping/
│       └── 📄 scraper.py           # Data collection scripts
├── 📄 requirements.txt             # Full dependencies
├── 📄 railway.toml                 # Railway deployment config
├── 📄 .dockerignore               # Docker ignore patterns
├── 📄 .gitignore                  # Git ignore patterns
└── 📄 README.md                   # This file
```

## 🤖 Machine Learning Model

### Model Details
- **Algorithm**: Support Vector Machine (SVM)
- **Accuracy**: 96.26% on test data
- **Features**: 12 engineered features
- **Classes**: Victory, Loss, Draw

### Feature Engineering
The model uses difference-based features between fighters:
- **Base Stats Differences** (10 features):
  - Reaction Speed, Stamina, Strength, Offense, Defense
  - Combat Skills, Battle IQ, Armament Haki, Observation Haki, Experience
- **Conqueror's Haki Features** (2 features):
  - Presence indicator and difference impact

### Training Data
- **100+ One Piece characters** with detailed combat statistics
- **Dataset** across victory/loss/draw outcomes
- **Feature scaling** using StandardScaler
- **Label encoding** for categorical outcomes

## 🔗 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```
Returns API status and model availability.

#### Fight Prediction
```http
POST /predict
```
Predicts fight outcome between two characters.

**Request Body:**
```json
{
  "fighter_1": {
    "reaction_speed": 85,
    "stamina": 90,
    "strength": 95,
    "offense": 88,
    "defense": 82,
    "combat_skills": 92,
    "battle_iq": 85,
    "armament_haki": 80,
    "observation_haki": 75,
    "conqueror_haki": 90,
    "experience": 88
  },
  "fighter_2": {
    "reaction_speed": 78,
    "stamina": 85,
    "strength": 82,
    "offense": 80,
    "defense": 88,
    "combat_skills": 85,
    "battle_iq": 90,
    "armament_haki": 85,
    "observation_haki": 88,
    "conqueror_haki": 0,
    "experience": 85
  }
}
```

**Response:**
```json
{
  "prediction": "victory",
  "confidence": 0.87,
  "probabilities": {
    "victory": 0.87,
    "loss": 0.10,
    "draw": 0.03
  },
  "fighter_1_advantage": {
    "reaction_speed": 7,
    "stamina": 5,
    "strength": 13,
    ...
  },
  "summary": "Fighter 1 wins with 87.0% confidence"
}
```

#### Model Information
```http
GET /model/info
```
Returns model metadata and performance metrics.

#### Example Request
```http
GET /example
```
Returns example fighter stats for testing.

## 🚀 Deployment

### Backend (Railway)
The FastAPI backend is automatically deployed to Railway on every push to the main branch.

**Environment Variables:**
- `PORT`: Automatically set by Railway
- `NIXPACKS_PYTHON_VERSION`: Set to 3.11

### Frontend (Streamlit Cloud)
The Streamlit frontend is deployed on Streamlit Cloud and automatically updates from GitHub.

### CI/CD Pipeline
```
GitHub Push → Railway Build → Health Check → Live Deployment ✅
            → Streamlit Cloud Build → Live Frontend ✅
```

## 📊 Character Database

The application includes 100+ One Piece characters with stats including:

- **Physical Stats**: Reaction Speed, Stamina, Strength
- **Combat Stats**: Offense, Defense, Combat Skills, Battle IQ
- **Haki Abilities**: Armament, Observation, Conqueror's Haki
- **Experience**: Overall battle experience

Popular characters include:
- Monkey D. Luffy, Roronoa Zoro, Sanji
- Kaido, Big Mom, Whitebeard
- Admiral Akainu, Kizaru, Aokiji
- And many more!

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** (if applicable)
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Areas for Contribution
- 🎨 **UI/UX improvements**
- 📊 **Additional character data**
- 🤖 **Model enhancements**
- 📝 **Documentation**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Eiichiro Oda** - Creator of One Piece
- **One Piece Community** - For character data and inspiration

---

<div align="center">
  <h3>🏴‍☠️ Made with ❤️ for the One Piece community! 🏴‍☠️</h3>
  <p><i>"I'm gonna be the King of the Pirates!"</i> - Monkey D. Luffy</p>
</div>

