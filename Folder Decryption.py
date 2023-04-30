import os
from cryptography.fernet import Fernet

# read the key from the file
with open('filekey.key', 'rb') as filekey:
    key = filekey.read()

# create a Fernet object using the key
fernet = Fernet(key)

# set the path of the directory to decrypt
directory_to_decrypt = r'D:\SEM-8\IBM Project\Review 3\files'

# loop through all the files in the directory
for filename in os.listdir(directory_to_decrypt):
    # set the path of the file to decrypt
    file_to_decrypt = os.path.join(directory_to_decrypt, filename)

    # open the encrypted file
    with open(file_to_decrypt, 'rb') as enc_file:
        encrypted = enc_file.read()

    # decrypt the file
    decrypted = fernet.decrypt(encrypted)

    # write the decrypted data to the same file
    with open(file_to_decrypt, 'wb') as dec_file:
        dec_file.write(decrypted)

print("Decryption complete!")
