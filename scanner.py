from github import Github
import chromadb
import ast
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from database import store_function, store_relation, get_token, LITESQL_URL
import requests

load_dotenv()

# Setup
github = Github(os.getenv("GITHUB_TOKEN"))
client = chromadb.PersistentClient(path="./code_db")
collection = client.get_or_create_collection("functions")
model = SentenceTransformer('all-MiniLM-L6-v2')

id_map = {}
file_counter = [0]
func_counters = {}

def get_func_code(content, node):
    lines = content.split('\n')
    return '\n'.join(lines[node.lineno-1:node.end_lineno])

def get_next_file_id():
    """Next available file ID lo"""
    token = get_token()
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT id FROM functions"}
    )
    data = response.json()
    if data["success"] and data["data"]:
        
        max_id = max([row["id"] for row in data["data"]])
        
        max_file = max_id // 1000
        return max_file + 1
    return 1

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
    
    if not ids_to_delete:
        return
    
   
    for old_id in ids_to_delete:
        requests.post(
            f"{LITESQL_URL}/api/query",
            headers={"Authorization": token},
            json={"sql": f"DELETE FROM functions WHERE id={old_id}"},
            timeout=30
        )
        print(f"🗑️ Function deleted: {old_id}")
    
   
    rel_response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT caller_id, callee_id FROM relations"},
        timeout=30
    )
    
    if rel_response.json()["success"] and rel_response.json()["data"]:
        
       
        relations_to_delete = []
        for row in rel_response.json()["data"]:
            if row["caller_id"] in ids_to_delete or \
               row["callee_id"] in ids_to_delete:
                relations_to_delete.append(row)
        
        print(f"Relations to delete: {relations_to_delete}")
        
       
        for rel in relations_to_delete:
            requests.post(
                f"{LITESQL_URL}/api/query",
                headers={"Authorization": token},
                json={"sql": f"DELETE FROM relations WHERE caller_id={rel['caller_id']}"},
                timeout=30
            )
            print(f"🗑️ Relation deleted: {rel['caller_id']} → {rel['callee_id']}")
    
   
    for old_id in ids_to_delete:
        try:
            collection.delete(ids=[str(old_id)])
        except:
            pass
    
    
    keys_to_delete = [k for k, v in id_map.items() if v in ids_to_delete]
    for key in keys_to_delete:
        del id_map[key]

def scan_file(file_path, content, file_num):
    """Ek file scan karo"""
    
    try:
        tree = ast.parse(content)
    except:
        print(f"❌ Parse error: {file_path}")
        return
    
    func_counters[file_path] = 0
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            
            func_counters[file_path] += 1
            func_num = func_counters[file_path]
            
            # ID banao
            func_id = (file_num * 1000) + func_num
            func_key = f"{file_path}__{node.name}"

            if func_key in id_map:
                print(f"⚠️ Already exists: {func_key}")
                continue
            
            id_map[func_key] = func_id
            
            func_code = get_func_code(content, node)
            
           
            store_function(func_id, node.name, file_path, func_key)
            
            
            vector = model.encode(func_code).tolist()
            try:
                collection.add(
                    ids=[str(func_id)],
                    documents=[func_code],
                    embeddings=[vector],
                    metadatas=[{
                        "name": node.name,
                        "file": file_path
                    }]
                )
            except:
                pass
            
            print(f"✅ Stored: {func_key} → {func_id}")

def scan_relations(file_path, content):
    """Relations dhundo"""
    
    try:
        tree = ast.parse(content)
    except:
        return
    
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imports[alias.name] = f"{node.module}.py"

    BUILTINS = {
        'print', 'len', 'range', 'zip', 'enumerate',
        'str', 'int', 'float', 'list', 'dict', 'set',
        'tuple', 'bool', 'round', 'sum', 'min', 'max',
        'sorted', 'map', 'filter', 'isinstance',
        'ValueError', 'TypeError', 'KeyError', 'Exception'
    }
    print(f"📦 Scanning relations for: {file_path}")
    print(f"📦 Imports found: {imports}")  # ← Add karo
    print(f"📦 id_map size: {len(id_map)}")  # ← Add karo
    
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            
            caller_key = f"{file_path}__{node.name}"
            caller_id = id_map.get(caller_key)
            
            if not caller_id:
                print(f"❌ Not in id_map: {caller_key}")
                continue
            stored_relations = set() 
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        call_name = child.func.id

                        if call_name in BUILTINS:
                            continue
                        
                        if call_name in imports:
                            source = imports[call_name]
                            call_key = None
                            for key in id_map.keys():
                                if source in key and f"__{call_name}" in key:
                                    call_key = key
                                    break
                        else:
                            call_key = f"{file_path}__{call_name}"
                        
                        if call_key:
                            call_id = id_map.get(call_key)
                            if call_id:
                                relation = (caller_id, call_id)
                                if relation not in stored_relations:
                                    stored_relations.add(relation)
                                    store_relation(caller_id, call_id)
                                    print(f"🔗 {caller_id} → {call_id}")
                        else:
                            if call_name not in BUILTINS:
                                print(f"❌ Call not in id_map: {call_key}") 

def scan_github_repo(repo_name):
    """Poora repo scan karo — pehli baar"""
    
    print(f"🔍 Scanning: {repo_name}")
    
    repo = github.get_repo(repo_name)
    contents = repo.get_contents("")
    
    py_files = {}
    
    while contents:
        file = contents.pop(0)
        if file.type == "dir":
            contents.extend(repo.get_contents(file.path))
        elif file.name.endswith('.py'):
            try:
                content = file.decoded_content.decode('utf-8')
                py_files[file.path] = content
                print(f"📄 Found: {file.path}")
            except:
                pass
    
    print(f"\nFound {len(py_files)} Python files")
    
   
    print("\n📦 Storing functions...")
    for file_path, content in py_files.items():
        file_counter[0] += 1
        scan_file(file_path, content, file_counter[0])
    
 
    print("\n🔗 Finding relations...")
    for file_path, content in py_files.items():
        scan_relations(file_path, content)
    
    print(f"\n✅ Scan Complete!")
    print(f"Total Functions: {len(id_map)}")

def update_on_pr(repo_name, pr_number):
    
    print(f"\n🔄 Updating for PR #{pr_number}")
    
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    changed_py_files = [
        f for f in pr.get_files()
        if f.filename.endswith('.py')
    ]
    
    if not changed_py_files:
        print("No Python files changed")
        return
    
    for file in changed_py_files:
        print(f"\n📄 Processing: {file.filename}")
        
        
        delete_file_data(file.filename)
        
        
        try:
            new_content = repo.get_contents(
                file.filename,
                ref=pr.head.sha
            ).decoded_content.decode('utf-8')
        except:
            print(f"❌ Could not get content: {file.filename}")
            continue
        
        new_file_id = get_next_file_id()
        
       
        scan_file(file.filename, new_content, new_file_id)
    
    
    print("\n🔄 Reloading id_map...")
    reload_id_map()
    
    
    print("\n🗑️ Deleting all relations...")
    token = get_token()
    rel_response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT caller_id, callee_id FROM relations"},
        timeout=30
    )
    
    if rel_response.json()["success"] and rel_response.json()["data"]:
        all_relations = rel_response.json()["data"]
        for row in all_relations:
            requests.post(
                f"{LITESQL_URL}/api/query",
                headers={"Authorization": token},
                json={"sql": f"DELETE FROM relations WHERE caller_id={row['caller_id']}"},
                timeout=30
            )
    
   
    print("\n🔗 Re-scanning ALL relations...")
    contents = repo.get_contents("")
    all_py_files = {}
    
    while contents:
        f = contents.pop(0)
        if f.type == "dir":
            contents.extend(repo.get_contents(f.path))
        elif f.name.endswith('.py'):
            try:
                content = f.decoded_content.decode('utf-8')
                all_py_files[f.path] = content
            except:
                pass
    
    for file_path, content in all_py_files.items():
        scan_relations(file_path, content)
    
    print(f"\n✅ DB Updated!")

def reload_id_map():
    """LiteSQL se id_map reload karo"""
    global id_map
    id_map = {}
    
    token = get_token()
    response = requests.post(
        f"{LITESQL_URL}/api/query",
        headers={"Authorization": token},
        json={"sql": "SELECT id, func_key FROM functions"},
        timeout=30
    )
    
    if response.json()["success"] and response.json()["data"]:
        for row in response.json()["data"]:
            id_map[row["func_key"]] = row["id"]
    
    print(f"✅ id_map reloaded: {len(id_map)} functions")


if __name__ == "__main__":
   
    scan_github_repo("Shashwat8732/test")