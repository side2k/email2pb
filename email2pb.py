import argparse
import base64
import email
import io
import logging
import os
import re
import sys

from datetime import datetime
from logging.handlers import RotatingFileHandler
from pushbullet import Pushbullet

# Read arguments
parser = argparse.ArgumentParser(description='Send PushBullet PUSH based on email message')
parser.add_argument(
    'infile', 
    nargs='?', 
    type=argparse.FileType('r'), 
    default=sys.stdin,
    help='MIME-encoded email file(if empty, stdin will be used)')
parser.add_argument('--key', help='API key for PushBullet', required=True)
parser.add_argument('--log_level', default='40', help='10=debug 20-info 30=warning 40=error', type=int)
parser.add_argument('--log_file', default='email2pb.log', help='Log file location', type=str)
args = parser.parse_args()

# Configure logging
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(args.log_file, mode='a', maxBytes=1024*1024, backupCount=1)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler) 
logger.setLevel(args.log_level)
logger.debug(args)

# Initialize Pushbullet client
pb = Pushbullet(args.key)

# Read infile (is stdin if no arg) 
stdin_data = args.infile.read()
args.infile.close()
logger.debug('in:\n' + stdin_data)
msg = email.message_from_string(stdin_data)

# Parse out the email parts
is_file = False
file_data = {}
body_text = ''
def parse_part(part):
    global is_file
    global file_data
    global body_text

    if part.is_multipart():
        for child_part in part.get_payload():
            parse_part(child_part)
        return

    # Handle plaintext including base64 encoded (who would base64 encode plaintext?)
    if part.get_content_type() == 'text/plain':
        text_part = part.get_payload()
        part_encoding = part.get_content_charset()

        if part.get('Content-Transfer-Encoding') == 'base64':
            text_part = bytearray(text_part, encoding=part_encoding)
            text_part = base64.decodestring(text_part)
            text_part = text_part.decode(part_encoding)
        
        logger.debug('Found plain text: ' + text_part)
        body_text = '%s\n%s' % (body_text, text_part)
            
    # Handle HTML - Pull plaintext out
    if part.get_content_type() == 'text/html':
        html_part = part.get_payload()
        clean_html = re.sub(r'(?is)<(script|style).*?>.*?(</\1>)', '', html_part.strip()) # Remove style tags
        html_text = re.sub(r'(?s)<.*?>', ' ', clean_html).strip() # Get text content
        logger.debug('Found HTML text: ' + html_text)
        body_text = '%s\n%s' % (body_text, html_text)

    # Handle images - Decode base64 and upload to pushbullet 
    # If there are multiple images it will only do the first one
    if part.get_content_type() == 'image/jpg' and not is_file:
        is_file = True
        image_part = part.get_payload()
        file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.jpg'
        file = io.BytesIO(image_part.decode('base64'))
        logger.debug('Uploading ' + file_name)
        file_data = pb.upload_file(file, file_name)


# Build the text
parse_part(msg)
sender = msg.get('From', 'Unknown')
body_text = '%s\nFrom: %s' % (body_text, sender)
body_text = body_text.strip()

# Send push
subject = msg.get('Subject', '(No subject)')
if is_file: 
    logger.debug('Sending file push')
    push = pb.push_file(body = body_text, title=subject, **file_data)
else:
    logger.debug('Sending note push')
    push = pb.push_note(title=subject, body = body_text)

logger.info('Successfully pushed')
