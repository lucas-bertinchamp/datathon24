import os
import sys

def save_file(folder, file_name, content):
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    with open(os.path.join(folder, file_name), "w", encoding="utf-8") as f:
        f.write(content)
        
    return os.path.join(folder, file_name)