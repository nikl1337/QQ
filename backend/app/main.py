from flask import Flask
from app.routes.nft_routes import nft_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(nft_bp) # This was missing nft_bp

@app.route('/')
def home():
    return "Backend is running!"

if __name__ == '__main__':
    # Make sure UPLOADS_DIR and GENERATED_GIFS_DIR are created when app starts
    # This is already handled by ensure_directories_exist() in nft_routes and gif_service
    # which are called upon import or first request depending on implementation.
    # To be absolutely sure, we can call it here as well, though it might be redundant.
    # from backend.app.services.gif_service import ensure_directories_exist as ensure_gif_dirs_exist
    # ensure_gif_dirs_exist()
    
    app.run(debug=True, host='0.0.0.0', port=5000) # Added host and port for clarity
