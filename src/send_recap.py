"""
Study Group Weekly Recap Email Automation
Main Script: send_recap.py

This script collects weekly study group information and sends
a formatted email to all members from a JSON file.
"""

from datetime import datetime
import json

from email_utils import load_recipients, display_recipients, send_email, get_sender_credentials, render_template

class StudyGroupEmailer:
    """Handles sending study group recap emails"""

    def __init__(self, recipients_file='recipients.json'):
        """Initialize with recipients file and load Gmail credentials."""
        self.recipients_file = recipients_file
        # Load credentials (this will load .env as needed)
        self.sender_email, self.sender_password = get_sender_credentials()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    # recipient loading is provided by `load_recipients` from email_utils
    
    # template creation provided by email_utils.create_template_recipients_file
    
    # display_recipients provided by email_utils.display_recipients
    
    def collect_recap_info(self):
        """Collect information for the weekly recap through user input"""
        print("\n=== Study Group Weekly Recap ===\n")
        
        # Get week information
        week_number = input("Week number: ")
        date = input("Meeting date (or press Enter for today): ")
        if not date:
            date = datetime.now().strftime("%B %d, %Y")
        
        # Get topics covered
        print("\nTopics covered (press Enter twice when done):")
        topics = []
        while True:
            topic = input(f"  Topic {len(topics) + 1}: ")
            if not topic:
                break
            topics.append(topic)
        
        # Get assignments
        print("\nAssignments for next week (press Enter twice when done):")
        assignments = []
        while True:
            assignment = input(f"  Assignment {len(assignments) + 1}: ")
            if not assignment:
                break
            assignments.append(assignment)
        
        # Get additional notes
        print("\nAdditional notes (press Enter to skip):")
        notes = input("  Notes: ")
        
        # Get next meeting info
        next_meeting = input("\nNext meeting date/time: ")
        
        return {
            'week_number': week_number,
            'date': date,
            'topics': topics,
            'assignments': assignments,
            'notes': notes,
            'next_meeting': next_meeting
        }
    
    def format_email_body(self, recap_info):
        """Format the recap information into a nice email using a template file."""

        # Provide raw lists/values to the Jinja2 template so it can render loops and conditionals
        context = {
            'week_number': recap_info.get('week_number', ''),
            'date': recap_info.get('date', ''),
            'topics': recap_info.get('topics', []),
            'assignments': recap_info.get('assignments', []),
            'notes': recap_info.get('notes', ''),
            'next_meeting': recap_info.get('next_meeting', '')
        }

        return render_template('templates/recap.j2', context)
    
    # sending is handled by email_utils.send_email
    
    def run(self):
        """Main workflow to collect info and send email"""
        
        # Step 1: Load recipients
        print("Loading recipients...")
        recipients_data = load_recipients(self.recipients_file,sort_by_name=False)
        display_recipients(recipients_data)
        
        # Step 2: Collect information
        recap_info = self.collect_recap_info()
        
        # Step 3: Format email
        email_body = self.format_email_body(recap_info)
        subject = f"Big Book Study Group Week {recap_info['week_number']} Recap"
        
        # Step 4: Show preview
        print("\n" + "="*50)
        print("EMAIL PREVIEW")
        print("="*50)
        print(f"Subject: {subject}\n")
        print(email_body)
        print("="*50)
        
        # Step 5: Confirm sending
        confirm = input("\nSend this email? (yes/no): ").lower()
        
        if confirm == 'yes':
            # Send email using shared helper
            send_email(self.sender_email, self.sender_password, recipients_data, subject, email_body)
        else:
            print("Email cancelled.")


def main():
    """Entry point of the script"""
    try:
        emailer = StudyGroupEmailer()
        emailer.run()
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nMake sure you have a .env file with:")
        print("  GMAIL_ADDRESS=your.email@gmail.com")
        print("  GMAIL_APP_PASSWORD=your_16_char_app_password")
    except FileNotFoundError:
        print("\nPlease edit recipients.json with your group members, then run again.")
    except KeyboardInterrupt:
        print("\n\nScript cancelled by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()