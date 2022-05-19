#!/usr/bin/env python
"""
Sends an HTML email with images rendered from Markdown
"""

import os
import sys
import argparse

import email
import email.mime
import email.mime.multipart
import email.mime.text
import email.mime.image
import smtplib

try:
    import markdown
    _HAVE_MD = True
except ImportError:
    _HAVE_MD = False

def send_email(subject, plain_text, fromaddr=None, toaddr=None, attach_images=None):
    # Define these once; use them twice!
    if not fromaddr:
        fromaddr = os.environ.get('USER')
    if not toaddr:
        toaddr = os.environ.get('USER')
    if attach_images is None:
        attach_images = []


    # Create the root message and fill in the from, to, and subject headers
    message = email.mime.multipart.MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = fromaddr
    message['To'] = toaddr
    # message.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    alt_part = email.mime.multipart.MIMEMultipart('alternative')
    message.attach(alt_part)

    if plain_text:
        alt_part.attach(email.mime.text.MIMEText(plain_text))

    # We reference the image in the IMG SRC attribute by the ID we give it below
    if _HAVE_MD:
        msg_html = markdown.markdown(plain_text)
    else:
        msg_html = plain_text.replace("\n", "<br>")
    for attach_file in attach_images:
        msg_html += '<img src="cid:%s" width="100%%"><br>' % attach_file

    if msg_html or attach_images:
        alt_part.attach(email.mime.text.MIMEText(msg_html, 'html'))

        for attach_file in attach_images:
            # This example assumes the image is in the current directory
            with open(attach_file, 'rb') as image_fp:
                image = email.mime.image.MIMEImage(image_fp.read())

            # Define the image's ID as referenced above
            image.add_header('Content-ID', '<%s>' % attach_file)
            message.attach(image)

    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP()
    smtp.connect()
    # smtp.login('exampleuser', 'examplepass')
    smtp.sendmail(fromaddr, toaddr, message.as_string())
    smtp.quit()

def emailer(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--subject", type=str, help="Subject")
    parser.add_argument("-f", "--from-addr", type=str, default=None, help="Sender address (default: $USER)")
    parser.add_argument("-t", "--to-addr", type=str, default=None, help="Recipient address (default: $USER)")
    parser.add_argument("-b", "--body", type=str, default=None, help="Path to file containing email body")
    parser.add_argument("-i", "--image", type=str, action="append", help="Path to image to include (use multiple times)")
    args = parser.parse_args(argv)

    body = ""
    with open(args.body, 'r') if args.body != "-" else sys.stdin as text_fp:
        body = text_fp.read()

    send_email(
        subject=args.subject,
        plain_text=body,
        fromaddr=args.from_addr,
        toaddr=args.to_addr,
        attach_images=args.image)

if __name__ == "__main__":
    emailer()
