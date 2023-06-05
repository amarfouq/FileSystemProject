# -*- coding: utf-8 -*-
"""
Created on Thu May 25 12:12:48 2023

@author: Ayman
"""
import unittest
from NewClassesDef import Root, Site, Client, Directory, File
from CommandParser import CommandParser

class CommandParserTest(unittest.TestCase):
    def setUp(self):
        # Create the root directory
        self.root_dir = Root("Root")

        # Create the super admin
        self.super_admin = Client("SuperAdmin", parent=self.root_dir, is_super_admin=True)
        self.root_dir.add_child(self.super_admin, self.super_admin)

        # Create the Paris site
        self.paris_site = Site("Paris", parent=self.root_dir)
        self.root_dir.add_child(self.super_admin, self.paris_site)

        # Create the Rennes site
        self.rennes_site = Site("Rennes", parent=self.root_dir)
        self.root_dir.add_child(self.super_admin, self.rennes_site)

        # Create the Paris admin
        self.paris_admin = Client("ParisAdmin", parent=self.paris_site, is_admin=True)
        self.paris_site.add_child(self.paris_admin, self.paris_admin)

        # Create the Rennes admin
        self.rennes_admin = Client("RennesAdmin", parent=self.rennes_site, is_admin=True)
        self.rennes_site.add_child(self.rennes_admin, self.rennes_admin)

        # Create some clients in Paris
        self.paris_client1 = Client("ParisClient1", parent=self.paris_site)
        self.paris_site.add_child(self.paris_admin, self.paris_client1)

        self.paris_client2 = Client("ParisClient2", parent=self.paris_site)
        self.paris_site.add_child(self.paris_admin, self.paris_client2)

        # Create some clients in Rennes
        self.rennes_client1 = Client("RennesClient1", parent=self.rennes_site)
        self.rennes_site.add_child(self.rennes_admin, self.rennes_client1)

        self.rennes_client2 = Client("RennesClient2", parent=self.rennes_site)
        self.rennes_site.add_child(self.rennes_admin, self.rennes_client2)

        # Create some random files
        self.file1 = File("File1", parent=self.root_dir)
        self.root_dir.add_child(self.super_admin, self.file1)

        self.file2 = File("File2", parent=self.paris_site)
        self.paris_site.add_child(self.paris_admin, self.file2)

        self.file3 = File("File3", parent=self.paris_admin)
        self.paris_admin.add_child(self.paris_admin, self.file3)

        # Create the command parser
        self.parser = CommandParser(self.root_dir)


    def test_mkdir(self):
        # Sign in with the super_admin to create a directory in the root directory
        self.parser.current_client = self.super_admin
        self.parser.parse_command("mkdir superadminstuff")
        new_directory = self.parser.current_directory.find_object("superadminstuff")
        self.assertIsInstance(new_directory, Directory)

        # Sign in with the Paris admin to create a directory in the Paris site directory
        self.parser.current_client = self.paris_admin
        self.parser.parse_command("cd Paris")
        self.parser.parse_command("mkdir adminstuff")
        new_directory = self.parser.current_directory.find_object("adminstuff")
        self.assertIsInstance(new_directory, Directory)

        # Sign in with a client in Paris to create a directory in their own directory
        self.paris_client1.add_permission(self.paris_client1, 'add_child')
        self.parser.current_client = self.paris_client1
        self.parser.parse_command("cd ParisClient1")
        self.parser.parse_command("mkdir clientstuff")
        new_directory = self.parser.current_directory.find_object("clientstuff")
        self.assertIsInstance(new_directory, Directory)

        # Reset the current_client for the next test
        self.parser.current_client = None


    def test_touch(self):
        # Sign in with the super_admin to create a file in the root directory
        self.parser.current_client = self.super_admin
        self.parser.parse_command("touch superadminfile.txt")
        new_file = self.parser.current_directory.find_object("superadminfile.txt")
        self.assertIsInstance(new_file, File)
        
        # Sign in with the Paris admin to create a file in the Paris site directory
        self.parser.current_client = self.paris_admin
        self.parser.parse_command("cd Paris")
        self.parser.parse_command("touch adminfile.txt")
        new_file = self.parser.current_directory.find_object("adminfile.txt")
        self.assertIsInstance(new_file, File)
        
        # Sign in with a client in Paris to create a file in their own directory
        self.paris_client1.add_permission(self.paris_client1, 'add_child')
        self.parser.current_client = self.paris_client1
        self.parser.parse_command("cd ParisClient1")
        self.parser.parse_command("touch clientfile.txt")
        new_file = self.parser.current_directory.find_object("clientfile.txt")
        self.assertIsInstance(new_file, File)
        
        # Reset the current_client for the next test
        self.parser.current_client = None

    def test_ls(self):
        # Test listing contents of the root directory
        output = self.parser.parse_command("ls")

        # Test listing contents of the Paris site
        output = self.parser.parse_command("ls Paris")
        
        # Test listing contents of the ParisClient1 site
        output = self.parser.parse_command("ls Paris/ParisClient1")

    def test_cd(self):
        # Test changing to the Paris site
        self.parser.parse_command("cd Paris")
        self.assertEqual(self.parser.current_directory, self.paris_site)

        # Test changing to the root directory
        self.parser.parse_command("cd ..")
        self.assertEqual(self.parser.current_directory, self.root_dir)
        
        # Test changing using a path
        self.parser.parse_command("cd Paris/ParisClient1")
        self.assertEqual(self.parser.current_directory, self.paris_client1)

    def test_mv(self):
        # Sign in with the client and create a directory in their own directory
        self.parser.current_client = self.rennes_client1
        self.parser.parse_command("cd Rennes/RennesClient1")
        self.parser.parse_command("mkdir clientdir")
        
        # Create a file in the client directory
        self.parser.parse_command("touch myfiletomove.txt")
        
        # Move the file to the new directory within the client directory
        self.parser.parse_command("mv myfiletomove.txt clientdir")
        
        # Sign in with the admin and move the file within the same site
        self.parser.current_client = self.rennes_admin
        self.parser.parse_command("cd ..")
        self.parser.parse_command("mkdir admindir")
        self.parser.parse_command("mv RennesClient1/clientdir/myfiletomove.txt admindir")
        
        # Sign in with the super_admin and create a special directory in the root directory
        self.parser.current_client = self.super_admin
        self.parser.parse_command("cd /")
        self.parser.parse_command("mkdir specialdir")
        
        # Move the file from the admin directory to the special directory
        self.parser.parse_command("mv Rennes/admindir/myfiletomove.txt specialdir")
        
        # Reset the current_client for the next test
        self.parser.current_client = None

    def test_cp(self):
        # Sign in with the client and create a directory in their own directory
        self.parser.current_client = self.rennes_client1
        self.parser.parse_command("cd Rennes/RennesClient1")
        self.parser.parse_command("mkdir clientdir")
        
        # Create a file in the client directory
        self.parser.parse_command("touch myfiletocopy.txt")
        
        self.parser.parse_command("ls")
        
        # Copy the file to a new directory within the client directory
        self.parser.parse_command("cp myfiletocopy.txt clientdir newfile.txt")
        
        # Sign in with the admin and copy the file within the same site
        self.parser.current_client = self.rennes_admin
        self.parser.parse_command("cd ..")
        self.parser.parse_command("mkdir admindir")
        self.parser.parse_command("cp RennesClient1/clientdir/newfile.txt admindir")
        
        # Sign in with the super_admin and create a special directory in the root directory
        self.parser.current_client = self.super_admin
        self.parser.parse_command("cd /")
        self.parser.parse_command("mkdir specialdir")
        
        # Copy the file from the admin directory to the special directory
        self.parser.parse_command("cp /Rennes/admindir/newfile.txt specialdir")
        
        # Reset the current_client for the next test
        self.parser.current_client = None

    def test_rm(self):
        # Sign in with the client and create a directory and file in their own directory
        self.parser.current_client = self.rennes_client1
        self.parser.parse_command("cd Rennes/RennesClient1")
        self.parser.parse_command("mkdir clientdir")
        self.parser.parse_command("touch myfile.txt")
        
        # Remove the file using relative path
        self.parser.parse_command("rm myfile.txt")
        removed_file = self.parser.current_directory.find_object("myfile.txt")
        self.assertIsNone(removed_file)
        
        # Sign in with the admin and create a directory and file in their own directory
        self.parser.current_client = self.rennes_admin
        self.parser.parse_command("cd /Rennes/RennesAdmin")
        self.parser.parse_command("mkdir admindir")
        self.parser.parse_command("touch adminfile.txt")
        
        # Remove the directory using relative path
        self.parser.parse_command("rm admindir")
        removed_dir = self.parser.current_directory.find_object("admindir")
        self.assertIsNone(removed_dir)
        
        # Sign in with the super_admin and create a directory and file in the root directory
        self.parser.current_client = self.super_admin
        self.parser.parse_command("cd /")
        self.parser.parse_command("mkdir rootdir")
        self.parser.parse_command("touch rootfile.txt")
        
        # Remove the file using absolute path
        self.parser.parse_command("rm /rootfile.txt")
        removed_file = self.parser.current_directory.find_object("rootfile.txt")
        self.assertIsNone(removed_file)
        
        # Reset the current_client for the next test
        self.parser.current_client = None
        
    def test_info(self):
        # Sign in with the client and create a file and directory in their own directory
        self.parser.current_client = self.rennes_client1
        self.parser.parse_command("cd Rennes/RennesClient1")
        self.parser.parse_command("touch myfile.txt")
        self.parser.parse_command("mkdir mydir")
        
        # Get info for the file
        self.parser.parse_command("info myfile.txt")
        
        # Get info for the directory
        self.parser.parse_command("info mydir")
        
        # Sign in with the admin and create a file and directory in their own directory
        self.parser.current_client = self.rennes_admin
        self.parser.parse_command("cd /Rennes/RennesAdmin")
        self.parser.parse_command("touch adminfile.txt")
        self.parser.parse_command("mkdir admindir")
        
        # Get info for the file
        self.parser.parse_command("info adminfile.txt")
        
        # Get info for the directory
        self.parser.parse_command("info admindir")
        
        # Sign in with the super_admin and create a file and directory in the root directory
        self.parser.current_client = self.super_admin
        self.parser.parse_command("cd /")
        self.parser.parse_command("touch rootfile.txt")
        self.parser.parse_command("mkdir rootdir")
        
        # Get info for the file
        self.parser.parse_command("info rootfile.txt")
        
        # Get info for the directory
        self.parser.parse_command("info rootdir")
        
        # Reset the current_client for the next test
        self.parser.current_client = None

    def test_chmod(self):
        # Sign in with the client and create a file in their own directory
        self.parser.current_client = self.rennes_client1
        self.parser.parse_command("cd Rennes/RennesClient1")
        self.parser.parse_command("touch myfile.txt")
        
        # Give permission to another client to copy the file
        self.parser.parse_command("chmod myfile.txt copy /Paris/ParisClient1")
        self.parser.parse_command("chmod myfile.txt -copy /Paris/ParisClient1")
        self.parser.parse_command("chmod myfile.txt copy /Paris/ParisClient1")
        
        # Sign in with the admin and give permission to another admin to move a directory
        self.parser.current_client = self.paris_admin
        self.parser.parse_command("cd /Paris")
        self.parser.parse_command("mkdir Compta")
        self.parser.parse_command("ls")
        
        self.parser.parse_command("chmod Compta move /Rennes/RennesAdmin")
        
        # Reset the current_client for the next test
        self.parser.current_client = None
        
        # Verify that ParisClient1 can copy the file
        self.parser.current_client = self.paris_client1
        self.parser.parse_command("cd /Paris/ParisClient1")
        self.parser.parse_command("cp /Rennes/RennesClient1/myfile.txt /Paris/ParisClient1 newfile.txt")
        new_file = self.parser.current_directory.find_object("newfile.txt")
        self.assertIsInstance(new_file, File)
    
        # Verify that RennesAdmin can move the Compta directory
        self.parser.current_client = self.rennes_admin
        self.parser.parse_command("cd /Rennes")
        self.parser.parse_command("mv /Paris/Compta /Rennes")
        moved_dir = self.parser.current_directory.find_object("Compta")
        self.assertIsNotNone(moved_dir)

if __name__ == "__main__":
    unittest.main()