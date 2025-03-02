import pandas as pd
import numpy as np
import pickle
import os
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError

# Define dataset path
CSV_PATH = r"C:\Users\ASWATH\OneDrive\Desktop\cloud_anomaly_detection\backend\data\final_cleaned_dataset.csv"

# Load Dataset
def load_dataset():
    print("[INFO] Loading dataset...")
    df = pd.read_csv(CSV_PATH)

    # Use only 10% of the dataset for training speed
    df = df.sample(frac=0.1, random_state=42)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    print(f"[INFO] Dataset shape: {df.shape}")
    return X, y

# Train SVM Model
def train_svm(X_train, y_train):
    print("[INFO] Training SVM...")
    svm = SVC(kernel='linear')
    svm.fit(X_train, y_train)
    with open("svm_model.pkl", "wb") as file:
        pickle.dump(svm, file)
    print("[INFO] SVM Training Completed!")
    return svm

# Train Random Forest Model
def train_rf(X_train, y_train):
    print("[INFO] Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=10, random_state=42)  # Reduced estimators for speed
    rf.fit(X_train, y_train)
    with open("rf_model.pkl", "wb") as file:
        pickle.dump(rf, file)
    print("[INFO] Random Forest Training Completed!")
    return rf

# Train Autoencoder
def train_autoencoder(X_train, X_test):
    print("[INFO] Training Autoencoder...")
    input_dim = X_train.shape[1]
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(4, activation='relu')(input_layer)  # Reduced neurons for speed
    decoded = Dense(input_dim, activation='sigmoid')(encoded)
    autoencoder = Model(input_layer, decoded)

    # Explicitly use MeanSquaredError as loss function
    mse_loss = MeanSquaredError()
    autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss=mse_loss)

    autoencoder.fit(X_train, X_train, epochs=1, batch_size=32, shuffle=True, validation_data=(X_test, X_test))

    autoencoder.save("autoencoder_model.h5")  # Save model
    print("[INFO] Autoencoder Training Completed!")
    return autoencoder

# Evaluate Model Accuracies
def evaluate_models(X_test, y_test, autoencoder, svm, rf):
    print("[INFO] Evaluating Models...")

    svm_acc = accuracy_score(y_test, svm.predict(X_test))
    rf_acc = accuracy_score(y_test, rf.predict(X_test))

    X_test_pred = autoencoder.predict(X_test)
    error = np.mean(np.abs(X_test - X_test_pred), axis=1)
    threshold = np.percentile(error, 95)
    autoencoder_acc = np.mean(error < threshold)

    print(f"[INFO] SVM Accuracy: {svm_acc}")
    print(f"[INFO] Random Forest Accuracy: {rf_acc}")
    print(f"[INFO] Autoencoder Accuracy: {autoencoder_acc}")

    return {"SVM Accuracy": svm_acc, "RF Accuracy": rf_acc, "Autoencoder Accuracy": autoencoder_acc}

# Train and Save Models
def train_and_save_models():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    X, y = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    svm = train_svm(X_train, y_train)
    rf = train_rf(X_train, y_train)
    autoencoder = train_autoencoder(X_train, X_test)

    accuracies = evaluate_models(X_test, y_test, autoencoder, svm, rf)
    print("✅ Model Training Completed!")
    print(accuracies)
    return accuracies

# Run the training process
if __name__ == "__main__":
    train_and_save_models()
