# knn_model.py 

# Import necessary libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Step 1: Load the dataset
data = pd.read_csv('autism_screening.csv')  # Make sure the CSV is in the same folder

# Step 2: Handle any missing data using forward fill (as in the previous code)
data.ffill(inplace=True)

# Step 3: Encode relevant categorical columns
label_encoder = LabelEncoder()
data['gender'] = label_encoder.fit_transform(data['gender'])
data['ethnicity'] = label_encoder.fit_transform(data['ethnicity'])
data['jaundice'] = label_encoder.fit_transform(data['jaundice'])
data['autism'] = label_encoder.fit_transform(data['autism'])
data['used_app_before'] = label_encoder.fit_transform(data['used_app_before'])
data['relation'] = label_encoder.fit_transform(data['relation'])
data['Class/ASD'] = label_encoder.fit_transform(data['Class/ASD'])  # Target variable

# Step 4: Define features (X) and target variable (y) - same features as in previous code
X = data[['A1_Score', 'A2_Score', 'A3_Score', 'A4_Score', 'A5_Score', 
          'A6_Score', 'A7_Score', 'A8_Score', 'A9_Score', 'A10_Score', 'age']]
y = data['Class/ASD']

# Step 5: Split the dataset into training and testing sets (70% training, 30% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 6: Standardize the features (important for k-NN)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Step 7: Train the k-NN model with k=5 (as in previous code)
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

# Step 8: Make predictions on the test set
y_pred = knn.predict(X_test)

# Step 9: Calculate accuracy, precision, recall, F1-score, and confusion matrix
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy of k-NN model: {accuracy * 100:.2f}%')
print(classification_report(y_test, y_pred))

# Step 10: Generate a confusion matrix and plot it
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Non-ASD', 'ASD'], yticklabels=['Non-ASD', 'ASD'])
plt.title('Confusion Matrix for k-NN')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# Step 11: Save the model and the scaler for future use
joblib.dump(knn, 'knn_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("Model and scaler saved as 'knn_model.pkl' and 'scaler.pkl'")
