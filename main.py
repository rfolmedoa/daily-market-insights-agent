from fastapi import FastAPI, HTTPException
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = FastAPI(
    title="YFinance API Backend",
    version="1.1.0",
    description="A simple API wrapper around the Python yfinance library."
)

# ---------------------------------------------
# Root Health Check
# ---------------------------------------------
@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "YFinance API running on Render"
    }


# ---------------------------------------------
# Price Endpoint
# ---------------------------------------------
@app.get("/price/{symbol}")
def get_price(symbol: str):
    ticker = yf.Ticker(symbol)

    try:
        info = ticker.info
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or unsupported ticker symbol")

    if "regularMarketPrice" not in info:
        raise HTTPException(status_code=400, detail="Invalid or unsupported ticker symbol")

    return {
        "symbol": symbol.upper(),
        "price": info.get("regularMarketPrice"),
        "currency": info.get("currency"),
        "name": info.get("shortName"),
    }


# ---------------------------------------------
# History Endpoint
# ---------------------------------------------
@app.get("/history/{symbol}")
def get_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
):
    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(period=period, interval=interval)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or unsupported ticker symbol")

    if hist.empty:
        raise HTTPException(status_code=400, detail="No historical data found")

    return {
        "Open": hist["Open"].to_dict(),
        "Close": hist["Close"].to_dict(),
        "High": hist["High"].to_dict(),
        "Low": hist["Low"].to_dict(),
    }


# ---------------------------------------------
# News Endpoint
# ---------------------------------------------
@app.get("/news/{symbol}")
def get_news(symbol: str):
    ticker = yf.Ticker(symbol)

    try:
        raw_news = ticker.news
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ticker symbol")

    articles = []
    for item in raw_news:
        content = item.get("content", {})

        articles.append({
            "title": content.get("title"),
            "publisher": content.get("provider", {}).get("displayName"),
            "link": content.get("canonicalUrl", {}).get("url"),
            "summary": content.get("summary"),
            "pubDate": content.get("pubDate"),
        })

    return articles



# ---------------------------------------------
# Sentiment Endpoint
# ---------------------------------------------
@app.get("/sentiment/{symbol}")
def get_sentiment(symbol: str):
    analyzer = SentimentIntensityAnalyzer()
    ticker = yf.Ticker(symbol)

    try:
        raw_news = ticker.news
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ticker symbol")

    articles = []
    compound_scores = []

    for item in raw_news:
        content = item.get("content", {})
        text = content.get("summary") or content.get("title") or ""

        if not text.strip():
            continue

        sentiment = analyzer.polarity_scores(text)
        compound_scores.append(sentiment["compound"])

        articles.append({
            "title": content.get("title"),
            "publisher": content.get("provider", {}).get("displayName"),
            "link": content.get("canonicalUrl", {}).get("url"),
            "summary": content.get("summary"),
            "sentiment": sentiment
        })

    if not compound_scores:
        return {
            "symbol": symbol.upper(),
            "overall_sentiment": "neutral",
            "compound_score": 0.0,
            "articles": []
        }

    avg = sum(compound_scores) / len(compound_scores)

    if avg > 0.05:
        overall = "positive"
    elif avg < -0.05:
        overall = "negative"
    else:
        overall = "neutral"

    return {
        "symbol": symbol.upper(),
        "overall_sentiment": overall,
        "compound_score": avg,
        "articles": articles
    }
