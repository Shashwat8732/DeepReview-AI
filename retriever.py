import chromadb
from database import get_func_id, get_relations
from dotenv import load_dotenv

load_dotenv()

# ChromaDB Setup
client = chromadb.PersistentClient(path="./code_db")
collection = client.get_or_create_collection("functions")

def get_all_related(func_id):
    """Poora tree traverse karo"""
    
    related = set()
    visited = set()
    
    def traverse(current_id):
        if current_id in visited:
            return
        visited.add(current_id)
        related.add(current_id)
        
        calls, called_by = get_relations(current_id)
        
        for call_id in calls:
            traverse(call_id)
        
        for caller_id in called_by:
            traverse(caller_id)
    
    traverse(func_id)
    return list(related)

def get_relevant_chunk(func_code, changed_code, max_lines=500):
    """
    Bade function se relevant chunk nikalo
    Changed code se similar lines dhundo
    """
    lines = func_code.split('\n')
    
    # Agar chota hai toh poora do
    if len(lines) <= max_lines:
        return func_code
    
    print(f"✂️ Chunking: {len(lines)} lines → {max_lines}")
    
   
    changed_words = set(changed_code.lower().split())
    
  
    chunks = []
    for i in range(0, len(lines), max_lines):
        chunk = '\n'.join(lines[i:i + max_lines])
        chunks.append(chunk)
    
   
    best_chunk = chunks[0]
    best_score = 0
    
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(changed_words & chunk_words)
        if score > best_score:
            best_score = score
            best_chunk = chunk
    
    return best_chunk

def get_context(func_name, file_path):
    """Changed function ka poora context banao"""
    
    print(f"\n🔍 Getting context for: {func_name}")
    
    
    func_key = f"{file_path}__{func_name}"
    
   
    func_id = get_func_id(func_key)
    if not func_id:
        print(f"❌ Function not found!")
        return None
    
    print(f"✅ ID: {func_id}")
    
   
    related_ids = get_all_related(func_id)
    print(f"✅ Related IDs: {related_ids}")
    
    
    result = collection.get(
        ids=[str(id) for id in related_ids]
    )
    
   
    changed_func_result = collection.get(ids=[str(func_id)])
    changed_code = ""
    if changed_func_result['documents']:
        changed_code = changed_func_result['documents'][0]
    
   
    context = "# CODE CONTEXT FOR REVIEW\n\n"
    total_lines = 0
    MAX_TOTAL_LINES = 2000  # Total context limit
    
    for code, metadata in zip(
        result['documents'],
        result['metadatas']
    ):
       
        lines = code.split('\n')
        print(f"📄 {metadata['name']}: {len(lines)} lines")
        
        
        if len(lines) > 500:
            code = get_relevant_chunk(code, changed_code)
            print(f"✂️ Chunked to 500 lines")
        
       
        chunk_lines = len(code.split('\n'))
        if total_lines + chunk_lines > MAX_TOTAL_LINES:
            print(f"⚠️ Total limit reached — skipping {metadata['name']}")
            continue
        
        total_lines += chunk_lines
        
        context += f"# File: {metadata['file']}\n"
        context += f"# Function: {metadata['name']}\n"
        context += f"{code}\n\n"
        context += "─" * 40 + "\n\n"
    
    print(f"✅ Context ready! Total lines: {total_lines}")
    return context

