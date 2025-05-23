import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.gif_service import create_gif_from_image, UPLOADS_DIR, GENERATED_GIFS_DIR, ensure_directories_exist
from app.services.price_service import get_current_mock_prices

# Ensure upload and generated_gifs directories exist when this module is loaded
# This is called in gif_service.create_gif_from_image and its test fixture,
# but also good to have it here if routes are imported before a service call in some scenarios.
ensure_directories_exist()

nft_bp = Blueprint('nft_bp', __name__, url_prefix='/api/nft')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
simulated_nft_db = [] # In-memory "database" for minted NFTs

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@nft_bp.route('/mint', methods=['POST']) # Renamed from '/upload_image'
def mint_nft_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    nft_type = request.form.get('nft_type') # Get 'nft_type' from form data

    if not nft_type or nft_type not in ['short', 'long']:
        return jsonify({"error": "Missing or invalid nft_type. Must be 'short' or 'long'."}), 400

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_image_path = os.path.join(UPLOADS_DIR, filename)
        
        try:
            file.save(uploaded_image_path)
        except Exception as e:
            return jsonify({"error": f"Failed to save uploaded file: {str(e)}"}), 500

        output_filename_no_ext = os.path.splitext(filename)[0]
        # Using absolute paths for gif_service and then creating relative ones for response
        absolute_gif_path = create_gif_from_image(uploaded_image_path, output_filename_no_ext)
        
        if absolute_gif_path:
            prices = get_current_mock_prices()
            
            # Create relative paths for URLs to be returned in JSON
            relative_gif_url = os.path.join('generated_gifs', os.path.basename(absolute_gif_path)).replace("\\", "/")
            relative_original_image_url = os.path.join('uploads', filename).replace("\\", "/")

            nft_data = {
                'id': str(uuid.uuid4()),
                'gif_url': f"/api/nft/{relative_gif_url}", # Full path for frontend to fetch
                'original_image_url': f"/api/nft/{relative_original_image_url}", # Full path
                'nft_type': nft_type,
                'creation_timestamp': datetime.utcnow().isoformat() + "Z", # Added Z for UTC
                'minting_price_btc': prices['btc_usd'],
                'minting_price_sol': prices['sol_usd']
            }
            simulated_nft_db.append(nft_data)
            
            return jsonify(nft_data), 201
        else:
            if os.path.exists(uploaded_image_path):
                os.remove(uploaded_image_path)
            return jsonify({"error": "Failed to create GIF"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

# Serve generated_gifs and uploads for the frontend to display
@nft_bp.route('/generated_gifs/<path:filename>', methods=['GET'])
def get_generated_gif(filename):
    abs_generated_gifs_dir = os.path.abspath(GENERATED_GIFS_DIR)
    return send_from_directory(abs_generated_gifs_dir, filename)

@nft_bp.route('/uploads/<path:filename>', methods=['GET'])
def get_uploaded_image(filename):
    abs_uploads_dir = os.path.abspath(UPLOADS_DIR)
    return send_from_directory(abs_uploads_dir, filename)

# Helper for send_from_directory - might be needed if not already imported by Flask.
# It's usually available if Flask is.
from flask import send_from_directory

@nft_bp.route('/all', methods=['GET']) # Changed to /all to avoid potential conflict if /api/nft/ is base
def list_all_nfts():
    """
    Returns a list of all minted NFTs.
    """
    # Sort by creation_timestamp descending if desired, but not strictly required here
    # sorted_nfts = sorted(simulated_nft_db, key=lambda x: x['creation_timestamp'], reverse=True)
    return jsonify(simulated_nft_db), 200
