"use strict";

import {
    removeAllErrors,
    getValueOrNull, 
    sendRequest, 
    checkEmpty, 
    InputEventListen, 
    removeReadonlyInputs, 
    createError, 
    removeError,
    checkField,
    checkFields,
    getAccountInputs,
} from "../utils.js";
import {makePopup} from "../popup/popup.js"
import {
    mainClass,
    accountBaseClass, 
    accountContainerClass, 
    accountContentClass,
} from "../config.js";

const detailsContainerClass = "account-details__container";
export const detailsContentClass = "account-details__content";
export const detailsAddRowButtonClass = "account-details__add-row-button";


class AccountDetails {
    #templateClass = "account-details-template";
    #removeRowButtonClass = "remove-row";

    #rowListeners;

    #detailsNode;

    #buttonCounter;

    constructor(detailsContainer) {
        this.detailsContainer = detailsContainer;

        this.#rowListeners = {};
        this.#buttonCounter = 0;
    }

    bindRowAddButton(detailsAddRowButton) {
        this.#setRowAddEventListener(detailsAddRowButton);
        this.#loadTemplate();
    }

    reset () {
        this.detailsContainer.innerHTML = "";
        this.#resetListeners();
        this.#addRow();
    }

    setRowRemoveButtons() {
        const content = this.detailsContainer.querySelectorAll(`.${detailsContentClass}`);

        content.forEach(detailsContent => {
            this.#addRowRemoveButton(detailsContent);
        });
    }

    unsetRowRemoveButtons() {
        const content = this.detailsContainer.querySelectorAll(`.${detailsContentClass}`);

        content.forEach(detailsContent => {
            this.#removeRowRemoveButton(detailsContent);
        });

        this.#resetListeners();
    }

    #createRowRemoveButton() {
        const button = document.createElement("button");
        
        button.id = this.#buttonCounter++;

        button.classList.add(this.#removeRowButtonClass);
        return button
    }

    #resetListeners() {
        this.#rowListeners = {};
        this.#buttonCounter = 0;
    }
    
    #addRowRemoveButton(detailsContent) {
        const current = this;
        const removeRowButton = this.#createRowRemoveButton();

        detailsContent.appendChild(removeRowButton);
        
        removeRowButton.addEventListener("click", function listener(event) {
            current.#rowListeners[removeRowButton.id] = listener;

            current.#removeRow(removeRowButton, detailsContent);
        });
    }

    #removeRowRemoveButton(detailsContent) {
        const button = detailsContent.querySelector(`.${this.#removeRowButtonClass}`);

        this.#removeRowRemoveEventListener(button);

        detailsContent.removeChild(button);
    }

    #addRow () {
        let row = this.#detailsNode.cloneNode(true);
        
        this.detailsContainer.appendChild(row);

        this.#addRowRemoveButton(this.detailsContainer.lastElementChild);
    }

    #removeRowRemoveEventListener (removeRowButton) {
        removeRowButton.removeEventListener("click", this.#rowListeners[removeRowButton.id]);

        delete this.#rowListeners[removeRowButton.id];
    }

    #removeRow(removeRowButton, detailsContent) {
        this.#removeRowRemoveEventListener(removeRowButton);
        
        this.detailsContainer.removeChild(detailsContent);
    }

    #setRowAddEventListener(button) {
        if (button) {
            const details = this;

            button.addEventListener("click", function (event) {
                details.#addRow();
            });
        }
    }

    #loadTemplate() {
        let template = document.querySelector(`.${this.#templateClass}`);
        let templateNode = document.importNode(template.content, true);

        removeReadonlyInputs(templateNode.querySelectorAll("input"));

        this.#detailsNode = templateNode;
    }
} 


export function makeAccountDetails(accountBase, bindRowAddButton=true) {
    const detailsContainer = accountBase.querySelector(`.${detailsContainerClass}`);
    const details = new AccountDetails(detailsContainer);

    if (bindRowAddButton) {
        const detailsAddRowButton = accountBase.querySelector(`.${detailsAddRowButtonClass}`);

        details.bindRowAddButton(detailsAddRowButton);
    }

    return details;
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
class AccountCreateStatusIndicator {
    #accountCreatedClass = "account-created";

    #accountCreatedLabel;

    constructor(accountTitleContainer, timeout=2000) {
        this.accountTitleContainer = accountTitleContainer;
        this.timeout = timeout;

        this.#accountCreatedLabel = this.#makeAccountCreatedLabel();
    }

    #makeAccountCreatedLabel() {
        let label = document.createElement("span");
        label.classList.add(this.#accountCreatedClass)
        return label;
    }

    #getLabel() {
        return this.#accountCreatedLabel.cloneNode(true);
    }

    showAccountCreatedLabel() {
        const timeout = this.timeout;
        let accountTitleContainer = this.accountTitleContainer;
        let label = this.#getLabel();

        label.innerHTML = "Аккаунт успешно создан";
        accountTitleContainer.appendChild(label)

        setTimeout(function () {
            accountTitleContainer.removeChild(label)
        }, timeout);
    }
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
class AccountCreateForm extends InputEventListen {
    constructor(
        accountContent,
        name, 
        details, 
        accountCreateButton, 
        indicator, 
        accountDataExtractor,
    ) {
        super(accountContent);

        this.accountContent = accountContent;

        this.name = name;
        this.details = details;

        this.inputs = [];

        this.accountCreateButton = accountCreateButton;

        this.indicator = indicator;

        this.accountDataExtractor = accountDataExtractor;
    }

    init() {
        this.setButtonEventListener(this.accountCreateButton); 

        this.details.setRowRemoveButtons();
    }
    
    setButtonEventListener(button, eventName="click") {
        // Проверка всех инпутов и формирование данных аккаунта
        const accountDataExtractor = this.accountDataExtractor;
        let current = this;     

        button.addEventListener(eventName, async function (event) {
            event.preventDefault();

            current.inputs = getAccountInputs(current.account);
            removeAllErrors(current.inputs);
            
            if (checkFields(current.inputs)) {
                let data = accountDataExtractor.extractData();

                await current.handleButtonEvent(data);
            } else if (current.inputsListeners.length == 0) {
                current.addInputsEventListeners(current.inputs, checkField);
            }
        });
    }

    async handleButtonEvent(newAccountData) {
        if (newAccountData) {
            const response = await sendRequest("/accounts/create", "POST", newAccountData, true, false);

            if (response.ok) {
                this.indicator.showAccountCreatedLabel();

            } else {
                const responseJSON = await response.json()
                let accountNameInput = this.name;

                createError(accountNameInput, responseJSON["error_message"]);

                accountNameInput.addEventListener("focusout", function(event) {
                    removeError(accountNameInput);
                })
            }
        }
    }

    reset() {
        this.name.value = "";
        this.details.reset();

        this.removeInputsEventListeners();

        removeAllErrors(this.inputs);
    }
}


const accountTitleClass = "account-title__name";


export function getAccountName(accountCreateBase) {
    return accountCreateBase.querySelector(`.${accountTitleClass}`);
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
export class AccountDataExtractor  {
    #detailNameClass = "account-detail__name";
    #detailValueClass = "account-detail__value";

    #accountNameItem;
    #accountDetails;

    constructor(accountNameItem, accountDetails) {
        this.#accountNameItem = accountNameItem;
        this.#accountDetails = accountDetails;
    }

    #extractDetailsData () {
        const detailsItems = this.#accountDetails.detailsContainer.querySelectorAll(`.${detailsContentClass}`);

        let detailsData = {};

        detailsItems.forEach(element => {
            const accountAttrName = getValueOrNull(element.querySelector(`.${this.#detailNameClass}`));

            if (accountAttrName) {
                detailsData[accountAttrName] = getValueOrNull(element.querySelector(`.${this.#detailValueClass}`));
            }
        });

        return detailsData
    }

    extractData () {
        let data = this.#extractDetailsData();

        if (checkEmpty(this.#accountNameItem)) {
            return false;
        }

        if (Object.keys(data).length !== 0) {
            return {name: this.#accountNameItem.value, data: data}
        }
    }
}


export function makeDataExtractor (accountCreateBase, accountName=null, accountDetails=null) {
    if (accountName && accountDetails) {
        return new AccountDataExtractor(accountName, accountDetails);
    }

    let name = getAccountName(accountCreateBase);
    let details = makeAccountDetails(accountCreateBase, false);
    
    return new AccountDataExtractor(name, details);
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
class AccountCreateFormFactory {
    templateClass = "account-create-template";

    accountCreateFormID = "add-account";

    accountCreateBaseClass = "account-create";
    accountCreateContainerClass = "account-create__container";
    accountCreateContentClass = "account-create__content";

    accountCreateButtonClass = "account-create__button";

    accountTitleContainerClass = "account-title__container";

    constructor() {
        this.#insertTemplate();
    }

    makeAccountCreateForm(accountCreateBase) {
        let accountCreateContainer = this.#getAccountCreateContainer(accountCreateBase);
        let accountCreateContent = this.#getAccountCreateContent(accountCreateBase);

        let accountCreateButton = this.#getAccountCreateButton(accountCreateBase); 

        let name = getAccountName(accountCreateBase);
        let details = makeAccountDetails(accountCreateBase);
        
        let indicator = this.#makeIndicator(this.#getAccountTitleContainer(accountCreateBase));
        let extractor = makeDataExtractor(accountCreateBase, name, details);

        this.#addAccountCreateFormClasses(
            accountCreateBase, 
            accountCreateContainer, 
            accountCreateContent,
        );

        this.#setAccountCreateFormID(accountCreateBase);

        removeReadonlyInputs(accountCreateBase.querySelectorAll("input"));

        let form = new AccountCreateForm(
            accountCreateContent, 
            name, 
            details, 
            accountCreateButton, 
            indicator,
            extractor,
        );

        form.init();

        return form;
    }

    #insertTemplate() {
        let main = document.querySelector(`.${mainClass}`);
        let template = document.querySelector(`.${this.templateClass}`);

        if (template) {
            let templateNode = document.importNode(template.content, true);

            main.appendChild(templateNode);
        } else {
            console.log("Unauthorized");
        }
    }

    #makeIndicator(accountTitleContainer) {
        return new AccountCreateStatusIndicator(accountTitleContainer);
    }

    #getAccountTitleContainer(accountCreateBase) {
        return accountCreateBase.querySelector(`.${this.accountTitleContainerClass}`);
    }

    #getAccountCreateButton(accountCreateBase) {
        return accountCreateBase.querySelector(`.${this.accountCreateButtonClass}`);
    }

    #getAccountCreateContainer(accountCreateBase) {
        return accountCreateBase.querySelector(`.${accountContainerClass}`);
    }

    #getAccountCreateContent(accountCreateBase) {
        return accountCreateBase.querySelector(`.${accountContentClass}`);
    }
    
    #setAccountCreateFormID(accountCreateBase) {
        accountCreateBase.setAttribute("id", this.accountCreateFormID);
    }

    #addAccountCreateFormClasses(accountCreateBase, accountCreateContainer, accountCreateContent) {
        accountCreateBase.classList.add(this.accountCreateBaseClass);
        accountCreateContainer.classList.add(this.accountCreateContainerClass);
        accountCreateContent.classList.add(this.accountCreateContentClass);
    }
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
const accountCreateFormFactory = new AccountCreateFormFactory();

const accountCreateTitleClass = "account-create__title";
const accountCreateCloseButtonClass = "account-create__close";
const accountAddLinkClass = "account-add__lnk";

const accountCreateTitle = document.querySelector(`.${accountCreateTitleClass}`);
const accountAddLink = document.querySelector(`.${accountAddLinkClass}`);


function startAccountsCreateForm() {
    if (accountCreateTitle) {
        const accountBase = accountCreateTitle.closest(`.${accountBaseClass}`);
    
        let accountCreateForm = accountCreateFormFactory.makeAccountCreateForm(accountBase);
        let accountCreateCloseButton = accountBase.querySelector(`.${accountCreateCloseButtonClass}`)

        makePopup(
            accountBase, 
            accountAddLink, 
            accountCreateCloseButton, 
            300,
            accountCreateForm.reset.bind(accountCreateForm), 
            accountCreateForm.reset.bind(accountCreateForm),
        );
    }
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
startAccountsCreateForm();