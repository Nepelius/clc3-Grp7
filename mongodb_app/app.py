from flask import Flask
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
import os

app = Flask(__name__)
api = Api(app)

# Connect to MongoDB
username = os.environ["username"]
password = os.environ["password"]
local_dns = "mongodb.mongodb.svc.cluster.local"     # dns name that can be accessed from inside the kubernetes cluster
port = "27017"      # mongodb service port
client = MongoClient("mongodb://{}:{}@{}:{}".format(username, password, local_dns, port))
#client = MongoClient("mongodb://user:password@localhost", 27017)

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
    
    def delete(self):
        args = parser.parse_args()
        name = args["name"]
        result = collection.delete_many({"name": name})
        if result.deleted_count >= 1:
            return {"message": f"Item '{name}' deleted successfully"}
        else:
            return {"message": f"Item '{name}' not found"}, 404
        
class Note(Resource):
    def get(self, name):
        items = [{"name": item["name"], "note": item["note"]} for item in collection.find({"name": name})]
        return {"items": items}

api.add_resource(HelloWorld, "/")
api.add_resource(Notes, "/notes")
api.add_resource(Note, "/notes/<string:name>")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")