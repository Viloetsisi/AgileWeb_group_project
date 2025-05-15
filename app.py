from flask import Flask
from config import Config
from model import db
from flask_mail import Mail
from flask_migrate import Migrate

application = Flask(__name__)
application.config.from_object(Config)

# Initialize extensions
db.init_app(application)
mail = Mail(application)
migrate = Migrate(application, db)

# Import and register all blueprints
from blueprints.auth_routes import auth_bp
from blueprints.profile_routes import profile_bp
from blueprints.jobs_routes import jobs_bp
from blueprints.share_routes import share_bp
from blueprints.market_routes import market_bp
from blueprints.dashboard_routes import dashboard_bp

application.register_blueprint(auth_bp)
application.register_blueprint(profile_bp)
application.register_blueprint(jobs_bp)
application.register_blueprint(share_bp)
application.register_blueprint(market_bp)
application.register_blueprint(dashboard_bp)

@application.route('/ping')
def ping():
    return "pong"

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True)
