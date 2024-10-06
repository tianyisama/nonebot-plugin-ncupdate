import zipfile
import shutil
import os

# 1.x版本的解压方式
async def unzip_v1(zip_file_path, base_path, topfolder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            try:
                relative_path = member.partition('/')[2]
                if relative_path:
                    new_path = os.path.join(base_path, topfolder, relative_path)
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    with zip_ref.open(member, 'r') as source, open(new_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
            except zipfile.BadZipFile:
                continue
            except OSError:
                continue
# 2.x版本的解压方式
async def unzip_v2(zip_file_path, base_path, topfolder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            try:
                relative_path = member if member.endswith('/') else member
                if relative_path:
                    new_path = os.path.join(base_path, topfolder, relative_path)
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    if not member.endswith('/'):
                        with zip_ref.open(member, 'r') as source, open(new_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
            except zipfile.BadZipFile:
                continue
            except OSError:
                continue