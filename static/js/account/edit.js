"use strict";

import {
    sendRequest, 
    showElement, 
    hideElement, 
    InputEventListen,
    checkField,
    removeAllErrors,
    checkFields,
    getAccountInputs,
} from "../utils.js";
import {accountBaseClass, accountContainerClass} from "../config.js";
import {makeDataExtractor, makeAccountDetails, detailsAddRowButtonClass} from "./acc.js";
import {getExporterButtons, AccountExporter} from "./export.js"



class ChangeManger extends InputEventListen {
    #itemChangeClass = "item-change";

    #accountBase;
    #accountID;

    #accountDetails;

    #cache;

    constructor(accountBase, accountID, accountDetails, dataExtractor) {        
        super(accountBase);
        this.#accountBase = accountBase;
        this.#accountID = accountID;

        this.#accountDetails = accountDetails;

        this.dataExtractor = dataExtractor;

        this.#cache = [];
    }

    startChange() {
        const inputs = getAccountInputs(this.#accountBase);

        this.#accountDetails.setRowRemoveButtons();

        inputs.forEach(input => {
            this.#makeCache(input);

            input.classList.add(this.#itemChangeClass)
            input.removeAttribute("readonly");
        });

        this.addInputsEventListeners(inputs, checkField);
    }

    stopChange() {
        const inputs = getAccountInputs(this.#accountBase);
        
        this.#accountDetails.unsetRowRemoveButtons();
        
        inputs.forEach(input => {
            input.classList.remove(this.#itemChangeClass);
            input.setAttribute("readonly", "");
        });

        this.removeInputsEventListeners();

        removeAllErrors(inputs);

        this.#cache = [];
    }

    async approveChange() {
        const inputs = getAccountInputs(this.#accountBase);

        this.removeInputsEventListeners();

        removeAllErrors(inputs);

        if (checkFields(inputs)) {
            let data = this.dataExtractor.extractData();

            await this.handleButtonEvent(data);
        }

        this.stopChange();
    }

    rollbackChange() {
        this.#cache.forEach(cachePair => {
            const input = cachePair[0], inputValue = cachePair[1];

            input.value = inputValue;
        });

        this.stopChange();
    }

    #makeCache(input) {
        this.#cache.push([input, input.value]);
    }

    async handleButtonEvent(updatedData) {
        if (updatedData) {
            let data = {id: this.#accountID, ...updatedData};

            const response = await sendRequest("/accounts/update/", "PATCH", data, true, false);

            if (response.ok == false) {
                this.rollbackChange();
            }
        }
    }
}


function makeChangeManager(accountBase) {
    const accountContainer = accountBase.querySelector(`.${accountContainerClass}`);
    const dataExtractor = makeDataExtractor(accountBase);
    const details = makeAccountDetails(accountBase);

    const accountID = parseInt(accountContainer.id);

    return new ChangeManger(accountBase, accountID, details, dataExtractor);
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
class DeleteManager {
    #accountContainer;
    #accountID;

    constructor (accountContainer) {
        this.#accountContainer  = accountContainer;
        this.#accountID = parseInt(this.#accountContainer.id)
    }

    async deleteAccount(onDelete=null) {
        const response = await sendRequest(`/accounts/delete/${this.#accountID}`, "DELETE", null, true, false);

        if (response.ok && onDelete) {
            onDelete();
        } else {
            alert("Произошла ошибка при удалении");
        }
    }
}


class AccountButtonsGUI {
    #accountContainer;

    #buttonChange;
    #buttonSave;
    #buttonRollback;
    #buttonDelete;

    #buttonsExport;

    #buttonDetailsRowAdd;

    constructor(
        accountContainer, 
        buttonChange, 
        buttonSave, 
        buttonRollback, 
        buttonDelete,
        buttonsExport,
        buttonDetailsRowAdd,
    ) {        
        this.#accountContainer = accountContainer;

        this.#buttonChange = buttonChange;
        this.#buttonSave = buttonSave;
        this.#buttonRollback = buttonRollback;
        this.#buttonDelete = buttonDelete;

        this.#buttonsExport = Object.values(buttonsExport);

        this.#buttonDetailsRowAdd = buttonDetailsRowAdd;
    }

    showButtons(buttons, strict=false) {
        buttons.forEach(button => {
            showElement(button, strict);
        });
    }

    hideButtons(buttons, strict=false) {
        buttons.forEach(button => {
            hideElement(button, strict);
        });
    }

    hideAccount() {
        hideElement(this.#accountContainer.parentElement, true);
    }

    showOnStartChange () {
        this.showButtons([this.#buttonDelete, this.#buttonDetailsRowAdd]);
        this.showButtons([this.#buttonSave, this.#buttonRollback], true);
        
        hideElement(this.#buttonChange, true);
        this.hideButtons(this.#buttonsExport, true);
    }

    showOnStopChange () {
        this.hideButtons([this.#buttonSave, this.#buttonRollback], true);

        showElement(this.#buttonChange, true);
        this.hideButtons([this.#buttonChange, this.#buttonDelete, this.#buttonDetailsRowAdd]);

        this.showButtons(this.#buttonsExport, true);
        this.hideButtons(this.#buttonsExport);
    }
}


class AccountEditor {
    #accountBase;

    #accountGUI;

    #changer;
    #remover;
    #exporter;
    
    #buttonChange;
    #buttonSave;
    #buttonRollback;
    #buttonDelete;

    #exporterButtons;

    #accountEditClass = "account-edit";

    constructor(
        accountBase, 
        accountGUI,
        changer,
        remover,
        exporter,
        buttonChange,
        buttonSave,
        buttonRollback,
        buttonDelete,
        exporterButtons,
        ) {
        this.#accountBase = accountBase;

        this.#accountGUI = accountGUI;

        this.#changer = changer;
        this.#remover = remover;
        this.#exporter = exporter;

        this.#buttonChange = buttonChange;
        this.#buttonSave = buttonSave;
        this.#buttonRollback = buttonRollback;
        this.#buttonDelete = buttonDelete;

        this.#exporterButtons = exporterButtons;
    }

    init() {
        this.#setOnClickEvents();

        this.#exporter.bindButtons(
            this.#exporterButtons.exportButtonTXT,
            this.#exporterButtons.exportButtonJSON,
            this.#exporterButtons.exportButtonCSV,
        )
    }

    #setOnClickEvents() {
        this.#buttonChange.onclick = this.#startChange.bind(this);
        this.#buttonSave.onclick = this.#approveChange.bind(this);
        this.#buttonRollback.onclick = this.#rollbackChange.bind(this);
        this.#buttonDelete.onclick = this.#doDelete.bind(this);
    }

    #startChange() {
        this.#changer.startChange();

        this.#accountBase.classList.add(this.#accountEditClass);

        this.#accountGUI.showOnStartChange();
    }

    async #approveChange() {
        await this.#changer.approveChange();

        this.#accountBase.classList.remove(this.#accountEditClass);

        this.#accountGUI.showOnStopChange();
    }

    #rollbackChange() {
        this.#changer.rollbackChange();

        this.#accountBase.classList.remove(this.#accountEditClass);

        this.#accountGUI.showOnStopChange();
    }

    #doDelete() {
        this.#remover.deleteAccount(this.#accountGUI.hideAccount.bind(this.#accountGUI));

        this.#accountBase.classList.remove(this.#accountEditClass);

        this.#accountGUI.showOnStopChange();
    }
}


class AccountEditorFactory {
    #changeButtonClass = "change-button";
    #saveButtonClass = "save-button";
    #rollbackButtonClass = "rollback-button";
    #deleteButtonClass = "delete-button";
    
    makeEditor(accountBase) {
        const accountContainer = accountBase.querySelector(`.${accountContainerClass}`);

        const editorButtons = this.#getEditorButtons(accountContainer);
        const exporterButtons = getExporterButtons(accountContainer);
        const exporter = this.#makeExporter(accountBase);

        const detailsAddRowButton = this.#getDetailsAddRowButton(accountBase)

        const gui = this.#makeButtonsGUI(
            accountContainer,
            editorButtons.buttonChange,
            editorButtons.buttonSave,
            editorButtons.buttonRollback,
            editorButtons.buttonDelete,
            exporterButtons,
            detailsAddRowButton,
        )

        return new AccountEditor(
            accountBase,
            gui,
            makeChangeManager(accountBase),
            this.#makeRemover(accountContainer),
            exporter,
            editorButtons.buttonChange,
            editorButtons.buttonSave,
            editorButtons.buttonRollback,
            editorButtons.buttonDelete,
            exporterButtons,
        )
    }

    #getEditorButtons(accountContainer) {
        const buttonChange = accountContainer.querySelector(`.${this.#changeButtonClass}`);
        const buttonSave = accountContainer.querySelector(`.${this.#saveButtonClass}`);
        const buttonRollback = accountContainer.querySelector(`.${this.#rollbackButtonClass}`);
        const buttonDelete = accountContainer.querySelector(`.${this.#deleteButtonClass}`);
        
        return {
            buttonChange,
            buttonSave,
            buttonRollback,
            buttonDelete,
        }
    }

    #getDetailsAddRowButton(accountBase) {
        return accountBase.querySelector(`.${detailsAddRowButtonClass}`);
    }

    #makeRemover(accountContainer) {
        return new DeleteManager(accountContainer);
    }

    #makeExporter(accountBase) {
        return new AccountExporter(accountBase);
    }

    #makeButtonsGUI(
        accountContainer, 
        buttonChange, 
        buttonSave, 
        buttonRollback, 
        buttonDelete, 
        exporterButtons,
        detailsAddRowButton,
    ) {
        return new AccountButtonsGUI(
            accountContainer,
            buttonChange,
            buttonSave,
            buttonRollback,
            buttonDelete,
            exporterButtons,
            detailsAddRowButton,
        )
    }
}


function startEditors() {
    const accountEditorFactory = new AccountEditorFactory();

    let accounts = document.getElementsByClassName(accountBaseClass);

    for (let index = 0; index < accounts.length; index++) {
        let account = accounts[index];

        if (account.classList.length == 1) {
            const accountEditor = accountEditorFactory.makeEditor(account);
            
            accountEditor.init();
        }
    }
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
startEditors();
