import os
import io
import json
import pytest
from app.main import app as flask_app # Import the Flask app instance
from app.routes.nft_routes import simulated_nft_db, UPLOADS_DIR, GENERATED_GIFS_DIR
from unittest.mock import patch

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Ensure the app is in testing mode
    flask_app.config.update({
        "TESTING": True,
    })
    # Clear the simulated_nft_db before each test
    simulated_nft_db.clear()
    
    # Ensure upload and generated_gifs directories exist
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    if not os.path.exists(GENERATED_GIFS_DIR):
        os.makedirs(GENERATED_GIFS_DIR)

    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# Mock prices for consistent testing of minting price in NFT data
MOCK_PRICES_FOR_TESTS = {'btc_usd': 50000, 'sol_usd': 150}

@patch('app.routes.nft_routes.get_current_mock_prices') # Path to where get_current_mock_prices is *used*
def test_mint_nft_success(mock_get_prices, client):
    mock_get_prices.return_value = MOCK_PRICES_FOR_TESTS
    
    # Create a minimal valid PNG in memory for testing
    img = Image.new('RGB', (2, 2), color='blue') # Small valid image
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0) # Reset stream position

    data = {
        'file': (img_byte_arr, 'test_image.png'), # Example filename
        'nft_type': 'long'
    }
    
    response = client.post('/api/nft/mint', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}. Response data: {response.data.decode()}"
    
    response_json = response.get_json()
    assert response_json is not None, "Response should be JSON"
    
    # Verify response JSON structure
    expected_keys = ['id', 'gif_url', 'original_image_url', 'nft_type', 'creation_timestamp', 'minting_price_btc', 'minting_price_sol']
    for key in expected_keys:
        assert key in response_json, f"Key '{key}' missing in mint response"
    
    assert response_json['nft_type'] == 'long'
    assert response_json['minting_price_btc'] == MOCK_PRICES_FOR_TESTS['btc_usd']
    assert response_json['minting_price_sol'] == MOCK_PRICES_FOR_TESTS['sol_usd']
    
    # Verify in-memory DB
    assert len(simulated_nft_db) == 1
    assert simulated_nft_db[0]['id'] == response_json['id']
    
    # Verify GIF and original file were "created" (mocked service, so check paths)
    # For a true check, we'd need to inspect GENERATED_GIFS_DIR and UPLOADS_DIR
    # This requires knowing the exact filename, which might be tricky if it's altered (e.g., secure_filename)
    # The gif_url and original_image_url in response are the best indicators here.
    
    # Extract relative paths from the URLs
    # Example: /api/nft/generated_gifs/test_image.gif -> generated_gifs/test_image.gif
    relative_gif_path = response_json['gif_url'].replace("/api/nft/", "")
    relative_original_path = response_json['original_image_url'].replace("/api/nft/", "")

    # Check if the files (as named in the response) exist
    # Note: create_gif_from_image might use a different name if secure_filename changes it.
    # This test assumes 'test_image.gif' and 'test_image.png' are the actual output names.
    # A more robust test might involve listing directory contents or having create_gif_from_image return the exact path.
    # For now, we'll assume the names are predictable for this test.
    
    # The dummy image content "dummy_image_content_for_test" is not a valid PNG.
    # Pillow will likely fail to open it. We need a valid PNG for create_gif_from_image to succeed.
    # Let's replace the dummy_image_data with a real minimal PNG.
    
    # This part of the test will be revisited after fixing the dummy image data.
    # For now, we focus on the API response and DB state.
    
    # Cleanup created files
    if os.path.exists(os.path.join(GENERATED_GIFS_DIR, os.path.basename(response_json['gif_url']))):
        os.remove(os.path.join(GENERATED_GIFS_DIR, os.path.basename(response_json['gif_url'])))
    if os.path.exists(os.path.join(UPLOADS_DIR, os.path.basename(response_json['original_image_url']))):
        os.remove(os.path.join(UPLOADS_DIR, os.path.basename(response_json['original_image_url'])))


def test_mint_nft_missing_file(client):
    data = {'nft_type': 'long'}
    response = client.post('/api/nft/mint', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'No file part' in response.get_json()['error']

def test_mint_nft_invalid_type(client):
    # Create a minimal valid PNG in memory for testing
    img = Image.new('RGB', (1, 1), color='yellow')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    data = {
        'file': (img_byte_arr, 'test.png'), # Valid image, but invalid type
        'nft_type': 'invalid_type' # Not 'long' or 'short'
    }
    response = client.post('/api/nft/mint', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'Missing or invalid nft_type' in response.get_json()['error']

@patch('app.routes.nft_routes.get_current_mock_prices')
def test_list_all_nfts(mock_get_prices, client):
    mock_get_prices.return_value = MOCK_PRICES_FOR_TESTS
    
    # First, mint an NFT to populate the database
    # Create a minimal valid PNG in memory
    img = Image.new('RGB', (1, 1), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    mint_data = {
        'file': (img_byte_arr, 'test_list.png'),
        'nft_type': 'short'
    }
    mint_response = client.post('/api/nft/mint', data=mint_data, content_type='multipart/form-data')
    assert mint_response.status_code == 201
    minted_nft_data = mint_response.get_json()

    # Now, test the /api/nft/all endpoint
    response = client.get('/api/nft/all')
    assert response.status_code == 200
    
    nfts_list = response.get_json()
    assert isinstance(nfts_list, list)
    assert len(nfts_list) == 1
    assert nfts_list[0]['id'] == minted_nft_data['id']
    assert nfts_list[0]['nft_type'] == 'short'

@patch('app.routes.nft_routes.get_current_mock_prices')
def test_file_serving(mock_get_prices, client):
    mock_get_prices.return_value = MOCK_PRICES_FOR_TESTS

    # Create a minimal valid PNG in memory
    img = Image.new('RGB', (10, 10), color='blue') # Slightly larger to avoid issues
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    mint_data = {
        'file': (img_byte_arr, 'serve_test.png'),
        'nft_type': 'long'
    }
    mint_response = client.post('/api/nft/mint', data=mint_data, content_type='multipart/form-data')
    assert mint_response.status_code == 201
    minted_nft_data = mint_response.get_json()

    # Test serving the generated GIF
    gif_url = minted_nft_data['gif_url']
    # gif_url is like /api/nft/generated_gifs/serve_test.gif
    # The test client makes requests to the app, so this path should work directly.
    gif_response = client.get(gif_url)
    assert gif_response.status_code == 200, f"Failed to get GIF. URL: {gif_url}. Response: {gif_response.data}"
    assert gif_response.content_type == 'image/gif' # Check content type

    # Test serving the original uploaded image
    original_image_url = minted_nft_data['original_image_url']
    image_response = client.get(original_image_url)
    assert image_response.status_code == 200, f"Failed to get original image. URL: {original_image_url}. Response: {image_response.data}"
    assert image_response.content_type == 'image/png' # Or 'image/jpeg' depending on upload

    # Clean up the created files after test (optional, but good practice)
    # Extract paths relative to project root or a known base directory
    gif_filename = os.path.basename(gif_url)
    original_filename = os.path.basename(original_image_url)

    # These paths are now relative to GENERATED_GIFS_DIR and UPLOADS_DIR
    if os.path.exists(os.path.join(GENERATED_GIFS_DIR, gif_filename)):
        os.remove(os.path.join(GENERATED_GIFS_DIR, gif_filename))
    if os.path.exists(os.path.join(UPLOADS_DIR, original_filename)):
        os.remove(os.path.join(UPLOADS_DIR, original_filename))

# Note: The test_mint_nft_success needs a valid image for create_gif_from_image to not fail.
# The current `dummy_image_data` is just bytes, not a PNG.
# This was addressed in test_list_all_nfts and test_file_serving by creating a valid PNG in memory.
# This should be retroactively applied or considered for test_mint_nft_success.
# For now, test_mint_nft_success primarily tests API contract and DB update.
# The file existence part in test_mint_nft_success might fail if the image is invalid.
# Let's refine test_mint_nft_success to use a valid image.

@patch('app.routes.nft_routes.get_current_mock_prices') # Path to where get_current_mock_prices is *used*
def test_mint_nft_success_with_valid_image(mock_get_prices, client):
    mock_get_prices.return_value = MOCK_PRICES_FOR_TESTS
    
    # Create a minimal valid PNG in memory
    img = Image.new('RGB', (5, 5), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0) # Reset stream position to the beginning
    
    data = {
        'file': (img_byte_arr, 'valid_test_image.png'),
        'nft_type': 'long'
    }
    
    response = client.post('/api/nft/mint', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 201, f"Response data: {response.data.decode()}"
    response_json = response.get_json()
    assert response_json is not None
    
    expected_keys = ['id', 'gif_url', 'original_image_url', 'nft_type', 'creation_timestamp', 'minting_price_btc', 'minting_price_sol']
    for key in expected_keys:
        assert key in response_json
    
    assert len(simulated_nft_db) == 1
    
    # Verify that actual files were created
    gif_filename = os.path.basename(response_json['gif_url'])
    original_filename = os.path.basename(response_json['original_image_url'])

    assert os.path.exists(os.path.join(GENERATED_GIFS_DIR, gif_filename)), f"GIF file {gif_filename} not found in {GENERATED_GIFS_DIR}"
    assert os.path.exists(os.path.join(UPLOADS_DIR, original_filename)), f"Original image {original_filename} not found in {UPLOADS_DIR}"

    # Cleanup
    if os.path.exists(os.path.join(GENERATED_GIFS_DIR, gif_filename)):
        os.remove(os.path.join(GENERATED_GIFS_DIR, gif_filename))
    if os.path.exists(os.path.join(UPLOADS_DIR, original_filename)):
        os.remove(os.path.join(UPLOADS_DIR, original_filename))

# Need to import Image from PIL for the valid image tests
from PIL import Image
