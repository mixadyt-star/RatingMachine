from flask import Flask, request, session, render_template, send_file
from threading import Thread
import json

from utils import email_worker, security, web_errors
from documents import generator
from data import database
import config

app = Flask(__name__, template_folder = "templates")

secret_code_app = security.get_secret_code()
if (secret_code_app == None):
    secret_code_app = security.create_secret_code()
    security.store_secret_code(secret_code_app)

app.secret_key = secret_code_app

def init_page(target_page, variables = {}):
    variables["login"] = session.get("login", False)
    return render_template("default.html", target_page = target_page, variables = variables)

def check_login():
    user_login = session.get("login", None)
    user_type = session.get("type", None)
    user_email = session.get("email", None)
    user_password = session.get("password", None)

    if (user_login and user_type and user_email and user_password):
        return database.check_login(user_email, user_password, user_type)
    
    return False

@app.route('/', methods = ["GET"])
def main_page():
    return init_page("main.html")

@app.route("/children", methods = ["GET"])
@web_errors.ErrorChecker
def children():
    if (not session.get("login", False) ):
        return (1, web_errors.PAGE, "Вы не вошли в аккаунт", None) # AccessError
    
    if (check_login() and session["type"] == "Teacher"):
        return (0, web_errors.PAGE, '', init_page("children.html"))
    
    return (1, web_errors.PAGE, "Данный раздел доступен только учителям", None) # AccessError

@app.route("/logout", methods = ["POST"])
@web_errors.ErrorChecker
def logout():
    if (not session.get("login", False)):
        return (1, web_errors.JSON, "Вы не вошли в аккаунт", None) # AccessError
    
    session["login"] = False
    session.pop("email", None)
    session.pop("password", None)
    session.pop("type", None)

    return (0, web_errors.JSON, '', {"logout": True})

@app.route("/login", methods = ["GET", "POST"])
@web_errors.ErrorChecker
def login():
    variables = {
        "server_origin": config.SERVER_ORIGIN
    }

    if check_login():
        return (1, web_errors.PAGE, "Вы уже вошли в аккаунт", None) # AccessError

    if (request.method == "GET"):
        return (0, web_errors.PAGE, '', init_page("login.html", variables=variables))
    
    elif (request.method == "POST"):
        try:
            user_data = json.loads(request.data)
        except json.JSONDecodeError:
            return (2, web_errors.JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
        
        user_type = user_data.get("type", '')
        user_email = user_data.get("email", '')
        user_password = user_data.get("password", '')
        if (user_type == None or user_email == None or user_password == None):
            return (3, web_errors.JSON, "Заполнены не все поля", None)

        if (user_type == "Child" or user_type == "Teacher"):
            user_login = database.check_login(user_email, user_password, user_type)
        else:
            return (4, web_errors.JSON, "Некорректный запрос", None) # TypeNotCorrectError

        if (user_login):
            session["type"] = user_type
            session["email"] = user_email
            session["password"] = user_password
            session["login"] = True

            return (0, web_errors.JSON, '', {"login": True})
        else:
            return (5, web_errors.JSON, "Неправильный пароль или почта аккаунта", None) # UserOrPasswordWrongError

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