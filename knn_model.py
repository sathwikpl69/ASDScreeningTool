import pandas as pd  
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Load the dataset
data = pd.read_csv('autism_screening.csv')
data.ffill(inplace=True)  # Fill missing values

# Keep only the relevant features for the quiz
quiz_columns = ['A1_Score', 'A2_Score', 'A3_Score', 'A4_Score', 'A5_Score',
                'A6_Score', 'A7_Score', 'A8_Score', 'A9_Score', 'A10_Score', 'Class/ASD']

# Filter the data to keep only the quiz-related columns and target variable
data_filtered = data[quiz_columns]

# Encode 'Class/ASD' to 0 (Non-ASD) and 1 (ASD)
data_filtered['Class/ASD'] = data_filtered['Class/ASD'].map({'NO': 0, 'YES': 1})

# Save the filtered data
preprocessed_data_file = 'autism_screening_filtered.csv'
data_filtered.to_csv(preprocessed_data_file, index=False)

# Define features and target variable
X = data_filtered[['A1_Score', 'A2_Score', 'A3_Score', 'A4_Score', 'A5_Score', 
                   'A6_Score', 'A7_Score', 'A8_Score', 'A9_Score', 'A10_Score']]  
y = data_filtered['Class/ASD']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train k-NN with optimal weights
knn = KNeighborsClassifier(n_neighbors=5, weights='distance')
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)

# Evaluation Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f'Accuracy of k-NN model: {accuracy * 100:.2f}%')
print(f'Precision of k-NN model: {precision * 100:.2f}%')
print(f'Recall of k-NN model: {recall * 100:.2f}%')
print(f'F1 Score of k-NN model: {f1:.2f}')

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Non-ASD', 'ASD'], yticklabels=['Non-ASD', 'ASD'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# Test different k values
k_values = range(1, 51)
accuracies = []

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    accuracies.append(accuracy_score(y_test, y_pred))

# Plot accuracy vs. k
optimal_k = k_values[accuracies.index(max(accuracies))]
plt.figure(figsize=(10, 6))
plt.plot(k_values, accuracies, marker='o', label='Accuracy')
plt.axvline(optimal_k, color='r', linestyle='--', label=f'Optimal k = {optimal_k}')
plt.title('Accuracy vs. Number of Neighbors (k)')
plt.xlabel('Number of Neighbors (k)')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.show()

# Save the final model and scaler
joblib.dump(knn, 'knn_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("Model and scaler saved as 'knn_model.pkl' and 'scaler.pkl'")
