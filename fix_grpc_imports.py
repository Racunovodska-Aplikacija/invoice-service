#!/usr/bin/env python3
"""Fix imports in generated gRPC files to use relative imports"""

import os
import re

CLIENT_DIR = "client"

def fix_imports_in_file(filepath):
    """Fix absolute imports to relative imports in generated _pb2_grpc.py files"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace 'import company_pb2 as company__pb2' with 'from . import company_pb2 as company__pb2'
    # Replace 'import partner_pb2 as partner__pb2' with 'from . import partner_pb2 as partner__pb2'
    # Replace 'import product_pb2 as product__pb2' with 'from . import product_pb2 as product__pb2'
    
    patterns = [
        (r'^import (\w+_pb2) as (\w+__pb2)', r'from . import \1 as \2'),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            content = new_content
            modified = True
    
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed imports in {filepath}")
    
    return modified

def main():
    """Fix imports in all generated _pb2_grpc.py files"""
    grpc_files = [
        os.path.join(CLIENT_DIR, "company_pb2_grpc.py"),
        os.path.join(CLIENT_DIR, "partner_pb2_grpc.py"),
        os.path.join(CLIENT_DIR, "product_pb2_grpc.py"),
    ]
    
    fixed_count = 0
    for filepath in grpc_files:
        if os.path.exists(filepath):
            if fix_imports_in_file(filepath):
                fixed_count += 1
    
    print(f"Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()
