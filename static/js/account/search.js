"use strict";

import {getValueOrNull} from "../utils.js";

const searchButtonClass = "search-button";

const searchButtons = document.getElementsByClassName(searchButtonClass);

const searchFormClass = "search__item";
const searchInputClass  = "search-input";


function setupSearch() {
    if (searchButtons) {
        for (let index = 0; index < searchButtons.length; index++) {
            const searchButton = searchButtons[index];
    
            searchButton.addEventListener("click", async function (event) {
                const searchForm = event.target.closest(`.${searchFormClass}`)
                const searchInput = searchForm.querySelector(`.${searchInputClass}`)
    
                if (getValueOrNull(searchInput) == null) {
                    event.preventDefault();
                }
            })
        }
    }
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
setupSearch();
