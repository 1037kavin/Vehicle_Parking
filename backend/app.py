from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
mail = Mail()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    from backend.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    
    # CORS configuration - very permissive for development
    CORS(app, 
         origins="*",
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    # JWT Error Handlers with detailed logging
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"JWT ERROR: Token expired - header: {jwt_header}, payload: {jwt_payload}")
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"JWT ERROR: Invalid token - {error}")
        return {'error': f'Invalid token: {error}'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"JWT ERROR: Missing token - {error}")
        return {'error': 'Authorization token is missing'}, 401
    
    # Add request logging
    @app.before_request
    def log_request_info():
        print(f"\n{'='*50}")
        print(f"REQUEST: {request.method} {request.path}")
        print(f"Headers: {dict(request.headers)}")
        print(f"{'='*50}\n")
    
    # Register blueprints
    from backend.routes import auth_bp, parking_lot_bp, parking_spot_bp, reservation_bp, admin_bp, user_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(parking_lot_bp, url_prefix='/api/parking-lots')
    app.register_blueprint(parking_spot_bp, url_prefix='/api/parking-spots')
    app.register_blueprint(reservation_bp, url_prefix='/api/reservations')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # Create database tables and admin user
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    # Serve Vue.js frontend (entry point only)
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app

def create_admin_user():
    """Create default admin user if not exists"""
    from backend.models import User
    from backend.config import config as app_config
    
    admin = User.query.filter_by(username=app_config['default'].ADMIN_USERNAME).first()
    if not admin:
        admin = User(
            username=app_config['default'].ADMIN_USERNAME,
            email=app_config['default'].ADMIN_EMAIL,
            role='admin',
            full_name='System Administrator'
        )
        admin.set_password(app_config['default'].ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)

