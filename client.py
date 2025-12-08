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
        
        #  Connection section 
        tk.Label(root, text="Username:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.connect_btn = tk.Button(root, text="Connect", command=self.connect)
        self.connect_btn.pack()

        self.status_label = tk.Label(root, text="Not connected", fg="red")
        self.status_label.pack()

        #  Search section 
        tk.Label(root, text="Keyword:").pack()
        self.keyword_entry = tk.Entry(root)
        self.keyword_entry.pack()

        self.search_btn = tk.Button(root, text="Search Headlines", command=self.search_headlines)
        self.search_btn.pack()
# Results section 
        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack()
        self.listbox.bind("<<ListboxSelect>>", self.show_details)

        self.details_text = tk.Text(root, height=10, width=50)
        self.details_text.pack()
    # Connect to the server
    def connect(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Enter username")
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.sock.sendall(json.dumps({"username": username}).encode())
            self.connected = True
            self.status_label.config(text="Connected", fg="green")
            self.connect_btn.config(state="disabled")
            self.username_entry.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot connect: {e}")

    # Send a request to the server
    def send_request(self, action, params=None):
        if not self.connected:
            messagebox.showwarning("Warning", "Connect first")
            return None
        if params is None:
            params = {}
        try:
            self.sock.sendall(json.dumps({"action": action, "params": params}).encode())
            data = self.sock.recv(65535)
            return json.loads(data.decode())
        except Exception as e:
            messagebox.showerror("Error", f"Communication error: {e}")
            return None
         # Search headlines by keyword
    def search_headlines(self):
        kw = self.keyword_entry.get().strip()
        if not kw:
            messagebox.showwarning("Warning", "Enter keyword")
            return
        resp = self.send_request("headlines_keyword", {"keyword": kw})
        self.listbox.delete(0, tk.END)
        self.details_text.delete("1.0", tk.END)
        self.items = resp.get("items", []) if resp else []
        if not self.items:
            self.listbox.insert(tk.END, "No results found")
        for item in self.items:
            self.listbox.insert(tk.END, item.get("title", ""))

    # Show details when selecting an item
    def show_details(self, event):
        if not self.items:
            return
        idx = self.listbox.curselection()
        if not idx:
            return
        item = self.items[idx[0]]
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, f"Title: {item.get('title','')}\n")
        self.details_text.insert(tk.END, f"Source: {item.get('source_name','')}\n")
        self.details_text.insert(tk.END, f"Author: {item.get('author','')}\n")
        self.details_text.insert(tk.END, f"Description: {item.get('description','')}\n")
        self.details_text.insert(tk.END, f"URL: {item.get('url','')}\n")

        
  # Start the app when the script is run directly
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsClient(root)
    root.mainloop()