async function check_login() {
    submit_button = document.getElementById("submit-login")
    submit_button.innerHTML = '<div class="loader"></div>'
    submit_button.disabled = true

    email = document.getElementById("email-input").value
    password = await sha256(document.getElementById("password-input").value)

    fetch_with_error_checker(
        url = window.location.origin + "/login",
        method = "POST",
        callback = function(json) {
            if (json["payload"]["login"] == true) {
                window.location.href = window.location.origin
            }
        },
        body = JSON.stringify({
            type: "Teacher",
            email: email,
            password: password
        }),
        on_error = function(_) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Сохранить"
            }, 1000)
        }
    )
}