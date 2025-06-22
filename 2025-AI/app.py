# app.py
import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image

# --- ML & UTILS IMPORTS ---
from ml_logic.processing import classify_image_with_clip, extract_dominant_colors, get_image_embedding
from ml_logic.recommender import generate_outfits
from ml_logic.utils import get_weather


# --- BASIC FLASK APP SETUP & DB ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/fashion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('uploads', 'clothing')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class ClothingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200), nullable=False) # The full server path
    category = db.Column(db.String(50), nullable=False)
    colors = db.Column(db.String(200), nullable=False)
    style_vector = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """Returns a dictionary representation that is safe for JSON serialization."""
        return {
            'id': self.id,
            'filename': self.filename, # Send only the filename to the frontend
            'category': self.category,
            'colors': json.loads(self.colors)
        }

with app.app_context():
    db.create_all()


# --- FLASK ROUTES ---

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serves an uploaded file from the UPLOAD_FOLDER."""
    # Note: Using os.path.basename to be extra safe, though secure_filename should handle it.
    return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(filename))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle image uploads, process them, and save to DB."""
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files')
    uploaded_items = []

    for file in files:
        if file.filename == '':
            continue
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            image = Image.open(filepath).convert("RGB")
            
            category = classify_image_with_clip(image)
            colors_json = extract_dominant_colors(filepath)
            embedding = get_image_embedding(image)
            embedding_json = json.dumps(embedding)

            new_item = ClothingItem(
                filename=filename,
                image_path=filepath, # Store the full path for server-side use
                category=category,
                colors=colors_json,
                style_vector=embedding_json
            )
            db.session.add(new_item)
            db.session.commit()
            
            uploaded_items.append(new_item.to_dict())

        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            os.remove(filepath)
            return jsonify({'error': f'Failed to process file {filename}.'}), 500

    return jsonify({'message': 'Files uploaded and processed successfully!', 'items': uploaded_items})


@app.route('/get_inventory', methods=['GET'])
def get_inventory():
    """Fetch all clothing items from the database."""
    items = ClothingItem.query.all()
    return jsonify([item.to_dict() for item in items])


@app.route('/generate', methods=['POST'])
def generate_recommendations():
    """Generate outfit recommendations."""
    data = request.get_json()
    city = data.get('city')

    if not city:
        return jsonify({'error': 'City is required'}), 400

    weather = get_weather(city)
    if not weather:
        return jsonify({'error': f'Could not get weather for {city}.'}), 404

    all_items = ClothingItem.query.all()
    outfits = generate_outfits(all_items, weather)
    
    serializable_outfits = []
    for outfit in outfits:
        serializable_outfit = {'label': outfit['label']}
        for key, item in outfit.items():
            if key != 'label':
                serializable_outfit[key] = item.to_dict()
        serializable_outfits.append(serializable_outfit)

    return jsonify({'outfits': serializable_outfits, 'weather': weather})


if __name__ == '__main__':
    app.run(debug=True, port=5001)