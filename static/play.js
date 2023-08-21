const currentPath = window.location.pathname;

function checkNumMemberChange() {
    // Send a GET request to the server to check if the number has changed
    var roomCodeElement = document.getElementById('playRoomCode');
    var roomCode = roomCodeElement.textContent;

    var xhr = new XMLHttpRequest();

    xhr.open('GET', '/number-of-members/' + roomCode, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                var numMembers = response.numMembers;
                document.getElementById('numMembers').innerText = "Number of players in room: " + numMembers;
                if(numMembers > 2){
                    document.getElementById("StartGame").style.display = "block";
                }
                else{
                    document.getElementById("StartGame").style.display = "none";
    }
            }
        }
    };
    xhr.send();

}

// Check for number changes every 500 milliseconds
setInterval(checkNumMemberChange, 500);