from flask import Flask
from flask_restful import Api
from users import Users
from student import CreateStudent
from staff import Staff

application = Flask(__name__)
config = application.config
config.from_object('config')
api = Api(application)

api.add_resource(Users, "/users/<type_data>")
api.add_resource(CreateStudent, "/student", "/student/<email_id>")
api.add_resource(Staff, "/staff", "/staff/<email>")

if __name__ == "__main__":
    application.run(debug=False)