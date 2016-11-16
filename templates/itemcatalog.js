
function setSelectedIndex(combo, value){
    for (i = 0; i< combo.options.length; i++){
        if (combo.options[i].value == value){
            combo.options[i].selected = true;
            break;
        }
    }
    return;
}
setSelectedIndex(document.getElementById("category-combo"),"{{item.category.id}}");

document.getElementById("picfile").onchange = function () {
    document.getElementById("picfile-label").innerHTML =
    document.getElementById("picfile").files[0].name;
};