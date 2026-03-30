const singleDayCheckbox = document.getElementById("singleDay");
singleDayCheckbox.addEventListener("change", singleDaySwitched());

function singleDaySwitched() {
    const finishDate = document.getElementById("finishDate")
    if (singleDayCheckbox.checked) {
        finishDate.style.display = "none";
    } else {
        finishDate.style.display = "block";
    }
}



