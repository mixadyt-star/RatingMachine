function logout() {
    logout_button = document.getElementById("logout-menu")
    logout_button.innerHTML = '<div class="loader"></div>'
    logout_button.disabled = true

    fetch_with_error_checker(
        url = window.location.origin + "/logout", 
        method = "POST", 
        callback = function (json) {
            if (json["payload"]["logout"] == true) {
                window.location.href = window.location.origin
            }
        },
        body = undefined,
        on_error = function (_) {
            logout_button.innerText = "Выйти"
            logout_button.disabled = false
        }
    )
}