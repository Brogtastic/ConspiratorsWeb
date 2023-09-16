const currentPath = window.location.pathname;
var gameStage = "round0";

var roomCodeElement = document.getElementById('playRoomCode');
var roomCode = roomCodeElement.textContent;

function checkNumMemberChange() {
    console.log("Sending from CheckNumMemberChange (Called successfully)");
    var xhr = new XMLHttpRequest();

    xhr.open('GET', '/number-of-members/' + roomCode, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                var numMembers = response.numMembers; // Corrected
                document.getElementById('numMembers').innerText = "Number of players in room: " + numMembers;

                console.log("Number of members in room: " + numMembers);
                console.log("Current round is " + gameStage);

                if (Number(numMembers) > 2) {
                    console.log("Start game display block");
                    document.getElementById("StartGame").style.display = "block";
                } else {
                    document.getElementById("StartGame").style.display = "none";
                }
            }
        }
    };
    xhr.send();
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
        var word = enterWordTextElement ? enterWordTextElement.value : "";
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
                    console.log("Game Stage is: " + response.gameStage);
                }

                // When round 3 begins
                // Add whatever unfinished word there is to the user's list
                if((response.gameStage === "round3") && (gameStage === "round2")){
                    var this_url = '/set-user-word?firstName=' + firstname + '&word=' + word + '&roomCode=' + roomCode;
                    var postData = 'firstName=' + encodeURIComponent(firstname) +
                   '&word=' + encodeURIComponent(word) +
                   '&roomCode=' + encodeURIComponent(roomCode);

                    SetUserWord(this_url, postData);
                    console.log("Game Stage is: " + response.gameStage);
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

// Create an EventSource instance to connect to your SSE server
const eventSource = new EventSource('/ssejavascript/' + roomCode);
console.log("Event source: /ssejavascript/" + roomCode);

// Define an event listener for handling incoming SSE messages
eventSource.addEventListener('message', function(e) {
    console.log(e.data);
}, false);

// Define an event listener for handling incoming SSE messages
eventSource.addEventListener('online', function(e) {
    console.log("ONLINE event listener");
    const data = JSON.parse(e.data);
    const eventData = data.info;

    if(eventData === "checkRound"){
        console.log("Check Round SSE");
        checkRound();
    }
    else if(eventData === "getUserTheory"){
        console.log("Get User Theory SSE");
        getUserTheory();
    }
    else if(eventData === "checkNumMemberChange"){
        console.log("Check Num Member Change SSE");
        checkNumMemberChange();
    }
    else{
        console.log("command " + eventData + " not recognized");
    }

    console.log("Received SSE: " + eventData);
}, true);


// Handle connection error
eventSource.addEventListener('error', (error) => {
    console.error('SSE Connection Error:', error);
    eventSource.close();
});


eventSource.addEventListener('open', (event) => {
    console.log('SSE Connection opened');
});


/*
if(gameStage === "round0"){
    // Check for number changes every 500 milliseconds
    setInterval(checkNumMemberChange, 500);
    setInterval(checkRound, 500);
}
*/