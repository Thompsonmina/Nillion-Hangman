//const
const container = document.getElementById("alphabetButtons");
var myStickman = document.getElementById("stickman");
var context = myStickman.getContext("2d");

var current_letter_store = {}

//generate alphabet button
function generateButton() {
  var buttonsHTML = "abcdefghijklmnopqrstuvwxyz"
    .split("")
    .map(
      (letter) =>
        `<button
         class = "alphabetButtonJS" 
         id="${letter}"
         >
        ${letter}
        </button>`
    )
    .join("");

  return buttonsHTML;
}

async function letterClick(event) {
    const isButton = event.target.nodeName === "BUTTON";
    console.log("here?")
    if (isButton) {
        let result = confirm("Are you sure you want to store and play this letter?");
        if (result) {
            console.log("User confirmed action.");
            // Add the function to store and play the letter here

          letter = event.target.id
          const letterbtn = document.getElementById(letter);
          letterbtn.classList.add("selected");
          let res = await store_letter_recieve_computation(letter)

          let compute_res = await perform_computation(res.store_id, res.party_id)
          console.log(compute_res)



          document.getElementById('slots-filled').innerHTML = "Slots Filled so Far:" + compute_res.slots_guessed;
          document.getElementById('slots-left').innerHTML = "Slots left to fill:" + compute_res.slots_left;
          document.getElementById('lives').innerHTML = "Attempts Left:  " + compute_res.attempts_left 

          render_frames(11-compute_res.attempts_left)

          


        } else {
            // Code to execute if user clicks 'Cancel'
            console.log("User cancelled action.");
        }
        
        
        //   fetch the number needed

  }
  return;
}

function store_letter_recieve_computation(letter) {

    const currentUrl = window.location.href;
    let program_id = currentUrl.split('/games/')[1];
    program_id_name = program_id.split("?")[0]

    let response = null
    console.log('/store-letter-for-user/' + program_id_name )
    return fetch('/store-letter-for-user/' + program_id, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            guess: letter,
        })
    })
      .then(response => response.json())
      .then(data => {
          console.log(data, "huh")

          return data
        })
        .catch(error => {
            console.error('Error:', error)
            return error
        });  
    
    return response

}

function perform_computation(letter_store_id, player_party_id) {
    const currentUrl = window.location.href;
    let rest_of_url = currentUrl.split('/games/')[1];

    return fetch('/perform-hangman-computation/' + rest_of_url, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        letter_store_id: letter_store_id,
        player_party_id: player_party_id
      })
  })
  .then(response => response.json())
  .then(data => {
      console.log(data, "huh")

      return data
    })
    .catch(error => {
        console.error('Error:', error)
        return error
    });  

}

//set question,answer and hint


document.addEventListener('DOMContentLoaded', function () {
    console.log("at least")
    container.innerHTML = generateButton();
    context.clearRect(0, 0, 400, 400);
    canvas()
    life = document.querySelector("#lives").getAttribute("data-value")
    console.log(life)
    container.addEventListener("click", letterClick);
    console.log("here?")


    
       
});


// container.addEventListener("click", guess);



// Animation


function canvas() {
  myStickman = document.getElementById("stickman");
  context = myStickman.getContext("2d");
  context.beginPath();
  context.strokeStyle = "#fff";
  context.lineWidth = 2;
}

function head() {
  myStickman = document.getElementById("stickman");
  context = myStickman.getContext("2d");
  context.beginPath();
  context.arc(60, 25, 10, 0, Math.PI * 2, true);
  context.stroke();
}

function draw($pathFromx, $pathFromy, $pathTox, $pathToy) {
  context.moveTo($pathFromx, $pathFromy);
  context.lineTo($pathTox, $pathToy);
  context.stroke();
}

function drawFrame(part, x1, y1, x2, y2) {
    draw(x1, y1, x2, y2);
}

function animate(frame) {
      //console.log(drawArray[life]);
      const parts = [
        () => drawFrame("rightLeg", 60, 70, 100, 100),
        () => drawFrame("leftLeg", 60, 70, 20, 100),
        () => drawFrame("rightArm", 60, 46, 100, 50),
        () => drawFrame("leftArm", 60, 46, 20, 50), 
        () => drawFrame("torso", 60, 36, 60, 70),
        () => head(),
        () => drawFrame("frame4", 60, 5, 60, 15),
        () => drawFrame("frame3", 0, 5, 70, 5),
        () => drawFrame("frame2", 10, 0, 10, 600),
        () => drawFrame("frame1" ,0, 150, 150, 150)
      ]
    
    parts[frame]()
}
  
function render_frames(frames) {
    for (var i = 0; i <= frames; i++) {
        animate(i)
    }
}
