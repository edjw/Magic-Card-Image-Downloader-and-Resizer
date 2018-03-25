from pathlib import Path
from string import punctuation
from urllib.request import urlretrieve
from urllib.parse import urlparse
from os.path import splitext
from os import remove
from gooey import Gooey, GooeyParser
from requests_html import HTMLSession
from PIL import Image


@Gooey(
    program_name="Magic Cards Image Downloader", program_description="Downloads and resizes images"
)
def main():
    parser = GooeyParser()

    parser.add_argument(
        "OutputDirectory",
        help="Select the directory to save images in",
        widget="DirChooser",
    )

    parser.add_argument(
        "URL",
        default="https://magic.wizards.com/en/products/ixalan/cards",
        help="Web address to download images from",
    )

    parser.add_argument(
        "CSS_Selectors",
        default=".rtecenter > img, .side.front > img",
        help="CSS selectors for the images",
    )

    args = parser.parse_args()

    WORKING_URL = args.URL
    OUTPUT_DIRECTORY = Path(args.OutputDirectory)
    CSS_SELECTORS = args.CSS_Selectors

    def create_directory():
        Path(OUTPUT_DIRECTORY).mkdir(parents=True, exist_ok=True)

    def cleanup_name(image_name):
        image_name = image_name.lower()
        remove_punctuation = str.maketrans('', '', punctuation)
        image_name = image_name.translate(remove_punctuation)
        image_name = image_name.replace("’", "")
        image_name = image_name.replace("  ", "_")
        image_name = image_name.replace(" ", "_")
        return image_name

    def get_file_format(image_url):
        path = urlparse(image_url).path
        extension = splitext(path)[1]
        return extension

    def get_image_links():
        print("Getting image links...\n", flush=True)
        session = HTMLSession()
        r = session.get(WORKING_URL)
        images = r.html.find(CSS_SELECTORS)
        return images

    def download_images():
        images = get_image_links()
        print("Downloading images...\n", flush=True)
        for image in images:
            image_name = image.attrs["alt"]
            image_url = image.attrs["src"]

            image_name = cleanup_name(image_name)
            image_format = get_file_format(image_url)
            image_save_name = image_name + image_format

            urlretrieve(image_url, OUTPUT_DIRECTORY / image_save_name)

    def resize_images():
        print("Resizing images...\n", flush=True)
        image_formats = [".jpg", ".jpeg", ".gif", ".png", ".tga", ".tiff", ".webp"]

        OUTPUT_DIRECTORY_Path = Path(OUTPUT_DIRECTORY)

        for img_file in OUTPUT_DIRECTORY_Path.glob('*.*'):
            if img_file.is_file() and img_file.suffix in image_formats:
                img = Image.open(img_file)
                longest_dimension = max(img.size)

                if longest_dimension < 500:
                    size = (longest_dimension, longest_dimension)
                else:
                    size = (500, 500)

                img.thumbnail(size, Image.ANTIALIAS)
                background = Image.new('RGBA', size, (255, 255, 255, 0))
                background.paste(
                    img,
                    (
                        int((size[0] - img.size[0]) / 2),
                        int((size[1] - img.size[1]) / 2),
                    ),
                )

                resized_image_save_name = str(img_file.stem) + ".png"

                background.save(OUTPUT_DIRECTORY_Path / resized_image_save_name)

                file_format = img_file.suffix
                if file_format != ".png":
                    remove(img_file)

    create_directory()
    download_images()
    resize_images()
    print("Finished!\n", flush=True)


main()
