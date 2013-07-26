import os
import re
import zipfile

current_path = os.path.dirname(os.path.abspath(__file__))

out_zip_name = os.path.join(current_path, 
                            os.path.basename(current_path) + ".esriaddin")

BACKUP_FILE_PATTERN = re.compile(".*_addin_[0-9]+[.]py$", re.IGNORECASE)

def looks_like_a_backup(filename):
    return bool(BACKUP_FILE_PATTERN.match(filename))

zip_file = zipfile.ZipFile(out_zip_name, 'w')
for filename in ('config.xml', 'README.md', 'makeaddin.py'):
    zip_file.write(os.path.join(current_path, filename), filename)
dirs_to_add = ['Images', 'Install']
for directory in dirs_to_add:
    for (path, dirs, files) in os.walk(os.path.join(current_path, directory)):
        archive_path = os.path.relpath(path, current_path)
        found_file = False
        for file in (f for f in files if not looks_like_a_backup(f)):
            archive_file = os.path.join(archive_path, file)
            print archive_file
            zip_file.write(os.path.join(path, file), archive_file)
            found_file = True
        if not found_file:
            zip_file.writestr(os.path.join(archive_path, 'placeholder.txt'), 
                              "(Empty directory)")
zip_file.close()
