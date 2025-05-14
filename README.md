# Tagify

Tagify is a desktop application for generating 3D printable Spotify code tags.

## Project Structure

- `main.py` - Entry point. Starts the application.
- `ui.py` - Contains the `TagifyApp` class and all UI logic.
- `modeling.py` - Handles 3D model generation and export.
- `utils.py` - Utility functions (Spotify parsing, web links, etc).
- `assets/` - Contains images, GIFs, and base models.
- `base_models/` - STEP files for base models.

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python main.py`

## How it Works

1. Enter a Spotify share link.
2. The app fetches the Spotify code and processes it.
3. Select a base model or upload your own.
4. Preview and export the 3D model.

## Extending

- Add new base models to `base_models/`.
- Customize model generation in `modeling.py`.
- UI changes go in `ui.py`.

## License

MIT License.
