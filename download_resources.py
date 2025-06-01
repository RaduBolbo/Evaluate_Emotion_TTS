import requests
import zipfile
import os
import shutil

def download_and_extract_flat_data(shared_url, output_zip="data.zip", target_dir="data"):
    # Extract file ID
    file_id = shared_url.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    print(f"📥 Downloading from: {download_url}")
    response = requests.get(download_url, stream=True)
    with open(output_zip, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Downloaded: {output_zip}")

    # Temporary extract path
    temp_dir = "__temp_extract__"
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(output_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Look for nested data/data/ structure
    nested_path = os.path.join(temp_dir, "data", "data")
    if not os.path.isdir(nested_path):
        raise FileNotFoundError("❌ Nested 'data/data/' folder not found in archive.")

    # Clean existing target_dir if needed
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    # Move the inner 'data' up to target_dir
    shutil.move(nested_path, target_dir)
    print(f"✅ Flattened and moved to: ./{target_dir}")

    # Cleanup
    shutil.rmtree(temp_dir)
    os.remove(output_zip)
    print("🧹 Cleaned up temporary files and folders.")

if __name__ == "__main__":
    zip_link = "https://drive.google.com/file/d/122cg35TezdCC_-wAhVTT6rK7FvnXKMZ0/view?usp=sharing"
    download_and_extract_flat_data(zip_link)
