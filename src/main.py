import os
import shutil
import sys

from copystatic import copy_files_recursive
from gencontent import generate_pages_recursive
import send_recap

def generate_static_site():
    print("Running task one...")
    
    dir_path_static = "./static"
    dir_path_public = "./docs"
    dir_path_content = "./content"
    template_path = "./template.html"
    default_basepath = "/"

    print("Deleting public directory...")
    if os.path.exists(dir_path_public):
        shutil.rmtree(dir_path_public)

    print("Copying static files to public directory...")
    copy_files_recursive(dir_path_static, dir_path_public)

    print("Generating content...")
    generate_pages_recursive(dir_path_content, template_path, dir_path_public, default_basepath)
    

def recap_email():
    print("Running task two...")
    # put your script logic here
    try:
        emailer = send_recap.StudyGroupEmailer()
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

def main():
    while True:
        print("\n=== Main Menu ===")
        print("1) Generate Static Site")
        print("2) Send Meeting Recap")
        print("3) Edit Meeting Attendees")
        print("4) Send Follow-up Email")
        print("q) Quit")

        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            generate_static_site()
        elif choice == "2":
            recap_email()
        elif choice == "q":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
