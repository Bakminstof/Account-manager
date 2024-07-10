"use strict";

import {noneElementClass} from "./config.js";
import {hiddenElementClass} from "./config.js";

const emptyStrPattern = new RegExp(/^\s*$/);
const noWhiteSpacePattern = new RegExp(/^\S+$/);


class BaseForm {
    constructor() {
        this.emailPattern = new RegExp(/^\S+@\S+\.\S+$/);
        this.passwordPattern = new RegExp(/^(?=.*[\\!\"\/\*\.\(\)+=-_;%:?&^$#~`])(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^\s]).{8,40}$/);
    }
}

function showElement(element, strict=false) {
    element.classList.remove(hiddenElementClass);
    
    if (strict) {
        element.classList.remove(noneElementClass);
    }
}

function hideElement(element, strict=false) {
    element.classList.add(hiddenElementClass);
    
    if (strict) {
        element.classList.add(noneElementClass);
    }
}

function removeReadonlyInputs(inputs) {
    inputs.forEach(input => {
        input.removeAttribute("readonly");
    });
}


// Listeners
class InputEventListen {
    constructor(account) {
        this.account = account;

        this.inputsListeners = [];
    }

    addInputsEventListeners(inputs, checkFunc) {
        inputs.forEach(input => {
            let listeners = listenInputsFocus(input, checkFunc);
            this.inputsListeners.push([input, listeners]);
        });
    }

    removeInputsEventListeners() {
        this.inputsListeners.forEach(inputListenerPair => {
            let input = inputListenerPair[0];
            let listener = inputListenerPair[1];

            for (const [eventName, callback] of Object.entries(listener)) {
                input.removeEventListener(eventName, callback);
            };
        });

        this.inputsListeners = [];
    }

}


function listenInputsFocus(
    input, 
    checkFunc, 
    isAsyncFunc=false, 
    canEmpty=false,
) {
    let focusin, focusout;

    function focusinCallback (event)  {
        removeError(event.target);
    }
    
    function focusoutCallback (event)  {
        checkFunc(input, canEmpty);
    }

    async function focusoutAsyncCallback (event)  {
        await checkFunc(input, canEmpty);
    }

    input.addEventListener('focusin', focusinCallback);
    focusin = focusinCallback

    if (isAsyncFunc == true) {
        input.addEventListener('focusout', focusoutAsyncCallback);
        focusout = focusoutAsyncCallback;
    } else {
        input.addEventListener('focusout', focusoutCallback);
        focusout = focusoutCallback;
    }

    return {focusin, focusout}
}

// 
function getAccountInputs(account) {
    return account.querySelectorAll("input");
}
// 

// Validation errors
class ValidationErrorEditor {
    #errorInputClass = "validation-error";
    #validationErrorLabelClass = "validation-error-label";

    #validationErrorLabel;

    constructor() {
        this.#validationErrorLabel = this.#makeValidationErrorLabel();
    }

    #makeValidationErrorLabel() {
        let label = document.createElement("span");
        label.classList.add(this.#validationErrorLabelClass)
        return label;
    }

    #getErrorLabel() {
        return this.#validationErrorLabel.cloneNode(true);
    }

    createError(element, text) {
        let error = this.#getErrorLabel();
        let parent = element.parentElement;

        element.classList.add(this.#errorInputClass);
        error.innerHTML = text;

        parent.appendChild(error);
    }

    removeError(element) {
        let parent = element.parentElement
        let error = parent.querySelector(`.${this.#validationErrorLabelClass}`);

        if (error) {
            element.classList.remove(this.#errorInputClass);
            parent.removeChild(error);
        }
    }
}

const validationErrorEditor = new ValidationErrorEditor();

function createError(element, text) {
    validationErrorEditor.createError(element, text);
}

function removeError(element) {
    validationErrorEditor.removeError(element);
}

function removeAllErrors(items) {
    items.forEach(item => {
        removeError(item);
    });
}

function handleValidate(element, checkResult, errorText) {
    if (checkResult == false) {
        createError(element, errorText)
        return false
    }
    return true
}

// Fields
function getValueOrNull(attribute) {
    if (!attribute || emptyStrPattern.test(attribute.value)) {
        return null
    }
    return attribute.value
}

function checkEmpty(element, canEmpty=false, showError=true) {
    if (emptyStrPattern.test(element.value)) {
        if (canEmpty == false && showError == true) {
            createError(element, "Обязательное поле");
        }
        return true;
    }
    return false;
}

function checkField(field, canEmpty=false) { 
    if (field == null) {
        return null;
    } 

    if (checkEmpty(field, canEmpty)) {
        if (canEmpty) {
            return true;
        }
        else {
            return false;
        } 
    }
    return true
}

function checkFields(fields) {
    let validateFlag = true;

    fields.forEach(field => {
        if (checkField(field) == false && validateFlag == true) {
            validateFlag = false;
        }
    });

    return validateFlag;
}

// HTTP requests
async function sendRequest(url, method="POST", data=null, returnErrors=false, returnJSON=true) {
    try {
        const response = await fetch(url, {
            method: method, // *GET, POST, PUT, DELETE, etc.
            mode: "cors", // no-cors, *cors, same-origin
            cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
            credentials: "same-origin", // include, *same-origin, omit
            headers: {
                "Content-Type": "application/json", // 'application/x-www-form-urlencoded'
            },
            redirect: "follow", // manual, *follow, error
            referrerPolicy: "no-referrer", // no-referrer, *client
            body: JSON.stringify(data), // body data type must match "Content-Type" header
        });

        if (response.ok || returnErrors == true) {
            if (returnJSON==true) {
                return await response.json();
            } else {
                return response
            }
        }

    } catch(error) {
        console.log("Error", error)
    }

    return null
}

async function sendFormData(form, URL) {
    let data = {}

    form.fields.forEach(field => {
        data[field.name] = getValueOrNull(field);
    });

    return await sendRequest(URL, "POST", data, true, false)
}

async function badRequest(response) {
    let errorData = await response.json();
    let error_locations = errorData["error_locations"]

    if (error_locations != undefined) {
        error_locations.forEach(location => {
            createError(
                document.getElementById(location), 
                errorData["error_message"],
            )
        });
    }

}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
export {
    emptyStrPattern,
    noWhiteSpacePattern,
    getValueOrNull, 
    removeAllErrors, 
    BaseForm,
    createError, 
    removeError,
    handleValidate,
    checkEmpty,
    listenInputsFocus,
    sendRequest,
    sendFormData,
    badRequest,
    // 
    showElement,
    hideElement,
    removeReadonlyInputs,
    // Mixins
    InputEventListen,
    // Fields
    checkField,
    checkFields,
    getAccountInputs
};