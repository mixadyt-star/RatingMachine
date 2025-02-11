from flask import Flask, request, session, render_template, send_file
from datetime import datetime
from threading import Thread
import numpy as np
import random
import base64
import json
import cv2

from utils.web_errors import error_checker, PAGE, JSON
from utils import email_worker, security
from data import database, storing
from recognition import recognizer
from documents import generator
from plotter import diograms, class_graph, user_graph

app = Flask(__name__, template_folder = "templates")

secret_code_app = security.get_secret_code()
if (secret_code_app == None):
    secret_code_app = security.create_secret_code()
    security.store_secret_code(secret_code_app)

app.secret_key = secret_code_app

def init_page(target_page, variables = {}):
    data = storing.get_data("data/menu.json")
    menu_items = []

    login = session.get("login", False)
    permission = "teacher" if login else "guest"

    for menu_item in data:
        if permission in menu_item["permission"]:
            menu_items.append(menu_item)

    return render_template("default.html", target_page = target_page, variables = variables, menu_items = menu_items)

def check_login():
    user_login = session.get("login", None)
    user_type = session.get("type", None)
    user_email = session.get("email", None)
    user_password = session.get("password", None)

    if (user_login and user_type and user_email and user_password):
        return database.check_login(user_email, user_password)
    
    return False

@app.route('/', methods = ["GET"])
def main_page():
    return init_page("main.html")

@app.route("/children", methods = ["GET"])
@error_checker
def children():
    if check_login():
        if (session["type"] == "Teacher"):
            return (0, PAGE, '', init_page("children.html"))
        
        return (1, PAGE, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, PAGE, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/children/class", methods = ["GET", "POST"])
@error_checker
def children_class():
    if check_login():
        if (session["type"] == "Teacher"):
            form = request.args.get("form", None)
            if form:
                if (request.method == "POST"):
                    full_name = request.form.get("full-name", None)

                    if full_name:
                        database.register_child(full_name, form)
                    else:
                        return (3, PAGE, "Должно быть передано ФИО ученика", None) # FewValuesError
                    
                variables = {
                    "form": form,
                    "children": {child_data[0]: str(i + 1) + ". " + child_data[1] for i, child_data in enumerate(database.get_children(form))}
                }
                return (0, PAGE, '', init_page("children_class.html", variables = variables))
            else:
                return (3, PAGE, "Поле form должно быть заполнено", None) # FewValuesError
        
        return (1, PAGE, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, PAGE, "Вы не вошли в аккаунт", None) # AccessError
    
@app.route("/tests", methods = ["GET", "POST"])
@error_checker
def tests():
    if check_login():
        if (session["type"] == "Teacher"):
            class_ = request.args.get("class", None)
            subject = request.args.get("subject", None)
            if (class_ and subject):
                if (request.method == "POST"):
                    test_name = request.form.get("test_name", None)
                    if test_name:
                        database.register_test(test_name, subject, class_)
                    else:
                        return (3, PAGE, "Вы должны передать название темы теста", None) # FewValuesError

                variables = {
                    "class": class_,
                    "subject": subject,
                    "tests": {test_data[0]: (test_data[1], json.loads(test_data[4])) for test_data in database.get_tests(class_, subject)},
                    "children": {form[0]: {child_data[0]: child_data[1] for child_data in database.get_children(form[0])} for form in database.get_forms_by_class(class_)},
                    "blanks": [(database.get_child(user_id)[1], test_id, json.loads(answers), file, sorted(json.loads(answers))) for _, user_id, test_id, answers, file in database.get_blanks(database.get_tests(class_, subject))]
                }
                return (0, PAGE, '', init_page("tests.html", variables))
            else:
                return (3, PAGE, "Не получен класс или предмет", None) # FewValuesError
        else:
            return (1, PAGE, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, PAGE, "Вы не вошли в аккаунт", None) # AccessError

def recognize_blank(data_url: str):
    _, data = data_url.split(',')
    image_data = base64.b64decode(data)
    image_array = np.frombuffer(image_data, np.uint8)
    orig_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    answers, image = recognizer.recognize(orig_image)
    _, buffer = cv2.imencode(".jpg", image)
    data = base64.b64encode(buffer).decode()
    file = f"data:image/jpeg;base64,{data}"
    hash_code = security.read_qrcode(orig_image)
    user_id, test_id, _ = database.get_working_test(hash_code)

    true_answers = json.loads(database.get_test(test_id)[4])
    subject = database.get_test(test_id)[2]

    count = 0
    correct = 0
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for i, answer in enumerate(true_answers):
        if answer != "":
            count += 1
            
            if answer == answers[alphabet[i]]:
                correct += 1

    if (correct / count > 0.8):
        mark = 5
    elif (correct / count > 0.7):
        mark = 4
    elif (correct / count > 0.6):
        mark = 3
    else:
        mark = 2

    database.register_blank(user_id, test_id, answers, file)
    marks = json.loads(database.get_child(user_id)[3])
    marks.append({
        "subject": subject,
        "date": datetime.datetime.today().strftime('%d.%m.%Y'),
        "mark": str(mark)
    })
    database.update_child(user_id, marks)
    database.delete_working_test(hash_code)

@app.route("/tests/upload_blanks", methods = ["POST"])
@error_checker
def upload_blanks():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
    
            blanks = data.get("blanks", None)
            if blanks:
                for blank in blanks:
                    thread = Thread(target = recognize_blank, args = (blank,))
                    thread.start()
                return (0, JSON, '', None)
            else:
                return (3, JSON, "Бланки не получены", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/tests/download_questions", methods = ["POST"])
@error_checker
def download_questions():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
    
            test_id = data.get("test_id", None)
            if test_id:
                if database.check_test(test_id):
                    questions = database.get_questions(test_id)[0]

                    if questions:
                        return (0,  JSON, '', questions)
                    else:
                        return (6, JSON, "Вопросы не загружены", None) # ContentDeleted
                else:
                    return (6, JSON, "Теста не существует", None) # ContentDeleted
            else:
                return (3, JSON, "ID теста не получен", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/tests/upload_questions", methods = ["POST"])
@error_checker
def upload_questions():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
    
            questions = data.get("questions", None)
            test_id = data.get("test_id", None)
            if test_id:
                if database.check_test(test_id):
                    if questions:
                        database.edit_questions(test_id, questions)

                        return (0, JSON, '', None)
                    else:
                        return (3, JSON, "Вы должны загрузить файл", None) #FewValuesError
                else:
                    return (6, JSON, "Теста не существует", None) # ContentDeleted
            else:
                return (3, JSON, "ID теста не получен", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/tests/delete", methods = ["POST"])
@error_checker
def delete_test():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
    
            test_id = data.get("test_id", None)
            if test_id:
                if database.check_test(test_id):
                    database.delete_test(test_id)
                    return (0, JSON, '', {})
                else:
                    return (6, JSON, "Теста не существует", None) # ContentDeleted
            else:
                return (3, JSON, "ID теста не получен", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/tests/answers", methods = ["POST"])
@error_checker
def edit_answers():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
    
            answers = data.get("answers", None)
            test_id = data.get("test_id", None)
            if test_id:
                if database.check_test(test_id):
                    if (answers and len(answers) == 26):
                        database.edit_answers(int(test_id), answers)
                        return (0, JSON, '', None)
                    else:
                        return (3, JSON, "Ответы не получены", None) # FewValuesError
                else:
                    return (6, JSON, "Теста не существует", None) # ContentDeleted
            else:
                return (3, JSON, "ID теста не получен", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/tests/download", methods = ["POST"])
@error_checker
def download():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
    
            children = data.get("children", None)
            test_id = data.get("test_id", None)
            if test_id:
                if database.check_test(test_id):
                    if children:
                        current_date = datetime.now().strftime("%d.%m.%Y")
                        users = []
                        for child_id in children:
                            if database.check_child(child_id):
                                secret_code = random.randint(10000000, 10000000000)
                                database.register_working_test(child_id, test_id, security.hash(secret_code))

                                child_data = database.get_child(child_id)
                                child_name = child_data[1]
                                child_form = child_data[2]

                                test_name = database.get_test(test_id)[1]

                                tmp = []
                                tmp.append(child_name)
                                tmp.append(child_form)
                                tmp.append(current_date)
                                tmp.append(test_name)
                                tmp.append(secret_code)

                                users.append(tmp)
                            else:
                                return (6, JSON, f"Ребёнка с ID {child_id} не существует", None) # ContentDeleted
                    else:
                        return (3, JSON, "Нужно выбрать хотя бы одного ученика", None) # FewValuesError
                else:
                    return (6, JSON, "Теста не существует", None) # ContentDeleted
            else:
                return (3, JSON, "ID теста не получен", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

    bytes_stream = generator.create_word_users(users)
    file = base64.b64encode(bytes_stream.getvalue()).decode()
    return (0, JSON, '', file)

@app.route("/children/class/delete", methods = ["POST"])
@error_checker
def delete_child():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
    
            child_id = data.get("child_id", None)
            if child_id:
                if database.check_child(child_id):
                    database.delete_child(child_id)
                    return (0, JSON, '', {})
                else:
                    return (6, JSON, "Ученика не существует", None) # ContentDeleted
            else:
                return (3, JSON, "ID ученика не получен", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/logout", methods = ["POST"])
@error_checker
def logout():
    if check_login():
        session["login"] = False
        session.pop("email", None)
        session.pop("password", None)
        session.pop("type", None)

        return (0, JSON, '', {"logout": True})
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/login", methods = ["GET", "POST"])
@error_checker
def login():
    if check_login():
        return (1, PAGE, "Вы уже вошли в аккаунт", None) # AccessError

    if (request.method == "GET"):
        return (0, PAGE, '', init_page("login.html"))
    
    elif (request.method == "POST"):
        try:
            user_data = json.loads(request.data)
        except json.JSONDecodeError:
            return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
        
        user_type = user_data.get("type", None)
        user_email = user_data.get("email", None)
        user_password = user_data.get("password", None)

        if (user_type == None or user_email == None or user_password == None):
            return (3, JSON, "Заполнены не все поля", None) # FewValuesError

        if (user_type == "Teacher"):
            is_logged = database.check_login(user_email, user_password)
        else:
            return (4, JSON, "Некорректный запрос", None) # TypeNotCorrectError

        if (is_logged):
            session["type"] = user_type
            session["email"] = user_email
            session["password"] = user_password
            session["login"] = True

            return (0, JSON, '', {"login": True})
        else:
            return (5, JSON, "Неправильный пароль или почта аккаунта", None) # UserOrPasswordWrongError

@app.route("/stats", methods = ["GET"])
@error_checker
def stats():
    if check_login():
        if (session["type"] == "Teacher"):
            subject = request.args.get("subject", None)
            if subject:
                stats_data = database.get_stats_data()
                diogram_uri = f"data:image/jpeg;base64,{base64.b64encode(diograms.plot(diograms.parse(stats_data, subject)).getvalue()).decode('utf-8')}"

                variables = {
                    "subject": subject,
                    "diogram_uri": diogram_uri
                }

                return (0, PAGE, '', init_page("stats.html", variables))
            else:
                return (3, PAGE, "Не получен предмет", None) # FewValuesError
        else:
            return (1, PAGE, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, PAGE, "Вы не вошли в аккаунт", None) # AccessError
    
@app.route("/stats/class", methods = ["GET"])
@error_checker
def stats_class():
    if check_login():
        if (session["type"] == "Teacher"):
            subject = request.args.get("subject", None)
            class_ = request.args.get("class", None)
            if (subject and class_):
                stats_data = database.get_stats_data()
                graph_uri = f"data:image/jpeg;base64,{base64.b64encode(class_graph.plot(class_graph.parse(stats_data, subject, class_)).getvalue()).decode('utf-8')}"

                variables = {
                    "subject": subject,
                    "diogram_uri": graph_uri,
                    "class": class_,
                    "children": {form[0]: {child_data[0]: child_data[1] for child_data in database.get_children(form[0])} for form in database.get_forms_by_class(class_)},
                }

                return (0, PAGE, '', init_page("stats_class.html", variables))
            else:
                return (3, PAGE, "Не получен предмет или класс", None) # FewValuesError
        else:
            return (1, PAGE, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, PAGE, "Вы не вошли в аккаунт", None) # AccessError
    
@app.route("/stats/render", methods = ["POST"])
@error_checker
def render_user():
    if check_login():
        if (session["type"] == "Teacher"):
            try:
                user_data = json.loads(request.data)
            except json.JSONDecodeError:
                return (2, JSON, "Не удалось распаковать запрос", None) # JsonDecodeError
            
            id = user_data.get("id", None)
            subject = user_data.get("subject", None)
            if (id and subject):
                if database.check_child(id):
                    user_data = database.get_child(id)
                    graph_uri = f"data:image/jpeg;base64,{base64.b64encode(user_graph.plot(user_graph.parse(user_data, subject)).getvalue()).decode('utf-8')}"

                    return (0, JSON, '', graph_uri)
                return (6, JSON, "Ученика не существует", None) # ContentDeleted
            else:
                return (3, JSON, "Не получен айди ученика или предмет", None) # FewValuesError
        else:
            return (1, JSON, "Данный раздел доступен только учителям", None) # AccessError
    else:
        return (1, JSON, "Вы не вошли в аккаунт", None) # AccessError

@app.route("/register", methods = ["GET"])
@error_checker
def register():
    if check_login():
        return (1, PAGE, "Вы уже вошли в аккаунт", None) # AccessError
    
    return (0, PAGE, '', init_page("register.html"))

@app.route("/email_verification", methods = ["POST"])
@error_checker
def email_verification():
    if check_login():
        return (1, PAGE, "Вы уже вошли в аккаунт", None) # AccessError
    
    user_email = request.form.get("email", None)
    user_password = request.form.get("password", None)

    if (user_email and user_password):
        if (not database.search_for_teacher(user_email)):
            verification_code = security.create_secret_code(length = 8).lower()
            email_worker.store_code(user_email, verification_code)

            Thread(target = email_worker.send_verification, args = [user_email, verification_code]).start()

            return (0, PAGE, '', init_page("email_verification.html"))
        else:
            return (1, PAGE, "Аккаунт уже существует", None) # AccessError
    else:
        return (3, PAGE, "Не получен email или пароль", None) # FewValuesError

