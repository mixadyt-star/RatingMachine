function password_eye_click(password_id, eye_id) {
    password_input = document.getElementById(password_id)
    password_eye = document.getElementById(eye_id)

    if (password_input.type == "password") {
        password_input.type = "text"
        password_eye.innerHTML = `
        <path d="M19.5 16L17.0248 12.6038" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 17.5V14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M4.5 16L6.96895 12.6124" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M3 8C6.6 16 17.4 16 21 8" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        `
    } else {
        password_input.type = "password"
        password_eye.innerHTML = `
        <path d="M3 13C6.6 5 17.4 5 21 13" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 17C10.3431 17 9 15.6569 9 14C9 12.3431 10.3431 11 12 11C13.6569 11 15 12.3431 15 14C15 15.6569 13.6569 17 12 17Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        `
    }
}