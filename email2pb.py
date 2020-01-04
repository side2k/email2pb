import argparse
import base64
import email
import logging
import nltk   
import os
import re
import sys

from pushbullet import Pushbullet

logger = logging.getLogger(__name__)

# Read arguments
parser = argparse.ArgumentParser(description='Send PushBullet PUSH based on email message')
parser.add_argument(
    'infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--key', help='API key for PushBullet', required=True)
parser.add_argument('--debug', help='Enable debug mode', action='store_true')
parser.add_argument("--debug_log", type=str)
args = parser.parse_args()

# Read stdin and write it out if needed
stdin_data = args.infile.read()
debug_mode = args.debug
if debug_mode:
    logger.debug('Debug mode enabled')
    logfile_path = args.debug_log or "debug.log"
    with open(logfile_path, "w") as debug_log:
        debug_log.write("\n")
        debug_log.write("Incoming message:\n")
        debug_log.write("-------------------------\n")
        debug_log.write(stdin_data)
        debug_log.write("-------------------------\n")

args.infile.close()

# Parse stdin
pb = Pushbullet(args.key)
parts = stdin_data.split("--=======JUAN_SMTP_V1_0=======")

# Parse out the text
text = parts[0]
text = re.findall("\n\n(.*)", text)[0] # Remove header info
text = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", text.strip()) # Remove style tags
text = re.sub(r"(?s)<.*?>", " ", text).strip() # Get text content

# Hardcoded: Only interested in channel 2
if(not re.findall("Event:Motion detect in video channel 2", text)):
    print("Not channel 2:")
    print(text)
    quit()

# Write out the base64 data to image file
image_part = parts[1]
file_name = re.findall("name=\"(.*?)\"", image_part)[0]
base64_image = re.findall("\n\n(.*)", image_part)[0].strip()
with open(file_name, "wb") as fh:
    fh.write(base64_image.decode('base64'))

# Upload the image to pushbullet
with open(file_name, "rb") as pic:
    file_data = pb.upload_file(pic, file_name)

# Send push
push = pb.push_file(body = text, **file_data)

# Delete the image
os.remove(file_name)
