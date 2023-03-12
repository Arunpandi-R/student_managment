import datetime
import uuid

from flask import make_response, jsonify
from flask_restful import Resource
from pymongo import MongoClient
from request_handle import get_meta_data_json
import config
import re
from werkzeug.security import generate_password_hash, check_password_hash


class Users(Resource):

    def __init__(self):
        self.db = MongoClient(host="localhost", port=27017)
        self.email_validation_data = r'([a-z0-9]+[.-_])*[a-z0-9]+@[a-z0-9-]+(\.[a-z]{2,})+'
        self.password_validation_data = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"

    def post(self, type_data = None):
        meta_data = get_meta_data_json()
        email_id = meta_data["email_id"]
        password = meta_data["password"]
        user_type = meta_data["user_type"]
        data_satus = self.email_and_password_validate(email=email_id, password=password)
        if data_satus and user_type in [1, 2]:
            database_status = self.database()
            if type_data == "login":
                if database_status is not None:
                    data_user = database_status.find_one({"email_id": email_id})
                    if data_user is not None:
                        password_status = check_password_hash(pwhash=data_user["password"], password=password)
                        if password_status:
                            return make_response(jsonify({"message": "Login successfully", "result": " ",
                                                          "status_code": 200}), 200)
                        elif data_user is None and type == 1:
                            return make_response(jsonify({"message": "Wrong Password please enter correct password", "result": " ",
                                                          "status_code": 400}), 400)
                    else:
                        return make_response(
                            jsonify({"message": "Please create new user", "result": " ",
                                     "status_code": 400}), 400)
                else:
                    return make_response(
                        jsonify({"message": "no database available", "result": "", "status_code": 400}),
                        400)
            elif type_data == "sin_up":
                hash_password = generate_password_hash(password=password)
                insert_data = self.create_data(email=email_id, password=hash_password, user_id=user_type)
                if database_status is not None:
                    data_user = database_status.find_one({"email_id": email_id})
                    if data_user is None:
                        insert_data_s = database_status.insert_one(insert_data)
                        if insert_data_s is not None:
                            return make_response(jsonify({"message": "Sin_up successfully", "result": " ",
                                                          "status_code": 200}), 200)
                    else:
                        return make_response(jsonify({"message": "Already user exist", "result": " ",
                                                      "status_code": 200}), 200)
        else:
            return make_response(
                jsonify({"message": "Enter the validate email id and enter the password"
                                    "Adjust it by modifying {8,} At least one uppercase English letter"
                                    "You can remove this condition by removing (?=.*?[A-Z]"
                                    "At least one lowercase English letter."
                                    "You can remove this condition by removing (?=.*?[a-z])"
                                    "At least one digit. You can remove this condition by removing (?=.*?[0-9])"
                                    "At least one special character,"
                                    "You can remove this condition by removing (?=.*?[#?!@$%^&*-])"
                                    "and enter user id is 1 is student or 2 is staff", "result": "",
                         "status_code": 400}), 400)

    def create_data(self, email, password, user_id):
        create_dict = dict()
        create_dict["email_id"] = email
        create_dict["password"] = password
        create_dict["user_type"] = user_id
        create_dict["guid"] = uuid.uuid4().hex
        create_dict["trash"] = False
        create_dict["create_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        create_dict["_modified_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return create_dict

    def email_and_password_validate(self, email, password):
        email_status = False
        password_status = False
        if re.match(self.email_validation_data, email):
            email_status = True
        if re.match(self.password_validation_data, password):
            password_status = True
        if email_status and password_status:
            return True
        else:
            return False

    def database(self):
        database = self.db.list_database_names()

        database_status = False
        collections_status = False

        if config.database_Name in database:
            database_status = True

        collect = None

        if database_status is False or database:
            data = self.db[config.database_Name]
            if config.user_details in data.list_collection_names():
                collect = data[config.user_details]
                collections_status = True
            else:
                collect = data[config.user_details]
                collections_status = True
        if collections_status is not None:
            return collect

        else:
            return None
