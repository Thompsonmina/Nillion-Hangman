
function toggle_first_card(id) {
    console.log(id)
    var code_body = document.querySelector(`#${id}`);
    if (code_body.style.display === "none") {
        code_body.style.display = "block";
    } else {
        code_body.style.display = "none";
    }
}


function displayProgramDetails(programId, gameMasterId) {
    console.log(programId, gameMasterId)
    const cardBody = document.getElementById("programCard");
    cardBody.innerHTML = `<div class="card">
        <div class="card-header">Program Details</div>
        <div class="card-body">
            <div>
            <span id="program-id" data-programid="${programId}">Program ID: ${programId}</span>
            </div>
            <br>
            <div>
            <span> Game Master Party ID: ${gameMasterId}</span>
            </div>
        </div>
    </div>`;
}

function submitProgram(event) {
    event.preventDefault();  // This stops the form from submitting

    var wordLength = document.getElementById('wordLength').value;
    var creatorName = document.getElementById('creatorName').value;

    if (!wordLength || wordLength < 1 || wordLength > 10 || !creatorName) {
        alert('Please ensure all fields are filled in correctly. Word Length should be between 1 and 10.');
        return; // Stop the function if validation fails
    }

    fetch('/store-hangman-program', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            wordLength: wordLength,
            creatorName: creatorName,
            action: "start_creation"
        })
    }).then(response => response.json())
        .then(data => {
            displayProgramDetails(data.program_id, data.game_master_party_id);
        })
        .catch(error => console.error('Error:', error));
}

function store_creator_gamedata(event) {
    event.preventDefault();  // This stops the form from submitting

    let creator_partyid = document.getElementById("creator-partyid").value;
    let creator_storeid = document.getElementById('creator-storeid').value;
    // let program_id = document.getElementById("program-id").attributes("data-programid")

    // program_id = "2pvWozAEy9QrKX4Yy2Wypr4Adik6HLTTLTcWEwRKtGqWSAjiubb2osmvTGADTbUzgNkPuuMxgyeFzNUdGqDyEnM$2Fhangman"
    
    let game_name = "hangman"
    fetch('/store-hangman-program', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            creator_party_id: creator_partyid,
            creator_store_id: creator_storeid,
            game_name: game_name,
            action: "finalise_creation"
        })
    }).then(response => {
        if (!response.ok) {
            console.log("something wrong")
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json(); 
    })
        .then(data => {
            console.log(data)
            const gameUrl = `http://localhost:5000/games/${data.game_name}`;
            alert(`You have successfully created a secret hangman game. You can find it here: ${gameUrl}`);
            window.location.href = gameUrl;
        })
        .catch(error => console.error('Error:', error));
}

function join_game(event) {
    event.preventDefault();  // This stops the form from submitting

    var name = document.getElementById("guesser-name").value;
    console.log(name)

    const currentUrl = window.location.href;
    let gamename = currentUrl.split('/games/')[1];
    gamename = gamename.split("?")[0]


    console.log(currentUrl, gamename, "dd")

    fetch('/game-actions/' + gamename, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            action: "join"
        })
    }).then(response => {
        if (!response.ok) {
            console.log("an error occured")
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json(); 
    })
        .then(data => {
            console.log("successfully joined")
            const gameUrl = `http://localhost:5000/games/${gamename}/${name}`;
            window.location.href = gameUrl
            console.log(gameUrl, name, gamename)
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function () {

    
       
});
