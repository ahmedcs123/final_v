import requests
import os

url = "https://images.unsplash.com/photo-1520038814766-02d556396341?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
save_path = r"c:\Users\Ahmed Abo-Essa\OneDrive\Desktop\F\app\static\img\hero-products.jpg"

os.makedirs(os.path.dirname(save_path), exist_ok=True)

try:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
    print("Image downloaded successfully to", save_path)
except Exception as e:
    print(f"Failed to download image: {e}")
