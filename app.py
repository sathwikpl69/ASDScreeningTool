from flask import Flask,flash, render_template, request, jsonify, redirect, url_for, session
from flask_mail import Mail, Message
from pymongo import MongoClient
from dotenv import load_dotenv
import random
import string
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pickle
from sklearn.preprocessing import StandardScaler
import joblib

# Load environment variables
load_dotenv()

# Flask App Configuration
app = Flask(
    __name__,
    template_folder='Frontend/templates',
    static_folder='Frontend/static'
)

app.secret_key = os.getenv("SECRET_KEY")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# MongoDB Connection Setup
MONGO_URI = os.getenv('MONGO_URI') 
client = MongoClient(MONGO_URI)
db = client['asd_screening']
users_collection = db['users']  # For storing user information
quiz_results_collection = db['quiz_results']  # To store quiz results
contact_messages_collection = db['contact_messages']  # To store contact form messages

# Load KNN model and scaler
knn_model = joblib.load('C:/Users/ASUS/Documents/ASD/ASDScreeningTool/knn_model.pkl')
scaler = joblib.load('C:/Users/ASUS/Documents/ASD/ASDScreeningTool/scaler.pkl')

# Helper Functions
def generate_random_password():
    password_length = 8
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(password_length))

def send_reset_email(to_email, temporary_password):
    msg = Message(
        'Password Reset Request',
        sender=app.config['MAIL_USERNAME'],
        recipients=[to_email]
    )
    msg.body = f'Your temporary password is: {temporary_password}\nPlease log in and change it immediately.'
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

# Routes
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullName = request.form['fullName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        dob = request.form['dob']
        gender = request.form['gender']
        contactNumber = request.form['contactNumber']
        guardianName = request.form.get('guardianName', '')
        relationshipToUser = request.form.get('relationshipToUser', '')  
        country = request.form['country']

        # Validate inputs
        if not username or not password or not confirmPassword:
            return 'Username, password, and confirm password are required', 400

        if password != confirmPassword:
            return 'Passwords do not match', 400

        # Check if username already exists in MongoDB
        if users_collection.find_one({"username": username}):
            return 'Username already exists', 400

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Save user to MongoDB
        users_collection.insert_one({
            "fullName": fullName,
            "username": username,
            "email": email,
            "password": hashed_password,
            "dob": dob,
            "gender": gender,
            "contactNumber": contactNumber,
            "guardianName": guardianName,
            "relationshipToUser": relationshipToUser, 
            "country": country
        })
        session['user'] = username

        # Print debugging info
        print("Redirecting to login page...")

        return redirect(url_for('login'))  # Redirect to login page after successful signup
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials in MongoDB
        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid username or password', 400
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=session["user"])  # Pass username to template

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        try:
            # Collect responses from the form
            responses = {f'q{i}': request.form.get(f'q{i}') for i in range(1, 11)}

            # Validate responses
            if None in responses.values():
                flash("Please answer all questions before submitting.")
                return redirect(url_for('quiz'))

            # Convert and scale responses
            response_values = [int(responses[q]) for q in responses]
            scaled_data = scaler.transform([response_values])

            # Predict using the KNN model
            prediction = knn_model.predict(scaled_data)[0]
            prediction_result = "positive" if prediction == 1 else "negative"

            # Save results in MongoDB
            user = session['user']
            quiz_data = {
                'user': user,
                'responses': responses,
                'prediction': prediction_result,
                'timestamp': datetime.now()
            }
            quiz_results_collection.insert_one(quiz_data)

            # Redirect to the results page
            return redirect(url_for('results', prediction=prediction_result))

        except Exception as e:
            app.logger.error(f"Error processing quiz submission: {e}")
            flash("An error occurred while processing your quiz. Please try again.")
            return redirect(url_for('quiz'))

    # Render the quiz form
    return render_template('quiz.html')


    
@app.route('/results', methods=['GET']) 
def results():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch the most recent quiz result for the logged-in user
    username = session['user']
    result = quiz_results_collection.find_one({'user': username}, sort=[('timestamp', -1)])

    if result:
        # Extract the prediction (positive/negative)
        prediction = result['prediction']  # assuming 'prediction' field stores the result
        
        # Calculate the total score by counting "Yes" answers (which are represented as '1')
        score = sum(1 for answer in result['responses'].values() if answer == '1')

        # (Optional) Calculate accuracy if applicable
        # Here, you can calculate the accuracy based on the model's performance
        # In this case, we simulate the accuracy value. You should calculate this based on your model's logic
        #accuracy = 95  # Example fixed accuracy, replace with actual calculation if available

        # Pass the data to the results.html template
        return render_template('results.html', 
                               prediction=prediction, 
                               score=score, 
                               responses=result['responses'])
                               #accuracy=accuracy)
    else:
        print("No quiz results found for user:", username)  # Debugging line
        return "No quiz results found."


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        if not email:
            return jsonify({"error": "Email is required"}), 400

        if '@' not in email:
            return jsonify({"error": "Invalid email format"}), 400

        # Check if the email exists in the database
        user = users_collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "Email not found"}), 404

        temporary_password = generate_random_password()
        send_reset_email(email, temporary_password)

        # Update the user's password in the database
        hashed_password = generate_password_hash(temporary_password)
        users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

        return redirect(url_for('login'))  # Redirect to login page after password reset
    
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))  # Redirect to home page after logout

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Validate inputs
        if not name or not email or not message:
            return "All fields are required", 400

        # Store the data in the 'contact_messages' collection
        contact_data = {
            "name": name,
            "email": email,
            "message": message,
            "timestamp": datetime.now()
        }
        contact_messages_collection.insert_one(contact_data)

        # Provide a confirmation message
        return "Message sent successfully!", 200         
        return redirect(url_for('home'))

    return render_template('contact.html')

@app.route('/faq')
def faq():
    # if 'user' not in session:
        # return redirect(url_for('login'))  # Redirect to login if not logged in
        return render_template('faq.html')

@app.route('/terms-of-service')
def terms_of_service():
    # if 'user' not in session:
        # return redirect(url_for('login'))  # Redirect to login if not logged in
        return render_template('terms-of-service.html')

@app.route('/privacy-policy')
def privacy_policy():
    # if 'user' not in session:
        # return redirect(url_for('login'))  # Redirect to login if not logged in
        return render_template('privacy-policy.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
