"""
=========================================
Route Resilience AI
Input Selector
=========================================
"""

from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename


SUPPORTED_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
)


def get_sample_images():

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    sample_folder = PROJECT_ROOT / "sample_images"

    if not sample_folder.exists():
        raise FileNotFoundError(
            "sample_images folder not found."
        )

    images = []

    for ext in SUPPORTED_EXTENSIONS:
        images.extend(sample_folder.glob(f"*{ext}"))

    images = sorted(images)

    if len(images) == 0:
        raise FileNotFoundError(
            "No sample images found."
        )

    return images


def choose_sample_image():

    images = get_sample_images()

    print("\nAvailable Sample Images\n")

    for i, img in enumerate(images, start=1):
        print(f"{i}. {img.name}")

    while True:

        try:

            choice = int(input("\nChoose Image Number: "))

            if 1 <= choice <= len(images):

                return str(images[choice - 1])

            print("Invalid choice.")

        except ValueError:

            print("Enter a valid number.")


def browse_image():

    root = Tk()

    root.withdraw()

    filepath = askopenfilename(

        title="Select Satellite Image",

        filetypes=[

            ("Image Files",
             "*.png *.jpg *.jpeg *.tif *.tiff")
        ]
    )

    root.destroy()

    if filepath == "":
        raise Exception("No image selected.")

    return filepath


def select_input_image():

    print("\n" + "=" * 50)

    print("        ROUTE RESILIENCE AI")

    print("=" * 50)

    print("\nChoose Input Source\n")

    print("1. Sample Images")

    print("2. Browse Computer")

    while True:

        choice = input("\nEnter Choice (1 or 2): ")

        if choice == "1":

            return choose_sample_image()

        elif choice == "2":

            return browse_image()

        else:

            print("Invalid Choice.")