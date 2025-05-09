import imaplib
import email
from email.header import decode_header
import pathlib
from datetime import datetime, timedelta

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
    imap.select(inboxtype)

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

    emails = []  # List to store email details
    
    for email_index in msg_number[0].split():
        _, data = imap.fetch(email_index, "(RFC822)")
        message = email.message_from_bytes(data[0][1])
        #email_subject = message.get("Subject")
        
        # Decode the email subject properly to handle emojis
        email_subject, encoding = decode_header(message.get("Subject"))[0]
        if isinstance(email_subject, bytes):
            email_subject = email_subject.decode(encoding or 'utf-8')

        email_from = message.get("From")
        email_date = message.get("Date")
        email_body = ""
        for part in message.walk():
            if part.get_content_type()=="text/plain":
                email_body = part.get_payload(decode=True).decode('utf-8')
                break
        '''
        #save email content to txt file
        file_name = f"{path}/{email_index.decode('utf-8')}.txt"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(f"From: {email_from}\n")
            file.write(f"Subject: {email_subject}\n")
            file.write(f"Date: {email_date}\n")
            file.write("\n")
            file.write(email_body)
        print(f"Email saved to {file_name}")
        '''

        # Append the email data to the list
        emails.append({
            "id": email_index.decode('utf-8'),
            "from": email_from,
            "subject": email_subject,
            "date": email_date,
            "body": email_body
        })
        emails.reverse()
    return emails

def summarise(content, tokenizer,device,model):
    print("Summarizing...")
    if (content == ""):
        return("No text detected in email")
    
    # Input text for summarization
    input_text = f"Summarize this email while ignoring links but still keeping the vital information such as events, dates and times:{content}"

    # Tokenize the input text
    inputs = tokenizer(input_text, return_tensors="pt").to(device)

    # Generate the output (summary)
    outputs = model.generate(
        inputs.input_ids, 
        max_length=100,  # Maximum length of the generated text
        min_length=0,  # Minimum length of the generated text
        length_penalty=2.0,  # Penalize long sentences
        num_beams=4,  # Use beam search for higher quality results
        early_stopping=True
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(summary)
    return(summary)

def main(): 
    imap_server, email_address, email_password = get_credentials()
    imap = imaplib.IMAP4_SSL(imap_server)
    try:
        email_signin(imap, email_address, email_password)

        #search filters. can pass in ltr but for now these are place holders
        subject = "Meeting Reminder"
        sender_email = "example_sender@gmail.com"
        date_since = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
        inboxtype = "Inbox"

        # Fetch and print the email thread
        return readmail(imap, inboxtype, subject=None, sender=None, since_date=date_since)

    finally:
        imap.logout()
