#  Notes
#  Used masking with opencv based on this reference:
#  https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv


from os import walk
import urllib

import cv2
import discord
import pytesseract
from skimage.metrics import structural_similarity

import card_dict
import numpy as np


# create a discord client bot #
# enable interaction with messages #
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def process(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY)
    img_canny = cv2.Canny(thresh, 0, 0)
    img_dilate = cv2.dilate(img_canny, None, iterations=7)
    return cv2.erode(img_dilate, None, iterations=7)


def get_masked_image(img):
    contours, _ = cv2.findContours(
        process(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    # crop image
    img = img[y:y+h, x:x+w]
    # resize
    img = cv2.resize(img, (200, 308))
    # convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def load_reference_images():
    file_names = []
    imgs = {}
    for (_, _, filenames) in walk("./stickers"):
        file_names.extend(filenames)

    for file_name in file_names:
        # read image from file
        img = cv2.imread("./stickers" + file_name, -1)
        # convert transparent background to black
        img[np.where(img[:, :, 3] == 0)] = (0, 0, 0, 255)
        # get masked region
        img = get_masked_image(img)

        # append reference image to list
        imgs[int(file_name.split('.')[0])] = img
    return imgs


refs = load_reference_images()


def download_img(image_url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1;' +\
        ' en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(image_url, None, headers)
    response = urllib.request.urlopen(request)
    img = cv2.imdecode(
        np.array(bytearray(response.read()), dtype=np.uint8), -1)
    return img


def compare_image(img):
    best_match = None
    best_score = 0.0
    best_key = None
    for key, ref in refs.items():
        score, _ = structural_similarity(img, ref, full=True)
        if score > best_score:
            best_score = score
            best_match = ref
            best_key = key
    return best_score, best_match, best_key


def get_image_name(img):
    score, best_img, key = compare_image(img)
    print(card_dict.cards[key], score)
    return card_dict.cards[key]


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(len(message.attachments))

    # for trade images #
    ft_imgs = []
    # looking for images #
    lf_imgs = []
    if message.attachments:
        for att in message.attachments:
            print(att.url)
            img = download_img(att.url)
            img = get_masked_image(img)
            img_name = get_image_name(img)
            if img_name == "Missing":
                # crop to text #
                img = img[125:225, 0:200]
                # use threshold to turn black/white
                img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)[1]
                # blur
                img = cv2.GaussianBlur(img, (1, 1), 0)
                img_name = pytesseract.image_to_string(
                    img).strip().replace('\n', ' ')

                # if not message.content or img_name not in message.content:
                lf_imgs.append(img_name)

            else:
                # if not message.content or img_name not in message.content:
                ft_imgs.append(img_name)
            print(img_name)

    reply = ""

    if len(lf_imgs) > 0:
        reply += "LF:\n"
        for img_name in lf_imgs:
            reply += img_name + "\n"

    if len(ft_imgs) > 0:
        reply += "FT:\n"
        for img_name in ft_imgs:
            reply += img_name + "\n"

    if len(reply) > 0:
        reply_to = await message.channel.fetch_message(message.id)
        await reply_to.reply(reply)

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


if __name__ == "__main__":
    client.run("YOUR TOKEN")
