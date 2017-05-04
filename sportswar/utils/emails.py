import email.utils

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.template.loader import render_to_string


EMAIL_TEMPLATES = {
    'watcher_alert': {
        'subject': ('Sports Warning! {{ team_name }} playing a {{ location }} game {{ gametime }}'),
        'template': 'emails/watcher_alert.txt',
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'recipient_list': ['{{ user.email }}', ],
    },
    'unsubscribe_success': {
        'subject': ('{{ user.email }} unsubscribed from {{ watcher }}'),
        'template': 'emails/unsubscribe_success.txt',
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'recipient_list': ['{{ user.email }}', ],
    },
    'user_confim': {
        'subject': ('{{ user.email }} confirm email message'),
        'template': 'emails/user_confirm.txt',
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'recipient_list': ['{{ user.email }}', ],
    },
    'user_welcome': {
        'subject': ('{{ user.email }} welcome message'),
        'template': 'emails/user_welcome.txt',
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'recipient_list': ['{{ user.email }}', ],
    }
}

_EMAIL_CONTEXT = {
    'site_url': settings.SITE_URL,
    'signature': '- The Sports Warning Team'
}


def get_display_name_and_email(user):
    """Return a display name and email address to use when sending mail from user."""
    if user.is_superuser:
        return email.utils.parseaddr(settings.DEFAULT_FROM_EMAIL)
    else:
        return user.display_name or user.email, user.email


def render_templates(email_dict, context_dict):
    html = None
    if 'html_template' in email_dict:
        html = render_to_string(email_dict['html_template'], context_dict)
    text = render_to_string(email_dict['template'], context_dict)
    return html, text


def prepare_and_send_email(event, context_dict, to_users=None, reply_to=None):
    context_dict.update(_EMAIL_CONTEXT)
    email_dict = EMAIL_TEMPLATES[event]
    subject = Template(email_dict['subject']).render(Context(context_dict, autoescape=False))
    html, text = render_templates(email_dict, context_dict)
    from_email = email_dict['from_email']
    bccs = email_dict.get('bccs', [])
    reply_to = reply_to if reply_to else [from_email]
    if to_users is None:
        recipient_list = [
            Template(x).render(Context(context_dict)) for x in email_dict['recipient_list']]
    elif to_users:
        recipient_list = [u.email for u in to_users]
    else:
        return
    recipient_list = [x for x in recipient_list if x.strip() not in {'', 'None'}]
    msg = EmailMultiAlternatives(subject, text, from_email, recipient_list,
                                 bcc=bccs, reply_to=reply_to)
    if html:
        msg.attach_alternative(html, 'text/html')
    msg.send()
