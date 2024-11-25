from flask import Flask, request, render_template, send_file

from documents import generator
import database

app = Flask(__name__, template_folder = "templates")

def init_page(target_page, variables = None):
    return render_template("default.html", target_page = target_page, variables = variables)

@app.route('/')
def main_page():
    return init_page("main.html")

# TODO: remove get
@app.route("/api/register", methods = ["GET", "POST"])
def register():
    type = request.args.get("type", None)

    if (type == "child"):
        email = request.args.get("email", None)
        password = request.args.get("password", None)
        full_name = request.args.get("full_name", None)

        database.register_child(email, password, full_name)
    elif (type == "teacher"):
        email = request.args.get("email", None)
        password = request.args.get("password", None)
        full_name = request.args.get("full_name", None)

        database.register_teacher(email, password, full_name)

@app.route("/api/download", methods = ["GET"])
def download():
    users = [
        [
            "Насыров Амаль Робертович",
            "8Б",
            "23.11.2024",
            "Структура общества"
        ],
        [
            "Насырова Марина Леонидовна",
            "Работа",
            "23.11.2024",
            "Структура общества"
        ],
    ]

    bytes_stream = generator.create_word_users(users)
    return send_file(bytes_stream, as_attachment = True, download_name = "Blanks.docx")