# QQ
Qrnft_final

---

## Project Structure

This project is organized into two main parts:

*   **`backend/`**: A Python Flask application that serves the API for NFT creation, management, and price data.
*   **`frontend/`**: A React application that provides the user interface for interacting with the platform.

## Running the Project

### Local Development

**1. Backend (Python/Flask):**
   *   Navigate to `cd backend`
   *   Create and activate a virtual environment:
       *   `python3 -m venv .venv`
       *   `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
   *   Install dependencies: `pip install -r requirements.txt`
   *   Run the backend: `python app/main.py`
   *   The backend will typically run on `http://127.0.0.1:5000`.

**2. Frontend (React):**
   *   Navigate to `cd frontend`
   *   Install dependencies: `npm install`
   *   Run the frontend: `npm start`
   *   The frontend will typically open on `http://localhost:3000` in your browser.

### Running in GitHub Codespaces

This project is configured to run smoothly in GitHub Codespaces.

**Automated Setup with `.devcontainer/devcontainer.json`:**

When you open this repository in a GitHub Codespace, the environment will be automatically configured based on the settings in the `.devcontainer/devcontainer.json` file. This includes:

*   Using a base image with Python and Node.js pre-installed.
*   **Automatic Dependency Installation**: The `postCreateCommand` will automatically run `pip install --user -r backend/requirements.txt` and `npm install --prefix frontend`. This means you don't need to manually install dependencies when the Codespace builds for the first time.
*   **Automatic Port Forwarding**: Ports `3000` (for the frontend) and `5000` (for the backend) will be automatically forwarded. You should see them listed in the "Ports" tab in VS Code, and Codespaces will often show notifications to open them in your browser or preview.
*   **Recommended VS Code Extensions**: Some useful extensions for Python and JavaScript development will be suggested or pre-installed.

**Starting the Application in Codespaces:**

Even with the automated setup, you still need to start the backend and frontend services manually in separate terminals within your Codespace:

1.  **Start the Backend:**
    *   Open a terminal in your Codespace.
    *   Navigate to the backend: `cd backend`
    *   If you prefer to use the virtual environment created by `postCreateCommand` (though dependencies are also globally available via `--user` for pip):
        *   `python3 -m venv .venv` (Only if you want a venv separate from the global user install. The `postCreateCommand` installs to user site-packages, which is fine for Codespaces.)
        *   `source .venv/bin/activate` (If you created it)
    *   Run the Flask app: `python app/main.py`
    *   The backend will be available on the forwarded port 5000.

2.  **Start the Frontend:**
    *   Open a new terminal in your Codespace (you can split the terminal or create a new tab).
    *   Navigate to the frontend: `cd frontend`
    *   Run the React app: `npm start`
    *   The frontend will be available on the forwarded port 3000. You can usually open this directly in a browser preview from the Codespace notification.

The `postAttachCommand` in `devcontainer.json` will also remind you of these commands when you connect to the Codespace.
