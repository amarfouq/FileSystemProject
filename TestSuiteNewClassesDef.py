# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:33:28 2023

@author: Ayman
"""

import unittest
from NewClassesDef import Site, Client, Directory, File, Group, Root

class TestFileSystem(unittest.TestCase):
    def setUp(self):
        # Create the Root
        self.root = Root('root')
        
        # Create the site
        self.paris = Site('Paris')
        self.rennes = Site('Rennes')

        # Create the super admin
        self.super_admin = Client('SuperAdmin', parent=self.paris, is_admin=True, is_super_admin=True)
        self.paris.add_child(self.super_admin, self.super_admin)
        
        # Add the site to the root children dir
        self.root.add_child(self.super_admin, self.paris)
        self.root.add_child(self.super_admin, self.rennes)
        
        # Create the admin and client for Paris
        self.paris_admin = Client('ParisAdmin', parent=self.paris, is_admin=True)
        self.paris.add_child(self.paris_admin, self.paris_admin)
        self.paris_client = Client('ParisClient', parent=self.paris)
        self.paris.add_child(self.paris_admin, self.paris_client)

        # Create the admin and client for Rennes
        self.rennes_admin = Client('RennesAdmin', parent=self.rennes, is_admin=True)
        self.rennes.add_child(self.rennes_admin, self.rennes_admin)
        self.rennes_client = Client('RennesClient', parent=self.rennes)
        self.rennes.add_child(self.rennes_admin, self.rennes_client)

        # Create directories and files
        self.paris_dir = Directory('ParisDir', parent=self.paris, owner=self.paris_admin)
        self.paris.add_child(self.paris_admin, self.paris_dir)
        self.protec_dir = Directory('ProtectedDir', parent=self.paris_dir, owner=self.paris_admin, protected=True)
        self.paris_dir.add_child(self.paris_admin, self.protec_dir)
        self.rennes_dir = Directory('RennesDir', parent=self.rennes, owner=self.rennes_admin)
        self.rennes.add_child(self.rennes_admin, self.rennes_dir)
        self.paris_file = File('ParisFile', parent=self.paris_dir, owner=self.paris_admin)
        self.paris_dir.add_child(self.paris_admin, self.paris_file)
        self.rennes_file = File('RennesFile', parent=self.rennes_dir, owner=self.rennes_admin)
        self.rennes_dir.add_child(self.rennes_admin, self.rennes_file)

    def test_add_child(self):
        # Create a new client and directory for testing
        client = Client('NewClient', parent=self.paris)
        directory = Directory('NewDirectory', parent=self.paris_dir)
        directory2 = Directory('NewDirectory2', parent=self.paris_dir)
        
        # Test adding a child with the necessary permission
        self.assertIsNone(self.paris_dir.add_child(self.paris_admin, directory))
    
        # Test adding a child without the necessary permission
        self.assertRaises(PermissionError, self.paris_dir.add_child, client, directory)
        
        # Test adding a child without the necessary permission as a super admin
        self.assertIsNone(self.paris_dir.add_child(self.super_admin, directory2))


    def test_delete_child(self):
        # Test deleting a child without permission
        with self.assertRaises(PermissionError):
            self.assertFalse(self.paris_dir.delete_child(self.paris_client, 'ParisFile'))

        # Test deleting a child with permission
        self.assertIsNone(self.paris_dir.delete_child(self.paris_admin, 'ParisFile'))
        self.assertNotIn('ParisFile', self.paris_dir.children)

        # Test deleting a protected child
        with self.assertRaises(PermissionError):
            self.assertFalse(self.paris_dir.delete_child(self.paris_admin, 'ProtectedDir'))

        # Test deleting a child as an admin within their site
        self.assertIsNone(self.paris.delete_child(self.paris_admin, 'ParisDir'))
        self.assertNotIn('ParisDir', self.paris.children)

        # Test deleting a child as a super admin
        self.assertIsNone(self.rennes.delete_child(self.super_admin, 'RennesDir'))
        self.assertNotIn('RennesDir', self.rennes.children)

    def test_rename(self):
        # Test renaming a file without permission
        with self.assertRaises(PermissionError):
            self.paris_file.rename(self.paris_client, 'NewParisFile')

        # Test renaming a file with permission
        self.assertIsNone(self.paris_file.rename(self.paris_admin, 'NewParisFile'))
        self.assertEqual(self.paris_file.name, 'NewParisFile')
        
        # Test renaming a directory without permission
        with self.assertRaises(PermissionError):
            self.paris_dir.rename(self.paris_client, 'NewParisDir')
            
        # Test renaming a directory with permission
        self.assertIsNone(self.paris_dir.rename(self.paris_admin, 'NewParisDir'))
        self.assertEqual(self.paris_dir.name, 'NewParisDir')
            
        # Test renaming a directory as an admin within their site
        self.assertIsNone(self.paris.rename(self.paris_admin, 'NewParisSite'))
        self.assertEqual(self.paris.name, 'NewParisSite')
            
        # Test renaming a directory as a super admin
        self.assertIsNone(self.rennes.rename(self.super_admin, 'NewRennesSite'))
        self.assertEqual(self.rennes.name, 'NewRennesSite')

    def test_move(self):
        # Test moving a file without permission
        #with self.assertRaises(PermissionError):
            #self.paris_file.move(self.paris_admin, self.rennes_dir)

        # Test moving a file within the same directory
        self.assertIsNone(self.paris_file.move(self.paris_admin, self.paris_dir))
        self.assertIn(self.paris_file.name, self.paris_dir.children)

        # Test moving a file to a different directory within the same site
        self.assertIsNone(self.paris_file.move(self.paris_admin, self.protec_dir))
        self.assertIn(self.paris_file.name, self.protec_dir.children)

        # Test moving a file to a different site
        #with self.assertRaises(PermissionError):
            #self.paris_file.move(self.paris_admin, self.rennes_dir)

        # Create a new file within the same site
        new_file = File('NewFile', owner=self.paris_admin)
        self.paris_dir.add_child(self.paris_admin, new_file)
        self.assertIsNone(new_file.move(self.paris_admin, self.paris))

        # Test moving the new file within the same site
        self.assertIsNone(new_file.move(self.paris_admin, self.protec_dir))
        self.assertIn(new_file.name, self.protec_dir.children)

    def test_copy(self):
        # Create a new directory and file within the same site
        admin_directory = Directory('AdminDir', owner=self.paris_admin)
        self.paris.add_child(self.paris_admin, admin_directory)
        admin_file = File('AdminFile', owner=self.paris_admin)
        admin_directory.add_child(self.paris_admin, admin_file)

        # Test copying a file without permission, with the updated version this should not raise an error
        #with self.assertRaises(PermissionError):
            #admin_file.copy(self.paris_admin, self.rennes_dir)

        # Test copying a file with permission within the same site
        self.assertIsNone(admin_file.copy(self.paris_admin, admin_directory, new_name='AdminDir2'))
        self.assertIn(admin_file.name, admin_directory.children)

        # Test copying a file with permission to a different site
        #with self.assertRaises(PermissionError):
            #admin_file.copy(self.paris_admin, self.rennes_dir)

        # Test copying a directory without permission
        #with self.assertRaises(PermissionError):
            #admin_directory.copy(self.paris_admin, self.rennes_dir)

        # Test copying a directory with permission within the same site
        self.assertIsNone(admin_directory.copy(self.paris_admin, self.paris_dir))
        self.assertIn(admin_directory.name, self.paris_dir.children)

        # Test copying a directory with permission to a different site
        #with self.assertRaises(PermissionError):
            #admin_directory.copy(self.paris_admin, self.rennes_dir)

        # Test copying a directory as a super admin
        self.assertIsNone(self.rennes.copy(self.super_admin, self.paris))
        self.assertIn(self.rennes.name, self.paris.children)

    def test_permission(self):
        # Create a new file and client for testing
        test_file = File('TestFile', parent=self.paris_dir, owner=self.paris_admin)
        test_client = Client('TestClient', parent=self.paris)

        # Test moving a file with permission
        self.assertIsNone(test_file.move(self.paris_admin, self.paris_dir))
        self.assertIn(test_file.name, self.paris_dir.children)

        # Test moving a file without permission
        with self.assertRaises(PermissionError):
            test_file.move(test_client, self.paris_dir)

        # Test renaming a file with permission
        self.assertIsNone(test_file.rename(self.paris_admin, 'NewName'))
        self.assertEqual(test_file.name, 'NewName')

        # Test renaming a file without permission
        with self.assertRaises(PermissionError):
            test_file.rename(test_client, 'NewName')

        # Test copying a file with permission
        test_file.copy(self.paris_admin, self.paris_dir, new_name='new_file')
        new_file = self.paris.find_object('new_file')
        self.assertIsNotNone(new_file)
        self.assertIn(new_file.name, self.paris_dir.children)

        # Test copying a file without permission
        with self.assertRaises(PermissionError):
            test_file.copy(test_client, self.paris_dir)


    def test_protected_file(self):
        pass
    def test_admin_scope(self):
        pass

    def test_super_admin_scope(self):
        pass

    def test_group_permissions(self):
        # Create clients
        client1 = Client('Client1', parent=self.paris)
        client2 = Client('Client2', parent=self.paris)
        client3 = Client('Client3', parent=self.paris)
    
        # Create files
        file1 = File('File1', parent=self.paris_dir, owner=self.paris_admin)
        file2 = File('File2', parent=self.paris_dir, owner=self.paris_admin)
        file3 = File('File3', parent=self.paris_dir, owner=self.paris_admin)
    
        # Create groups
        group1 = Group('Group1')
        group2 = Group('Group2')
    
        # Add clients to groups
        group1.add_client(client1)
        group1.add_client(client2)
        group2.add_client(client3)
    
        # Assign permissions to groups
        file1.add_permission(group1, 'move')
        file2.add_permission(group2, 'rename')
    
        # Test permissions for clients in groups
        self.assertTrue(file1.has_permission(client1, 'move'))
        self.assertTrue(file1.has_permission(client2, 'move'))
        self.assertFalse(file1.has_permission(client3, 'move'))
        self.assertTrue(file2.has_permission(client3, 'rename'))
        self.assertFalse(file2.has_permission(client1, 'rename'))
        self.assertFalse(file2.has_permission(client2, 'rename'))
        self.assertFalse(file3.has_permission(client1, 'move'))
        self.assertFalse(file3.has_permission(client2, 'move'))
        self.assertFalse(file3.has_permission(client3, 'move'))

if __name__ == '__main__':
    unittest.main()
