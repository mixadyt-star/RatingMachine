function null_form() {
    if ( window.history.replaceState ) {
        window.history.replaceState( null, null, window.location.href );
    }
}

function prevent_default(button_id) {
    document.getElementById(button_id).addEventListener("click", function(event) {
        event.preventDefault()
    })
}

function toggle_dark_background(id) {
    document.getElementById(id).classList.toggle("show")
    document.getElementById(id).classList.toggle("hidden")
}