from tkinter import *
from tkinter import messagebox
import PIL
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageFont
from io import BytesIO
import requests
import platform

# -------------------------WINDOW-------------------------
root = Tk()
root.title("Watermark App")

if platform.system() == "Windows":
    root.state('zoomed')
else:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")


# -------------------------METHODS-------------------------
def get_img_from_url():
    try:
        url = img_url_input.get()
        response = requests.get(url)
        img_data = BytesIO(response.content)
        img_pil = Image.open(img_data).convert("RGBA")

    except requests.exceptions.MissingSchema:
        messagebox.showerror("Error", message="The provided URL is missing a protocol (e.g., https://).")
        return False

    except PIL.UnidentifiedImageError:
        messagebox.showerror("Error", message="The file could not be identified as a valid image.")
        return False

    except requests.exceptions.InvalidSchema:
        "The URL contains an invalid or unsupported protocol."
        return False
    else:
        return img_pil


def generate_preview(img_orig):
    max_width = 1000
    max_height = 400

    watermark_text = watermark_text_input.get().strip()
    if watermark_text:
        if img_orig.height > max_height:
            width_scale = max_height / img_orig.height
            img_orig = img_orig.resize((int(img_orig.width * width_scale), max_height), Image.Resampling.LANCZOS)
            img_orig = img_orig.filter(ImageFilter.SHARPEN)

        if img_orig.width > max_width:
            height_scale = max_width / img_orig.width
            img_orig = img_orig.resize((max_width, int(img_orig.height * height_scale)), Image.Resampling.LANCZOS)
            img_orig = img_orig.filter(ImageFilter.SHARPEN)

        img_orig = add_watermark(img_orig, f"© {watermark_text}")
        img_tk = ImageTk.PhotoImage(img_orig)

        return img_tk
    else:
        messagebox.showerror("Error", "Watermark text input cannot be empty.")
        return False


def generate_img():
    # Getting image from url
    img_pil = get_img_from_url()
    clear_button.config(state="normal")

    if not img_pil:
        return

    # Preview Image
    img_tk_preview = generate_preview(img_pil)
    if not img_tk_preview:
        return

    img_label.config(image=img_tk_preview)  # type: ignore
    img_label.image = img_tk_preview

    img_label.config(width=str(img_tk_preview.width()), height=str(img_tk_preview.height()))


def add_watermark(image: Image, watermark_txt: str):
    text_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    font_size = int(min(image.width, image.height) * 0.1)
    font = ImageFont.load_default(font_size)
    text_size = draw.textbbox((0, 0), watermark_txt, font)

    x = (image.width - text_size[2] - text_size[0]) / 2
    y = (image.height - text_size[3] - text_size[1]) / 2
    draw.text(xy=(x, y), text=watermark_txt, font=ImageFont.load_default(font_size), fill=(255, 255, 255, 128))
    return Image.alpha_composite(image, text_layer).convert("RGB")


def clear():
    placeholder = PhotoImage(file="white-placeholder.png")
    img_url_input.delete(0, END)
    img_label.config(image=placeholder, width=400, height=400)
    img_label.image = placeholder
    download_button.config(state="disabled")
    clear_button.config(state="disabled")


# -------------------------OBJECTS-------------------------
Label(text="Watermatk Text").pack(pady=(35, 0))
watermark_text_input = Entry(width=80)
watermark_text_input.pack()

Label(text="Image Url").pack(pady=(4, 0))
top_frame = Frame(root)
top_frame.pack(pady=(0, 10))

clear_button = Button(top_frame, text="Clear", width=8, command=clear, state="disabled")
clear_button.pack(side=LEFT)

img_url_input = Entry(top_frame, width=80)
img_url_input.pack(side=LEFT, padx=10)

generate_button = Button(top_frame, text="Generate", width=8, command=generate_img)
generate_button.pack(side=RIGHT)

img = PhotoImage(file="white-placeholder.png")
img_label = Label(root, image=img, width=400, height=400, anchor="center")
img_label.pack(pady=20)

download_button = Button(text="Download", state="disabled", width=8)
download_button.pack(pady=10)


# ----------------------------------------------------------
root.mainloop()