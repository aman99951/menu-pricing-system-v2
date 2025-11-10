from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from database import db, init_db
from pricing_engine import pricing_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

init_db(app)

@app.route('/api/pricing/suggest', methods=['POST'])
def suggest_pricing():
    """
    POST /api/pricing/suggest
    Accept data inputs and return optimized pricing suggestions
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        menu_item_id = data.get('menu_item_id')
        current_price = data.get('current_price')
        
        if not menu_item_id or not current_price:
            return jsonify({
                'error': 'menu_item_id and current_price are required'
            }), 400
        
        # Extract optional fields with defaults
        competitor_prices = data.get('competitor_prices', [])
        weather = data.get('weather', {})
        events = data.get('events', [])
        
        # Get AI-powered pricing recommendation
        result = pricing_engine.calculate_price(
            menu_item_id=menu_item_id,
            current_price=current_price,
            competitor_prices=competitor_prices,
            weather=weather,
            events=events
        )
        
        # Format response exactly as requested
        response = {
            'menu_item_id': menu_item_id,
            'recommended_price': result['recommended_price'],
            'factors': {
                'internal_weight': result['internal_weight'],
                'external_weight': result['external_weight']
            },
            'reasoning': result['reasoning']
        }
        
        logger.info(f"Pricing suggestion generated for item {menu_item_id}: ${result['recommended_price']}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in pricing suggestion: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    ai_status = 'connected' if Config.OPENAI_API_KEY else 'not configured'
    
    return jsonify({
        'status': 'healthy',
        'ai_status': ai_status
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'message': 'AI-Powered Menu Pricing System',
        'endpoints': {
            'pricing': 'POST /api/pricing/suggest',
            'health': 'GET /health',
            'swagger': 'GET /swagger'
        }
    }), 200

# Swagger configuration
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "AI-Powered Menu Pricing System"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.json', methods=['GET'])
def swagger_json():
    """Swagger JSON specification"""
    swagger_spec = {
        "swagger": "2.0",
        "info": {
            "title": "AI-Powered Menu Pricing System API",
            "description": "REST API for dynamic menu pricing recommendations using OpenAI GPT",
            "version": "1.0.0"
        },
        "host": request.host,
        "basePath": "/",
        "schemes": ["http", "https"],
        "paths": {
            "/api/pricing/suggest": {
                "post": {
                    "summary": "Get pricing suggestion",
                    "description": "Returns optimized pricing suggestions based on internal and external factors",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "description": "Pricing request data",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "required": ["menu_item_id", "current_price"],
                                "properties": {
                                    "menu_item_id": {
                                        "type": "integer",
                                        "example": 123
                                    },
                                    "current_price": {
                                        "type": "number",
                                        "example": 250
                                    },
                                    "competitor_prices": {
                                        "type": "array",
                                        "items": {"type": "number"},
                                        "example": [240, 260, 245]
                                    },
                                    "weather": {
                                        "type": "object",
                                        "properties": {
                                            "temperature": {
                                                "type": "number",
                                                "example": 32
                                            },
                                            "condition": {
                                                "type": "string",
                                                "example": "Sunny"
                                            }
                                        }
                                    },
                                    "events": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {
                                                    "type": "string",
                                                    "example": "Food Festival"
                                                },
                                                "popularity": {
                                                    "type": "string",
                                                    "example": "High"
                                                },
                                                "distance_km": {
                                                    "type": "number",
                                                    "example": 2.5
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful pricing suggestion",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "menu_item_id": {
                                        "type": "integer",
                                        "example": 123
                                    },
                                    "recommended_price": {
                                        "type": "number",
                                        "example": 268
                                    },
                                    "factors": {
                                        "type": "object",
                                        "properties": {
                                            "internal_weight": {
                                                "type": "number",
                                                "example": 0.6
                                            },
                                            "external_weight": {
                                                "type": "number",
                                                "example": 0.4
                                            }
                                        }
                                    },
                                    "reasoning": {
                                        "type": "string",
                                        "example": "Higher demand expected due to nearby food event and warm weather."
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    }
                }
            }
        }
    }
    return jsonify(swagger_spec), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(
        debug=Config.DEBUG,
        host=Config.APP_HOST,
        port=Config.APP_PORT
    )