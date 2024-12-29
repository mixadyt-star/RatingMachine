function delete_child(child_id) {
    fetch_with_error_checker(
        url = window.location.origin + "/children/class/delete",
        method = "POST",
        callback = function(json) {
            document.location.reload()
        },
        body = JSON.stringify({
            child_id: child_id
        })
    )
}