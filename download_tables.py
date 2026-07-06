# Version: 2026-07-06T01:26:50+08:00
# Description: Download CSV.gz files from the CORRECT path (/data/tables/) of the original benchmark site, decompress them, and save them.

import gzip
import os
import urllib.request

CSV_FILES = [
    "Customer.csv",
    "Date.csv",
    "Product.csv",
    "Reseller.csv",
    "Sales.csv",
    "Sales_Order.csv",
    "Sales_Territory.csv"
]

BASE_URL = "https://sql-benchmark.nicklothian.com/data/tables/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def download_and_decompress():
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tables")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")

    for filename in CSV_FILES:
        gz_filename = filename + ".gz"
        url = BASE_URL + gz_filename
        temp_gz_path = os.path.join(target_dir, gz_filename)
        dest_csv_path = os.path.join(target_dir, filename)

        print(f"Downloading {url} -> {temp_gz_path}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req) as response:
                with open(temp_gz_path, "wb") as f:
                    f.write(response.read())
            print(f"Decompressing {temp_gz_path} -> {dest_csv_path}...")
            with gzip.open(temp_gz_path, "rb") as f_in:
                with open(dest_csv_path, "wb") as f_out:
                    f_out.write(f_in.read())
            print(f"Successfully created {filename}")

            # Clean up the temp .gz file
            os.remove(temp_gz_path)
        except Exception as e:
            print(f"Failed to download/decompress {filename}: {e}")

if __name__ == "__main__":
    download_and_decompress()
