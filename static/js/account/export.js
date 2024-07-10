"user strict";

import {accountContainerClass} from "../config.js";
import {sendRequest} from "../utils.js";


const exportHeaderMenuClass = "export";

const searchResultClass = "search-result";

const exportButtonClassTXT = "txt-export-button";
const exportButtonClassJSON = "json-export-button";
const exportButtonClassCSV = "csv-export-button";

const exportTypes = {
    csv: "csv",
    json: "json",
    txt: "txt",
}

class AccountExporter {
    #exportItem; 

    constructor (exportItem) {
        this.#exportItem = exportItem;
    }

    #extractAccountsIDs() {
        let accountContainers = this.#exportItem.querySelectorAll(`.${accountContainerClass}`);
        let accountsIDs = [];

        accountContainers.forEach(accountContainer => {
            accountsIDs.push(parseInt(accountContainer.id));
        });

        return accountsIDs;
    }

    bindButtons(
        exportButtonTXT, 
        exportButtonJSON, 
        exportButtonCSV,
    ) {
        exportButtonTXT.onclick = this.#exportAsTXT.bind(this);
        exportButtonJSON.onclick = this.#exportAsJSON.bind(this);
        // exportButtonCSV.onclick = this.#exportAsCSV.bind(this);
    }

    async #exportAsTXT() {
        await this.#sendExportRequest(this.#extractAccountsIDs(), exportTypes.txt);
    }

    async #exportAsJSON() {
        await this.#sendExportRequest(this.#extractAccountsIDs(), exportTypes.json);
    }

    async #exportAsCSV() {
        await this.#sendExportRequest(this.#extractAccountsIDs(), exportTypes.csv);
    }

    async #sendExportRequest(accountsIDs, exportType) {
        if (accountsIDs.length > 0) {
            let exportData = {
                accounts_ids: accountsIDs,
                export_type: exportType
            }

            const response = await sendRequest("/accounts/export", "POST", exportData, true, false);
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            const filename = `Accounts.${exportType}`

            this.#saveFile(blobUrl, filename)

            if (response.ok == false) {
                alert("Произошла ошибка при экспорте");
            }
        }
    }

    #saveFile(url, filename) {
        const a = document.createElement("a");

        a.href = url;
        a.download = filename || "file-name";

        document.body.appendChild(a);

        a.click();

        document.body.removeChild(a);
    }
}


function getExporterButtons(exportItem) {
    let exportButtonTXT = exportItem.querySelector(`.${exportButtonClassTXT}`);
    let exportButtonJSON = exportItem.querySelector(`.${exportButtonClassJSON}`);
    // let exportButtonCSV = exportItem.querySelector(`.${exportButtonClassCSV}`);

    return {
        exportButtonTXT,
        exportButtonJSON,
        // exportButtonCSV,
    }
}


function startMainExporter() {
    const exportHeaderMenu = document.querySelector(`.${exportHeaderMenuClass}`)

    if (exportHeaderMenu) {
        const searchResultContainer = document.querySelector(`.${searchResultClass}`);
        const header = document.querySelector("header");
        
        let buttons = getExporterButtons(header);

        const exporter = new AccountExporter(searchResultContainer);

        exporter.bindButtons(
            buttons.exportButtonTXT, 
            buttons.exportButtonJSON, 
            // buttons.exportButtonCSV,
        );
    }
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
export {getExporterButtons, AccountExporter};
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
startMainExporter();
