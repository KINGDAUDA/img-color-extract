import os
from flask import Flask, render_template, request, flash, redirect, url_for
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from flask_bootstrap import Bootstrap5
import io, base64
import webcolors

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "img-proc-secret-key")
bootstrap = Bootstrap5(app)

#   Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}


def allowed_filename(filename):
    # os.path.splitext splits 'img.jpg' into ('img', 'jpg')
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    return ext in ALLOWED_EXTENSIONS

def get_closest_color_name(requested_rgb):
    """Finds the closest CSS3 color name using Euclidean distance via webolors."""
    try:
        # Check if the RGB matches an exact CSS3 name first
        return webcolors.rgb_to_name(requested_rgb, spec="css3")
    except ValueError:
        # If no exact match, find the closest Euclidean distance in 3d RGB
        min_distance = float("inf")
        closest_name = "unknown"
        r_target, g_target, b_target = requested_rgb

        try:
            css3_names = webcolors.names("css3")
        except AttributeError:
            css3_names = webcolors.CSS3_NAMES_TO_HEX.keys()

        for name in css3_names:
            r_c, g_c, b_c = webcolors.name_to_rgb(name)
            distance = (r_target - r_c) ** 2 + (g_target - g_c) ** 2 + (b_target - b_c) ** 2
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        return closest_name

def extract_colors_from_array(img_array, k):
    """Quantizes an image from a NumPy array and calculates color frequency"""
    # Convert numpy array back to PIL Image for mediancut quantization
    quantized = Image.fromarray(img_array).quantize(colors=k, method=Image.Quantize.MEDIANCUT)

    total_pixels = img_array.shape[0] * img_array.shape[1]

    # Retriev pizel counts and flat RGB palette
    palette_counts = quantized.getcolors(maxcolors=k * 2) or []
    raw_palette = quantized.getpalette()

    # Sort descending by pixel count
    palette_counts.sort(key=lambda item: item[0], reverse=True)

    grouped_colors = {}

    for count, idx in palette_counts:
        r = raw_palette[idx * 3]
        g = raw_palette[idx * 3 + 1]
        b = raw_palette[idx * 3 + 2]

        rgb_str = f"rgb({r}, {g}, {b})"
        hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
        name = get_closest_color_name((r, g, b))
        percentage = round((count / total_pixels) * 100, 1)

        variation_data = {
            "hex": hex_code,
            "rgb": rgb_str,
            "count": count,
            "percentage": percentage
        }

        if name not in grouped_colors:
            grouped_colors[name] = {
                "name": name,
                "primary_hex": hex_code,
                "total_percentage": percentage,
                "variations": [variation_data]
            }
        else:
            grouped_colors[name]["variations"].append(variation_data)
            grouped_colors[name]["total_percentage"] = round(
                grouped_colors[name]["total_percentage"] + percentage, 1
            )

    # Convert dictionary values to a list sorted by total percentage presence
    sorted_groups = sorted(
        grouped_colors.values(),
        key=lambda x:  x["total_percentage"],
        reverse=True
    )

    return sorted_groups



#   ROUTES
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract():

        #   1. Grab the file and validate response
        uploaded_image = request.files.get("image")
        if not uploaded_image or uploaded_image.filename == "":
            flash("Please select an image file.", "danger")
            return redirect(url_for("home"))

        #   2. Check extension on the string filename
        if not allowed_filename(uploaded_image.filename):
            flash(f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}", "danger")
            return redirect(url_for("home"))

        #   3. Parse and clamp k

        k = int(request.form.get("num_colors", 5))
        k = max(1, min(k, 10))

        #   4. In-memory validation
        try:
            #   Read the file directly into memory without saving to disk
            img_bytes = uploaded_image.read()
            image = Image.open(io.BytesIO(img_bytes))

            #   Verify it is actually a valid image file, not a malicious script
            image.verify()

            #Re-open after verify (verifying it closes/exhausts the buffer pointer)
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            resized_img = image.resize((150, 150), Image.Resampling.LANCZOS)
            img_array = np.array(resized_img)

            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            buffered.seek(0)    # Rewinding buffer pointer to start

        except Exception as e:
            flash(f"Not a valid image. {str(e)}", "danger")
            return redirect(url_for("home"))

        #   5. Extract colors using Quantization + webcolors
        colors = extract_colors_from_array(img_array, k)

        #   6. Encode original image bytes for index.html display
        raw_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")


        return render_template(
            "index.html",
            processed=True,
            image_b64=raw_b64,    # base64 string
            colors=colors
        )




if __name__ == "__main__":
    app.run(debug=True)