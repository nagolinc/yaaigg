import os
import glob

# Path to the user_data.json file
user_data_path = 'user_data.json'

# Path to the static/samples directory
samples_dir = 'static/samples/*'

# Delete user_data.json if it exists
if os.path.exists(user_data_path):
    os.remove(user_data_path)
    print(f"Deleted {user_data_path}")
else:
    print(f"{user_data_path} does not exist")

# Delete all files in the static/samples directory
files = glob.glob(samples_dir)
for file in files:
    if os.path.isfile(file):
        os.remove(file)
        #print(f"Deleted {file}")
    else:
        print(f"{file} is not a file")