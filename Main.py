# -*- coding: utf-8 -*-
"""
Created on Fri May 26 17:33:11 2023

@author: Ayman
"""

from NewClassesDef import *
from CommandParser import *
import pickle

def save_state(root):
    with open("tree_state.pkl", "wb") as file:
        pickle.dump(root, file)

def load_state():
    try:
        with open("tree_state.pkl", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None

def authenticate(parser, user, password):
    client = parser.get_object(user)
    if client == None:
        return False
    hashed_password = client._hash_password(password)
    if client.password_hash == hashed_password:
        parser.current_client = client
        client.log_file.append_log("Log in")
        return True
    else:
        print("here")
        return False

def main():
    root = load_state()
    if not root:
        # Create the root directory
        root = Root("Root")
        
    # Create CommandParser instance
    parser = CommandParser(root)
    
    # Check if a super admin exit and authentication
    super_admin_exist=False
    for child in root.children.values():
        if isinstance(child, Client) and child.is_super_admin:
            super_admin_exist=True
            break
    
    ValidUser = False
    if super_admin_exist:
        while ValidUser == False:
            user = input("Enter your username: ")
            password = input("Enter your password: ")
            ValidUser = authenticate(parser, user, password)
            if ValidUser == False:
                print("Please retry log in, the username or (and) the password are not correct")
    else:
        print("Welcome to the Auto File System Management")
        print("First we need to create a super admin")
        user = input("Enter your username: ")
        password = input("Enter your password: ")
        client = Client(user, parent=root, is_super_admin=True, password=password)
        root.add_child(client, client)
        parser.current_client = client
        client.log_file.append_log("New account created")
        ValidUser = True
        
    # Start the command prompt
    while ValidUser:
        command = input("Enter a command: ")
        if command == "exit":
            parser.current_client.log_file.append_log("Log out")
            break
        parser.parse_command(command)
        
    save_state(root)

if __name__ == "__main__":
    main()
