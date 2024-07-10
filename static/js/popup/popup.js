"use strict";

import {
    bodyClass, 
    bodyContainerClass,
    mainClass,
    accountContainerClass, 
    accountContentClass
} from "../config.js";

class PopupFactory {
    constructor(documentBody) {
        this.documentBody = documentBody;
    }

    makePopup(
        accountBase, 
        openButton, 
        closeButton,         
        timeout,
        onOpen,
        onClose,
    ) {
        let popupContainer = this.#getPopupContainer(accountBase);
        let popupContent = this.#getPopupContent(accountBase);
        let lockPaddingItems = this. #getLockPaddingItems();
        let documentMain = this.#getDocumentMain();

        let popup = new Popup(
            accountBase, 
            popupContainer, 
            popupContent,
            openButton,
            closeButton,
            lockPaddingItems,  
            documentMain,
            timeout,
            onOpen,
            onClose,
        );

        popup.init();
        return popup;
    }

    #getDocumentMain() {
        return document.querySelector(mainClass);
    }

    #getPopupContainer(accountBase) {
        return accountBase.querySelector(`.${accountContainerClass}`);

    }
    #getPopupContent(accountBase) {
        return accountBase.querySelector(`.${accountContentClass}`);
    }

    #getLockPaddingItems() {
        return document.querySelectorAll(`.${Popup.prototype.lockPaddingClass}`);
    }

}

class Popup {
    popupBaseClass = "popup";
    popupContainerClass = "popup-container";
    popupContentClass = "popup-content";
    
    openPopupClass = "open-popup";

    popupCloseButtonClass = "popup-close-button";

    lockPaddingClass = "lock-padding";
    lockClass = "lock";

    #unlock;

    constructor(
        popupBase, 
        popupContainer, 
        popupContent, 
        popupLink, 
        popupClose,
        lockPaddingItems,
        documentMain,
        timeout,
        onOpen=null,
        onClose=null,
    ) {
        this.base = popupBase;
        this.container = popupContainer;
        this.content = popupContent;

        this.popupLink = popupLink;

        this.closeButton = popupClose;

        this.lockPaddingItems = lockPaddingItems;
        this.documentMain = documentMain;

        this.timeout = timeout;

        this.onOpen = onOpen;
        this.onClose = onClose;

        this.#unlock = true;
    }

    init() {
        this.#makePopup();
        
        this.#addPopupLinkEventListener();
        this.#addPopupCloseEventListener();
        this.#setupEscapeEventListener();
    }

    #makePopup() {
        this.base.classList.add(this.popupBaseClass);
        this.container.classList.add(this.popupContainerClass);
        this.content.classList.add(this.popupContentClass);

        this.closeButton.classList.add(this.popupCloseButtonClass);
    }

    #open() {
        const currentPopup = this;

        if (this.#unlock) {
            this.#mainLock();

            this.base.classList.add(this.openPopupClass);

            this.base.addEventListener("click", function (event) {
                if (event.target == currentPopup.base) {
                    currentPopup.#close(true);
                }
            });

            if (this.onOpen != null) {
                this.onOpen();
            }
        }
    }

    #close(unlockBody = true) {
        if (this.#unlock) {
            this.base.classList.remove(this.openPopupClass);

            if (unlockBody) {
                this.#mainUnlock();
            }

            if (this.onClose != null) {
                this.onClose();
            }
        }
    }

    #mainLock() {
        const currentPopup = this;
        const lockPaddingValue = window.innerWidth - document.querySelector(`.${bodyContainerClass}`).offsetWidth + "px";

        if (currentPopup.lockPaddingItems.length > 0) {
            for (let index = 0; index < currentPopup.lockPaddingItems.length; index++) {
                const element = currentPopup.lockPaddingItems[index];
                element.style.paddingRight = lockPaddingValue;
            }
        }

        currentPopup.documentMain.style.paddingRight = lockPaddingValue;
        currentPopup.documentMain.classList.add(this.lockClass);

        currentPopup.#unlock = false;

        setTimeout(function () {
            currentPopup.#unlock = true;
        }, currentPopup.timeout);
    }

    #mainUnlock() {
        const currentPopup = this;

        setTimeout(function() {
            if (currentPopup.lockPaddingItems.length > 0) {
                for (let index = 0; index < currentPopup.lockPaddingItems.length; index++) {
                    const element = currentPopup.lockPaddingItems[index];
                    element.style.paddingRight = "0px";
                }
            }
    
            currentPopup.documentMain.style.paddingRight = "0px";
            currentPopup.documentMain.classList.remove(currentPopup.lockClass);
    
        }, currentPopup.timeout);

        currentPopup.#unlock = false;

        setTimeout(function () {
            currentPopup.#unlock = true;
        }, currentPopup.timeout);
    }

    #addPopupLinkEventListener() {
        const currentPopup = this;

        currentPopup.popupLink.addEventListener("click", function (event) {
            event.preventDefault();
            currentPopup.#open();
        });
    }

    #addPopupCloseEventListener() {
        const currentPopup = this;

        currentPopup.closeButton.addEventListener("click", function (event) {
            event.preventDefault();
            currentPopup.#close(true);
        })
    }

    #setupEscapeEventListener() {
        const currentPopup = this;

        document.addEventListener("keydown", function(event) {
            if (event.key === "Escape") {
                currentPopup.#close(true);
            }
        });
    }
}

const popupFactory = new PopupFactory(document.querySelector(bodyClass));

function makePopup(
    accountBase, 
    openButton, 
    closeButton,        
    timeout,
    onOpen=null,
    onClose=null,
) {
    return popupFactory.makePopup(
        accountBase,
        openButton, 
        closeButton,
        timeout,
        onOpen,
        onClose,
    );
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
export {makePopup};
