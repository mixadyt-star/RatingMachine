var notification_timer;

function fetch_with_error_checker(url, method, callback, body = "{}", on_error = function (json) {console.log(json["error_message"])}) {
    fetch(url, {
        method: method,
        body: body
      })
        .then((response) => response.json())
        .then(function (json) {
            if (json["error"]) {
                on_error(json)
                clearTimeout(notification_timer)
                notification = document.getElementById("notification")
                notification.childNodes[1].childNodes[1].innerText = json["error_message"]
                notification.classList.add("show")
                notification_timer = setTimeout(() => notification.classList.remove("show"), 3000)
            } else {
                callback(json)
            }
    });
}