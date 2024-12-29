from flask import render_template

JSON = 0
PAGE = 1

class WebError:
    def __init__(self, error_code: int):
        self.error_code = error_code

    def get_json(self, error: bool = True, message: str | None = None, payload: dict | list | int | str | None = None):
        return {
            "error": error,
            "error_code": self.error_code,
            "error_message": message,
            "payload": payload
        }

    def get_page(self, message: str):
        return render_template("error_page.html", error_message = message)

class AccessError(WebError):
    def __init__(self):
        super().__init__(error_code = 1)

class JsonDecodeError(WebError):
    def __init__(self):
        super().__init__(error_code = 2)

class FewValuesError(WebError):
    def __init__(self):
        super().__init__(error_code = 3)

class TypeNotCorrectError(WebError):
    def __init__(self, message = "Некорректный запрос"):
        super().__init__(error_code = 4)

class UserOrPasswordWrongError(WebError):
    def __init__(self):
        super().__init__(error_code = 5)

class ContentDeleted(WebError):
    def __init__(self):
        super().__init__(error_code = 6)

errors = {
    1: AccessError,
    2: JsonDecodeError,
    3: FewValuesError,
    4: TypeNotCorrectError,
    5: UserOrPasswordWrongError,
    6: ContentDeleted
}

def error_checker(func):
    def inner():
        error_code, type, message, payload = func()

        if (error_code == 0):
            if (type == JSON):
                return WebError(0).get_json(error = False, payload = payload)
            elif (type == PAGE):
                return payload
        else:
            error = errors[error_code]()
            if (type == JSON):
                return error.get_json(message = message, payload = payload)
            elif (type == PAGE):
                return error.get_page(message)

    inner.__name__ = func.__name__
    return inner