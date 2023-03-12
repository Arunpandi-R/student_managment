import datetime
import uuid

from flask import make_response, jsonify
from flask_restful import Resource
from pymongo import MongoClient
from request_handle import get_meta_data_json
import config
import re

class CreateStudent(Resource):
    def __init__(self):
        super().__init__()
        self.db = MongoClient(host="localhost", port=27017)
        self.email_validation_data = r'([a-z0-9]+[.-_])*[a-z0-9]+@[a-z0-9-]+(\.[a-z]{2,})+'

    def post(self):
        meta_data = get_meta_data_json()
        find_user = False
        find_user_1 = False
        data_base_details = None
        sinup = None

        if self.email_validate(meta_data["email_id"]):
            data_sinup = self.database()
            data_base_details = data_sinup["collect"]
            sinup = data_sinup["sinup"]
            if data_base_details is not None:
                status = sinup.find_one({"trash": False, "email_id": meta_data["email_id"]})
                status_1 = data_base_details.find_one({"trask": False, "email_id": meta_data["email_id"]})
                if status is not None:
                    find_user = True
                if status_1 is None:
                    find_user_1 = True

        if find_user:
            if find_user_1 :
                create_dict = dict()
                create_dict["email_id"] = meta_data["email_id"]
                create_dict["first_name"] = meta_data["first_name"]
                create_dict["surname"] = meta_data["surname"]
                create_dict["class"] = meta_data["class"]
                create_dict["section"] = meta_data["section"]
                create_dict["Tamil"] = meta_data["Tamil"]
                create_dict["English"] = meta_data["English"]
                create_dict["Maths"] = meta_data["Maths"]
                create_dict["Science"] = meta_data["Science"]
                create_dict["Social_science"] = meta_data["Social_science"]
                total, pecent, rank = self.rank_calculate(meta_data)
                create_dict["Total"] = total
                create_dict["percentage"] = str(pecent)+"%"
                create_dict["rank"] = rank
                create_dict["guid"] = uuid.uuid4().hex
                create_dict["trash"] = False
                create_dict["create_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                create_dict["_modified_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                if data_base_details is not None:
                    data_base_details.insert_one(create_dict)
                    del create_dict["_id"]
                    return make_response(jsonify({"message": "add student data successfully ", "result": create_dict, "status_code": 201}), 201)
        else:
            return make_response(jsonify({"message": "first crate user or ", "result": " ", "status_code": 400}), 400)

    def rank_calculate(self, data):
        Total_Mark = data["Tamil"] + data["English"] + data["Maths"] + data["Science"] + data["Social_science"]

        percentage = Total_Mark/5

        if percentage < 50:
            rank = "Fail"
        elif 50 <= percentage <= 55:
            rank = "E"
        elif 56 <= percentage <= 60:
            rank = "D"
        elif 61 <= percentage <= 70:
            rank = "C"
        elif 71 <= percentage <= 80:
            rank = "B"
        elif 81 <= percentage <= 90:
            rank = "A"
        else:
            rank = "S"
        return Total_Mark, percentage, rank

    def get(self, email_id):
        find_user = False
        find_user_1 = False
        data_base_details = None
        sinup = None
        status_1 = None
        data_sinup = self.database()
        data_base_details = data_sinup["collect"]
        sinup = data_sinup["sinup"]
        if data_base_details is not None:
            status = sinup.find_one({"trash": False, "email_id": email_id})
            status_1 = data_base_details.find_one({"trash": False, "email_id": email_id})
            if status is not None:
                find_user = True
            if status_1 is not None:
                find_user_1 = True

        if find_user and find_user_1:
            del status_1["_id"]
            return make_response(jsonify({"message": "get data successfully", "result": status_1,
                                          "status_code": 200}), 200)
        else:
            return make_response(jsonify({"message": "first crate user ", "result": " ", "status_code": 400}), 400)

    def put(self):
        meta_data = get_meta_data_json()

        find_user = False
        find_user_1 = False
        data_base_details = None
        sinup = None
        status_1 = ""
        data_sinup = self.database()
        data_base_details = data_sinup["collect"]
        sinup = data_sinup["sinup"]
        if data_base_details is not None:
            status = sinup.find_one({"trash": False, "email_id": meta_data["email_id"]})
            status_1 = data_base_details.find_one({"trask": False, "email_id": meta_data["email_id"]})
            if status is not None:
                find_user = True
            if status_1 is None:
                find_user_1 = True
        if find_user:
            create_dict = dict()
            create_dict["Tamil"] = meta_data["Tamil"]
            create_dict["English"] = meta_data["English"]
            create_dict["Maths"] = meta_data["Maths"]
            create_dict["Science"] = meta_data["Science"]
            create_dict["Social_science"] = meta_data["Social_science"]
            total, pecent, rank = self.rank_calculate(meta_data)
            create_dict["Total"] = total
            create_dict["percentage"] = str(pecent)+"%"
            create_dict["rank"] = rank
            if data_base_details is not None:
                data_base_details.update_one({"email_id": meta_data["email_id"]}, {"$set": create_dict})
                return make_response(jsonify({"message": "Update data successfully", "result": create_dict,
                                              "status_code": 200}), 200)

        else:
            return make_response(jsonify({"message": "first crate user ", "result": " ", "status_code": 400}), 400)

    def delete(self, email_id):
        find_user = False
        find_user_1 = False
        data_base_details = None
        sinup = None
        status_1 = ""
        data_sinup = self.database()
        data_base_details = data_sinup["collect"]
        sinup = data_sinup["sinup"]
        if data_base_details is not None:
            status = sinup.find_one({"trash": False, "email_id": email_id})
            status_1 = data_base_details.find_one({"trash": False, "email_id": email_id})
            if status is not None:
                find_user = True
            if status_1 is not None:
                find_user_1 = True
            if find_user and find_user_1:
                status = data_base_details.delete_one({"email_id": email_id})
                status_1_s =sinup.delete_one({"email_id": email_id})
                return make_response(jsonify({"message": "Delete successfully ", "result": " ", "status_code": 200}), 200)
            else:
                return make_response(jsonify({"message": "first crate user ", "result": " ", "status_code": 400}), 400)


    def email_validate(self, email):
        email_status = False
        if re.match(self.email_validation_data, email):
            email_status = True
        if email_status:
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
        sinup = None
        if database_status is False or database:
            data = self.db[config.database_Name]
            if config.student_details in data.list_collection_names():
                collect = data[config.student_details]
                sinup = data[config.user_details]
                collections_status = True
            else:
                collect = data[config.student_details]
                sinup = data[config.user_details]
                collections_status = True
        if collections_status is not None and sinup is not None:
            return {"collect": collect, "sinup": sinup}

        else:
            return None
