"""Generate application icon (run once before building installer)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)


def create_icon() -> None:
    size = 256
    img = Image.new("RGBA", (size, size), (37, 99, 235, 255))
    draw = ImageDraw.Draw(img)

    margin = 48
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=24,
        fill=(255, 255, 255, 255),
    )

    text = "PDF"
    try:
        font = ImageFont.truetype("arial.ttf", 56)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 8), text, fill=(37, 99, 235, 255), font=font)

    png_path = ASSETS / "icon.png"
    ico_path = ASSETS / "icon.ico"
    img.save(png_path)

    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
    icons[0].save(ico_path, format="ICO", sizes=[(i.width, i.height) for i in icons])
    print(f"Created {ico_path}")


if __name__ == "__main__":
    create_icon()
