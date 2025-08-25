**CPU\_Line\_Art - Futuristic Image Processor**

CPU\_Line\_Art is a Python desktop tool that transforms images into futuristic line art using edge detection, styling effects, and background transparency.

---

## Table of Contents

1. [Features](#features)
2. [Demo](#demo)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Configuration & Settings](#configuration--settings)
7. [Project Structure](#project-structure)
8. [Logging & Assets](#logging--assets)
9. [Contributing](#contributing)
10. [License](#license)

---

## Features

* **Interactive GUI** built with Tkinter and ttk
* **Edge Detection**: Adjustable Canny thresholds
* **Styling Options**: Smooth, Sharp, Clean effects
* **Color Modes**: Black-on-white, White-on-black
* **Brightness & Thickness Controls**
* **Export**: Save as BMP, JPEG, PNG, TIFF, or PDF
* **Transparent Background** export on PNG
* **Aspect Ratio Lock** with custom dimensions
* **Quality Profiles**: Good, Best, Highest (memory-aware)
* **Logging** to `All_Logs.log`

---

## Demo

1. Run the application:

   ```bash
   python main.py
   ```
2. In the GUI, click **Upload Image** and choose an image file.
3. Adjust **Detail**, **Thickness**, **Brightness**, **Style**, and **Color Mode**.
4. Preview original vs processed art side-by-side.
5. Set desired **Width** & **Height**, toggle **Maintain Aspect Ratio**.
6. Choose **Format** and **Quality**, then click **Download Image** or **Download Transparent**.

---

## Requirements

List of required Python packages (no versions):

```txt
pillow
opencv-python
numpy
psutil
```

> **Note:** `tkinter`, `threading`, `subprocess`, `sys`, and `logging` are in the standard library.

---

## Installation

1. Clone or download this repository.
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

```bash
python main.py
```

* Use the intuitive GUI to load images and apply effects.
* Export final art via the download buttons.

---

## Configuration & Settings

* **Detail Slider**: Controls edge sensitivity.
* **Thickness Slider**: Adjusts line boldness.
* **Brightness Slider**: Alters image brightness pre-detection.
* **Styles**: *Smooth*, *Sharp*, *Clean*.
* **Color Mode**: *Black-on-white* or *White-on-black*.
* **Maintain Aspect Ratio** toggle.
* **Quality Profiles**: impacts resolution and memory usage.

---

## Project Structure

```
├── main.py            # Application entry point
├── botboy_icon.ico    # App icon asset
├── botboy_jpg.jpg     # Example image asset
├── README.md          # Project documentation
├── requirements.txt   # Dependency list
└── All_Logs.log       # Generated logs
```

---

## Logging & Assets

* **All\_Logs.log**: Records all operations and errors.
* **Assets**:

  * `botboy_icon.ico`: Application icon
  * `botboy_jpg.jpg`: Sample input image

---

## Contributing

1. Fork the repo.
2. Create a branch: `git checkout -b feature/your-feature`.
3. Commit: `git commit -m 'Add feature'`.
4. Push: `git push origin feature/your-feature`.
5. Open a Pull Request.

---

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
