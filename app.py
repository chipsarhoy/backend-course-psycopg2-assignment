from flask import Flask
import os

from db import create_all
import routes

flask_host = os.environ.get("FLASK_HOST")
flask_port = os.environ.get("FLASK_PORT")

app = Flask(__name__)

app.register_blueprint(routes.product)
app.register_blueprint(routes.category)
app.register_blueprint(routes.company)
app.register_blueprint(routes.warranty)
app.register_blueprint(routes.product_category)

if __name__ == "__main__":
    create_all()
    app.run(host=flask_host, port=flask_port)