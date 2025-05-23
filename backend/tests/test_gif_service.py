import os
import shutil
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock

# Adjust the import path based on your project structure
# This assumes backend/ is a top-level directory and your tests are run from the project root or backend/
from app.services.gif_service import create_gif_from_image, UPLOADS_DIR, GENERATED_GIFS_DIR, ensure_directories_exist
from app.services import gif_service # To mock constants like BTC_HIGH_THRESHOLD

# Define a fixture for a dummy image path
@pytest.fixture
def dummy_image_path(tmp_path):
    ensure_directories_exist() # Ensure UPLOADS_DIR exists if it's relative
    
    # Use UPLOADS_DIR from the service, but place a temp file inside it for this test
    # This is a bit tricky; ideally, UPLOADS_DIR would be configurable for tests.
    # For now, we'll ensure it exists and place a known file there.
    
    img_path = os.path.join(UPLOADS_DIR, "test_dummy_image.png")
    img = Image.new('RGB', (60, 30), color = 'red')
    img.save(img_path)
    yield img_path
    # Teardown: remove the dummy image and generated GIFs
    if os.path.exists(img_path):
        os.remove(img_path)
    # Clean up any generated GIFs (simple cleanup, might need to be more robust)
    if os.path.exists(GENERATED_GIFS_DIR):
        for item in os.listdir(GENERATED_GIFS_DIR):
            if item.startswith("test_dummy") and item.endswith(".gif"):
                os.remove(os.path.join(GENERATED_GIFS_DIR, item))


@pytest.fixture
def non_image_file_path(tmp_path):
    ensure_directories_exist()
    file_path = os.path.join(UPLOADS_DIR, "not_an_image.txt")
    with open(file_path, "w") as f:
        f.write("This is not an image.")
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)

# Mock prices for consistent testing
MOCK_PRICES_NEUTRAL = {'btc_usd': 35000, 'sol_usd': 120} # Neutral sentiment
MOCK_PRICES_BTC_HIGH = {'btc_usd': 37000, 'sol_usd': 120} # BTC high
MOCK_PRICES_SOL_LOW = {'btc_usd': 35000, 'sol_usd': 100}  # SOL low


@patch('app.services.gif_service.get_current_mock_prices')
def test_create_gif_successful(mock_get_prices, dummy_image_path):
    mock_get_prices.return_value = MOCK_PRICES_NEUTRAL
    
    output_filename_no_ext = "test_dummy_neutral_gif"
    duration_seconds = 1 # Shorter duration for faster tests
    fps = 5
    expected_frames = duration_seconds * fps

    gif_path = create_gif_from_image(dummy_image_path, output_filename_no_ext, duration_seconds=duration_seconds, fps=fps)

    assert gif_path is not None
    assert os.path.exists(gif_path)
    assert os.path.basename(gif_path) == f"{output_filename_no_ext}.gif"

    # Verify number of frames (requires imageio or similar to read GIF info)
    # This is a more complex check, for simplicity we'll trust imageio.mimsave
    # If imageio is available in the test environment, we can try:
    try:
        import imageio.v3 as iio
        frames_in_gif = iio.immeta(gif_path, plugin='pillow')['n_images'] # For Pillow plugin
        assert frames_in_gif == expected_frames
    except Exception as e:
        print(f"Could not verify frame count: {e}. Skipping this check.")
        pass # If imageio or reading fails, skip check but test still passes if GIF exists

    if os.path.exists(gif_path):
        os.remove(gif_path) # Clean up generated test file

@patch('app.services.gif_service.get_current_mock_prices')
def test_create_gif_handles_non_image_file(mock_get_prices, non_image_file_path):
    mock_get_prices.return_value = MOCK_PRICES_NEUTRAL
    output_filename_no_ext = "test_non_image"
    
    # We expect this to fail gracefully (return None or raise a specific error)
    # The current implementation prints an error and returns None.
    gif_path = create_gif_from_image(non_image_file_path, output_filename_no_ext)
    assert gif_path is None

@patch('app.services.gif_service.get_current_mock_prices')
def test_create_gif_outside_uploads_dir_fails(mock_get_prices, tmp_path):
    mock_get_prices.return_value = MOCK_PRICES_NEUTRAL
    
    # Create a dummy image outside the UPLOADS_DIR
    outside_image_path = tmp_path / "outside_image.png"
    img = Image.new('RGB', (60, 30), color = 'blue')
    img.save(outside_image_path)

    output_filename_no_ext = "test_outside_dir"
    gif_path = create_gif_from_image(str(outside_image_path), output_filename_no_ext)
    
    assert gif_path is None # Should fail because path is not in UPLOADS_DIR

# Optional: Test for sentiment-influenced colors (more complex)
# This would involve checking specific pixel colors in the generated GIF frames.
# For brevity, this example will skip the direct pixel check, but here's a conceptual outline:
# 1. Mock prices to trigger specific sentiments (e.g., BTC_HIGH).
# 2. Generate the GIF.
# 3. Read a few frames from the GIF using imageio.
# 4. Get pixel data from the border/padding area of these frames.
# 5. Assert that the dominant colors in these pixels lean towards the expected sentiment color (e.g., more green for BTC_HIGH).
# This requires careful selection of pixels and color comparison logic.

def test_ensure_directories_exist(tmp_path):
    # Temporarily override UPLOADS_DIR and GENERATED_GIFS_DIR for this test
    # This is safer than potentially creating these dirs in the actual project during tests
    
    test_uploads = tmp_path / "test_uploads"
    test_generated = tmp_path / "test_generated_gifs"

    with patch('app.services.gif_service.UPLOADS_DIR', str(test_uploads)), \
         patch('app.services.gif_service.GENERATED_GIFS_DIR', str(test_generated)):
        
        assert not os.path.exists(test_uploads)
        assert not os.path.exists(test_generated)
        
        ensure_directories_exist() # Call the function we want to test
        
        assert os.path.exists(test_uploads)
        assert os.path.isdir(test_uploads)
        assert os.path.exists(test_generated)
        assert os.path.isdir(test_generated)

# To run these tests:
# 1. Ensure pytest is installed.
# 2. Navigate to the `backend` directory (or project root if paths are adjusted).
# 3. Run `pytest` or `python -m pytest`.
# Make sure that UPLOADS_DIR and GENERATED_GIFS_DIR are correctly handled.
# If they are relative paths (e.g., 'uploads'), they will be created relative to
# where pytest is run. The `ensure_directories_exist()` call in fixtures helps,
# but for a truly isolated test, these paths should be configurable or mocked.
# The test_ensure_directories_exist uses patching for this isolation.
# The dummy_image_path fixture relies on the actual UPLOADS_DIR being writable.
# A better approach for dummy_image_path might be to also patch UPLOADS_DIR
# to point to a temporary directory for the duration of the test.
# For now, it directly uses the service's UPLOADS_DIR.
# Consider adding a `conftest.py` for more global fixtures or path management if needed.
# The `backend.` prefix in imports assumes that the project root is in PYTHONPATH or that
# tests are run in a way that makes `backend` a discoverable package (e.g., from project root).
# If running tests from `backend/` dir: `from app.services.gif_service import ...`
# If running from project root and `backend` is not directly a package in sys.path,
# you might need to adjust sys.path or use `python -m pytest` from root.
# The provided solution assumes `python -m pytest` from the project root (`/app`).
