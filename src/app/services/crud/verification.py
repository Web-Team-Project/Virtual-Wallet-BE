import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_verification_email(email: str, verification_link: str):
    password = "uichtbofletmfdfm"
    msg = MIMEMultipart()
    msg["From"] = "k.v.ivanov98@gmail.com"
    msg["To"] = email
    msg["Subject"] = "Email Verification"

    message = f"Please click the following link to verify your email: {verification_link}"
    msg.attach(MIMEText(message, "plain"))

    server = smtplib.SMTP("smtp.gmail.com: 587")
    server.starttls()
    server.login(msg["From"], password)
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    server.quit()

    print("Successfully sent email to %s:" % (msg["To"]))