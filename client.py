import socket  
import json    
from tkinter import Tk, simpledialog, messagebox  

HOST = '127.0.0.1'  
PORT = 59999 
root = Tk()
root.withdraw()  # Hide the main Tkinter window

# Function to receive JSON data from the server safely
def recv_json(sock):
    buffer = ""
    while True:
        chunk = sock.recv(4096)  # Receive data in chunks
        if not chunk:
            if buffer == "":
                return None
            try:
                return json.loads(buffer)  # Try to parse JSON
            except:
                return None
        try:
            buffer += chunk.decode('utf-8')  # Decode using UTF-8
        except:
            buffer += chunk.decode('latin-1')  # Fallback decoding
        try:
            return json.loads(buffer)  # Return JSON if valid
        except json.JSONDecodeError:
            continue  # Wait for more data if incomplete

# Function to get input from user via GUI
def gui_input(prompt):
    while True:
        res = simpledialog.askstring("A1", prompt)
        if res:
            return res  # Return input if provided

 # Function to show headlines and handle headline-related operations
def show_headlines(soc):
    soc.sendall("Search headlines".encode())  # Tell server we want headlines
    options = {
        "1": "Search for keywords",
        "2": "Search by category",
        "3": "Search by country",
        "4": "List all new headlines",
        "5": "Back to the main menu"
    }
    while True:
        choice = gui_input(
            "Headlines Menu:\n1- Search for keywords\n2- Search by category\n3- Search by country\n4- List all new headlines\n5- Back to main menu"
        )
        option_text = options.get(choice)
        if not option_text:
            messagebox.showinfo("A1", "Invalid option")
            continue
        if option_text == "Back to the main menu":
            break

        soc.sendall(option_text.encode())  # Send chosen option to server
        value = None
        if option_text in ["Search for keywords", "Search by category", "Search by country"]:
            value = gui_input(f"Enter value for {option_text}")  # Ask for search term
            soc.sendall(value.encode())

        summary = recv_json(soc)  # Get results from server
        if summary is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(summary, dict) and summary.get("error"):
            messagebox.showinfo("A1", f"Error: {summary['error']}")
            continue

# Display list of headlines
        headlines_text = "\n".join(
            f"{idx}. {item.get('title')} - {item.get('source')} (Author: {item.get('author')})"
            for idx, item in enumerate(summary, 1)
        )
        idx_input = gui_input(f"Headlines List:\n{headlines_text}\n\nEnter the number to see full details (or 0 to skip):")
        if idx_input == "":
            idx_input = "0"
        soc.sendall(idx_input.encode())

        details = recv_json(soc)  # Get detailed info of selected headline
        if details is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(details, dict) and details.get("error"):
            messagebox.showinfo("A1", f"Error: {details['error']}")
            continue
        if details:
             # Build message showing full details of headline
            detail_msg = (
                f"Source: {details.get('source', {}).get('name') 
if isinstance(details.get('source'), dict) else details.get('source')}/n"
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
            messagebox.showinfo("A1", detail_msg)  # Show details in GUI
# Function to show sources and handle source-related operations
def show_sources(soc):
    soc.sendall("List of sources".encode())  # Request sources from server
    options = {
        "1": "Search by category",
        "2": "Search by country",
        "3": "Search by language",
        "4": "List all",
        "5": "Back to the main menu"
    }
    while True:
        choice = gui_input(
            "Sources Menu:\n1- Search by category\n2- Search by country\n3- Search by language\n4- List all\n5- Back to main menu"
        )
        option_text = options.get(choice)
        if not option_text:
            messagebox.showinfo("A1", "Invalid option")
            continue
        if option_text == "Back to the main menu":
            break

        soc.sendall(option_text.encode())
        value = None
        if option_text in ["Search by category", "Search by country", "Search by language"]:
            value = gui_input(f"Enter value for {option_text}")
            soc.sendall(value.encode())

        summary = recv_json(soc)
        if summary is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(summary, dict) and summary.get("error"):
            messagebox.showinfo("A1", f"Error: {summary['error']}")
            continue

        sources_text = "\n".join(f"{idx}. {item.get('name')}" for idx, item in enumerate(summary, 1))
        idx_input = gui_input(f"Sources List:\n{sources_text}\n\nEnter number for details (0 to skip):")
        if idx_input == "":
            idx_input = "0"
        soc.sendall(idx_input.encode())

        details = recv_json(soc)
        if details is None:
            messagebox.showinfo("A1", "Server closed connection or invalid response.")
            return
        if isinstance(details, dict) and details.get("error"):
            messagebox.showinfo("A1", f"Error: {details['error']}")
            continue
        if details:
            # Show detailed information about selected source
            detail_msg = (
                f"Name: {details.get('name')}\n"
                f"Country: {details.get('country')}\n"
                f"Category: {details.get('category')}\n"
                f"Language: {details.get('language')}\n"
                f"Description: {details.get('description')}\n"
                f"URL: {details.get('url')}"
            )
            messagebox.showinfo("A1", detail_msg)
