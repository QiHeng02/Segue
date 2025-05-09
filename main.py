from flask import Flask, render_template, session, jsonify, request
from flask_session import Session
import flaskwebgui
#from msal import ConfidentialClientApplication
import pathlib
import mail
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

#setting path for files
path = pathlib.Path(__file__).parent.resolve()

#flask app setup
app = Flask(__name__, template_folder=f'{path}/frontend')
gui = flaskwebgui.FlaskUI(app=app, server="flask", width=800, height=600)

app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

'''# Microsoft Graph API credentials
CLIENT_ID = "4a92c3b5-f676-4cd6-9b2e-e048e67d5990"  #app id
CLIENT_SECRET = "502961bd-28e1-4968-9eb1-840be5da2eb6"
TENANT_ID = "14442076-8ff1-47e2-8afe-4a40eef8529c"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

# MSAL API setup
msal_app = ConfidentialClientApplication(
    client_id = CLIENT_ID, 
    client_credential=CLIENT_SECRET, 
    authority = AUTHORITY
)'''


#set up LLM
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)


# Helper function to get access token
def get_access_token():
    token = session.get("access_token")
    if not token:
        result = msal_app.acquire_token_for_client(scopes=SCOPES)
        if "access_token" in result:
            token = result["access_token"]
            session["access_token"] = token
    return token



#helper function for storing emails in session
def get_emails():
    if 'emails' not in session:
        session['emails'] = mail.main()
    return session['emails']


#dashboard
@app.route("/")
def index():
    return render_template("index.html")

#calendar
@app.route("/calendar")
def calendar():
    print()

#mail
@app.route("/mail")
def email():
    emails = get_emails()
    return render_template("mail.html", emails=emails)

@app.route('/summarize_email', methods=['POST'])
def summarize_email():
    try:
        email_id = request.json.get('email_id')
        if not email_id:
            return jsonify({"error": "Email ID is required"}), 400
        
        emails = get_emails()
        email_body = None
        
        # Find the email with matching ID
        for email in emails:
            if email["id"] == email_id:
                email_body = email["body"]
                break
        
        if email_body is None:
            return jsonify({"error": "Email not found"}), 404
        
        summary = mail.summarise(email_body, tokenizer,device,model)
        return jsonify({'summary': summary})
    
    except Exception as e:
        print(f"Error in summarize_email: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# To-Do list route
@app.route("/todo")
def todo():
    print()

if __name__ == "__main__":
    gui.run()