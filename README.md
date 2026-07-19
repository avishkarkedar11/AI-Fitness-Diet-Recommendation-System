# 🏋️ AI Fitness & Diet Recommendation System

An AI-powered web application that generates personalized fitness and diet recommendations based on a user's health profile, body metrics, and fitness goals. The system combines machine learning, intelligent recommendations, progress tracking, and an intuitive dashboard to help users achieve healthier lifestyles.

## 🌐 Live Demo

🚀 **Application:** https://ai-fitness-diet-recommendation-system-3mzl.onrender.com

---

## 📖 Overview

The AI Fitness & Diet Recommendation System is a full-stack Flask application that enables users to:

- Create a secure account
- Build a personalized fitness profile
- Calculate BMI and calorie requirements
- Receive AI-powered workout and diet recommendations
- Track weight and fitness progress
- Visualize health metrics using interactive charts
- Monitor their journey through a modern dashboard

The application focuses on delivering personalized recommendations through user-specific health information while providing a clean and responsive user experience.

---

## ✨ Features

### 🔐 Authentication
- User Registration
- Secure Login & Logout
- Password Hashing
- Session Management

### 👤 User Profile
- Personal Information
- Age
- Height
- Weight
- Gender
- Activity Level
- Fitness Goal
- Medical Information

### 🤖 AI Recommendations
- Personalized Workout Plans
- Personalized Diet Plans
- Daily Calorie Recommendation
- BMI Analysis
- Nutrition Guidance
- Fitness Suggestions

### 📊 Dashboard
- Personalized Dashboard
- Daily Health Summary
- Progress Overview
- Interactive Charts
- Recommendation Summary
- Quick Actions

### 📈 Progress Tracking
- Weight History
- BMI Monitoring
- Progress Visualization
- Historical Records

### 📱 Responsive Design
- Mobile Friendly
- Tablet Support
- Desktop Optimized
- Modern UI

---

## 🛠 Tech Stack

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Chart.js
- Bootstrap Icons

### Backend

- Python
- Flask
- Flask Blueprint
- Flask Login
- Flask SQLAlchemy
- Flask Migrate

### Database

- MySQL

### AI & Machine Learning

- Scikit-learn
- Joblib
- Pandas
- NumPy

### Deployment

- Render

---

## 📂 Project Structure

```text
AI-Fitness-Diet-Recommendation-System/
│
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   ├── static/
│   ├── utils/
│   └── ml/
│
├── migrations/
├── instance/
├── requirements.txt
├── run.py
└── README.md
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/your-username/AI-Fitness-Diet-Recommendation-System.git

cd AI-Fitness-Diet-Recommendation-System
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configure Environment

Create a `.env` file.

Example:

```env
SECRET_KEY=your_secret_key

DATABASE_URL=mysql+pymysql://username:password@localhost/database_name

GEMINI_API_KEY=your_api_key
```

---

## 🗄 Database Migration

```bash
flask db upgrade
```

---

## ▶ Run Application

```bash
python run.py
```

Visit

```
http://127.0.0.1:5000
```


## 🎯 Learning Outcomes

This project demonstrates:

- Full Stack Web Development
- Flask Architecture
- Authentication System
- RESTful Design Principles
- Database Design
- Machine Learning Integration
- Data Visualization
- Responsive UI Development
- Deployment on Render
- Clean Project Structure



## 📄 License

This project is licensed under the MIT License.

---

