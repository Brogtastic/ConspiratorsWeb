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

function SetUserTheory(url, postData){
    var xhr = new XMLHttpRequest();
    console.log("SetUserTheory function called with URL: " + url);
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Set appropriate content type
    xhr.onreadystatechange = function () {
        console.log("On Ready State Change check");
        if (xhr.readyState === XMLHttpRequest.DONE) {
            console.log("XML HTTP Request Done");
            if (xhr.status === 200) {
                console.log("status === 200");
                var response = JSON.parse(xhr.responseText);
            }
        }
    }
    xhr.send(postData);
}


function SetUserWord(url, postData){
    var xhr = new XMLHttpRequest();
    console.log("SetUserWord function called with URL: " + url);
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Set appropriate content type
    xhr.onreadystatechange = function () {
        console.log("On Ready State Change check");
        if (xhr.readyState === XMLHttpRequest.DONE) {
            console.log("XML HTTP Request Done");
            if (xhr.status === 200) {
                console.log("status === 200");
                var response = JSON.parse(xhr.responseText);
            }
        }
    }
    xhr.send(postData);
}


function getUserTheory() {
    var roomCode = document.getElementById('playRoomCode').textContent;
    var firstname = document.getElementById('playerName').textContent;

    var xhr = new XMLHttpRequest();
    var url = '/member-theory-return/' + roomCode + '/' + firstname;

    xhr.open('GET', url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                var receivedTheory = response.receivedTheory;
                var receivedName = response.receivedName;
                if(receivedTheory === "None"){
                    receivedTheory = "...";
                }
                document.getElementById('receivedTheory').innerText = receivedTheory;
                document.getElementById('round2PlayerTheory').innerText = receivedName + "'s theory";
                document.getElementById('round2Prompt').innerText = "Write some words that " + receivedName + " has to work into their theory!";
                console.log("Get User Theory Successful. Received Name: " + receivedName);
            }
        }
    };
    xhr.send();
}

//if(gameStage === "round2"){
//    setInterval(getUserTheory, 3000);
//}

function checkRound() {
    var roomCodeElement = document.getElementById('playRoomCode');
    var roomCode = roomCodeElement.textContent;
    var firstname = document.getElementById('playerName').textContent;
    if(gameStage === "round1"){
        var enterTheoryTextElement = document.getElementById('enterTheoryText');
        var theory = enterTheoryTextElement ? enterTheoryTextElement.value : "";
    }
    else{
        var theory = "";
    }
    if(gameStage === "round2"){
        var enterWordTextElement = document.getElementById('enterWordText');
        var word = enterTheoryTextElement ? enterTheoryTextElement.value : "";
    }
    else{
        var word = "";
    }

    var xhr = new XMLHttpRequest();
    var url = '/game-stage/' + roomCode;

    xhr.open('GET', url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);

                // When round 2 begins
                // Set current_user's theory to value of input field
                if((response.gameStage === "round2") && (gameStage === "round1") && (theory.length > 0)){
                    var this_url = '/set-user-theory?firstName=' + firstname + '&theory=' + theory + '&roomCode=' + roomCode;
                    var postData = 'firstName=' + encodeURIComponent(firstname) +
                   '&theory=' + encodeURIComponent(theory) +
                   '&roomCode=' + encodeURIComponent(roomCode);

                    SetUserTheory(this_url, postData);
                }

                // When round 3 begins
                // Add whatever unfinished word there is to the user's list
                if((response.gameStage === "round3") && (gameStage === "round2") && (word.length > 0)){
                    var this_url = '/set-user-word?firstName=' + firstname + '&word=' + word + '&roomCode=' + roomCode;
                    var postData = 'firstName=' + encodeURIComponent(firstname) +
                   '&word=' + encodeURIComponent(word) +
                   '&roomCode=' + encodeURIComponent(roomCode);

                    SetUserTheory(this_url, postData);
                }

                gameStage = response.gameStage;

                if(gameStage === "round0"){
                    document.getElementById("round0").style.display = "block";
                    document.getElementById("round1").style.display = "none";
                    document.getElementById("round2").style.display = "none";
                    document.getElementById("round3").style.display = "none";
                    document.getElementById("disconnected").style.display = "none";
                }
                else if(gameStage === "round1"){
                    document.getElementById("round0").style.display = "none";
                    document.getElementById("round1").style.display = "block";
                    document.getElementById("round2").style.display = "none";
                    document.getElementById("round3").style.display = "none";
                    document.getElementById("disconnected").style.display = "none";
                }
                else if(gameStage === "round2"){
                    document.getElementById("round0").style.display = "none";
                    document.getElementById("round1").style.display = "none";
                    getUserTheory();
                    document.getElementById("round2").style.display = "block";
                    document.getElementById("round3").style.display = "none";
                    document.getElementById("disconnected").style.display = "none";
                }
                else if(gameStage === "round3"){
                    document.getElementById("round0").style.display = "none";
                    document.getElementById("round1").style.display = "none";
                    document.getElementById("round2").style.display = "none";
                    document.getElementById("round3").style.display = "block";
                    document.getElementById("disconnected").style.display = "none";
                }
                else{
                    document.getElementById("round0").style.display = "none";
                    document.getElementById("round1").style.display = "none";
                    document.getElementById("round2").style.display = "none";
                    document.getElementById("round3").style.display = "none";
                    document.getElementById("disconnected").style.display = "block";
                }
            }
        }
    };
    xhr.send();
}

checkRound();
setInterval(checkRound, 150);