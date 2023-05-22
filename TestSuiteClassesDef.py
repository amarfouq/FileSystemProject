# -*- coding: utf-8 -*-
"""
Created on Thu May 18 13:02:58 2023

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
        
    def test_add_child(self):
        # test adding a child
        self.paris.add_child(self.paris_admin, self.paris_client)
        self.assertEqual(self.paris.children[self.paris_client.name], self.paris_client)
    
    def test_delete_child(self):
        # test deleting a child
        self.paris.add_child(self.paris_admin, self.paris_client)
        self.paris.delete_child(self.paris_admin, self.paris_client.name)
        self.assertNotIn(self.paris_client.name, self.paris.children)
        
    def test_rename(self):
        # test renaming a node
        self.paris.rename(self.paris_admin, "NewParis")
        self.assertEqual(self.paris.name, "NewParis")
        
    def test_move(self):
        # test moving a client
        self.paris.add_child(self.paris_admin, self.paris_client)
        self.paris_client.move(self.paris_admin, self.rennes)
        self.assertNotIn(self.paris_client.name, self.paris.children)
        self.assertIn(self.paris_client.name, self.rennes.children)
        
    def test_copy(self):
        # test copying a node
        self.paris.add_child(self.paris_admin, self.paris_client)
        self.paris_client.copy(self.paris_admin, self.rennes)
        self.assertIn(self.paris_client.name, self.paris.children)
        self.assertIn(self.paris_client.name, self.rennes.children)
        self.assertIsNot(self.paris_client, self.rennes.children[self.paris_client.name])
        
    def test_admin(self):
        # test the admin attribute
        self.assertTrue(self.paris_admin.is_admin)
        self.assertTrue(self.paris_admin.is_super_admin)
        self.assertFalse(self.paris_client.is_admin)
        self.assertFalse(self.paris_client.is_super_admin)

    def test_file(self):
        # test the content attribute of a file
        file = File("TestFile", self.paris_admin, "Test content", owner=self.paris_admin)
        self.assertEqual(file.content, "Test content")

if __name__ == '__main__':
    unittest.main()
