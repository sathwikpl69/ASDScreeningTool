document.getElementById('quizForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form from refreshing the page

    // Collect quiz responses
    const responses = {
        q1: document.querySelector('input[name="q1"]:checked') ? document.querySelector('input[name="q1"]:checked').value : null,
        q2: document.querySelector('input[name="q2"]:checked') ? document.querySelector('input[name="q2"]:checked').value : null,
        q3: document.querySelector('input[name="q3"]:checked') ? document.querySelector('input[name="q3"]:checked').value : null,
        q4: document.querySelector('input[name="q4"]:checked') ? document.querySelector('input[name="q4"]:checked').value : null,
        q5: document.querySelector('input[name="q5"]:checked') ? document.querySelector('input[name="q5"]:checked').value : null,
        q6: document.querySelector('input[name="q6"]:checked') ? document.querySelector('input[name="q6"]:checked').value : null,
        q7: document.querySelector('input[name="q7"]:checked') ? document.querySelector('input[name="q7"]:checked').value : null,
        q8: document.querySelector('input[name="q8"]:checked') ? document.querySelector('input[name="q8"]:checked').value : null,
        q9: document.querySelector('input[name="q9"]:checked') ? document.querySelector('input[name="q9"]:checked').value : null,
        q10: document.querySelector('input[name="q10"]:checked') ? document.querySelector('input[name="q10"]:checked').value : null
    };

    // Check if all questions have been answered
    if (Object.values(responses).includes(null)) {
        alert("Please answer all questions before submitting.");
        return; // Exit the function if any question is not answered
    }

    // Store responses in localStorage
    localStorage.setItem('quizResponses', JSON.stringify(responses));

    // Send data to backend API
    fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(responses),
    })
    .then(response => response.json())
    .then(data => {
        // Redirect to results.html with the prediction result
        localStorage.setItem('predictionResult', JSON.stringify(data.prediction)); // Store prediction result
        window.location.href = "results.html"; // Redirect to results page
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred while processing the data. Please try again.");
    });
});