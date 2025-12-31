# Professional Background Removal Tool

> **A local, high-performance background removal tool for designers, developers, and creators.**

![Demo](assets/demo.png)
*(Note: Add a `demo.png` to the assets folder showing Original | Mask | Result)*

## Problem
Removing backgrounds manually is tedious, and online tools often charge fees or compromise privacy. This tool provides **state-of-the-art AI background removal** locally on your machine, free and private.

## Features
-   **Multiple Models**: Choose between `u2net`, `birefnet`, `RMBG-2.0`, and `SAM 2` for different needs.
-   **Batch Processing**: Process hundreds of images in seconds.
-   **GPU Support**: Fully accelerated with CUDA for maximum speed.
-   **Privacy First**: No images leave your computer.

## Quick Start (Run in < 60s)

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Tool**
    ```bash
    python main.py remove -i input.jpg
    ```
    *Result will be saved as `input_no_bg.png`.*

## Detailed Usage

### Remove Background
The main command is `remove`. You can specify the model and output location.

```bash
# Basic usage
python main.py remove -i image.jpg

# Specify model and output directory
python main.py remove -i image1.jpg image2.jpg -o ./processed/ -m birefnet
```

**Flags:**
-   `-i`, `--input`: Path to one or more image files.
-   `-o`, `--output`: (Optional) Output directory or filename.
-   `-m`, `--model`: AI Model to use.
    -   `u2net` (Default): Fast, general purpose.
    -   `birefnet`: Best for fine details (hair, fur).
    -   `rmbg2`: High accuracy commercial model.
    -   `sam2`: Segment Anything Model 2 (Subject detection).

## Project Structure

```text
├── assets/              # Documentation images
├── backend/             # (Internal) Model weights and inference logic
├── main.py              # 🚀 Entry Point (Run this!)
├── requirements.txt     # Dependency list
├── LICENSE              # MIT License
└── *.py                 # Processing modules (imported by main.py)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)
