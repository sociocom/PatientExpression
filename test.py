from dev import API
from flask import Flask
from flask_restful import Api


app = Flask(__name__)
api = Api(app)
api.add_resource(API, "/API")

## おまじない
if __name__ == "__main__":
    app.run(debug=True)