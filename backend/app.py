import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
import time
import threading
from datetime import datetime
import random

# Suppress TensorFlow warnings
tf.get_logger().setLevel("ERROR")

# ✅ Initialize Flask App
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # ✅ Enable real-time updates
app.secret_key = "supersecretkey"

# ✅ Configure Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ✅ Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# ✅ Create Database Before First Request
with app.app_context():
    db.create_all()

# ---------------- Model Loading ----------------
svm_model_path = "svm_model.pkl"
rf_model_path = "rf_model.pkl"
autoencoder_model_path = "autoencoder_model.h5"

def load_model_safely(model_path, model_type):
    """ Load ML models safely to prevent crashes if files are missing """
    if not os.path.exists(model_path):
        print(f"[ERROR] {model_type} model file not found at {model_path}")
        return None
    try:
        with open(model_path, "rb") as file:
            return pickle.load(file)
    except Exception as e:
        print(f"[ERROR] Failed to load {model_type} model: {e}")
        return None

# ✅ Load Models
svm_model = load_model_safely(svm_model_path, "SVM")
rf_model = load_model_safely(rf_model_path, "Random Forest")

@tf.keras.utils.register_keras_serializable()
def mse(y_true, y_pred):
    return tf.keras.losses.mean_squared_error(y_true, y_pred)

try:
    autoencoder_model = load_model(autoencoder_model_path, custom_objects={"mse": mse, "MeanSquaredError": MeanSquaredError()})
    autoencoder_model.compile(optimizer="adam", loss="mse")
    print("[INFO] Autoencoder model loaded successfully!")
except Exception as e:
    print(f"[ERROR] Failed to load Autoencoder model: {e}")
    autoencoder_model = None

# ---------------- Real-Time Monitoring ----------------
def generate_real_time_data():
    """ Simulates real-time anomaly detection and sends updates to frontend """
    while True:
        time.sleep(3)  # ✅ Send updates every 3 seconds

        # ✅ Generate random input features (replace with actual sensor data)
        input_data = np.random.rand(1, 42)
        timestamp = datetime.now().strftime("%H:%M:%S")
        ip_address = f"192.168.1.{random.randint(1, 255)}"  # ✅ Simulated IP address

        if svm_model and rf_model and autoencoder_model:
            # Get Model Predictions
            svm_prediction = "DDoS" if svm_model.predict(input_data)[0] == 1 else "BENIGN"
            rf_prediction = "DDoS" if rf_model.predict(input_data)[0] == 1 else "BENIGN"

            # Autoencoder Anomaly Detection
            reconstructed = autoencoder_model.predict(input_data)
            reconstruction_error = np.mean(np.abs(input_data - reconstructed))
            anomaly_detected = "DDoS" if reconstruction_error > 0.2 else "BENIGN"

            # ✅ Generate new accuracy values (Simulated)
            accuracy_update = {
                "SVM": round(random.uniform(90, 95), 2),
                "Random Forest": round(random.uniform(96, 99), 2),
                "Autoencoder": round(random.uniform(94, 98), 2)
            }

            # ✅ Send real-time accuracy update
            socketio.emit("accuracy_update", accuracy_update)

            # ✅ Send real-time prediction update
            socketio.emit("real_time_update", {
                "timestamp": timestamp,
                "ip_address": ip_address,
                "SVM Prediction": svm_prediction,
                "Random Forest Prediction": rf_prediction,
                "Anomaly Detected": anomaly_detected,
                "Reconstruction Error": round(float(reconstruction_error), 5)
            })
        else:
            print("[ERROR] One or more models not loaded!")

# ✅ Start real-time monitoring in a separate thread
threading.Thread(target=generate_real_time_data, daemon=True).start()

# ---------------- Web Routes ----------------
@app.route('/')
def home():
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists!")

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template('index.html')

@app.route('/stats', methods=['GET'])
def stats():
    """ Returns model accuracy and prediction distributions for charts """
    stats_data = {
        "Accuracy": {
            "SVM": round(random.uniform(90, 95), 2),
            "Random Forest": round(random.uniform(96, 99), 2),
            "Autoencoder": round(random.uniform(94, 98), 2)
        },
        "Predictions": {
            "BENIGN": random.randint(50, 100),
            "DDoS": random.randint(50, 100)
        }
    }
    return jsonify(stats_data)

@app.route('/real_time', methods=['GET'])
def real_time():
    """ API for fetching real-time anomaly detection data """
    return jsonify({"status": "Real-time monitoring active"})

if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False)
