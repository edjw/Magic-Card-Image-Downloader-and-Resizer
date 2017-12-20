from string import punctuation
from os import makedirs
from os.path import splitext
from pathlib import Path
from requests import get
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from PIL import Image


def download__magic_card_images(url):

    res = get(url)
    webpage_html = BeautifulSoup(res.text, 'html.parser')
    counter = 0

    # Select all images
    images = webpage_html.select("img")

    # Dictionary of card name and link
    card_name_and_link = {}

    for img in images:
        # Only the card images have a style attribute
        if img.has_attr('style'):
            image_name = img['alt']
            image_link = img['src']
            card_name_and_link.update({image_name: image_link})

    makedirs("magic_card_images", exist_ok=True)

    print("Downloading images ...")
    for card in card_name_and_link:

        counter += 1
        print(str(counter) + " / " + str(len(card_name_and_link)))

        card_image_link = card_name_and_link[card]

        file_name = card_image_link.split('/')[-1]  # eg en_JB0lDoCGgA.png
        file_format = splitext(file_name)[1]  # eg .png

        card_name = card.lower()

        remove_punctuation = str.maketrans('', '', punctuation)
        card_name = card_name.translate(remove_punctuation)

        card_name = card_name.replace("’", "")
        card_name = card_name.replace("  ", "_")
        card_name = card_name.replace(" ", "_")

        urlretrieve(card_image_link, "magic_card_images/" +
                    card_name + file_format)


def resize_images(images_directory):

    counter = 0
    img_files = []

    p = Path(images_directory)

    for img_file in p.glob('*.*'):
        if img_file.is_file():
            img_files.append(img_file.name)

    print("Resizing images...")
    for img_file in img_files:
        counter += 1
        print(str(counter) + " / " + str(len(img_files)))

        # Opening image file
        image = Image.open(images_directory + img_file)

        # Determining longest side of file
        longest_dimension = max(image.size)

        # If longest dimension is less than 500px
        # Make a square of largest side
        if longest_dimension < 500:
            size = (longest_dimension, longest_dimension)

        # Otherwise, crop the square to 500px
        else:
            size = (500, 500)

        # Makes a transparent background and pastes game image over the centre
        image.thumbnail(size, Image.ANTIALIAS)
        background = Image.new('RGBA', size, (255, 255, 255, 0))
        background.paste(
            image, (int((size[0] - image.size[0]) / 2),
                    int((size[1] - image.size[1]) / 2))
        )
        background.save(images_directory + img_file)

    print("Finished")


download__magic_card_images(
    "https://magic.wizards.com/en/products/ixalan/cards")
resize_images("magic_card_images/")
