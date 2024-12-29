function null_form() {
    if ( window.history.replaceState ) {
        window.history.replaceState( null, null, window.location.href );
    }
}