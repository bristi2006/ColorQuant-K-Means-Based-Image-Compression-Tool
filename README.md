# K-Means Image Compression

A Streamlit application for image compression with K-Means clustering and a Pillow-based encoding pipeline.

The app keeps the existing K-Means algorithm in [kmeans.py](kmeans.py), but the surrounding flow has been refactored for production-style deployment:

- Real file-size compression using Pillow encoding
- PNG and JPEG output support
- Configurable JPEG quality and PNG compression level
- Automatic resizing for large uploads before clustering
- Real compression metrics, including file-size reduction, compression ratio, dimensions, and execution time
- In-memory processing that is suitable for Streamlit Community Cloud

## Run Locally

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Launch the Streamlit app:

```bash
streamlit run app.py
```

## How It Works

1. Upload a PNG or JPEG image.
2. Choose the K-Means cluster count and iteration budget.
3. Set the maximum processing dimension to automatically resize large uploads.
4. Choose PNG or JPEG output and configure the encoder.
5. The app runs K-Means on the resized working image, encodes the result with Pillow, and reports the real byte savings.

## Project Structure

```text
image_compression/
|-- app.py
|-- kmeans.py
|-- utils.py
|-- requirements.txt
|-- README.md
|-- notebooks/
|   |-- main.ipynb
|-- outputs/
```

## Deployment Notes

This repository is ready for Streamlit Community Cloud as long as `app.py` is the entry point and `requirements.txt` is used during build.

The runtime writes nothing permanent to disk. The compressed file is generated in memory and delivered directly through the download button.

## Notes

- Input formats: PNG, JPG, JPEG
- Output formats: PNG, JPEG
- Transparency is flattened to white before RGB processing and JPEG encoding.
- The output can become larger than the input when the chosen settings favor quality over size reduction. The metrics panel reports that honestly.