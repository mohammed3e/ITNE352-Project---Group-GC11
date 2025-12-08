# ITNE352 Project - Group GC11

---

## Project Description
This project implements a Python-based client-server system that exchanges information about current news. The server retrieves news updates from [NewsAPI.org](https://newsapi.org/) and handles multiple client connections simultaneously using multithreading. Clients can search headlines and sources by keyword, category, country, or language, and request detailed information on selected items. The project emphasizes network communication, API integration, and proper coding practices.

---

## Semester
2025-2025-1

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

1. **Python 3**: Download and install from [Python.org](https://www.python.org/).

2. **NewsAPI library**: Install via command line using:
  


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

### Responsibilities:

- Reads user commands

- Calls fetch_headlines() or fetch_sources()

- Sends results back to the client

- Stores fetched data into local JSON files

- Handles article/source detail selection

- Manages user disconnection

 

5. **Server Startup Loop**
- Starts listening for clients and creates a new thread for each client:
 ```python
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
     soc.bind((HOST, PORT))
     soc.listen(MAX_CONNECTIONS)
      while True:
        sock, address = soc.accept(s)
        threading.Thread(target=handle_client, args=(sock, address)).start()

