import json
import socket  # Needed for client-server communication
from tkinter import Tk, simpledialog, messagebox

#  Configuration 
HOST = '127.0.0.1'  # Server IP address
PORT = 59999        # Server port

# Hide the main Tkinter window because we only use dialog boxes
root = Tk()
root.withdraw()

#  Utility Functions 
def recv_json(sock):
    """
    Receive a JSON object safely from the server.
    Handles:
    - Chunked data (multiple recv calls)
    - Different text encodings
    - Incomplete JSON
    Returns:
    - Python object if successful
    - None if connection closed or invalid JSON
    """
    buffer = ""
    while True:
        chunk = sock.recv(4096)  # Receive data from socket
        if not chunk:  # Connection closed
            if buffer == "":
                return None
            try:
                return json.loads(buffer)
            except:
                return None
        try:
            buffer += chunk.decode('utf-8')  # Try UTF-8 decoding
        except:
            buffer += chunk.decode('latin-1')  # Fallback decoding
        try:
            return json.loads(buffer)  # Try to parse JSON
        except json.JSONDecodeError:
            continue  # Wait for more data if JSON incomplete

def gui_input(prompt):
    
    while True:
        res = simpledialog.askstring("A1", prompt)
        if res:
            return res

#  Headlines Menu 
def show_headlines(soc):
    """
    Handle the Headlines menu:
    - Send headline search request to server.
    - Present menu options to the user.
    - Receive a list of headlines from server.
    - Allow user to select a headline to see details.
    """

    # Map menu options
    options = {
        "1": "Search for keywords",
        "2": "Search by category",
        "3": "Search by country",
        "4": "List all new headlines",
        "5": "Back to the main menu"
    }

    while True:
        

        # Ask user to choose an option
        choice = gui_input(
            "Headlines Menu:\n1- Search for keywords\n2- Search by category\n3- Search by country\n4- List all new headlines\n5- Back to main menu"
        )
        option_text = options.get(choice)
        if not option_text:  # Invalid choice
            messagebox.showinfo("A1", "Invalid option")
            continue
        if option_text == "Back to the main menu":
            break
        soc.sendall("Search headlines".encode())  # Notify server about headlines menu
        soc.sendall(option_text.encode())  # Send the selected option to server

        # Ask for additional input if required
        value = None
        if option_text in ["Search for keywords", "Search by category", "Search by country"]:
            value = gui_input(f"Enter value for {option_text}")
            soc.sendall(value.encode())

        # Receive list of headlines from server
        summary = recv_json(soc)
        if summary is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(summary, dict) and summary.get("error"):
            messagebox.showinfo("A1", f"Error: {summary['error']}")
            continue

        # Display headlines in a numbered list
        headlines_text = "\n".join(
            f"{idx}. {item.get('title')} - {item.get('source')} (Author: {item.get('author')})"
            for idx, item in enumerate(summary, 1)
        )

        # Ask user to select a headline for details
        idx_input = gui_input(
            f"Headlines List:\n{headlines_text}\n\nEnter the number to see full details (or 0 to skip):"
        )
        if idx_input == "":
            idx_input = "0"
        soc.sendall(idx_input.encode())  # Send selection to server

        # Receive full details of selected headline
        details = recv_json(soc)
        if details is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(details, dict) and details.get("error"):
            messagebox.showinfo("A1", f"Error: {details['error']}")
            continue

        # Format and display headline details
        if details:
            detail_msg = (
                f"Source: {details.get('source', {}).get('name') if isinstance(details.get('source'), dict) else details.get('source')}\n"
                f"Author: {details.get('author')}\n"
                f"Title: {details.get('title')}\n"
                f"Description: {details.get('description')}\n"
                f"URL: {details.get('url')}\n"
            )
            if details.get("publishedAt"):
                parts = details["publishedAt"].split("T")
                if len(parts) == 2:
                    date, time = parts
                    time = time.replace("Z", "")
                    detail_msg += f"Published Date: {date}\nPublished Time: {time}"
            messagebox.showinfo("A1", detail_msg)

#  Sources Menu 
def show_sources(soc):
    """
    Handle the Sources menu:
    - Send source list request to server.
    - Present menu options to the user.
    - Receive a list of sources from server.
    - Allow user to select a source to see details.
    """
    
    # Map menu options
    options = {
        "1": "Search by category",
        "2": "Search by country",
        "3": "Search by language",
        "4": "List all",
        "5": "Back to the main menu"
    }

    while True:

        # Ask user to choose an option
        choice = gui_input(
            "Sources Menu:\n1- Search by category\n2- Search by country\n3- Search by language\n4- List all\n5- Back to main menu"
        )
        option_text = options.get(choice)
        if not option_text:
            messagebox.showinfo("A1", "Invalid option")
            continue
        if option_text == "Back to the main menu":
            break
        soc.sendall("List of sources".encode())  # Notify server about sources menu
        soc.sendall(option_text.encode())  # Send selected option to server

        # Ask for additional input if required
        value = None
        if option_text in ["Search by category", "Search by country", "Search by language"]:
            value = gui_input(f"Enter value for {option_text}")
            soc.sendall(value.encode())

        # Receive list of sources from server
        summary = recv_json(soc)
        if summary is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(summary, dict) and summary.get("error"):
            messagebox.showinfo("A1", f"Error: {summary['error']}")
            continue

        # Display sources in a numbered list
        sources_text = "\n".join(f"{idx}. {item.get('name')}" for idx, item in enumerate(summary, 1))

        # Ask user to select a source for details
        idx_input = gui_input(f"Sources List:\n{sources_text}\n\nEnter number for details (0 to skip):")
        if idx_input == "":
            idx_input = "0"
        soc.sendall(idx_input.encode())

        # Receive full details of selected source
        details = recv_json(soc)
        if details is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(details, dict) and details.get("error"):
            messagebox.showinfo("A1", f"Error: {details['error']}")
            continue

        # Format and display source details
        if details:
            detail_msg = (
                f"Name: {details.get('name')}\n"
                f"Country: {details.get('country')}\n"
                f"Category: {details.get('category')}\n"
                f"Language: {details.get('language')}\n"
                f"Description: {details.get('description')}\n"
                f"URL: {details.get('url')}"
            )
            messagebox.showinfo("A1", detail_msg)

# Main Function 
def main():
    
    user = gui_input("Enter your name:")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        
        try:
          soc.connect((HOST, PORT))  # Connect to server
        except:
          messagebox.showerror("Error", "Server is not running.")
          return

        soc.sendall(user.encode())  # Send username

        while True:
            # Main menu
            choice = gui_input("Main Menu:\n1- Search headlines\n2- List of sources\n3- Quit")
            if choice == "1":
                show_headlines(soc)  # Open headlines menu
            elif choice == "2":
                show_sources(soc)    # Open sources menu
            elif choice == "3":
                soc.sendall("EXIT".encode())  # Inform server to disconnect
                messagebox.showinfo("A1", "Disconnected from server.")
                break
            else:
                messagebox.showinfo("A1", "Invalid choice.")

#  Start Program 
if __name__ == "__main__":
    main()