const uploadFormClass = "upload";
const uploadLabelClass = "upload-title";
const uploadInputFileClass = "file-upload";


function getFiles(form) {
    const input = form.querySelector(`.${uploadInputFileClass}`);
    return input.files;
}


function getFormData(form) {
    return new FormData(form);
}


function senFile(data) {
    fetch("/accounts/upload", {
        method: "POST",
        body: data
    })
    .then(response => {
        if (response.ok) {
            response.json().then((data) => {
                alert(`Загружено аккаунтов: ${data["created_accounts"]}`)

            });
        } else {
            alert(`Ошибка отправки`)
        }
    })
    .catch(error => alert(`Ошибка отправки: ${error}`)); 
}


function initUploads() {
    const form = document.querySelector(`.${uploadFormClass}`);
    const inputFile = document.querySelector(`.${uploadInputFileClass}`);

    inputFile.addEventListener("change", async function(event) {
        senFile(getFormData(form));
    });
}
// // // // // // // // // // // // // // // // // // // // // // // // // // // // // // 
initUploads();
