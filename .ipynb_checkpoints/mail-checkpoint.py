import imaplib
import email
import pathlib

path = pathlib.Path(__file__).parent.resolve()
def get_credentials():
    imap_server = "imap.gmail.com"
    email_address="louistzx@gmail.com"
    email_password=""
    app_password="inzk sktj ojxn leeq"
    
    if app_password:
        email_password = app_password

    return imap_server, email_address, email_password


def email_signin(imap, email_address, email_password):
    imap.login(email_address, email_password)


def readmail(imap, inboxtype, subject=None, sender=None, since_date=None):
    
    print("Reading mail..")
    imap.select("Inbox")

    #for filtering
    search_criteria = []
    if subject:
        search_criteria.append(f'SUBJECT "{subject}"')
    if sender:
        search_criteria.append(f'FROM "{sender}"')
    if since_date:
        search_criteria.append(f'SINCE "{since_date}"')
    
    search_query = " ".join(search_criteria) if search_criteria else "ALL" #if no filter, search all mail
    _, msg_number = imap.search(None, search_query)

    for email_index in msg_number[0].split():
        _, data = imap.fetch(email_index, "(RFC822)")
        message = email.message_from_bytes(data[0][1])

        email_from = message.get("From")
        email_subject = message.get("Subject")
        email_date = message.get("Date")
        email_body = ""
        for part in message.walk():
            if part.get_content_type()=="text/plain":
                email_body = part.get_payload(decode=True).decode('utf-8')
                break

        #save email content to txt file
        file_name = f"{path}/{email_index.decode('utf-8')}.txt"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(f"From: {email_from}\n")
            file.write(f"Subject: {email_subject}\n")
            file.write(f"Date: {email_date}\n")
            file.write("\n")
            file.write(email_body)

        print(f"Email saved to {file_name}")


if __name__ == "__main__":
    
    imap_server, email_address, email_password = get_credentials()
    imap = imaplib.IMAP4_SSL(imap_server)
    try:
        email_signin(imap, email_address, email_password)

        #search filters. can pass in ltr but for now these are place holders
        specific_subject = "Meeting Reminder"
        sender_email = "example_sender@gmail.com"
        date_since = "13-Jan-2025"
        inboxtype = "Inbox"

        # Fetch and print the email thread
        readmail(imap, inboxtype, subject=None, sender=None, since_date=date_since)

    finally:
        imap.logout()