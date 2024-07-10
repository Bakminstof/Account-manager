"use strict";

import {
    removeAllErrors,
    BaseForm,
    noWhiteSpacePattern,  
    listenInputsFocus, 
    handleValidate,
    checkEmpty,
    sendFormData,
    sendRequest, 
    badRequest, 
} from "../utils.js"

class RegisterForm extends BaseForm {
    form = document.getElementById("register-form");

    constructor () {
        super()
        
        this.username = this.form.querySelector(".auth-item__container > .username");
        this.email = this.form.querySelector(".auth-item__container > .email");
        this.password = this.form.querySelector(".auth-item__container > .password");
        this.passwordCheck = this.form.querySelector(".auth-item__container > .password-check");

        this.fields = [
            this.username,
            this.email,
            this.password,
            this.passwordCheck,
        ]
    }
    
    validateUsername () {
        return noWhiteSpacePattern.test(this.username.value)
    }
    validateEmail () {
        return this.emailPattern.test(this.email.value)
    }
    validatePassword () {
        return this.passwordPattern.test(this.password.value)
    }
    validatePasswordCheck () {
        return this.passwordCheck.value == this.password.value
    }
}

const registerForm = new RegisterForm();

// Check
async function checkUsername(username, canEmpty=false) {   
    if (checkEmpty(username, canEmpty)) {
        if (canEmpty) {
            return true;
        }
        else {
            return false;
        } 
    }

    if (handleValidate(username, registerForm.validateUsername(), "Неверный формат логина") == false) {
        return false;
    } 
        
    if (handleValidate(username, await checkUsernameRequest(username), "Логин занят") == false) {
        return false;
    }

    return true
}

async function checkEmail(email, canEmpty=true) {
    if (checkEmpty(email, canEmpty)) {
        if (canEmpty) {
            return true;
        }
        else {
            return false;
        } 
    }
    
    if (handleValidate(email, registerForm.validateEmail(), "Неверный формат почты") == false) {
        return false;
    }

    if (handleValidate(email, await checkEmailRequest(email), "Почта уже используется") == false) {
        return false;
    }

    return true
}

function checkPassword(password, canEmpty=false) {
    if (checkEmpty(password, canEmpty)) {
        if (canEmpty) {
            return true;
        }
        else {
            return false;
        } 
    }
    
    if (handleValidate(password, registerForm.validatePassword(), "Пароль не соответствует требованиям") == false) {
        return false;
    }
    return true
    
}

function checkPasswordCheck(passwordCheck, canEmpty=false) {
    if (checkEmpty(passwordCheck, canEmpty)) {
        if (canEmpty) {
            return true;
        }
        else {
            return false;
        } 
    }

    if (handleValidate(passwordCheck, registerForm.validatePasswordCheck(), "Пароли не совпадают") == false) {
        return false;
    }

    return true

}

// From validation
async function validationRegisterFrom() {
    var validationResult = true;

    if ((await checkUsername(registerForm.username)) == false) {
        validationResult = false;
    } 

    if ((await checkEmail(registerForm.email, true)) == false) {
        validationResult = false;
    }

    if (checkPassword(registerForm.password) == false) {
        validationResult = false;
    }

    if (checkPasswordCheck(registerForm.passwordCheck) == false) {
        validationResult = false;
    }

    return validationResult
}

async function checkUsernameRequest(usernameItem) {
    return await checkUserData(usernameItem, "username")
}

async function checkEmailRequest(emailItem) {
    return await checkUserData(emailItem, "email")
}

async function checkUserData(item, attributeName, checkURL="/check") {
    let data = {}
    data[attributeName] = item.value

    let responseJSON = await sendRequest(checkURL, "POST", data)

    if (responseJSON == null) {
        return null
    }

    let attr = responseJSON[attributeName]

    if (attr  == "free"){
        return true
    } else if (attr  == "exists") {
        return false 
    }

    return null
}

// Input listeners 
function startRegListeners() {
    listenInputsFocus(registerForm.username, checkUsername, true);
    listenInputsFocus(registerForm.email, checkEmail, true, true);

    listenInputsFocus(registerForm.password, checkPassword);
    listenInputsFocus(registerForm.passwordCheck, checkPasswordCheck);
}


function startRegister() {
    startRegListeners();

    registerForm.form.addEventListener(
        "submit", async function(event) {
            event.preventDefault()

            removeAllErrors(registerForm.fields)

            if (await validationRegisterFrom()) {
                let response = await sendFormData(registerForm, "/register")
                
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
startRegister();
