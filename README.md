# AI-Powered Menu Pricing System

An AI-driven pricing engine that dynamically recommends competitive menu item prices based on internal and external factors.

## 📁 Project Structure

```
menu-pricing-system/
├── app.py                # Main Flask application
├── config.py             # Configuration settings
├── database.py           # Database initialization
├── models.py             # SQLAlchemy models
├── pricing_engine.py     # AI/ML pricing logic
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md             # Documentation
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a **.env** file:

```env
# Flask
FLASK_ENV=development
PORT=8000

# Database
DATABASE_URL=postgresql://username:password@host/database


```

### 3. Run Application

```bash
python app.py
```

Server runs at: [http://localhost:8000](http://localhost:8000)

---

## 📚 API Documentation

Swagger UI: [http://localhost:8000/swagger](http://localhost:8000/swagger)

---

## 🔌 API Endpoint

**POST /api/pricing/suggest**

### Request Example

```bash
curl -X POST http://localhost:8000/api/pricing/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "menu_item_id": 123,
    "current_price": 250,
    "competitor_prices": [240, 260, 245],
    "weather": {
      "temperature": 32,
      "condition": "Sunny"
    },
    "events": [
      {
        "name": "Food Festival",
        "popularity": "High",
        "distance_km": 2.5
      }
    ]
  }'
```

### Response Example

```json
{
  "menu_item_id": 123,
  "recommended_price": 268,
  "factors": {
    "internal_weight": 0.6,
    "external_weight": 0.4
  },
  "reasoning": "Higher demand expected due to warm weather and nearby food festival."
}
```

---

## 🛠 Tech Stack

* **Framework:** Flask 2.3.2
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **API Documentation:** Swagger UI

---

## 📊 Pricing Algorithm

* **Internal Factors (60%)** → Current price + Competitor prices
* **External Factors (40%)** → Weather conditions + Nearby events

---

## 🔐 Requirements

* Python 3.8+
* PostgreSQL 12+

---
