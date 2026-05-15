import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# LiteSQL Config
LITESQL_URL = "https://litesql.onrender.com"
USERNAME = os.getenv("LITESQL_USERNAME")
PASSWORD = os.getenv("LITESQL_PASSWORD")

import chromadb

client = chromadb.PersistentClient(path="./code_db")
collection = client.get_or_create_collection("functions")

def get_token():
    """LiteSQL se token lo"""
    response = requests.post(
        f"{LITESQL_URL}/api/auth/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    data = response.json()
    if data["success"]:
        return data["session_token"]
    else:
        print("❌ Login failed!")
        return None

def setup_database():
    """Reviews table banao"""
    token = get_token()
    
    query = """CREATE TABLE code_reviews (id INT, repo_name STR, pr_number INT, file_name STR, severity STR, review_text STR, date STR, time STR)"""
    
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": query}
    )
    print("Response:", response.json())
    print("✅ Table ready!")

def save_review(repo_name, pr_number, file_name, severity, review_text):
    """Review save karo"""
    token = get_token()
    date = datetime.now().strftime("%Y-%m-%d")
    time= datetime.now().strftime("%H:%M:%S")

    def clean(text):
        return str(text).replace("'", "").replace('"', '').replace("\n", " ").replace(" ", "_").replace("/", "_")
    
    repo_clean    = clean(repo_name)
    file_clean    = clean(file_name)
    severity_clean= clean(severity)
    
    critical_count = review_text.count("CRITICAL")
    medium_count   = review_text.count("MEDIUM")
    low_count      = review_text.count("LOW")

    summary = f"Critical_{critical_count}_Medium_{medium_count}_Low_{low_count}"
    
    
    
    
    query = f"""INSERT INTO code_reviews VALUES (1,{repo_clean},{pr_number},{file_clean},{severity_clean},{summary},{date},{time})"""
    
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": query}
    )
    print("Response:", response.json())
    print(f"✅ Review saved in LiteSQL!")

def get_all_reviews():
    """Saari reviews dekho"""
    token = get_token()
    
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT * FROM code_reviews"}
    )
    return response.json()

def setup_scanner_tables():
    token = get_token()
    
    
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "CREATE TABLE functions (id INT, name STR, file STR, func_key STR)"}
    )
    print("Functions table:", response.json())
    
   
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "CREATE TABLE relations (caller_id INT, callee_id INT)"}
    )
    print("Relations table:", response.json())

def store_function(func_id, name, file_path, func_key):
    token = get_token()
    
    def clean(text):
        return str(text).replace("'", "").replace('"', '').replace("\n", "").replace(" ", "_").replace("/", "_")
    
    name_clean     = clean(name)
    file_clean     = clean(file_path)
    func_key_clean = clean(func_key)
    
   
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": f"INSERT INTO functions VALUES ({func_id},{name_clean},{file_clean},{func_key_clean})"}
    )
    return response.json()

def store_relation(caller_id, callee_id):
    token = get_token()
    
   
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": f"INSERT INTO relations VALUES ({caller_id},{callee_id})"}
    )
    return response.json()


def get_func_id(func_key):
    """func_key se ID lo"""
    token = get_token()
    
    print(f"Searching for: {func_key}")
    
   
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT id, func_key FROM functions"},
        timeout=30
    )
    
    data = response.json()
    
    if data["success"] and data["data"]:
        
       
        matching_ids = [
            row["id"] 
            for row in data["data"]
            if row["func_key"] == func_key
        ]
        
        print(f"Matching IDs: {matching_ids}")
        
        if matching_ids:
            
            latest_id = max(matching_ids)
            print(f"Latest ID: {latest_id}")
            return latest_id
    
    return None
    
    

def get_relations(func_id):
   token = get_token()
    
    
   response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT caller_id, callee_id FROM relations"},
        timeout=30
    )
    
   calls = []
   called_by = []
    
   data = response.json()
   if data["success"] and data["data"]:
        for row in data["data"]:
            # Python mein filter karo
            if row["caller_id"] == func_id:
                calls.append(row["callee_id"])
            if row["callee_id"] == func_id:
                called_by.append(row["caller_id"])
    
   return calls, called_by

def delete_file_data(file_path):
    token = get_token()
    
   
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT id, file FROM functions"},
        timeout=30
    )
    
    if not response.json()["success"]:
        return
    
   
    ids_to_delete = []
    for row in response.json()["data"]:
        if row["file"] == file_path:
            ids_to_delete.append(row["id"])
    
    print(f"IDs to delete: {ids_to_delete}")
    
   
    for old_id in ids_to_delete:
        
        requests.post(
            f"{LITESQL_URL}/api/query",
            headers={"Authorization": token},
            json={"sql": f"DELETE FROM functions WHERE id={old_id}"},
            timeout=30
        )
       
        
        requests.post(
            f"{LITESQL_URL}/api/query",
            headers={"Authorization": token},
            json={"sql": f"DELETE FROM relations WHERE caller_id={old_id}"},
            timeout=30
        )
      
        requests.post(
            f"{LITESQL_URL}/api/query",
            headers={"Authorization": token},
            json={"sql": f"DELETE FROM relations WHERE callee_id={old_id}"},
            timeout=30
        )
       
        
        try:
            collection.delete(ids=[str(old_id)])
        except:
            pass
        
        print(f"🗑️ Deleted: {old_id}")
