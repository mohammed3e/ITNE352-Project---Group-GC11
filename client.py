import socket
import json
from tkinter import Tk, simpledialog, messagebox

# Server info
HOST = "127.0.0.1"
PORT = 59999

# Allowed values from the project
ALLOWED_COUNTRIES = ["au", "ca", "jp", "ae", "sa", "kr", "us", "ma"]
ALLOWED_LANGUAGES = ["ar", "en"]
ALLOWED_CATEGORIES = ["business", "general", "health", "science", "sports", "technology"]

# Start hidden Tk window
root = Tk()
root.withdraw()


# ------------------ Receive JSON safely ------------------
def recv_json(sock, timeout=10):
    """
    Receive full JSON message from server.
    I keep reading until JSON becomes complete.
    """
    sock.settimeout(timeout)
    buffer = ""

    try:
        while True:
            try:
                data = sock.recv(4096)
            except socket.timeout:
                return None

            if not data:
                # server closed
                if buffer.strip() == "":
                    return None
                try:
                    return json.loads(buffer)
                except:
                    return None

            # decode chunk
            try:
                buffer += data.decode("utf-8")
            except:
                buffer += data.decode("latin-1", errors="ignore")

            # check if full JSON
            try:
                return json.loads(buffer)
            except json.JSONDecodeError:
                continue

    finally:
        sock.settimeout(None)


# ------------------ Input box helper ------------------
def gui_input(text, title="A1"):
    """
    Show a simple input dialog and return user input.
    """
    while True:
        res = simpledialog.askstring(title, text)
        if res is None:
            raise KeyboardInterrupt("User cancelled")
        return res.strip()


# ------------------ Format source name ------------------
def format_source_short(src):
    """Return source name whether dict or string."""
    if isinstance(src, dict):
        return src.get("name", "-")
    return src or "-"


# ------------------ Headlines menu logic ------------------
def show_headlines(soc):
    """
    Show headlines menu:
    - ask for option
    - send option number
    - send parameter if needed
    - get list and show details
    """
    while True:
        try:
            choice = gui_input(
                "Headlines Menu:\n"
                "1- Search keywords\n"
                "2- Search category\n"
                "3- Search country\n"
                "4- List all\n"
                "5- Back\n\n"
                "Enter number:"
            )
        except KeyboardInterrupt:
            return

        # check valid number
        if choice not in {"1", "2", "3", "4", "5"}:
            messagebox.showinfo("A1", "Invalid number")
            continue

        # send option
        soc.sendall(choice.encode())

        param = None

        # ask parameter if needed
        if choice == "1":
            param = gui_input("Enter keyword:")
        elif choice == "2":
            param = gui_input("Enter category:\n" + ", ".join(ALLOWED_CATEGORIES))
            if param not in ALLOWED_CATEGORIES:
                messagebox.showinfo("A1", "Invalid category")
                continue
        elif choice == "3":
            param = gui_input("Enter country:\n" + ", ".join(ALLOWED_COUNTRIES))
            if param not in ALLOWED_COUNTRIES:
                messagebox.showinfo("A1", "Invalid country")
                continue

        # send parameter
        if param is not None:
            soc.sendall(param.encode())

        # get list
        summary = recv_json(soc)
        if summary is None:
            messagebox.showinfo("A1", "Server connection lost")
            return

        if not summary:
            messagebox.showinfo("A1", "No results")
            continue

        # max 15 items
        results = summary[:15]

        # build list text
        text = "\n".join(
            f"{i}. {item.get('title','-')} - {format_source_short(item.get('source'))}"
            for i, item in enumerate(results, 1)
        )

        try:
            idx = gui_input(
                f"Headlines:\n{text}\n\nEnter item number (0 to skip):"
            )
        except KeyboardInterrupt:
            soc.sendall("0".encode())
            continue

        if not idx.isdigit():
            messagebox.showinfo("A1", "Enter a number")
            continue

        idx = int(idx)
        if idx < 0 or idx > len(results):
            messagebox.showinfo("A1", "Out of range")
            continue

        soc.sendall(str(idx).encode())

        if idx == 0:
            continue

        details = recv_json(soc)
        if details is None:
            messagebox.showinfo("A1", "Server error")
            return

        # show details
        src = details.get("source")
        if isinstance(src, dict):
            src = src.get("name")

        msg = (
            f"Source: {src}\n"
            f"Author: {details.get('author','-')}\n"
            f"Title: {details.get('title','-')}\n"
            f"Description: {details.get('description','-')}\n"
            f"URL: {details.get('url','-')}\n"
        )

        if "publishedAt" in details:
            date, time = details["publishedAt"].replace("Z", "").split("T")
            msg += f"Date: {date}\nTime: {time}"

        messagebox.showinfo("Details", msg)


# ------------------ Sources menu logic ------------------
def show_sources(soc):
    """
    Show sources menu:
    - send choice
    - ask for parameter if needed
    - show list and details
    """
    while True:
        try:
            choice = gui_input(
                "Sources Menu:\n"
                "1- Category\n"
                "2- Country\n"
                "3- Language\n"
                "4- List all\n"
                "5- Back\n\n"
                "Enter number:"
            )
        except KeyboardInterrupt:
            return

        if choice not in {"1", "2", "3", "4", "5"}:
            messagebox.showinfo("A1", "Invalid number")
            continue

        soc.sendall(choice.encode())

        param = None

        if choice == "1":
            param = gui_input("Category:\n" + ", ".join(ALLOWED_CATEGORIES))
            if param not in ALLOWED_CATEGORIES:
                messagebox.showinfo("A1", "Invalid")
                continue
        elif choice == "2":
            param = gui_input("Country:\n" + ", ".join(ALLOWED_COUNTRIES))
            if param not in ALLOWED_COUNTRIES:
                messagebox.showinfo("A1", "Invalid")
                continue
        elif choice == "3":
            param = gui_input("Language:\n" + ", ".join(ALLOWED_LANGUAGES))
            if param not in ALLOWED_LANGUAGES:
                messagebox.showinfo("A1", "Invalid")
                continue

        if param is not None:
            soc.sendall(param.encode())

        summary = recv_json(soc)
        if summary is None:
            messagebox.showinfo("A1", "Server error")
            return

        results = summary[:15]

        text = "\n".join(f"{i}. {item.get('name','-')}" for i, item in enumerate(results, 1))

        try:
            idx = gui_input(
                f"Sources:\n{text}\n\nEnter item number (0 to skip):"
            )
        except KeyboardInterrupt:
            soc.sendall("0".encode())
            continue

        if not idx.isdigit():
            messagebox.showinfo("A1", "Enter number only")
            continue

        idx = int(idx)
        soc.sendall(str(idx).encode())

        if idx == 0:
            continue

        details = recv_json(soc)
        if details is None:
            messagebox.showinfo("A1", "Server error")
            return

        msg = (
            f"Name: {details.get('name','-')}\n"
            f"Country: {details.get('country','-')}\n"
            f"Category: {details.get('category','-')}\n"
            f"Language: {details.get('language','-')}\n"
            f"Description: {details.get('description','-')}\n"
            f"URL: {details.get('url','-')}"
        )

        messagebox.showinfo("Details", msg)


# ------------------ MAIN ------------------
def main():
    """
    Main menu:
    - ask for username
    - connect to server
    - show main options
    """
    try:
        username = gui_input("Enter your name:")
    except KeyboardInterrupt:
        return

    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((HOST, PORT))
    except Exception as e:
        messagebox.showinfo("A1", f"Can't connect: {e}")
        return

    # send username
    soc.sendall(username.encode())

    while True:
        try:
            choice = gui_input(
                "Main Menu:\n"
                "1- Headlines\n"
                "2- Sources\n"
                "3- Quit\n\n"
                "Enter number:"
            )
        except KeyboardInterrupt:
            choice = "3"

        if choice not in {"1", "2", "3"}:
            messagebox.showinfo("A1", "Invalid number")
            continue

        soc.sendall(choice.encode())

        if choice == "1":
            show_headlines(soc)
        elif choice == "2":
            show_sources(soc)
        else:
            messagebox.showinfo("A1", "Goodbye!")
            soc.close()
            break


if __name__ == "__main__":
    main()

    