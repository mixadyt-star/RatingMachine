function delete_test(test_id) {
    fetch_with_error_checker(
        url = window.location.origin + "/tests/delete",
        method = "POST",
        callback = function(json) {
            document.location.reload()
        },
        body = JSON.stringify({
            test_id: test_id
        })
    )
}

function generate_blanks(test_id) {
    let checkboxes = document.querySelectorAll("input[name='children']")
    children = []

    checkboxes.forEach(element => {
        if (element.checked) {
            children.push(element.value)
        }
    })

    fetch_with_error_checker(
        url = window.location.origin + "/tests/download",
        method = "POST",
        callback = function(json) {
            base64 = json["payload"]
            fetch(
                `data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,${base64}`
            ).then(res => {
                    res.blob().then(blob => {
                        file = new File([blob], "Бланки.docx", {
                            type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        })
                        url = window.URL.createObjectURL(file)
                        window.location.assign(url)
                    })
            })
        },
        body = JSON.stringify({
            children: children,
            test_id: test_id
        }),
    )
}

function save_answers(test_id) {
    let inputs = document.getElementsByName(`answer-input-${test_id}`)

    let answers = []
    inputs.forEach(element => {
        answers.push(element.value)
    })

    submit_button = document.getElementById(`save-answers-button-${test_id}`)
    submit_button.innerHTML = '<div class="loader"></div>'
    submit_button.disabled = true

    fetch_with_error_checker(
        url = window.location.origin + "/tests/answers",
        method = "POST",
        callback = function(json) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Сохранить"
            }, 1000)
        },
        body = JSON.stringify({
            answers: answers,
            test_id: test_id
        }),
        on_error = function(_) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Сохранить"
            }, 1000)
        }
    )
}

function edit_quests(test_id) {
    toggle_dark_background(`dark-background-quests-${test_id}`)
    toggle_dark_background(`edit-quests-wrapper-${test_id}`)

    setTimeout(function() {
        document.addEventListener("click", function handler(event) {
            if (!document.getElementById(`edit-quests-block-${test_id}`).contains(event.target)) {
                toggle_dark_background(`dark-background-quests-${test_id}`)
                toggle_dark_background(`edit-quests-wrapper-${test_id}`)
                document.removeEventListener("click", handler)
            }
        })
    }, 100)
}

function edit_tests(test_id) {
    toggle_dark_background(`dark-background-${test_id}`)
    toggle_dark_background(`edit-test-wrapper-${test_id}`)

    setTimeout(function() {
        document.addEventListener("click", function handler(event) {
            if (!document.getElementById(`edit-test-block-${test_id}`).contains(event.target)) {
                toggle_dark_background(`dark-background-${test_id}`)
                toggle_dark_background(`edit-test-wrapper-${test_id}`)
                document.removeEventListener("click", handler)
            }
        })
    }, 100)
}

function show_blanks(test_id) {
    toggle_dark_background(`dark-background-blanks-${test_id}`)
    toggle_dark_background(`show-blanks-wrapper-${test_id}`)

    let checkboxes = document.querySelectorAll("input[name='children']")
    children = []

    checkboxes.forEach(element => {
        if (element.checked) {
            children.push(element.value)
        }
    })

    setTimeout(function() {
        document.addEventListener("click", function handler(event) {
            if (!document.getElementById(`show-blanks-block-${test_id}`).contains(event.target)) {
                toggle_dark_background(`dark-background-blanks-${test_id}`)
                toggle_dark_background(`show-blanks-wrapper-${test_id}`)
                document.removeEventListener("click", handler)
            }
        })
    }, 100)
}

function set_input_range(name) {
    document.getElementsByName(name).forEach(element => {
        element.onkeydown = function(e) {
            if (!"123456789".includes(e.key)) {
                e.preventDefault()
            }
        }
    })
}

function save_questions(test_id, questions) {
    submit_button = document.getElementById(`input-button-${test_id}`)
    submit_button.innerHTML = '<div class="loader"></div>'
    submit_button.disabled = true

    fetch_with_error_checker(
        url = window.location.origin + "/tests/upload_questions",
        method = "POST",
        callback = function(json) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Выгрузить вопросы"
            }, 1000)
        },
        body = JSON.stringify({
            questions: questions,
            test_id: test_id
        }),
        on_error = function(_) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Выгрузить вопросы"
            }, 1000)
        }
    )
}

function output_file(test_id) {
    submit_button = document.getElementById(`output-button-${test_id}`)
    submit_button.innerHTML = '<div class="loader"></div>'
    submit_button.disabled = true

    fetch_with_error_checker(
        url = window.location.origin + "/tests/download_questions",
        method = "POST",
        callback = function(json) {
            if (json["payload"]) {
                let byte_string = atob(json["payload"].split(',')[1])
                let mime_string = json["payload"].split(',')[0].split(':')[1].split(';')[0]
                let buffer = new ArrayBuffer(byte_string.length)
                let char_array = new Uint8Array(buffer)

                for (let i = 0; i < byte_string.length; i++) {
                    char_array[i] = byte_string.charCodeAt(i)
                }

                let blob = new Blob([buffer], {
                    type: mime_string
                })

                let file = new File([blob], "Вопросы.docx", {
                    type: mime_string
                })

                let url = window.URL.createObjectURL(file)
                window.location.assign(url)
            }
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Скачать вопросы"
            }, 1000)
        },
        body = JSON.stringify({
            test_id: test_id
        }),
        on_error = function(_) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Скачать вопросы"
            }, 1000)
        }
    )
}

function save_blanks(blanks) {
    submit_button = document.getElementById("input-blanks-button")
    submit_button.innerHTML = '<div class="loader"></div>'
    submit_button.disabled = true

    fetch_with_error_checker(
        url = window.location.origin + "/tests/upload_blanks",
        method = "POST",
        callback = function(json) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Загрузить заполненные бланки ответов"
            }, 1000)
        },
        body = JSON.stringify({
            blanks: blanks
        }),
        onerror = function(_) {
            setTimeout(function () {
                submit_button.disabled = false
                submit_button.innerText = "Загрузить заполненные бланки ответов"
            }, 1000)
        },
    )
}

function init_file_input(test_id) {
    let input = document.getElementById(`file-input-${test_id}`)
    let button = document.getElementById(`input-button-${test_id}`)

    button.addEventListener("click", event => {
        input.click()
    })

    input.addEventListener("change", event => {
        let file = event.target.files[0]
        if (file) {
            let reader = new FileReader()

            reader.onload = event => {
                save_questions(test_id, event.target.result)
            }

            reader.readAsDataURL(file)
        }
    })
}

function init_blanks_input() {
    let input = document.getElementById("input-blanks")
    let button = document.getElementById("input-blanks-button")

    button.addEventListener("click", event => {
        input.click()
    })

    input.addEventListener("change", event => {
        let files = [...event.target.files]
        let buffer = Array()

        files.forEach(file => {
            if (file) {
                let reader = new FileReader()

                reader.onload = event => {
                    buffer.push(event.target.result)
                    if (buffer.length == files.length) {
                        save_blanks(buffer)
                    }
                }

                reader.readAsDataURL(file)
            }
        })
    })
}