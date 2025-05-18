#scan directory deep, count files, count, total size, for .jpg and .mp4

import os
import sys

def scan_directory(directory):
    jpg_count = 0
    jpg_size = 0
    mp4_count = 0
    mp4_size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.jpg'):
                jpg_count += 1
                jpg_size += os.path.getsize(os.path.join(root, file))
            elif file.endswith('.mp4'):
                mp4_count += 1
                mp4_size += os.path.getsize(os.path.join(root, file))
    return jpg_count, jpg_size, mp4_count, mp4_size

if __name__ == "__main__":
    jpg_count, jpg_size, mp4_count, mp4_size = scan_directory(sys.argv[1])
    print(f"JPGs: {jpg_count}, {jpg_size / 1024 / 1024 / 1024:.2f} GB")
    print(f"MP4s: {mp4_count}, {mp4_size / 1024 / 1024 / 1024:.2f} GB")
    print(f"Total: {jpg_count + mp4_count}, {(jpg_size + mp4_size) / 1024 / 1024 / 1024:.2f} GB")
