import socket
import json
import requests
import threading

HOST = '127.0.0.1'
PORT = 59999
MAX_CONNECTIONS = 3
NEWSAPI_KEY = "841626c7c99549e4977d8c2a2ad7f63e"
GROUP_ID = "GC11"



def fetch_headlines(param_name=None, param_value=None):
    try:
        if param_name and param_value:
            url = f"https://newsapi.org/v2/top-headlines?{param_name}={param_value}&pageSize=15&apiKey={NEWSAPI_KEY}"
        else:
            url = f"https://newsapi.org/v2/top-headlines?pageSize=15&apiKey={NEWSAPI_KEY}"
        r = requests.get(url)
        data = r.json()

        if data.get("status") != "ok":
            print("NewsAPI Error:", data)
            return None

        return data.get("articles", [])[:15]

    except Exception as e:
        print("Exception:", e)
        return None


def send_json(conn, data):
    conn.sendall(json.dumps(data).encode())


def handle_client(conn, address):
    last_articles={}
    last_sources ={}

    user = conn.recv(1024).decode("utf-8")
    print(f"--- Connected: {user} | {address} ---")

    while True:
        main = conn.recv(1024).decode("utf-8")
        if not main:
            break

        if main == "Search headlines":
            option = conn.recv(1024).decode("utf-8")
            value = None

            if option in ["Search for keywords", "Search by category", "Search by country"]:
                value = conn.recv(1024).decode("utf-8")

          
            print(f"[REQUEST] User={user} | Type=Headlines | Option={option} | Value={value}")

           
            if option == "Search for keywords":
                articles = fetch_headlines("q", value)
            elif option == "Search by category":
                articles = fetch_headlines("category", value)
            elif option == "Search by country":
                articles = fetch_headlines("country", value)
            elif option == "List all new headlines":
                articles = fetch_headlines()
            else:
                send_json(conn, ["Invalid option"])
                continue

            if articles is None:
                send_json(conn, {"error": "Failed to fetch headlines"})
                continue

 
            last_articles[user] = articles

            filename = f"{user}headlines{GROUP_ID}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)

           
            summary_list = []
            for a in articles:
             summary_list.append({
                   "source": a.get("source", {}).get("name"),
                  "author": a.get("author"),
                     "title": a.get("title")
                   })


            send_json(conn, summary_list)

        
            
        elif main == "EXIT":
            print(f"--- {user} disconnected ---")
            conn.close()
            break

        else:
            send_json(conn, ["Unknown command"])


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
    soc.bind((HOST, PORT))
    soc.listen(MAX_CONNECTIONS)
    print(f"SERVER LISTENING on {HOST}:{PORT}")
    while True:
        sock, address = soc.accept()
        threading.Thread(target=handle_client, args=(sock, address)).start()