# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:16:28 2023

@author: Ayman
"""

#The copy module will be used during the copy method
import copy


"""
About permissions,

Super Admin - Has full access and control over all sites. They can perform any operation (like add, move, delete, rename, copy etc.) on any node in the tree.

Admin - Limited to their specific site. They can manage all clients and directories within their site, including creating new directories, managing client directories, and creating shared directories. However, they don't have control over other sites.

Client - Only has access to their own directories. They can perform operations within their directory but cannot modify anything outside of it. They can also access (read-only) shared directories.
"""

# We use a hierachical tree to get a flexible way to create our filesystem
class Node:
    def __init__(self, name, parent=None, protected=False):
        self.name = name
        self.parent = parent
        self.children = {}
        self.protected = protected
        self.permissions = {}
    
    # Return the site we are in on a specific node by going to the top level until it 
    # reaches a site
    def get_site(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node if isinstance(node, Site) else None

    # Same as the get_site but for the client
    def get_client(self):
        node = self
        while node.parent is not None and not isinstance(node, Client):
            node = node.parent
        return node if isinstance(node, Client) else None

    
    # We want to add a child such as adding subdirectories of Client for example. Now when
    # we use this method we need to be sure that the child is indeed an instance of Node
    # if so we add it to the children dictionary.
    def add_child(self, client, child):
        
        if client.is_super_admin:
            # Super admins can do anything
            pass
        elif client.is_admin:
            # Regular admins can only modify nodes within their site
            if self.get_site() != client.get_site():
                raise PermissionError("You do not have permission to modify this node.")
        else:
            # Clients can only modify nodes within their own directory
            if self.get_client() != client:
                raise PermissionError("You do not have permission to modify this node.")
        
        if isinstance(child, Node):
            child.parent = self  # Update the child's parent
            self.children[child.name] = child
        else:
            raise TypeError("Child must be an instance of Node or its subclass.")
    
    # This method will delete a child, but like in the file system of linux, if the child
    # have children it will raise an exception that can be brute force if the parameter
    # force is set to True.
    def delete_child(self, client, child_name, force=False):
        
        if client.is_super_admin:
            # Super admins can do anything
            pass
        elif client.is_admin:
            # Regular admins can only modify nodes within their site
            if self.get_site() != client.get_site():
                raise PermissionError("You do not have permission to modify this node.")
        else:
            # Clients can only modify nodes within their own directory
            if self.get_client() != client:
                raise PermissionError("You do not have permission to modify this node.")
                
        if child_name in self.children:
            child = self.children[child_name]
            
            if child.protected and not (client.is_admin or client.is_super_admin):
                raise Exception("You do not have the necessary permissions to delete this node.")

            if not force and len(child.children) > 0:
                raise Exception("Cannot delete a node that has children unless 'force' is True.")
        
            child.parent = None  # Remove the child's reference to its parent
            del self.children[child_name]  # Remove the child from its parent's children
        else:
            raise Exception("The child doesn't exist.")
    
    # This method will just rename the child but the new_name must respect the condition
    # that it cannot be only space or it cannot contain special caracter
    def rename(self, client, new_name):
        
        if client.is_super_admin:
            # Super admins can do anything
            pass
        elif client.is_admin:
            # Regular admins can only modify nodes within their site
            if self.get_site() != client.get_site():
                raise PermissionError("You do not have permission to modify this node.")
        else:
            if isinstance(self, Directory):
                # If the node is a directory, make sure the client is the owner
                if self.owner != client:
                    raise PermissionError("You do not have permission to rename this directory.")
            else:
                # If the node is not a directory, make sure it's in the client's directory
                if self.get_client() != client:
                    raise PermissionError("You do not have permission to rename this node.")
        
        if not new_name or new_name.isspace() or not new_name.isprintable():
            raise ValueError("Invalid name.")
        self.name = new_name
    
    # This method will move the a node to another parent, like for example, if we want to change
    # the path of a directory, we need to check if we the parent is a node of the instances that 
    # we want and check for any error and then we just change the parent by removing the curent
    # link that exist with the old parent
    def move(self, client, new_parent):
        
        if client.is_super_admin:
            # Super admins can do anything
            pass
        elif client.is_admin:
            # Regular admins can only modify nodes within their site
            if self.get_site() != client.get_site():
                raise PermissionError("You do not have permission to modify this node.")
        else:
            # Clients can only modify nodes within their own directory
            if self.get_client() != client:
                raise PermissionError("You do not have permission to modify this node.")
        
        # Check for protected node
        if self.protected and not (client.is_admin or client.is_super_admin):
            raise Exception("You do not have the necessary permissions to move this node.")
        
        # Check if new_parent is of the right type
        if not isinstance(new_parent, (Directory, Client, Site)):
            raise TypeError("New parent must be an instance of Directory or Client.")
            
        # Check if new_parent already has a child with the same name as self
        if self.name in new_parent.children:
            raise ValueError("New parent already has a child with this name.")
                
        # Remove self from current parent's children
        self.parent.delete_child(client, self.name)
                
        # Change parent and add self to new parent's children
        self.parent = new_parent
        new_parent.add_child(client, self)
    
    # This method will copy a node to another parent, it work like a basic copy. I use
    # the copy module to create a deep copy of the node that we want to copy, so in this 
    # case we will copy even the children of the node
    def copy(self, client, new_parent):
        
        if client.is_super_admin:
            # Super admins can do anything
            pass
        elif client.is_admin:
            # Regular admins can only modify nodes within their site
            if self.get_site() != client.get_site():
                raise PermissionError("You do not have permission to modify this node.")
        else:
            # Clients can only modify nodes within their own directory
            if self.get_client() != client:
                raise PermissionError("You do not have permission to modify this node.")
        
        # Check for protected node
        if self.protected and not (client.is_admin or client.is_super_admin):
            raise Exception("You do not have the necessary permissions to copy this node.")
        
        # Check if new_parent is of the right type
        if not isinstance(new_parent, (Directory, Client, Site)):
            raise TypeError("New parent must be an instance of Directory or Client.")
        
        # Check if new_parent already has a child with the same name as self
        if self.name in new_parent.children:
            raise ValueError("New parent already has a child with this name.")
            
        # Create a deep copy of self
        new_node = copy.deepcopy(self)
        new_node.parent = new_parent

        # Add the new_node to new_parent's children
        new_parent.add_child(client, new_node)
    
    # Give a specific permission to a client or group.
    def add_permission(self, client_or_group, permission_type):
        
        if client_or_group not in self.permissions:
            self.permissions[client_or_group] = set()

        self.permissions[client_or_group].add(permission_type)

    # Revoke a specific permission from a client or group.
    def remove_permission(self, client_or_group, permission_type):
        
        
        if client_or_group in self.permissions:
            self.permissions[client_or_group].discard(permission_type)

    # Check if the client has a specific type of permission on the node.
    def has_permission(self, client, permission_type):

        if client in self.permissions and permission_type in self.permissions[client]:
            return True

        # Check if any of the client's groups have the permission
        for group in client.groups:
            if group in self.permissions and permission_type in self.permissions[group]:
                return True

        return False



# This class define what a site is but for now we don't need any additionnal methods
class Site(Node):
    def __init__(self, name, parent=None, protected=False):
        super().__init__(name, parent, protected)

# This class define what a client is, we also need to start thinking about permission
# and since there is user, admin and super_admin (for the Paris admin) we need to define
# this here
class Client(Node):
    def __init__(self, name, parent=None, is_admin=False, is_super_admin=False, protected=False):
        super().__init__(name, parent, protected)
        self.is_admin = is_admin
        self.is_super_admin = is_super_admin
        self.groups = set()

# This class define what a directory is
class Directory(Node):
    def __init__(self, name, parent=None, owner=None, protected=False):
        super().__init__(name, parent, protected)
        self.owner = owner  # Owner is the client who created the directory

# This class define what a file is, in this case we add content, to eventually know what
# kind of data is stored in this node. (metadata)
class File(Node):
    def __init__(self, name, parent=None, content=None, owner=None, protected=False):
        super().__init__(name, parent, protected)
        self.content = content
        self.owner = owner



# This class will helps us to introduce the notion of group rights    
class Group:
    def __init__(self, name):
        self.name = name
        self.clients = set()

    def add_client(self, client):
        self.clients.add(client)

    def remove_client(self, client):
        self.clients.remove(client)

    def has_client(self, client):
        return client in self.clients
