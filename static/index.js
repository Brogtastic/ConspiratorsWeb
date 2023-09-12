const currentPath = window.location.pathname;

document.getElementById("roomCode").addEventListener("input", function() {
    this.value = this.value.toUpperCase();
});

if(currentPath === '/'){
    const textarea = document.getElementById('name');
    const counter = document.getElementById('nameCounter');
    const maxCount = 12;

    textarea.addEventListener('input', function() {
        const remainingChars = maxCount - textarea.value.length;
        counter.innerHTML = remainingChars;
    });
}