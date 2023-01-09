from django.core.mail import EmailMessage

class AuthNotificationFacotory:
    
    @staticmethod
    def register_email_notification(domain_name, user, token, abs_path):
        subject = f"ACCOUNT VERIFICATION"
        absurl = 'http://'+domain_name+abs_path+'?token='+str(token)
        message = f"Hi {user.first_name}, \n Kindly use below link to activate your email \n {absurl}"
        print("message: ",message)
        email = EmailMessage(subject=subject,body=message,to=[user.email])
        email.send(fail_silently=True)
    
    @staticmethod 
    def send_password_reset_email(domain_name,abs_path,user):
        subject = f"PASSWORD RESET REQUEST"
        absurl = 'http://'+domain_name+abs_path
        message = f"Hi {user.first_name}, \n Kindly use below link to reset your password \n {absurl}"
        print("message: ",message)
        email = EmailMessage(subject=subject,body=message,to=[user.email])
        email.send(fail_silently=True)