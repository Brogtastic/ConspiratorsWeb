const currentPath = window.location.pathname;
var gameStage = "round0";

function checkNumMemberChange() {
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

if(gameStage === "round0"){
    // Check for number changes every 500 milliseconds
    setInterval(checkNumMemberChange, 500);
}

function checkRound() {
    var roomCodeElement = document.getElementById('playRoomCode');
    var roomCode = roomCodeElement.textContent;

    var xhr = new XMLHttpRequest();
    var url = '/game-stage/' + roomCode;

    xhr.open('GET', url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                var gameStage = response.gameStage;
                if(gameStage === "round0"){
                    document.getElementById("round0").style.display = "block";
                    document.getElementById("round1").style.display = "none";
                }
                else{
                    document.getElementById("round0").style.display = "none";
                    document.getElementById("round1").style.display = "block";
    }
            }
        }
    };
    xhr.send();
}

setInterval(checkRound, 1000);