import datetime
import uuid

from flask import make_response, jsonify
from flask_restful import Resource
from pymongo import MongoClient
from request_handle import get_meta_data_json
import config
import re


class Staff(Resource):
    def __init__(self):
        super().__init__()
        self.db = MongoClient(host="localhost", port=27017)
        self.email_validation_data = r'([a-z0-9]+[.-_])*[a-z0-9]+@[a-z0-9-]+(\.[a-z]{2,})+'

    def post(self):
        sinup_status = False
        staff_status = False
        sinup_collect = None
        staff_collect = None
        meta_data = get_meta_data_json()
        if self.email_validate(meta_data["email_id"]):
            data = self.database()
            sinup_collect = data["sinup"]
            staff_collect = data["staff"]
            s = sinup_collect.find_one({"trash": False, "email_id": meta_data["email_id"]})
            s_1 = staff_collect.find_one({"trash": False, "email_id": meta_data["email_id"]})
            if s is not None:
                sinup_status = True
            if s_1 is None:
                staff_status = True

        if sinup_status:
            if staff_status:
                create_data = dict()

                create_data["email_id"] = meta_data["email_id"]
                create_data["first_name"] = meta_data["first_name"]
                create_data["surname"] = meta_data["surname"]
                create_data["taking_subject"] = meta_data["taking_subject"]
                create_data["taking_class"] = meta_data["tacking_class"]
                create_data["taking_section"] = meta_data["taking_section"]
                create_data["guid"] = uuid.uuid4().hex
                create_data["trash"] = False
                create_data["create_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                create_data["_modified_date"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                if staff_collect is not None:
                    staff_collect.insert_one(create_data)
                    del create_data["_id"]
                    return make_response(jsonify({"message": "Create data successfully", "result": create_data, "status_code": 200}), 200)
            else:
                return make_response(jsonify({"message": "already your details exist", "result": "", "status_code": 400}), 400)
        else:
            return make_response(jsonify({"message": "first crate user or ", "result": " ", "status_code": 400}), 400)

    def get(self, email):
        sinup_status = False
        staff_status = False
        sinup_collect = None
        staff_collect = None
        student_data = ""
        s_1 = ""
        if self.email_validate(email):
            data = self.database()
            sinup_collect = data["sinup"]
            staff_collect = data["staff"]
            student_collect = data["collect"]
            s = sinup_collect.find_one({"trash": False, "email_id":email})
            s_1 = staff_collect.find_one({"trash": False, "email_id": email})
            student_data = student_collect.find({}, {"_id": 0})
            if s is not None:
                sinup_status = True
            if s_1 is not None:
                staff_status = True

        if sinup_status:
            if staff_status and s_1 and student_data != "":
                student_list = list()
                for data_value in student_data:
                    if data_value["class"] in s_1["taking_class"] and data_value["section"] in s_1["taking_section"]:
                        create_data = dict()
                        create_data["first_name"] = data_value["first_name"]
                        create_data["email_id"] = data_value["email_id"]
                        create_data["your_taking_subject_mark"] = data_value[s_1["taking_subject"]]
                        create_data["rank"] = data_value["rank"]
                        student_list.append(create_data)
                return make_response(
                    jsonify({"message": "Get data successfully", "result": student_list, "status_code": 200}), 200)
            else:
                return make_response(
                    jsonify({"message": "No data available", "result": "", "status_code": 400}), 400)
        else:
            return make_response(jsonify({"message": "first crate user or ", "result": " ", "status_code": 400}), 400)

    def put(self):

        sinup_status = False
        staff_status = False
        sinup_collect = None
        staff_collect = None
        meta_data = get_meta_data_json()
        if self.email_validate(meta_data["email_id"]):
            data = self.database()
            sinup_collect = data["sinup"]
            staff_collect = data["staff"]
            s = sinup_collect.find_one({"trash": False, "email_id": meta_data["email_id"]})
            s_1 = staff_collect.find_one({"trash": False, "email_id": meta_data["email_id"]})
            if s is not None:
                sinup_status = True
            if s_1 is not None:
                staff_status = True

        if sinup_status:
            if staff_status:
                create_data = dict()

                create_data["taking_subject"] = meta_data["taking_subject"]
                create_data["taking_class"] = meta_data["taking_class"]
                create_data["taking_section"] = meta_data["taking_section"]

                if staff_collect is not None:
                    staff_collect.update_one({"email_id": meta_data["email_id"]},{"$set": create_data})
                    return make_response(jsonify({"message": "Create data successfully", "result": create_data,
                                                  "status_code": 200}), 200)
            else:
                return make_response(jsonify({"message": "already your details exist", "result": "",
                                              "status_code": 400}), 400)
        else:
            return make_response(jsonify({"message": "first crate user or ", "result": " ", "status_code": 400}), 400)

    def delete(self, email_id):
        sinup_status = False
        staff_status = False
        sinup_collect = None
        staff_collect = None

        s_1 = ""
        if self.email_validate(email_id):
            data = self.database()
            sinup_collect = data["sinup"]
            staff_collect = data["staff"]
            s = sinup_collect.find_one({"trash": False, "email_id": email_id})
            s_1 = staff_collect.find_one({"trash": False, "email_id": email_id})
            if s is not None:
                sinup_status = True
            if s_1 is not None:
                staff_status = True
            if sinup_status and staff_status:
                sinup_collect.delete_one({"email_id": email_id})
                staff_collect.delete_one({"email_id": email_id})
                return make_response(jsonify({"message": "delete user data successfully", "resul": "", "status_code": 200}), 200)
            else:
                return make_response(
                    jsonify({"message": "User not available", "resul": "", "status_code": 400}), 400)
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

        student = None
        sinup = None
        staff = None
        if database_status is False or database:
            data = self.db[config.database_Name]
            if config.student_details in data.list_collection_names():
                student = data[config.student_details]
                staff = data[config.staff_details]
                sinup = data[config.user_details]

                collections_status = True
            else:
                student = data[config.student_details]
                staff = data[config.staff_details]
                sinup = data[config.user_details]
                collections_status = True
        if collections_status:
            return {"collect": student, "sinup": sinup, "staff": staff}

        else:
            return None