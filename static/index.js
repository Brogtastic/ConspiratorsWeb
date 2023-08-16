const currentPath = window.location.pathname;


function checkNumberChange() {
    // Send a GET request to the server to check if the number has changed
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/profile', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                var newNumber = response.number;
                if (newNumber !== "{{ number }}") {
                    // Update the page with the new number
                    document.getElementById('number').innerText = newNumber;
                }
            }
        }
    };
    xhr.send();
}
// Check for number changes every 500 milliseconds
setInterval(checkNumberChange, 500);


if(currentPath === '/'){
    const textarea = document.getElementById('name');
    const counter = document.getElementById('nameCounter');
    const maxCount = 12;

    textarea.addEventListener('input', function() {
        const remainingChars = maxCount - textarea.value.length;
        counter.innerHTML = remainingChars;
    });
}