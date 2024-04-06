# MoGostickerBot

When playing Monopoly Go, part of the game mechanics is to trade stickers with others.  The game is on mobile devices and so it is relatively easy to screenshot your stickers and post them on forums like Discord.  When trading, to identify a card, it is best to type in the name of a single card to search for it.  The challenge is that on mobile, those offering cards to trade can easily take screenshots, but it would be painful to try and type dozens of card names to identify them and make them searchable for mobile users.

Here is a bot that can listen in on a Discord channel and when a player uploads pictures of either cards they have for trade or cards they are missing, the bot can identify them (using OpenCV to recognize the type of card, and sometimes Tesseract OCR for similar cards to identify the text).  The bot then replies to the original message, posting a succinct trade offer based on the cards attached, saying either "FT" for trade and "LF" looking for specific cards.

Here is an example picture of that:

![image](https://github.com/scprotz/MoGoCardBot/assets/7061526/d5f1b2b6-6075-485f-9de5-2ce54486368b)

To run the bot, you will need to install python, opencv-python, and pytesseract.  You will also need to create your own application on Discord (allowing intents), create a token, insert the token into your python code, run the python code and invite the bot to your discord server.  At that point the bot will identify any picture on the channel and try to reply FT and LF.

This is a work in progress and has some known shortcomings for now (i.e. it just picks the 'best match' for any picture.  Thresholds could make it not respond if the picture quality is too low).
