from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from flask_cors import CORS
import traceback
from PIL import Image

app = Flask(__name__)
CORS(app)  # Izinkan akses dari frontend

# LOAD MODEL
print("Memuat model Tomato97.keras...")
try:
    model = tf.keras.models.load_model("Tomato97.keras")
    print("Model berhasil dimuat!")
except Exception as e:
    print("Gagal memuat model:", e)
    raise e

# LABEL KELAS
class_names = [
    "Blight",
    "Healthy",
    "Leaf_Mold",
    "Spider_Mites",
    "Yellow_Leaf_Curl_Virus"
]

# PREPROCESSING
def preprocess_image(pil_image):
    pil_image = pil_image.resize((256, 256))

    img_array = image.img_to_array(pil_image)
    img_array = np.expand_dims(img_array, axis=0)

    # EfficientNet preprocess
    img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
    return img_array


# ENDPOINT PREDICT
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Pastikan ada file
        if "file" not in request.files:
            return jsonify({"error": "Tidak ada file yang diupload"}), 400

        uploaded_file = request.files["file"]

        # Load gambar dari stream
        img = Image.open(uploaded_file.stream).convert("RGB")

        # Preprocess
        processed_img = preprocess_image(img)

        # Predict
        predictions = model.predict(processed_img)
        idx = np.argmax(predictions[0])

        predicted_label = class_names[idx]
        confidence = float(predictions[0][idx])
        confidence_percent = f"{confidence * 100:.2f}%"

        # Probabilitas lengkap
        prob_dict = {
            class_names[i]: float(predictions[0][i])
            for i in range(len(class_names))
        }

        return jsonify({
            "label": predicted_label,
            "accuracy": confidence_percent,
            "probabilities": prob_dict
        })

    except Exception as e:
        print("\n=== ERROR TERJADI ===")
        print(traceback.format_exc())
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


@app.route("/")
def home():
    return "Tomato Disease Detection API is running!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)