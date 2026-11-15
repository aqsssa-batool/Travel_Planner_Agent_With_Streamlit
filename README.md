# ✈️ PlanSpark – Multi-Agent AI Powered Travel Planner

**PlanSpark** is an AI-powered travel planning application that helps users create personalized travel itineraries based on their destination, budget, travel duration, number of travelers, travel style, and personal interests.

The application uses a multi-agent AI architecture to plan, analyze, write, and review travel itineraries until the final plan receives approval. It also provides live weather information and currency conversion to help users make informed travel decisions.

## 🌟 Features

### 1. AI-Powered Trip Planning
- Enter your desired travel destination.
- Select the number of travel days and travelers.
- Set your total travel budget and preferred currency.
- Choose a travel style:
  - Budget / Backpacking
  - Comfort / Mid-Range
  - Luxury / Premium
- Add personal interests such as beaches, food, culture, shopping, nature, and adventure.
- Generate a personalized travel itinerary using AI agents.

### 2. Multi-Agent AI System

PlanSpark uses four specialized AI agents:

| Agent | Responsibility |
|---|---|
| Planner Agent | Creates a structured JSON trip blueprint based on user requirements. |
| Budget Agent | Analyzes the budget, estimates expenses, and uses live tools when needed. |
| Writer Agent | Generates a detailed and practical Markdown travel itinerary. |
| Reviewer Agent | Checks the itinerary for accuracy, budget limits, duration, and consistency. |

**Approval Workflow:**

The agents work together in the following sequence:

1. Planner creates the initial trip blueprint.
2. Budget Agent analyzes expenses and budget feasibility.
3. Writer generates the complete itinerary.
4. Reviewer evaluates the generated plan.
5. If revisions are required, feedback is sent back to the Planner.
6. The process repeats until the Reviewer approves the itinerary.

The application maintains a review history so users can see the approval process and feedback.

### 3. Live Weather Information
- Search for weather by city.
- View current temperature and weather conditions.
- Check humidity and wind speed.
- View daily minimum and maximum temperatures.
- Check the probability of rain.

Weather information is retrieved using the Open-Meteo API.

### 4. Currency Converter
- Convert between supported currencies.
- View live exchange rates.
- Calculate converted amounts.
- Display exchange-rate update information.

Supported currencies include PKR, USD, EUR, GBP, AED, SAR, JPY, CAD, AUD, INR, CHF, and CNY.

Currency conversion uses the ExchangeRate-API.

### 5. Explore Destinations
- Explore suggested destinations such as Bali, London, and the Swiss Alps.
- Select a destination to start planning a trip.
- Discover travel experiences and activities.

### 6. My Trips
- View the latest generated itinerary.
- Review your trip details.
- Download your itinerary in Markdown format.

### 7. Travel Inspiration
- Explore suggested travel experiences.
- Add interests to your trip preferences.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application interface |
| Groq API | AI model integration |
| OpenAI GPT-OSS | Language model used through Groq |
| Open-Meteo API | Live weather information |
| ExchangeRate-API | Live currency conversion |
| HTML & CSS | Custom dashboard styling |
| JSON | Structured trip planning and agent communication |

## 📁 Project Structure

```text
PlanSpark/
│
├── app.py          # Streamlit application and user interface
├── agents.py       # Multi-agent AI system and API integrations
├── .env            # Environment variables (create locally)
├── README.md       # Project documentation
└── requirements.txt # Python dependencies (create locally)
```

## 🤖 AI Model Configuration

The application supports the following Groq-hosted models:

- `openai/gpt-oss-120b` (default)
- `openai/gpt-oss-20b`

The model can be selected from the AI Settings section in the sidebar.

## 🔄 How the Application Works

1. The user provides travel requirements through the Streamlit interface.
2. The Planner Agent converts the requirements into a structured JSON blueprint.
3. The Budget Agent analyzes expenses and retrieves live weather or currency information when needed.
4. The Writer Agent creates a detailed travel itinerary.
5. The Reviewer Agent checks the itinerary against the user's requirements.
6. If the itinerary does not pass review, the Planner receives feedback and prepares a revised plan.
7. Once approved, the final itinerary is displayed and made available for download.

## 👨‍💻 Project Purpose

PlanSpark demonstrates the practical application of Artificial Intelligence, multi-agent collaboration, API integration, and interactive web development.

Its goal is to simplify travel planning by combining personalized itinerary generation, budget analysis, live weather information, and currency conversion in one application.

---

**PlanSpark – Discover Places. Plan Experiences. Travel Smarter.**

**👩‍💻 Author**

**Aqsa Batool**

Aspiring AI Engineer | Python | Data Analysis | Machine Learning | Deep Learning
