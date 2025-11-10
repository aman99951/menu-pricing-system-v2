import json
from openai import OpenAI
from database import db
from models import WeatherData, EventData, PricingSuggestion
from config import Config
import logging
from datetime import datetime
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMLPricingEngine:
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.temperature = Config.OPENAI_TEMPERATURE
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        
        self.price_increase_max = Config.PRICE_INCREASE_MAX
        self.price_decrease_max = Config.PRICE_DECREASE_MAX
        self.conservative_adjustment = Config.CONSERVATIVE_PRICE_ADJUSTMENT
        self.default_internal_weight = Config.DEFAULT_INTERNAL_WEIGHT
        self.default_external_weight = Config.DEFAULT_EXTERNAL_WEIGHT
        
        
        self.high_temp_threshold = Config.HIGH_TEMPERATURE_THRESHOLD
        self.low_temp_threshold = Config.LOW_TEMPERATURE_THRESHOLD
        self.extreme_high_temp = Config.EXTREME_HIGH_TEMPERATURE
        self.extreme_low_temp = Config.EXTREME_LOW_TEMPERATURE
        
       
        self.event_proximity = Config.EVENT_PROXIMITY_THRESHOLD
        self.event_far_distance = Config.EVENT_FAR_DISTANCE
        
       
        self.high_competitor_count = Config.HIGH_COMPETITOR_COUNT
        
    def calculate_price(self, menu_item_id, current_price, competitor_prices, weather, events):
        """
        Pure AI-driven pricing logic using OpenAI GPT
        """
        try:
            
            ai_result = self._get_complete_ai_recommendation(
                menu_item_id=menu_item_id,
                current_price=current_price,
                competitor_prices=competitor_prices,
                weather=weather,
                events=events
            )
            
          
            self._store_data(
                menu_item_id, 
                weather, 
                events, 
                ai_result['recommended_price'], 
                ai_result['reasoning'],
                ai_result['internal_weight'],
                ai_result['external_weight']
            )
            
            return ai_result
            
        except Exception as e:
            logger.error(f"Error in AI pricing calculation: {str(e)}")
            return self._emergency_fallback(current_price)
    
    def _calculate_statistics(self, prices):
        """Calculate statistics without numpy"""
        if not prices:
            return {}
        
        return {
            "mean": statistics.mean(prices),
            "min": min(prices),
            "max": max(prices),
            "std_dev": statistics.stdev(prices) if len(prices) > 1 else 0.0
        }
    
    def _get_complete_ai_recommendation(self, menu_item_id, current_price, 
                                        competitor_prices, weather, events):
        """
        Let OpenAI handle ALL pricing logic including weight calculation
        """
        
        # Calculate statistics without numpy
        stats = self._calculate_statistics(competitor_prices) if competitor_prices else {}
        
        # Prepare comprehensive data for AI
        market_data = {
            "menu_item_id": menu_item_id,
            "current_price": current_price,
            "competitor_prices": competitor_prices,
            "number_of_competitors": len(competitor_prices),
            "avg_competitor_price": stats.get('mean', current_price),
            "min_competitor_price": stats.get('min', current_price),
            "max_competitor_price": stats.get('max', current_price),
            "price_std_dev": stats.get('std_dev', 0)
        }
        
       
        thresholds = {
            "price_bounds": {
                "min_multiplier": self.price_decrease_max,
                "max_multiplier": self.price_increase_max,
                "min_price": current_price * self.price_decrease_max,
                "max_price": current_price * self.price_increase_max
            },
            "weather": {
                "high_temp": self.high_temp_threshold,
                "low_temp": self.low_temp_threshold,
                "extreme_high": self.extreme_high_temp,
                "extreme_low": self.extreme_low_temp
            },
            "events": {
                "proximity_km": self.event_proximity,
                "far_distance_km": self.event_far_distance
            },
            "competitors": {
                "high_count": self.high_competitor_count
            }
        }
        
       
        prompt = f"""
        You are an advanced AI pricing strategist. Your task is to analyze market data and provide a complete pricing strategy.
        
        MARKET DATA:
        {json.dumps(market_data, indent=2)}
        
        WEATHER DATA:
        {json.dumps(weather, indent=2)}
        
        EVENTS DATA:
        {json.dumps(events, indent=2)}
        
        CONFIGURATION THRESHOLDS:
        {json.dumps(thresholds, indent=2)}
        
        YOUR TASK:
        Analyze all the provided data and determine:
        
        1. DYNAMIC WEIGHT ALLOCATION:
           - Calculate internal_weight (0.0 to 1.0): How much should market/competitor factors influence pricing?
           - Calculate external_weight (0.0 to 1.0): How much should weather/events influence pricing?
           - Weights must sum to 1.0
           - Consider:
             * More than {self.high_competitor_count} competitors or high price variance → higher internal_weight
             * Temperature above {self.high_temp_threshold}°C or below {self.low_temp_threshold}°C → higher external_weight
             * Extreme conditions (>{self.extreme_high_temp}°C, <{self.extreme_low_temp}°C) → much higher external_weight
             * High popularity events within {self.event_proximity}km → higher external_weight
             * Events farther than {self.event_far_distance}km → minimal impact
        
        2. PRICE RECOMMENDATION:
           - Recommend an optimal price (integer value)
           - Price must be between {int(thresholds['price_bounds']['min_price'])} and {int(thresholds['price_bounds']['max_price'])}
           - Apply internal_weight to market-based pricing
           - Apply external_weight to demand-based pricing
        
        3. REASONING:
           - Provide a clear, concise explanation (1-2 sentences)
           - Explain why you allocated weights the way you did
           - Mention key factors driving the price recommendation
        
        Respond ONLY with valid JSON in this exact format:
        {{
            "internal_weight": <decimal between 0.0 and 1.0>,
            "external_weight": <decimal between 0.0 and 1.0>,
            "recommended_price": <integer>,
            "reasoning": "<your explanation>"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert AI pricing analyst with deep knowledge of:
                        - Dynamic pricing strategies
                        - Market analysis and competitive positioning
                        - Demand forecasting based on external factors
                        - Weight allocation for multi-factor decision making
                        
                        Always provide data-driven recommendations with precise numerical weights.
                        Respond only in valid JSON format."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
          
            ai_response = json.loads(response.choices[0].message.content)
            
           
            validated_response = self._validate_ai_response(ai_response, current_price)
            
            logger.info(f"AI Recommendation - Price: {validated_response['recommended_price']}, "
                       f"Weights: {validated_response['internal_weight']}/{validated_response['external_weight']}")
            
            return validated_response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _validate_ai_response(self, ai_response, current_price):
        """
        Validate AI response using configuration values
        """
        try:
          
            internal_weight = float(ai_response.get('internal_weight', self.default_internal_weight))
            external_weight = float(ai_response.get('external_weight', self.default_external_weight))
            recommended_price = int(float(ai_response.get('recommended_price', current_price)))
            reasoning = str(ai_response.get('reasoning', 'Price optimized based on AI analysis'))
            
          
            total_weight = internal_weight + external_weight
            if total_weight > 0:
                internal_weight = round(internal_weight / total_weight, 2)
                external_weight = round(1.0 - internal_weight, 2)
            else:
                internal_weight = self.default_internal_weight
                external_weight = self.default_external_weight
            
          
            max_price = int(current_price * self.price_increase_max)
            min_price = int(current_price * self.price_decrease_max)
            recommended_price = max(min_price, min(max_price, recommended_price))
            
            return {
                'recommended_price': recommended_price,
                'internal_weight': internal_weight,
                'external_weight': external_weight,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
         
            return self._ask_ai_to_fix_response(ai_response, current_price)
    
    def _ask_ai_to_fix_response(self, broken_response, current_price):
        """
        Ask OpenAI to fix a malformed response
        """
        try:
            min_price = int(current_price * self.price_decrease_max)
            max_price = int(current_price * self.price_increase_max)
            
            fix_prompt = f"""
            The following pricing response has issues:
            {json.dumps(broken_response, indent=2)}
            
            Please provide a corrected version with:
            - internal_weight: decimal between 0.0 and 1.0
            - external_weight: decimal between 0.0 and 1.0 (must sum with internal_weight to 1.0)
            - recommended_price: integer between {min_price} and {max_price}
            - reasoning: brief explanation string
            
            Respond ONLY with valid JSON.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You fix malformed pricing data. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": fix_prompt
                    }
                ],
                temperature=self.temperature * 0.5,  
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            fixed_response = json.loads(response.choices[0].message.content)
            return self._validate_ai_response(fixed_response, current_price)
            
        except Exception as e:
            logger.error(f"Fix attempt failed: {str(e)}")
            # Ultimate fallback
            return {
                'recommended_price': int(current_price * self.conservative_adjustment),
                'internal_weight': self.default_internal_weight,
                'external_weight': self.default_external_weight,
                'reasoning': 'Standard pricing applied due to processing error.'
            }
    
    def _emergency_fallback(self, current_price):
        """Emergency fallback using AI with minimal data"""
        try:
            emergency_prompt = f"""
            Provide emergency pricing for item with current price ${current_price}.
            Suggest a safe price adjustment within {(self.price_decrease_max-1)*100:.0f}% to +{(self.price_increase_max-1)*100:.0f}%.
            
            Respond with JSON:
            {{
                "recommended_price": <integer>,
                "internal_weight": {self.default_internal_weight},
                "external_weight": {self.default_external_weight},
                "reasoning": "<brief explanation>"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Provide safe pricing recommendations."},
                    {"role": "user", "content": emergency_prompt}
                ],
                temperature=self.temperature * 0.5,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            # Ensure price is within bounds
            result['recommended_price'] = max(
                int(current_price * self.price_decrease_max),
                min(int(current_price * self.price_increase_max), 
                    int(result.get('recommended_price', current_price * self.conservative_adjustment)))
            )
            return result
            
        except:
            return {
                'recommended_price': int(current_price * self.conservative_adjustment),
                'internal_weight': self.default_internal_weight,
                'external_weight': self.default_external_weight,
                'reasoning': 'Conservative price increase applied.'
            }
    
    def _store_data(self, menu_item_id, weather, events, recommended_price, reasoning, 
                   internal_weight, external_weight):
        """Store all data in database"""
        try:
            # Store weather data
            weather_record = WeatherData(
                temperature=weather.get('temperature') if weather else None,
                condition=weather.get('condition') if weather else None,
                location=Config.DEFAULT_LOCATION
            )
            db.session.add(weather_record)
            
            # Store events data
            for event in (events or []):
                event_record = EventData(
                    name=event.get('name'),
                    popularity=event.get('popularity'),
                    distance_km=event.get('distance_km')
                )
                db.session.add(event_record)
            
            # Store pricing suggestion
            suggestion = PricingSuggestion(
                menu_item_id=menu_item_id,
                recommended_price=recommended_price,
                internal_weight=internal_weight,
                external_weight=external_weight,
                reasoning=reasoning
            )
            db.session.add(suggestion)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error: {str(e)}")

# Create global instance
pricing_engine = AIMLPricingEngine()