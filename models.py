from database import db
from datetime import datetime

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    current_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CompetitorPrice(db.Model):
    __tablename__ = 'competitor_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    price = db.Column(db.Float)
    competitor_name = db.Column(db.String(100))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    condition = db.Column(db.String(50))
    location = db.Column(db.String(100))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventData(db.Model):
    __tablename__ = 'events_data'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    popularity = db.Column(db.String(50))
    distance_km = db.Column(db.Float)
    event_date = db.Column(db.DateTime)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class PricingSuggestion(db.Model):
    __tablename__ = 'pricing_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    recommended_price = db.Column(db.Float)
    internal_weight = db.Column(db.Float)
    external_weight = db.Column(db.Float)
    reasoning = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)