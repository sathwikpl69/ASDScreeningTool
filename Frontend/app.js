document.getElementById('quizForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form from refreshing the page

    // Collect quiz responses
    const responses = {
        q1: document.querySelector('input[name="q1"]:checked').value,
        // Add similar code for the other quiz questions
    };

    // Send data to backend API (we'll connect to Shivani's backend later)
    fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(responses),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = "Prediction: " + data.prediction;
    })
    .catch(error => console.error('Error:', error));
});
