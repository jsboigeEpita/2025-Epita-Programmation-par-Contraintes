let optionsContainer = document.getElementById('options_container')
let categoryTemplate = document.getElementsByClassName('options-category')[0]
let rangeOptionTemplate = document.getElementsByClassName('option-range-container')[0]
let checkboxOptionTemplate = document.getElementsByClassName('option-checkbox-container')[0]
let selectOptionTemplate = document.getElementsByClassName('option-select-container')[0]

eel.expose(registerOptions)

function registerOptions(options) {
    let opts = {}

    for (let opt of options) {
        opts[opt.id] = {}
        opts[opt.id]['dependencies'] = {}

        for (let [dep_oid, dep_v] of opt.depends_on) {
            opts[opt.id]['dependencies'][dep_oid] = dep_v
        }
    }

    function hideOrShowDeps() {
        let i = 0;
        entries = Object.entries(opts)

        while (i < entries.length) {
            let [id, opt] = entries[i]
            let respectsAll = true

            for (let [d_id, d_v] of Object.entries(opt['dependencies'])) {
                respectsAll = respectsAll && opts[d_id]['get']() === d_v
            }

            let somethingChanged = false

            if (respectsAll && opt['obj'].classList.contains('hidden')) {
                somethingChanged = true
                opt['obj'].classList.remove('hidden')
            } else if (!respectsAll && !opt['obj'].classList.contains('hidden'))
            {
                somethingChanged = true
                opt['obj'].classList.add('hidden')
                opt['reset']()
            }

            i = somethingChanged ? 0 : i + 1;
        }
    }

    for (let opt of options) {
        let op = opts[opt.id]

        let category = document.getElementById(`category-${opt.category}`)

        let defaultValue = localStorage.getItem(opt.id)
        
        if (defaultValue === null)
            defaultValue = opt.default 

        if (category === null)
        {
            category = categoryTemplate.cloneNode(true)
            category.id = `category-${opt.category}`

            let catName = category.querySelector('.category-title')
            catName.innerText = opt.category

            optionsContainer.appendChild(category)
        }

        if (opt.type === 'range') {
            let o = rangeOptionTemplate.cloneNode(true)
            let oRange = o.querySelector('.option-range')
            let oName = o.querySelector('.option-range-name')
            oName.innerText = `${opt.name} : ${oRange.value}`

            oRange.min = opt.min_range
            oRange.max = opt.max_range
            oRange.step = opt.step

            op['update'] = function() {
                oName.innerText = `${opt.name} : ${oRange.value}`
                eel.option_update(opt.id, parseInt(oRange.value))
                localStorage.setItem(opt.id, oRange.value)

                hideOrShowDeps()
            }
            oRange.onchange = op['update']

            op['setup'] = () => { 
                if (defaultValue !== null)
                    oRange.value = defaultValue
                op['update']()
            }
            op['reset'] = () => {}
            op['get'] = () => { return oRange.value }

            o.classList.remove('template')
            category.appendChild(o)

            op['obj'] = o
        }
        else if (opt.type == 'checkbox') {
            let o = checkboxOptionTemplate.cloneNode(true)
            let oCheck = o.querySelector('.option-checkbox')
            let oName = o.querySelector('.option-checkbox-name')
            oName.innerText = `${opt.name}`

            op['update'] = () => {
                eel.option_update(opt.id, oCheck.checked)
                localStorage.setItem(opt.id, oCheck.checked)

                hideOrShowDeps()
            }
            oCheck.onchange = op['update']

            op['setup'] = () => {
                if (defaultValue !== null) 
                    oCheck.checked = defaultValue === "true" ? true : defaultValue === true
                op['update']()
            }
            op['reset'] = () => { 
                oCheck.checked = false;
                op['update']()
            }
            op['get'] = () => { return oCheck.checked }
            op['obj'] = o

            o.classList.remove('template')
            category.appendChild(o)
        }
        else if (opt.type == 'select') {
            let o = selectOptionTemplate.cloneNode(true)
            let oSelect = o.querySelector('.option-select')
            let oName = o.querySelector('.option-select-name')
            oName.innerText = `${opt.name}`

            for (let select_o of opt.options) {
                let dom_o = document.createElement('option')
                dom_o.value = select_o
                dom_o.text = select_o

                oSelect.appendChild(dom_o)
            }

            op['update'] = () => {
                eel.option_update(opt.id, oSelect.value)
                localStorage.setItem(opt.id, oSelect.value)

                hideOrShowDeps()
            }

            oSelect.onchange = op['update']
            oSelect.value = opt.options[0]

            op['setup'] = () => {
                if (defaultValue !== null)
                    oSelect.value = defaultValue
                op['update']()
            }
            op['reset'] = () => {}
            op['get'] = () => { return oSelect.value } 
            op['obj'] = o

            o.classList.remove('template')
            category.appendChild(o)
        }

        category.classList.remove('template')
    }

    for (let opt of options) {
        opts[opt.id]['setup']()
    }

    console.log(opts)
}