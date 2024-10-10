# send text mail

import smtplib, ssl

port = 587  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "sae92679@gmail.com"  # Enter your address
receiver_email = "l.petit723@gmail.com"  # Enter receiver address
password = "sae301sae301sae301"
message = """\
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)