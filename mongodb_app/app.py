from flask import Flask
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

# Connect to MongoDB
#client = MongoClient("mongodb://root:ssr0ojsSv9@localhost:27017")
#client = MongoClient("mongodb://mongo:27017")  # 'mongo' is the service name in Kubernetes
client = MongoClient("mongodb://root:ssr0ojsSv9@mongodb.mongodb.svc.cluster.local:27017")

# Create a database and collection
collection = client.admin["notes"]

# Create parser for request data
parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("note")

class HelloWorld(Resource):
    def get(self):
        return {"message": "Welcome to the note service!", "message": "Go to /Notes to access the database"}

class Notes(Resource):
    def get(self):
        items = [{"name": item["name"], "note": item["note"]} for item in collection.find()]
        return {"items": items}

    def post(self):
        args = parser.parse_args()
        name = args["name"]
        note = args["note"]
        collection.insert_one({"name": name, "note": note})
        return {"message": "New note added", "name": name, "note": note}

api.add_resource(HelloWorld, "/")
api.add_resource(Notes, "/notes")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")