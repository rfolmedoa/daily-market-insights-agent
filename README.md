# YFinance API – FastAPI Backend for IBM Watsonx Agent

A lightweight API wrapper around the Python `yfinance` library.
This service exposes safe endpoints for:

- Real-time stock price
- Historical OHLC data
- News
- Symbol details

## 🚀 Deployment on Render
This project is ready for Render Web Service deployment.

1. Push this repo to GitHub  
2. In Render → Create New → Web Service  
3. Connect GitHub  
4. Select this repo  
5. Render detects:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📌 API Endpoints

### GET `/price/{symbol}`
Example: