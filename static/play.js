const currentPath = window.location.pathname;
var gameStage = "round0";

var roomCodeElement = document.getElementById('playRoomCode');
var roomCode = roomCodeElement.textContent;

var wordButton1 = document.getElementById('wordButton1');
var wordButton2 = document.getElementById('wordButton2');
var wordButton3 = document.getElementById('wordButton3');

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
    getUserWords();
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


function getUserWords() {
    console.log("Get user words workin now");
    var firstname = document.getElementById('playerName').textContent;

    var xhr = new XMLHttpRequest();
    var url = '/member-words-return/' + roomCode + '/' + firstname;

    xhr.open('GET', url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                var word1 = response.word1;
                var word2 = response.word2;
                var word3 = response.word3;
                console.log("Word 1: " + word1);
                console.log("Word 2: " + word2);
                console.log("Word 3: " + word3);

                if(word1 === "NO_ENTRY"){
                    wordButton1.style.display = "none";
                }
                else{
                    wordButton1.style.display = "block";
                    wordButton1.innerText = word1;
                }
                if(word2 === "NO_ENTRY"){
                    wordButton2.style.display = "none";
                }
                else{
                    wordButton2.style.display = "block";
                    wordButton2.innerText = word2;
                }
                if(word3 === "NO_ENTRY"){
                    wordButton3.style.display = "none";
                }
                else{
                    wordButton3.style.display = "block";
                    wordButton3.innerText = word3;
                }


            }
        }
    };
    xhr.send();
}


function checkRound() {
    console.log("Check Round Called");
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
                console.log("New round: " + gameStage);

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
                    getUserWords();
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

function displayWord(url, postData){
    var xhr = new XMLHttpRequest();
    console.log("displayWord function called with URL: " + url);
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Set appropriate content type
    xhr.onreadystatechange = function () {
        console.log("On Ready State Change check");
        if (xhr.readyState === XMLHttpRequest.DONE) {
            console.log("XML HTTP Request Done");
            if (xhr.status === 200) {
                console.log("status === 200");
                var response = JSON.parse(xhr.responseText);
                console.log("Word display " + response.status);
            }
        }
    }
    xhr.send(postData);
}


checkRound();


wordButton1.onclick = function(){
    console.log("WordButton1 clicked!");
    var word = wordButton1.innerText;

    var this_url = '/display-word?word=' + word + '&roomCode=' + roomCode;
    var postData = 'word=' + encodeURIComponent(word) +
   '&roomCode=' + encodeURIComponent(roomCode);

    displayWord(this_url, postData);
    wordButton1.disabled = true;
};

wordButton2.onclick = function(){
    console.log("WordButton2 clicked!");
    var word = wordButton2.innerText;

    var this_url = '/display-word?word=' + word + '&roomCode=' + roomCode;
    var postData = 'word=' + encodeURIComponent(word) +
   '&roomCode=' + encodeURIComponent(roomCode);

    displayWord(this_url, postData);
    wordButton2.disabled = true;
};

wordButton3.onclick = function(){
    console.log("WordButton3 clicked!");
    var word = wordButton3.innerText;

    var this_url = '/display-word?word=' + word + '&roomCode=' + roomCode;
    var postData = 'word=' + encodeURIComponent(word) +
   '&roomCode=' + encodeURIComponent(roomCode);

    displayWord(this_url, postData);
    wordButton3.disabled = true;
};


// Create an EventSource instance to connect to your SSE server
const eventSource = new EventSource('/ssejavascript/' + roomCode);
console.log("Event source: /ssejavascript/" + roomCode);

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
    else if(eventData === "getUserWords"){
        console.log("Get User Words SSE");
        getUserWords();
    }
    else if(eventData === "checkNumMemberChange"){
        console.log("Check Num Member Change SSE");
        checkNumMemberChange();
    }
    else if(eventData === "Connection Established"){
        console.log("Connection Established");
    }
    else{
        console.log("command " + eventData + " not recognized");
    }

    console.log("Received SSE: " + eventData);
}, true);

// Handle connection error
eventSource.addEventListener('error', (error) => {
    console.error('SSE Connection Error:', error);

    document.getElementById("round0").style.display = "none";
    document.getElementById("round1").style.display = "none";
    document.getElementById("round2").style.display = "none";
    document.getElementById("round3").style.display = "none";
    document.getElementById("disconnected").style.display = "block";

    eventSource.close();
});

eventSource.addEventListener('open', (event) => {
    console.log('SSE Connection opened');
});

