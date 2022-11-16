function setSelectDefault(selectElement, value) {
    let options = Array.from(selectElement.children);
    options.forEach((element) => {
        if(element.value === value) {
            element.setAttribute("selected", "selected");
        }
    })
}