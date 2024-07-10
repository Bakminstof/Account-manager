"use strict";

import {
    removeAllErrors, 
    BaseForm,
    noWhiteSpacePattern,  
    listenInputsFocus, 
    handleValidate,
    checkEmpty,
    sendFormData, 
    badRequest, 
} from "../utils.js"


class AuthForm extends BaseForm {
    form = document.getElementById("auth-form");

    constructor () {
        super();

        this.username = this.form.querySelector(".auth-item__container > .username");
        this.password = this.form.querySelector(".auth-item__container > .password");

        this.fields = [
            this.username,
            this.password,
        ]
    }
    
    validateUsername = () => {
        return noWhiteSpacePattern.test(this.username.value)
    }
}

const authForm = new AuthForm();

function checkUsername(username, canEmpty=false) {
    if (checkEmpty(username, canEmpty)) {
        if (canEmpty) {
            return true;
        }
        else {
            return false;
        } 
    }

    if (handleValidate(username, authForm.validateUsername(), "Неверный формат логина") == false) {
        return false;
    }

    return true
}

// From validation
function validationAuthFrom() {
    let validationResult = true;
    
    if (checkUsername(authForm.username) == false) {
        validationResult = false;
    }

    return validationResult
}

function startAuthListeners() {
    listenInputsFocus(authForm.username, checkUsername);
}

function startAuth() {
    startAuthListeners();

    authForm.form.addEventListener(
        "submit", async function(event) {
            event.preventDefault()


            removeAllErrors(authForm.fields)

            if (validationAuthFrom()) {
                let response = await sendFormData(authForm, "/login")
                
                if (response.ok) {
                    window.location.replace(response.url);
                } else {
                    await badRequest(response)
                }
            }
        }
    )
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
startAuth();
