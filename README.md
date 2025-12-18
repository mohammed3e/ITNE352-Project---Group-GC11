# ITNE352 Project - Group GC11

---

## Project Description
This project implements a Python-based client-server system that exchanges information about current news. The server retrieves news updates from [NewsAPI.org](https://newsapi.org/) and handles multiple client connections simultaneously using multithreading. Clients can search headlines and sources by keyword, category, country, or language, and request detailed information on selected items. The project emphasizes network communication, API integration, and proper coding practices.

---


## Semester
S1 2025–2026


---

## Group
- **Group Name:** GC11  
- **Course Code:** ITNE352  
- **Section:** 3 
- **Student Name:** Mohammed Abdulghani Mohammed  
- **Student ID:** 202308038  
- **Student Name:** Ahmed Mohammed Omar  
- **Student ID:** 202307323
- **Student Name:** Ahmed Mohammed Amin Alsalim 
- **Student ID:** 202307672

---

## Table of Contents
1. [Project Description](#project-description)  
2. [Semester](#semester)  
3. [Group](#group)  
4. [Requirements](#requirements)  
5. [How to](#how-to)  
6. [The Scripts](#the-scripts)    
8. [Acknowledgments](#acknowledgments)  
9. [Conclusion](#conclusion)  


---

## Requirements

To set up and run this project locally, make sure to install the following:

1.  Install Python 3.x (the newest version is 3.12) from the official Python website: https://www.python.org/downloads/

2. Install the required Python packages by running the following command:

```
pip install requests 
```

3. Get an API key from news API website: https://NewsAPI.org and replace the "NEWSAPI_KEY" constant in the server.py file with your API key.


## How to

### Running the Server
To start the server, run the following command:

```
python server.py
```

The server will start listening for incoming client connections.  
Once a client connects, the server will display the client's name and all received requests.

### Running the Client
To start the client, run:

```
python client.py
```


### Interaction Steps

1. Enter your username (this name will be displayed on the server side).  
2. Choose an option from the main menu:  
   - Search Headlines  
   - List of Sources  
   - Quit  

3. Inside each menu, you can search by:  
   - Keyword  
   - Category  
   - Country  
   - Language  

4. After receiving a list of results, you may:  
   - Select an item to get detailed information  
   - Go back to the previous menu  
   - Quit the program


## The Scripts

### server.py

**Main Functionalities**  

The server:  
- Accepts and manages multiple clients using multithreading  
- Receives search requests (headlines or sources)  
- Fetches news from NewsAPI  
- Sends JSON responses back to the client  
- Saves results into JSON files  

**Key Functions in server.py**  

1. **fetch_headlines(param_name=None, param_value=None)**  
   Fetches top headlines based on keyword, category, or country.  
   ```python
   def fetch_headlines(param_name=None, param_value=None):
       url = f"https://newsapi.org/v2/top-headlines?{param_name}={param_value}&pageSize=15&apiKey={NEWSAPI_KEY}"

- Purpose: Queries NewsAPI, returns a list of articles, and handles errors/API failures.

2. **fetch_sources(param_name=None, param_value=None)**
- Retrieves a list of news sources filtered by category, country, or language.
    ```python
   def fetch_sources(param_name=None, param_value=None):
         url = f"https://newsapi.org/v2/sources?{param_name}={param_value}&apiKey={NEWSAPI_KEY}"


3. **send_json(conn, data)**
- Sends JSON data to the client through a socket.
    ```python 
  def send_json(conn, data):
        conn.sendall(json.dumps(data).encode())

4. **handle_client(conn, address)**
- Handles menu navigation and user requests.
    ```python
    def handle_client(conn, address):
    user = conn.recv(1024).decode("utf-8").strip()

## Responsibilities:

- Reads user commands

- Calls fetch_headlines() or fetch_sources()

- Sends results back to the client

- Stores fetched data into local JSON files

- Handles article/source detail selection

- Manages user disconnection


### client.py

**Main Functionalities**  

The client:
- Connects to the server
- Sends user choices and search queries
- Displays results in GUI popups using Tkinter
- Allows selecting items for more details

**Key Functions in client.py**

1. recv_json(sock)  
   - Purpose: Receives and decodes JSON data from the server, handles incomplete packets and returns Python objects.  
   - Example:
   ```python
   def recv_json(sock):
       buffer = ""
       while True:
           chunk = sock.recv(4096)
           if not chunk:
               break
           buffer += chunk.decode(errors="ignore")
           try:
               return json.loads(buffer)
           except json.JSONDecodeError:
               continue
       return None
   ```

2. gui_input(prompt)  
   - Purpose: Displays a Tkinter input dialog and returns the user input.
   ```python
   def gui_input(prompt):
       return simpledialog.askstring("A1", prompt)
   ```

3. show_headlines(sock, user)  
   - Purpose: Handles the headlines search flow:
     - Sends search request to server
     - Receives a list of article summaries
     - Displays headlines in a popup
     - Lets user select an article and requests full details from server
     - Shows article details in a popup

4. show_sources(sock, user)  
   - Purpose: Handles source-search flow:
     - Requests list of sources (optionally filtered)
     - Displays list in a popup
     - Sends selected source index to server and shows details


   


**Responsibilities**

- Take username and connect to server
- Send user commands and queries
- Receive and display results via Tkinter dialogs
- Handle user navigation and selection
- Cleanly disconnect and notify server on exit

## Additional Concepts

- Multithreading (server-side) for multiple clients
- JSON communication (json.dumps / json.loads)
- TCP sockets for client-server communication
- Tkinter for simple GUI interaction (simpledialog, messagebox)
- External API integration: server uses NewsAPI (requests.get )

## Acknowledgments

We  thank our instructor for the support and advice throughout the development of this project.
We also appreciate NewsAPI.org for making real-time news data available, which was essential for building our system.

## Conclusion

This project successfully demonstrates a working client-server application in Python. It combines network programming, multithreading, and API integration to allow multiple users to request and receive news at the same time.
The project highlights how Python can be used to handle real-world tasks like fetching live data, managing concurrent connections, and presenting information to users in a simple and interactive way.