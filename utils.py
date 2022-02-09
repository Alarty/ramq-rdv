import os

# for email sending
import sendgrid
from sendgrid.helpers.mail import *


def send_mail(slots, url, to_email):
    """
    from a specific dict of slots, send an email to the addresses
    :param slots: dict containing all available slots with tags for new ones
    :param url: clickable url in email
    :param to_email: Address or list of address
    :return: status code of email sent
    """

    subject = "New slot in RAMQ"

    mail_txt = "<html><head></head><body><h1>These are the currently available slots :</h1><br><br><br>"
    print(slots)
    mail_txt += f"<a href=\"{url}\">Lien direct</a><br><br>"
    mail_txt += f"&nbsp;&nbsp;&nbsp; {slots}<br>"
    mail_txt += "<br>"
    mail_txt += "</body></html>"
    # send mail through SendGrid
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('from'))
    content = Content("text/html", mail_txt)
    mail = Mail(from_email=from_email, subject=subject, to_emails=to_email, html_content=content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code


def compare_results(new_slots, old_slots):
    """
    compare the two json
    :param new_slots: the dict of the new results
    :param old_slots: the older dict
    :return: flag if something new, and old slots refreshed with new stuff
    """
    # flag if something new changed
    new_flag = False
    if old_slots is None:
        print("There is no older slots stored, so this will trigger because everything is new")
        new_flag = True
    else:
        print(str(new_slots))
        print(str(old_slots))
        print('-----')
        if str(new_slots) != str(old_slots):
            new_flag = True
        else:
            print("There is no new spot compared to last result stored in json file")
    return new_flag
