from flask_mail import Message
from app import mail
import secrets

def send_password_reset_email(email, token):
    msg = Message(
        'Password Reset Request - FinanceFlow',
        recipients=[email]
    )
    
    reset_link = f"http://localhost:5173/reset-password/{token}"
    
    msg.body = f'''Hello,

You requested to reset your password for FinanceFlow.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you did not request this, please ignore this email.

Best regards,
FinanceFlow Team
'''
    
    msg.html = f'''
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">Password Reset Request</h2>
                <p>Hello,</p>
                <p>You requested to reset your password for FinanceFlow.</p>
                <p>Click the button below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                </div>
                <p style="color: #666; font-size: 14px;">This link will expire in 1 hour.</p>
                <p style="color: #666; font-size: 14px;">If you did not request this, please ignore this email.</p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px;">Best regards,<br>FinanceFlow Team</p>
            </div>
        </body>
    </html>
    '''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_sms(phone, message):
    try:
        from twilio.rest import Client
        from flask import current_app
        
        client = Client(
            current_app.config['TWILIO_ACCOUNT_SID'],
            current_app.config['TWILIO_AUTH_TOKEN']
        )
        
        message = client.messages.create(
            body=message,
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=phone
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def generate_reset_token():
    return secrets.token_urlsafe(32)