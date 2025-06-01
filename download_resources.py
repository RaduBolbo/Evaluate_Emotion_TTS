import requests
import zipfile
import os
import shutil

def download_and_extract_flat_data(shared_url, output_zip="data.zip", target_dir="data"):
    file_id = shared_url.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    print(f"📥 Downloading from: {download_url}")
    response = requests.get(download_url, stream=True)
    with open(output_zip, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Downloaded: {output_zip}")

    temp_dir = "__temp_extract__"
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(output_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    #nested_path = os.path.join(temp_dir, "data", "data")
    nested_path = os.path.join(temp_dir, "data")
    if not os.path.isdir(nested_path):
        raise FileNotFoundError("❌ Nested 'data/data/' folder not found in archive.")

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    shutil.move(nested_path, target_dir)
    print(f"✅ Flattened and moved to: ./{target_dir}")

    shutil.rmtree(temp_dir)
    os.remove(output_zip)
    print("🧹 Cleaned up temporary files and folders.")

if __name__ == "__main__":
    zip_link = "https://drive.google.com/file/d/14rccGeMWVnuudF7UjZHa7lYcwrr8dl3c/view?usp=sharing"
    download_and_extract_flat_data(zip_link)
