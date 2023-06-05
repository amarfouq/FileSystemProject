# -*- coding: utf-8 -*-
"""
Created on Sun May 28 15:26:21 2023

@author: Ayman
"""

class FTPServer:
    def __init__(self, file_system):
        self.file_system = file_system

    def archive_files(self, site_name, files):
        archive_dir = f"/{site_name}/archive"  # Define the archive directory path in your file system

        for file_path in files:
            file_name = self.get_file_name(file_path)  # Extract the file name from the file path
            version = self.get_file_version(file_path)  # Extract the file version from the file path

            # Create the archive file path using the site name, file name, and version
            archive_file_path = f"{archive_dir}/{file_name}_v{version}"

            # Copy the file to the archive directory in your file system
            self.file_system.copy_object(file_path, archive_file_path)

    def get_file_name(self, file_path):
        # Implement your logic to extract the file name from the file path
        pass

    def get_file_version(self, file_path):
        # Implement your logic to extract the file version from the file path
        pass
