"""Shared email utilities for study_group_emailer.

Provides: load_recipients, create_template_recipients_file,
get_sender_credentials, display_recipients, send_email.
"""
import os
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except Exception:
    Environment = None
    FileSystemLoader = None
    select_autoescape = None


def _resolve_path(file_path: str) -> str:
    if not os.path.isabs(file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, file_path)
    return file_path


def create_template_recipients_file(file_path: str = "recipients.json"):
    path = _resolve_path(file_path)
    template = {
        "study_group_members": [
            {
                "name": "Your Name",
                "email": "your.email@example.com",
                "active": True
            }
        ],
        "cc_list": []
    }
    with open(path, "w") as f:
        json.dump(template, f, indent=2)


def load_recipients(file_path: str = "recipients.json", sort_by_name: bool = False) -> list[str]:
    """Load and normalize recipients JSON.

    Returns dict with keys: 'members' (list of dicts) and 'cc' (list of dicts).
    """
    path = _resolve_path(file_path)

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"✗ Recipients file '{file_path}' not found!")
        print("  Creating a template file for you...")
        create_template_recipients_file(file_path)
        raise

    members = [m for m in data.get("study_group_members", []) if m.get("active", True)]
    if sort_by_name:
        members = sorted(members, key=lambda x: (x.get("name") or "").lower())

    raw_cc = data.get("cc_list", []) or []
    cc_list = []
    for item in raw_cc:
        if isinstance(item, dict):
            if "email" in item:
                item.setdefault("name", "")
                cc_list.append(item)
        elif isinstance(item, str):
            parts = [p.strip() for p in re.split(r"[;,]", item) if p.strip()]
            for p in parts:
                cc_list.append({"name": "", "email": p})
        else:
            continue

    return {"members": members, "cc": cc_list}


def display_recipients(recipients_data):
    print("\n=== Recipients ===")
    print(f"\nStudy Group Members ({len(recipients_data['members'])}):")
    for member in recipients_data['members']:
        print(f"  • {member.get('name','(no name)')} <{member.get('email','(no email)')}>")

    if recipients_data.get('cc'):
        print(f"\nCC List ({len(recipients_data['cc'])}):")
        for person in recipients_data['cc']:
            role = person.get('role', '')
            role_str = f" ({role})" if role else ""
            print(f"  • {person.get('name','').strip()} <{person.get('email')}>{role_str}")


def get_sender_credentials():
    """Load .env and return (sender_email, sender_password) or raise ValueError."""
    load_dotenv()
    sender = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not sender or not password:
        raise ValueError("Gmail credentials not found! Please check your .env file.")
    return sender, password


def render_template(template_path: str, context: dict) -> str:
    """Render a simple template file by replacing placeholders using str.format_map.

    The caller should prepare any list or conditional sections as strings in the
    context (e.g. 'topics' or 'members'). This avoids adding a template
    dependency while keeping templates readable.
    """
    # Prefer Jinja2 if available, fall back to simple format_map
    if not os.path.isabs(template_path):
        # Resolve relative to project root (parent of src directory)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, template_path)
    else:
        path = template_path
    
    if Environment is not None:
        # Load templates from the templates directory under project
        templates_dir = os.path.dirname(path)
        tpl_name = os.path.basename(path)
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(enabled_extensions=('j2',))
        )
        try:
            template = env.get_template(tpl_name)
        except Exception as e:
            raise FileNotFoundError(f"Template file not found or failed to load: {template_path} ({e})")
        return template.render(**context)

    # Fallback: simple format_map
    try:
        with open(path, "r") as f:
            tpl = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template_path} (resolved to {path})")

    class SafeDict(dict):
        def __missing__(self, key):
            return ""

    return tpl.format_map(SafeDict(context))


def send_email(sender_email, sender_password, recipients_data, subject, body, smtp_server='smtp.gmail.com', smtp_port=587):
    to_emails = [m.get("email") for m in recipients_data.get("members", []) if m.get("email")]
    cc_emails = [c.get("email") for c in recipients_data.get("cc", []) if c.get("email")]

    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ", ".join(to_emails)
        if cc_emails:
            message['Cc'] = ", ".join(cc_emails)
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()

        print(f"✓ Email sent successfully to {len(to_emails) + len(cc_emails)} recipient(s)!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("✗ Authentication failed! Check your email and app password.")
        return False
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False
