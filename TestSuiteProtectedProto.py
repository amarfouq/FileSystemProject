# -*- coding: utf-8 -*-
"""
Created on Fri May 19 12:19:58 2023

@author: Ayman
"""
from ClassesDef import Site, Client, Directory, File
import unittest

class TestFileSystem(unittest.TestCase):
    def setUp(self):
        # Setup runs before each test case
        self.paris = Site('Paris')
        self.rennes = Site('Rennes')
        self.paris_admin = Client('ParisAdmin', self.paris, is_admin=True, is_super_admin=True)
        self.rennes_admin = Client('RennesAdmin', self.rennes, is_admin=True, is_super_admin=False)
        self.paris_client = Client('ParisClient', self.paris, is_admin=False)
        self.rennes_client = Client('RennesClient', self.rennes, is_admin=False)
        self.protected_directory = Directory('ProtectedDir', self.paris_admin, owner=self.paris_admin, protected=True)

    def test_admin_delete_protected(self):
        # Test if a regular admin cannot delete a protected directory outside of their site
        self.paris.add_child(self.paris_admin, self.protected_directory)
        with self.assertRaises(Exception):
            self.paris.delete_child(self.rennes_admin, self.protected_directory.name)

    def test_superadmin_delete_protected(self):
        # Test if a super admin can delete a protected directory
        self.paris.add_child(self.paris_admin, self.protected_directory)
        try:
            self.paris.delete_child(self.paris_admin, self.protected_directory.name)
        except:
            self.fail("delete_child() raised Exception unexpectedly for super admin!")

    def test_client_delete_protected(self):
        # Test if a client cannot delete a protected directory
        self.paris.add_child(self.paris_admin, self.protected_directory)
        with self.assertRaises(Exception):
            self.paris.delete_child(self.paris_client, self.protected_directory.name)
            
    def test_move_protected(self):
        # Test if a client cannot move a protected directory
        self.paris.add_child(self.paris_admin, self.protected_directory)
        with self.assertRaises(Exception):
            self.protected_directory.move(self.paris_client, self.rennes)
    
    def test_copy_protected(self):
        # Test if a client cannot copy a protected directory
        self.paris.add_child(self.paris_admin, self.protected_directory)
        with self.assertRaises(Exception):
            self.protected_directory.copy(self.paris_client, self.rennes)
            
    def test_superadmin_move_protected_between_sites(self):
        # Test if a super admin can move a protected directory between sites
        self.paris.add_child(self.paris_admin, self.protected_directory)
        try:
            self.protected_directory.move(self.paris_admin, self.rennes)  # moving to another site
        except:
            self.fail("move() raised Exception unexpectedly for super admin!")
    
    def test_admin_move_protected_within_site(self):
        # Test if a regular admin can move a protected directory within their site
        rennes_protected_directory = Directory('RennesProtectedDir', self.rennes_admin, owner=self.rennes_admin, protected=True)
        self.rennes.add_child(self.rennes_admin, rennes_protected_directory)
        rennes_client_2 = Client('RennesClient2', self.rennes, is_admin=False)  # Create another client in Rennes site
        try:
            rennes_protected_directory.move(self.rennes_admin, rennes_client_2)  # moving within the same site
        except:
            self.fail("move() raised Exception unexpectedly for admin!")
            
    def test_move_file(self):
        # Test if a client can move a non-protected file they own
        my_file = File('MyFile', self.paris_client, owner=self.paris_client)
        self.paris_client.add_child(self.paris_client, my_file)
        with self.assertRaises(Exception):
            my_file.move(self.paris_client, self.rennes_client)
            
    def test_move_protected_file(self):
        # Test if a client cannot move a protected file they don't own
        protected_file = File('ProtectedFile', self.paris_admin, owner=self.paris_admin, protected=True)
        self.paris.add_child(self.paris_admin, protected_file)
        with self.assertRaises(Exception):
            protected_file.move(self.paris_client, self.rennes_client)
            
    def test_rename_file(self):
        # Test if a client cannot rename a file they don't own
        another_file = File('AnotherFile', self.paris_admin, owner=self.paris_admin)
        self.paris.add_child(self.paris_admin, another_file)
        with self.assertRaises(Exception):
            another_file.rename(self.paris_client, 'NewName')
            
    def test_move_file_within_client_directory(self):
        # Test if a client can move a non-protected file they own within their directory
        my_file = File('MyFile', self.paris_client, owner=self.paris_client)
        self.paris_client.add_child(self.paris_client, my_file)

        archive_directory = Directory('Archive', self.paris_client, owner=self.paris_client)
        self.paris_client.add_child(self.paris_client, archive_directory)

        try:
            my_file.move(self.paris_client, archive_directory)
        except:
            self.fail("move() raised Exception unexpectedly for client!")

if __name__ == '__main__':
    unittest.main()

