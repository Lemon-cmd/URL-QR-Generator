import argparse
import os
import subprocess
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import numpy as np
from PIL import Image
import qrcode

COLOR_MAP = {
    "red": (1.0, 0.0, 0.0),
    "black": (0.0, 0.0, 0.0),
    "green": (0.0, 0.5, 0.0),
    "blue": (0.0, 0.2, 0.8),
    "brown": (0.55, 0.27, 0.07),
}


def copy_png_to_macos_clipboard(pil_img: Image.Image):
    """Writes a transparent PNG to temp storage and loads it into the macOS pasteboard."""
    temp_path = os.path.abspath("/tmp/temp_qr_clip.png")
    pil_img.save(temp_path, format="PNG")

    # Tell macOS pasteboard to accept the file as transparent PNG bytes
    apple_script = f'set the clipboard to (read (POSIX file "{temp_path}") as «class PNGf»)'
    subprocess.run(["osascript", "-e", apple_script], check=True)

    if os.path.exists(temp_path):
        os.remove(temp_path)


def main():
    parser = argparse.ArgumentParser(
        description="macOS QR Code Generator with Alpha slider & direct Clipboard button."
    )
    parser.add_argument("url", type=str, help="The target URL or text to encode")
    parser.add_argument(
        "--color",
        "-c",
        type=str,
        default="blue",
        choices=COLOR_MAP.keys(),
        help="QR color (default: blue)",
    )
    args = parser.parse_args()

    # 1. Build QR matrix
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=2,
    )
    qr.add_data(args.url)
    qr.make(fit=True)

    matrix = np.array(qr.get_matrix(), dtype=bool)
    h, w = matrix.shape

    base_rgb = COLOR_MAP[args.color]
    initial_alpha = 1.0

    # 2. Build RGBA array
    rgba = np.zeros((h, w, 4), dtype=float)
    rgba[matrix, :3] = base_rgb
    rgba[matrix, 3] = initial_alpha
    rgba[~matrix, 3] = 0.0  # Transparent background

    # 3. Setup window
    fig, ax = plt.subplots(figsize=(6, 7))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    plt.subplots_adjust(bottom=0.25)

    im = ax.imshow(rgba, interpolation="nearest")
    ax.axis("off")

    # 4. Add Alpha Slider
    slider_ax = plt.axes([0.2, 0.14, 0.6, 0.03])
    alpha_slider = Slider(
        ax=slider_ax,
        label="Alpha",
        valmin=0.05,
        valmax=1.0,
        valinit=initial_alpha,
        valstep=0.01,
        color=base_rgb,
    )

    def update(val):
        rgba[matrix, 3] = alpha_slider.val
        im.set_data(rgba)
        fig.canvas.draw_idle()

    alpha_slider.on_changed(update)

    # 5. Add Copy Button
    button_ax = plt.axes([0.35, 0.05, 0.3, 0.05])
    copy_btn = Button(button_ax, "Copy QR", color="#EDEDED", hovercolor="#DCDCDC")

    def on_copy_click(event):
        # Convert float RGBA [0.0, 1.0] to uint8 [0, 255]
        img_bytes = (rgba * 255).astype(np.uint8)

        # Scale up using NEAREST neighbor so pixels stay crisp
        # (Default QR matrix is around ~35x35 px, this scales it to ~500-600 px)
        scale_factor = 16
        pil_img = Image.fromarray(img_bytes, "RGBA").resize(
            (w * scale_factor, h * scale_factor), Image.Resampling.NEAREST
        )

        try:
            copy_png_to_macos_clipboard(pil_img)
            copy_btn.label.set_text("Copied!")
            plt.close("all")
        except Exception as e:
            copy_btn.label.set_text("Error")
            print(f"Failed to copy: {e}")

        fig.canvas.draw_idle()

    copy_btn.on_clicked(on_copy_click)

    plt.show()


if __name__ == "__main__":
    main()
