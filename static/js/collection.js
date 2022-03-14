let cardNameEntry = document.querySelector("#card-name-search")

function card_name_autocomplete(){
    
    let results = []
    if (cardNameEntry.value.length > 3){
        for(let i = 0; i < card_list.length; i++){
            let y = card_list[i]
            if(y.includes(cardNameEntry.value)){
                results.push(y)
            }
        }
    }
    show_card_results(results)
}

window.onload=function(){
    cardNameEntry.addEventListener("input", card_name_autocomplete)

}

function show_card_results(arr) {
    res = document.getElementById("result-card")
    res.innerHTML = ""
    let list = ""
    for (let i = 0; i < arr.length; i++) {
        list += `<li class='result-item' id='${arr[i]}'>` + arr[i] + "</li>"
    }
    
    res.innerHTML = "<ul class='result-item'>" + list + "</ul>"
    let resultItems = document.querySelectorAll('.result-item')
    for(let i = 0; i <resultItems.length; i++){
        resultItems[i].addEventListener("click", getItemInfoCard)
    }
}


const getItemInfoCard = (e) =>{
    cardNameEntry.value = e.target.id
    e.stopPropagation()
    e.preventDefault()
    closeList()
}

const closeList = (e) =>{
    let x = document.getElementsByClassName('result-item')
    for(let i = 0; i < x.length; i++){
        x[i].parentNode.removeChild(x[i])
    }
}




let setNameEntry = document.querySelector("#set-name-search")

async function set_name_autocomplete(){
    let card_name = document.getElementById('card-name-search').value

    let sets_list = await get_set_names(card_name)
    

    let results = []
    if (setNameEntry.value.length >= 0){
        for(let i = 0; i < sets_list.length; i++){
            let y = sets_list[i]
            if(y.includes(setNameEntry.value)){
                results.push(y)
            }
        }
    }
    show_set_results(results)
}

setNameEntry.addEventListener("input", set_name_autocomplete)

function show_set_results(arr) {
    res = document.getElementById("result-set")
    res.innerHTML = ""
    let list = ""
    for (let i = 0; i < arr.length; i++) {
        list += `<li class='result-item' id='${arr[i]}'>` + arr[i] + "</li>"
    }
    
    res.innerHTML = "<ul class='result-item'>" + list + "</ul>"
    let resultItems = document.querySelectorAll('.result-item')
    for(let i = 0; i <resultItems.length; i++){
        resultItems[i].addEventListener("click", getItemInfoSet)
    }
}

function getItemInfoSet(e) {
    setNameEntry.value = e.target.id
    e.stopPropagation()
    e.preventDefault()
    closeList2()
}

const closeList2 = (e) =>{
    let x = document.getElementsByClassName('result-item')
    for(let i = 0; i < x.length; i++){
        x[i].parentNode.removeChild(x[i])
    }
    run_finish_finder()
}

async function run_finish_finder(){
    let card_name = document.getElementById('card-name-search').value
    let set_name = document.getElementById('set-name-search').value
    let finishes_list = await get_finishes_list(card_name, set_name)
    load_finishes_options(finishes_list)
}
function load_finishes_options(arr) {
    let select = document.getElementById("finish-select")
    
    for (let i = 0; i < arr.length; i++){
        let newOption = new Option(arr[i])
        select.add(newOption,undefined)
    }
}

let addnewcardbtn = document.querySelector('.add-card-btn')

addnewcardbtn.addEventListener("click", addtocollection)

