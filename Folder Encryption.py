import os
from cryptography.fernet import Fernet

# generate a new key
key = Fernet.generate_key()

# write the key to a file for later use
with open('filekey.key', 'wb') as filekey:
    filekey.write(key)

# create a Fernet object using the generated key
fernet = Fernet(key)

# set the path of the directory to encrypt
directory_to_encrypt = r'D:\SEM-8\IBM Project\Review 3\files'

# loop through all the files in the directory
for filename in os.listdir(directory_to_encrypt):
    # set the path of the file to encrypt
    file_to_encrypt = os.path.join(directory_to_encrypt, filename)

    # open the file to encrypt
    with open(file_to_encrypt, 'rb') as file:
        original = file.read()

    # encrypt the file
    encrypted = fernet.encrypt(original)

    # write the encrypted data to the same file
    with open(file_to_encrypt, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

print("Encryption complete!")