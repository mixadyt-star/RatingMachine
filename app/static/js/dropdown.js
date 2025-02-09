function toggle_menu(menu_id) {
    menu = document.getElementById(menu_id)
    menu.classList.toggle("show")
}

function init_checkboxes(all_checkbox_id, parent_id) {
    let checkboxes = document.getElementById(parent_id).querySelectorAll("input[name]")
    let all_checkbox = document.getElementById(all_checkbox_id)

    checkboxes.forEach(element => {
        element.addEventListener('change', event => {
            if (event.target.checked) {
                if ([...checkboxes].every(cb => cb.checked === true)) {
                    all_checkbox.checked = true
                }
            } else {
                all_checkbox.checked = false
            }
        })
    });

    all_checkbox.addEventListener('change', event => {
        checkboxes.forEach(element => {
            element.checked = event.target.checked
        })
    })
}

function init_checkboxes_one(parent_id, subject) {
    let checkboxes = document.querySelectorAll("input[name]")
    let image = document.getElementById("mega-diograma-realno")
    inited_image = image.src

    checkboxes.forEach(element => {
        element.addEventListener('change', event => {
            if (event.target.checked) {
                checkboxes.forEach(element => {
                    if (element != event.target) {
                        element.checked = false
                    }
                })
                let image = document.getElementById("mega-diograma-realno")
                let tmp = image.src
                let loader = document.createElement("div")
                
                loader.classList.add("loader")
                loader.setAttribute("style", "--circle: radial-gradient(farthest-side,#0000 calc(95% - 3px),#000 calc(100% - 3px) 98%,#0000 101%) no-repeat;")
                loader.id = "mega-diograma-realno"
                image.replaceWith(loader)
            
                fetch_with_error_checker(
                    url = window.location.origin + "/stats/render",
                    method = "POST",
                    callback = function(json) {
                        setTimeout(function () {
                            let image = document.getElementById("mega-diograma-realno")
                            img = document.createElement("img")
                            img.src = json["payload"]
                            img.id = "mega-diograma-realno"
                            image.replaceWith(img)
                        }, 300)
                    },
                    body = JSON.stringify({
                        id: event.target.value,
                        subject: subject
                    }),
                    onerror = function(_) {
                        setTimeout(function () {
                            let image = document.getElementById("mega-diograma-realno")
                            img = document.createElement("img")
                            img.src = tmp
                            img.id = "mega-diograma-realno"
                            image.replaceWith(img)
                        }, 300)
                    },
                )
            } else {
                let image = document.getElementById("mega-diograma-realno")
                img = document.createElement("img")
                img.src = inited_image
                img.id = "mega-diograma-realno"
                image.replaceWith(img)
            }
        })
    });
}