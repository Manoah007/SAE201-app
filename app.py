from flask import Flask
from config import Config
from controllers.accueil import bp_accueil

app = Flask(__name__)
app.config.from_object(Config)

# Enregistrement des contrôleurs (blueprints)
app.register_blueprint(bp_accueil)

if __name__ == "__main__":
    app.run(debug=True)