import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox

HOST = "127.0.0.1"
PORT = 59999  

class NewsClient:
    def __init__(self, root):
        self.root = root
        self.root.title("News Client")

        self.sock = None
        self.connected = False
        self.items = []

        # Username
        tk.Label(root, text="Username:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.connect_btn = tk.Button(root, text="Connect", command=self.connect)
        self.connect_btn.pack()

        self.status_label = tk.Label(root, text="Not connected", fg="red")
        self.status_label.pack()
        
       # OPTIONS MENU (NEW)
        options_frame = tk.LabelFrame(root, text="Headlines Options")
        options_frame.pack(pady=10)

        tk.Label(options_frame, text="Select Option:").grid(row=0, column=0, padx=5)

        self.option_var = tk.StringVar()
        self.option_menu = ttk.Combobox(
            options_frame,
            textvariable=self.option_var,
            values=[
                "Search for keywords",
                "Search by category",
                "Search by country",
                "List all new headlines"
            ],
            state="readonly",
            width=30
        )
        self.option_menu.grid(row=0, column=1, padx=5)
        self.option_menu.current(0)

        tk.Label(options_frame, text="Value:").grid(row=1, column=0, padx=5)
        self.option_value_entry = tk.Entry(options_frame)
        self.option_value_entry.grid(row=1, column=1, padx=5)

        tk.Button(options_frame, text="Run Search", command=self.run_option_search).grid(row=2, column=0, columnspan=2, pady=5)

         # Results list
        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack()
        self.listbox.bind("<<ListboxSelect>>", self.show_details)

        self.details_text = tk.Text(root, height=10, width=50)
        self.details_text.pack()


    # Connect
    def connect(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Enter username")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))

            
            self.sock.sendall(username.encode())

            self.connected = True
            self.status_label.config(text="Connected", fg="green")
            self.connect_btn.config(state="disabled")
            self.username_entry.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"Cannot connect: {e}")
# NEW — Running selected option
    def run_option_search(self):
        if not self.connected:
            messagebox.showwarning("Warning", "Connect first")
            return

        option = self.option_var.get()
        value = self.option_value_entry.get().strip()

        # 1) send: "Search headlines"
        # 2) send: option
        # 3) send: value 

        try:
            self.sock.sendall("Search headlines".encode())
            self.sock.sendall(option.encode())

            # only send value if needed
            if option in ["Search for keywords", "Search by category", "Search by country"]:
                if not value:
                    messagebox.showwarning("Warning", "Enter a value (keyword/category/country)")
                    return
                self.sock.sendall(value.encode())
            else:
                # no value needed
                pass

            # Receive summary list
            data = self.sock.recv(65535).decode()
            summaries = json.loads(data)

            self.listbox.delete(0, tk.END)
            self.details_text.delete("1.0", tk.END)

            if "error" in summaries:
                self.listbox.insert(tk.END, summaries["error"])
                return

            self.items = summaries

            for i, item in enumerate(self.items, start=1):
                title = item.get("title", "No title")
                self.listbox.insert(tk.END, f"{i}. {title}")

        except Exception as e:
            messagebox.showerror("Error", f"Communication error: {e}")

            
            # Show details
    def show_details(self, event):
        if not self.items:
            return

        idx = self.listbox.curselection()
        if not idx:
            return

        real_idx = idx[0] + 1

        try:
            self.sock.sendall(str(real_idx).encode())

            data = self.sock.recv(65535).decode()
            article = json.loads(data)

            self.details_text.delete("1.0", tk.END)

            if "error" in article:
                self.details_text.insert(tk.END, article["error"])
                return

            self.details_text.insert(tk.END, f"Title: {article.get('title','')}\n")
            self.details_text.insert(tk.END, f"Source: {article.get('source',{}).get('name','')}\n")
            self.details_text.insert(tk.END, f"Author: {article.get('author','')}\n")
            self.details_text.insert(tk.END, f"Description: {article.get('description','')}\n")
            self.details_text.insert(tk.END, f"URL: {article.get('url','')}\n")

        except Exception as e:
            messagebox.showerror("Error", f"Communication error: {e}")

            
# run app
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsClient(root)
    root.mainloop()