let stepTitle = document.getElementById('step-title')

eel.expose(step)

function step(message) {
    console.log(message)
    stepTitle.innerText = message
}