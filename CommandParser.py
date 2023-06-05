# -*- coding: utf-8 -*-
"""
Created on Wed May 24 12:45:40 2023

@author: Ayman
"""

# The file system's API refer in our case to the NewClassesDef.py implementation of the file system

from NewClassesDef import Node, Root, Site, Client, Directory, File

class CommandParser:
    def __init__(self, root_directory):
        self.root_directory= root_directory
        self.current_directory = root_directory
        self.current_client = None

    def parse_command(self, command_line):
        parts = command_line.split()
        command = parts[0].lower()
        arguments = parts[1:]

        if command == 'mkdir':
            self.create_directory(arguments)
        elif command == 'touch':
            self.create_file(arguments)
        elif command == 'ls':
            self.list_contents(arguments)
        elif command == 'cd':
            self.change_directory(arguments)
        elif command == 'mv':
            self.move_object(arguments)
        elif command == 'cp':
            self.copy_object(arguments)
        elif command == 'rm':
            self.delete_object(arguments)
        elif command == 'info':
            self.show_object_details(arguments)
        elif command == 'chmod':
            self.set_permissions(arguments)
        elif command == 'help':
            self.get_help()
        elif command == 'whoami':
            print(self.current_client.name)
        elif command == 'log':
            self.command_log(arguments)
        elif command == 'newclient':
            self.create_client(arguments)
        elif command == 'newsite':
            self.create_site(arguments)
        else:
            print("Invalid command.")
            print("Use 'help' command to display all the command")
            
        # Keep the command in a log    
        if self.current_client:
            self.current_client.log_file.append_log(command_line)

    # Create a new client
    def create_client(self, arguments):
        if len(arguments) > 3:
            print("Invalid command. Usage: NewClient <client_name> <password> <admin>")
            print("The admin parameter need to be either true,1,yes (for creation of an admin) or false")
            return
        
        if self.current_client.is_super_admin and arguments[2].lower() in ["true", "1", "yes"]:
            client_name = arguments[0]
            current_directory = self.get_current_directory()
            client = self.current_client
            new_client = Client(client_name, parent=current_directory, is_admin=True, password=arguments[1])
            try:
                current_directory.add_child(client, new_client)
                print("Created directory:", client_name)
            except PermissionError as e:
                print("Error:", str(e))
        elif self.current_client.is_super_admin or self.current_client.is_admin:
            client_name = arguments[0]
            current_directory = self.get_current_directory()
            client = self.current_client
            new_client = Client(client_name, parent=current_directory, password=arguments[1])
            try:
                current_directory.add_child(client, new_client)
                print("Created directory:", client_name)
            except PermissionError as e:
                print("Error:", str(e))
        else:
            raise PermissionError("A regular User cannot add a client")
        
    # Create a new site
    def create_site(self, arguments):
        if len(arguments) != 1:
            print("Invalid command. Usage: NewSite <site_name>")
            return
        site_name = arguments[0]
        current_directory = self.get_current_directory()
        if current_directory != self.root_directory and not self.current_client.is_super_admin:
            return print("To create a Site you need to be a super admin and in the root directory")
        client = self.current_client
        new_site = Site(site_name, parent=current_directory, protected=True)
        try:
            current_directory.add_child(client, new_site)
            print("Created directory:", site_name)
        except PermissionError as e:
            print("Error:", str(e))
    
    def create_directory(self, arguments):
        if len(arguments) != 1:
            print("Invalid command. Usage: mkdir <directory_name>")
            return
        directory_name = arguments[0]
        current_directory = self.get_current_directory()
        client = self.current_client
        new_directory = Directory(directory_name, parent=current_directory, owner=self.current_client)
        try:
            current_directory.add_child(client, new_directory)
            print("Created directory:", directory_name)
        except PermissionError as e:
            print("Error:", str(e))

    def create_file(self, arguments):
        if len(arguments) != 1:
            print("Invalid command. Usage: touch <file_name>")
            return
        file_name = arguments[0]
        current_directory = self.get_current_directory()
        client = self.current_client
        new_file = File(file_name, parent=current_directory, owner=self.current_client)
        try:
            current_directory.add_child(client, new_file)
            print("Created file:", file_name)
        except PermissionError as e:
            print("Error:", str(e))

    def list_contents(self, arguments):
        if len(arguments) > 1:
            print("Invalid command. Usage: ls [<directory_path>]")
            return
    
        directory_path = arguments[0] if arguments else None
        target_directory = self.find_directory_or_file(directory_path) if directory_path else self.get_current_directory()
    
        if target_directory:
            print("Listing contents of directory:", target_directory.name)
            for child_name in target_directory.children:
                child = target_directory.children[child_name]
                if isinstance(child, Directory):
                    print("Directory:", child_name)
                elif isinstance(child, File):
                    print("File:", child_name)
        else:
            print("Directory not found:", directory_path)

    def change_directory(self, arguments):
        if len(arguments) != 1:
            print("Invalid command. Usage: cd <directory_path>")
            return
    
        directory_path = arguments[0]
        target_directory = self.find_directory_or_file(directory_path)
    
        if target_directory and isinstance(target_directory, Directory):
            self.current_directory = target_directory
            print("Changed directory to:", target_directory.name)
        else:
            print("Directory not found:", directory_path)

    def move_object(self, arguments):
        if len(arguments) != 2:
            print("Invalid command. Usage: mv <source_name> <destination_name>")
            return
    
        source_name = arguments[0]
        destination_name = arguments[1]
    
        source_object = self.find_directory_or_file(source_name)
        destination_object = self.find_directory_or_file(destination_name)
    
        if source_object and destination_object:
            try:
                source_object.move(self.current_client, destination_object)
                print("Moved object:", source_name, "to:", destination_name)
            except PermissionError as e:
                print("Error:", str(e))
        else:
            print("Object not found:", source_name if not source_object else destination_name)

    def copy_object(self, arguments):
        if len(arguments) > 3:
            print("Invalid command. Usage: cp <source_name> <destination_name> [<new_name>]")
            return
    
        source_name = arguments[0]
        destination_name = arguments[1]
    
        source_object = self.find_directory_or_file(source_name)
        destination_object = self.find_directory_or_file(destination_name)
    
        if isinstance(source_object, (Directory, File)) and isinstance(destination_object, Directory):
            try:
                new_name = None
                if len(arguments) == 3:
                    new_name = arguments[2]
                
                source_object.copy(self.current_client, destination_object, new_name)
                print("Copied object:", source_name, "to:", destination_name)
            except PermissionError as e:
                print("Error:", str(e))
        else:
            print("Invalid source or destination object:", source_name if not isinstance(source_object, Directory) else destination_name)

    def delete_object(self, arguments):
        if len(arguments) != 1:
            print("Invalid command. Usage: rm <object_name> or rm <path>")
            return
    
        object_identifier = arguments[0]
        object_to_delete = self.find_directory_or_file(object_identifier)
    
        if isinstance(object_to_delete, Node):
            try:
                object_to_delete.parent.delete_child(self.current_client, object_to_delete.name)
                print("Deleted object:", object_identifier)
            except PermissionError as e:
                print("Error:", str(e))
        else:
            print("Object not found:", object_identifier)

    def show_object_details(self, arguments):
        if len(arguments) != 1:
            print("Invalid command. Usage: info <object_name>")
            return
        object_name = arguments[0]
        object_to_show = self.get_object(object_name)
        if object_to_show:
            print("Name of the object:", object_to_show.name)
            if isinstance(object_to_show, Directory):
                print("Type of the object: Directory")
            else:
                print("Type of the object: File")
            print("Owner of the object:", object_to_show.owner.name)
            # Access and display the details of the object using the file system's API
            # Example: print("Object details:", object_to_show.details())
        else:
            print("Object not found:", object_name)

    def set_permissions(self, arguments):
        if len(arguments) != 3:
            print("Invalid command. Usage: chmod <object_name> <permission> <client>")
            return
    
        object_name = arguments[0]
        permission = arguments[1]
        clientName = arguments[2]
        client = self.find_directory_or_file(clientName)
        object_to_set_permissions = self.find_directory_or_file(object_name)
    
        if isinstance(object_to_set_permissions, Directory) or isinstance(object_to_set_permissions, File):
            #client = self.current_client
        
            try:
                if self.current_client.is_super_admin:
                    if permission.startswith('-'):
                        # Remove permission
                        permission_to_remove = permission[1:]
                        object_to_set_permissions.remove_permission(client, permission_to_remove)
                    else:
                        object_to_set_permissions.add_permission(client, permission)
                elif self.current_client.is_admin and client.site == object_to_set_permissions.get_site():
                    if permission.startswith('-'):
                        # Remove permission
                        permission_to_remove = permission[1:]
                        object_to_set_permissions.remove_permission(client, permission_to_remove)
                    else:
                        object_to_set_permissions.add_permission(client, permission)
                elif object_to_set_permissions.owner == self.current_client:
                    if permission.startswith('-'):
                        # Remove permission
                        permission_to_remove = permission[1:]
                        object_to_set_permissions.remove_permission(client, permission_to_remove)
                    else:
                        object_to_set_permissions.add_permission(client, permission)
                else:
                    raise PermissionError("You do not have permission to set permissions on this object.")
                
                print("Setting permissions of object:", object_name, "action:", permission, "to:", client.name)
            except PermissionError as e:
                print("Error:", str(e))
        else:
            print("Object not found:", object_name)

    def get_help(self):
        # Print all the command that is possible
        print("To create an new directory: 'mkdir'")
        print("To create an new file: 'touch'")
        print("To show the content of a directory: 'ls'")
        print("To navigate through a directory: 'cd'")
        print("To remove a directory or a file: 'rm'")
        print("To move a directory or a file: 'mv'")
        print("To copy a directory or a file: 'cp'")
        print("To display info about a directory or a file: 'info'")
        print("To set new permission over a directory or a file: 'chmod'")
        print("To know which user you are controlling: 'whoami'")
        print("To display a log of a client: 'log'")
        print("To create a new client: 'newclient'")
        print("To create a new Site: 'newsite'")

    def get_current_directory(self):
        # Get the current directory based on your file system's API
        return self.current_directory

    def go_up_directory(self):
        if self.current_directory.parent:
            self.current_directory = self.current_directory.parent
            print("Went up to parent directory.")
        else:
            print("Already in the root directory.")

    def get_children_directory(self, directory_name):
        # Get the directory based on your file system's API
        if isinstance(self.current_directory.find_object(directory_name), File):
            return ValueError("The object with the given name is not a directory")
        return self.current_directory.find_object(directory_name)

    def find_directory_or_file(self, path):
        if not path:
            print("Invalid path.")
            return None

        if path == '/':
            return self.root_directory
        
        if path[0] == '/':
            current_node = self.root_directory
            parts = path[1:].split('/')
        else:
            current_node = self.current_directory
            parts = path.split('/')

        for part in parts:
            if part == '..':
                if current_node.parent:
                    current_node = current_node.parent
                else:
                    print("Invalid path.")
                    return None
            elif part == '.':
                continue
            else:
                if part in current_node.children:
                    node = current_node.children[part]
                    if isinstance(node, (Directory, File)):
                        current_node = node
                    else:
                        print("Invalid path.")
                        return None
                else:
                    print("Invalid path.")
                    return None

        return current_node

    def get_object(self, object_name):
        # Get the object based on your file system's API
        return self.current_directory.find_object(object_name)
    
    # Command log take for argument the client's name
    def command_log(self, arguments):
        if len(arguments) != 1:
            print("Invalid command. Usage: log <client_name>")
            return
        
        if not self.current_client.is_admin and not self.current_client.is_super_admin:
            print("Only an admin or super admin can display the content of a lof file")
            return
        
        client_name = arguments[0]
        client = self.root_directory.find_object(client_name)
        
        if client:
            log_file = client.log_file
            if log_file:
                print(log_file.content)
            else:
                print("Log file not found.")
        else:
            return
