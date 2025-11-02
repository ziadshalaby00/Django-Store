from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def specific_send_mail(*, subject, message, link, from_email, recipient_list):
    # ✅ HTML template
    html_content = f'''<!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f5f7fa; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
        
        <h2 style="text-align: center; color: #4A90E2;">🔐 Reset Your Password</h2>

        <p style="font-size: 16px; color: #333;">
            { message }
        </p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{ link }" 
            style="background: #4A90E2; color: white; padding: 12px 20px; 
                    text-decoration: none; font-size: 16px; border-radius: 6px;">
            Reset Password
            </a>
        </div>

        <p style="font-size: 14px; color: #777;">
            If the button doesn’t work, copy and paste this link:
        </p>

        <p style="word-break: break-all; color: #555;">
            { link }
        </p>

        </div>
    </body>
    </html>
    '''

    # ✅ Create email with both text + html
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,  # plain text fallback
        from_email=from_email,
        to=recipient_list
    )

    email.attach_alternative(html_content, "text/html")
    email.send()