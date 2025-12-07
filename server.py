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
        r = requests.get(url, timeout=8)
        data = r.json()
        if data.get("status") != "ok":
            print("NewsAPI Error:", data)
            return None
        return data.get("articles", [])[:15]
    except Exception as e:
        print("Exception:", e)
        return None

def fetch_sources(param_name=None, param_value=None):
    try:
        if param_name and param_value:
            url = f"https://newsapi.org/v2/sources?{param_name}={param_value}&apiKey={NEWSAPI_KEY}"
        else:
            url = f"https://newsapi.org/v2/sources?apiKey={NEWSAPI_KEY}"
        r = requests.get(url, timeout=8)
        data = r.json()
     
        if data.get("status") and data.get("status") != "ok":
            return None
        return data.get("sources", [])[:15]
    except Exception as e:
        print("Exception:", e)
        return None

def send_json(conn, data):
    try:
        conn.sendall(json.dumps(data).encode())
    except Exception as e:
        print("[SEND ERROR]", e)

def handle_client(conn, address):
    last_articles = {}
    last_sources = {}

    try:
        user = conn.recv(1024).decode("utf-8").strip()
    except:
        conn.close()
        return

    print(f"--- Connected: {user} | {address} ---")

    while True:
        try:
            main = conn.recv(1024).decode("utf-8")
        except:
            break
        if not main:
            break

        if main == "Search headlines":
            option = conn.recv(1024).decode("utf-8")
            value = None

            if option == "Back to main menu":
                continue
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
                send_json(conn, {"error": "Invalid option"})
                continue

            if articles is None:
                send_json(conn, {"error": "Failed to fetch headlines"})
                continue

        
            if len(articles) == 0:
                send_json(conn, {"error": "No results found"})
                continue

            last_articles[user] = articles
            filename = f"{user}_headlines_{GROUP_ID}.json"
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

      
            idx = conn.recv(1024).decode("utf-8").strip()
            if not idx or idx == "0":
              send_json(conn, {})  
              continue


            if idx.isdigit():
                idx = int(idx) - 1
                if 0 <= idx < len(articles):
                    send_json(conn, articles[idx])
                else:
                    send_json(conn, {"error": "Invalid index"})
            else:
                send_json(conn, {"error": "Invalid input"})

        elif main == "List of sources":
            option = conn.recv(1024).decode("utf-8")
            value = None

            if option == "Back to main menu":
                continue
            if option in ["Search by category", "Search by country", "Search by language"]:
                value = conn.recv(1024).decode("utf-8")

            print(f"[REQUEST] User={user} | Type=Sources | Option={option} | Value={value}")

            if option == "Search by category":
                sources = fetch_sources("category", value)
            elif option == "Search by country":
                sources = fetch_sources("country", value)
            elif option == "Search by language":
                sources = fetch_sources("language", value)
            elif option == "List all":
                sources = fetch_sources()
            else:
                send_json(conn, {"error": "Invalid option"})
                continue

            if sources is None:
                send_json(conn, {"error": "Failed to fetch sources"})
                continue

           
            if len(sources) == 0:
                send_json(conn, {"error": "No results found"})
                continue

            last_sources[user] = sources
            filename = f"{user}_sources_{GROUP_ID}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(sources, f, indent=2, ensure_ascii=False)

            summary = [{"name": s.get("name")} for s in sources]
            send_json(conn, summary)

            
            idx = conn.recv(1024).decode("utf-8").strip()
            if not idx or idx == "0":
               send_json(conn, {})  
               continue


            if idx.isdigit():
                idx = int(idx) - 1
                if 0 <= idx < len(sources):
                    send_json(conn, sources[idx])
                else:
                    send_json(conn, {"error": "Invalid index"})
            else:
                send_json(conn, {"error": "Invalid input"})

        elif main == "EXIT":
            print(f"--- {user} disconnected ---")
            conn.close()
            break
        

        else:
            send_json(conn, {"error": "Unknown command"})

    try:
        conn.close()
    except:
        pass

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
    soc.bind((HOST, PORT))
    soc.listen(MAX_CONNECTIONS)
    print(f"SERVER LISTENING on {HOST}:{PORT}")
    while True:
        sock, address = soc.accept()
        threading.Thread(target=handle_client, args=(sock, address)).start()
