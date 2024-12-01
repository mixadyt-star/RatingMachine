from flask import Flask, request, session, render_template, send_file
from threading import Thread

from documents import generator
from utils import email_worker, security
from data import database
import config

app = Flask(__name__, template_folder = "templates")

secret_code_app = security.get_secret_code()
if (secret_code_app == None):
    secret_code_app = security.create_secret_code()
    security.store_secret_code(secret_code_app)

app.secret_key = secret_code_app

def init_page(target_page, variables = None):
    return render_template("default.html", target_page = target_page, variables = variables)

@app.route('/', methods = ["GET"])
def main_page():
    return init_page("main.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    variables = {
        "server_origin": config.SERVER_ORIGIN
    }

    if (request.method == "GET"):
        return init_page("login.html", variables=variables)
    
    elif (request.method == "POST"):
        data = request.json
        if (data["type"] == "Child"):
            user_data = database.search_for_child(data["email"])
        elif (data["type"] == "Teacher"):
            user_data = database.search_for_teacher(data["email"])

        if (user_data):
            if (user_data[2] == security.hash(data["password"])):
                session["email"] = data["email"]
                session["password"] = data["password"]
                session["login"] = True

                return {"login": True, "error_message": ""}
            else:
                return {"login": False, "error_message": "Неправильный пароль или почта аккаунта"}
        else:
            return {"login": False, "error_message": "Неправильный пароль или почта аккаунта"}

@app.route("/register", methods = ["GET"])
def register():
    return init_page("register.html")

@app.route("/email_verification", methods = ["POST"])
def email_verification():
    email = request.form.get("email", None)
    password = request.form.get("password", None)

    session["email"] = email
    session["password"] = security.hash(password)

    verification_code = security.create_secret_code(length = 8).lower()
    email_worker.store_code(email, verification_code)

    Thread(target = email_worker.send_verification, args = [email, verification_code]).start()

    return init_page("email_verification.html")

# # TODO: remove it
# @app.route("/api/register", methods = ["GET", "POST"])
# def register():
#     type = request.args.get("type", None)

#     if (type == "child"):
#         email = request.args.get("email", None)
#         password = request.args.get("password", None)
#         full_name = request.args.get("full_name", None)

#         database.register_child(email, password, full_name)
#     elif (type == "teacher"):
#         email = request.args.get("email", None)
#         password = request.args.get("password", None)
#         full_name = request.args.get("full_name", None)

#         database.register_teacher(email, password, full_name)

# # TODO: remove it
# @app.route("/api/download", methods = ["GET"])
# def download():
#     users = [
#         [
#             "Насыров Амаль Робертович",
#             "8Б",
#             "23.11.2024",
#             "Структура общества"
#         ],
#         [
#             "Насырова Марина Леонидовна",
#             "Работа",
#             "23.11.2024",
#             "Структура общества"
#         ],
#     ]

#     bytes_stream = generator.create_word_users(users)
#     return send_file(bytes_stream, as_attachment = True, download_name = "Blanks.docx")