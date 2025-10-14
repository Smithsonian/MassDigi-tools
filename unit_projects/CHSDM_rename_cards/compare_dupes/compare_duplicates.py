#!/usr/bin/env python3
#
# Compare dupes between two folders to distinguish between true dupes and filename issues
# Written with code suggested by CoPilot

import os
import hashlib
import difflib
import pandas as pd
import argparse
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import logging
import shutil 

# Configure logging
logging.basicConfig(
    filename='comparison.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

real_dupes = "real_dupes"
if not os.path.exists(real_dupes):
    os.makedirs(real_dupes)

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def compare_text_files(file1, file2):
    with open(file1, 'r', errors='ignore') as f1, open(file2, 'r', errors='ignore') as f2:
        content1 = f1.read()
        content2 = f2.read()
    similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
    return similarity

def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None or img1.shape != img2.shape:
        logging.warning(f"Image comparison failed due to incompatible files: {img1_path}, {img2_path}")
        return 0.0
    score, _ = ssim(img1, img2, full=True)
    return score

def compare_folders(folder1, folder2):
    logging.info(f"Starting comparison between '{folder1}' and '{folder2}'")
    files1 = [os.path.join(folder1, f) for f in os.listdir(folder1) if os.path.isfile(os.path.join(folder1, f))]
    files2 = [os.path.join(folder2, f) for f in os.listdir(folder2) if os.path.isfile(os.path.join(folder2, f))]

    results = []
    for f1 in files1:
        
        ext1 = os.path.splitext(f1)[1].lower()
        hash1 = get_file_hash(f1)
        for f2 in files2:
            if os.path.basename(f1).replace("_dupe1.jpg", ".jpg") != os.path.basename(f2):
                continue
            msg = f"Working on file {f1}"
            print(msg)
            logging.info(msg)
            ext2 = os.path.splitext(f2)[1].lower()
            hash2 = get_file_hash(f2)
            if hash1 == hash2:
                similarity = 1.0
                status = 'Exact Duplicate'
                logging.info(f"Exact duplicate found: {f1} and {f2}")
                with open("real_dupe.txt", "a") as f:
                    f.write(f"{f1},1\n")
                shutil.move(f"{f1}", f"{real_dupes}/{os.path.basename(f1)}")
            elif ext1 in ['.jpg', '.jpeg', '.png'] and ext2 in ['.jpg', '.jpeg', '.png']:
                similarity = compare_images(f1, f2)
                status = 'Similar Image' if similarity > 0.9 else 'Different Image'
                logging.info(f"Image comparison: {f1} vs {f2} - Similarity: {similarity:.2f}")
                if similarity > 0.9:
                    with open("real_dupe.txt", "a") as f:
                        f.write(f"{f1},{similarity}\n")
                    shutil.move(f"{f1}", f"{real_dupes}/{os.path.basename(f1)}")
            else:
                similarity = compare_text_files(f1, f2)
                status = 'Similar Text' if similarity > 0.8 else 'Different Text'
                logging.info(f"Text comparison: {f1} vs {f2} - Similarity: {similarity:.2f}")
            results.append({
                'File1': os.path.basename(f1),
                'File2': os.path.basename(f2),
                'Similarity': f"{similarity:.2f}",
                'Status': status
            })
            print({
                'File1': os.path.basename(f1),
                'File2': os.path.basename(f2),
                'Similarity': f"{similarity:.2f}",
                'Status': status
            })

    df = pd.DataFrame(results)
    df.to_csv('comparison_results.csv', index=False)
    logging.info("Comparison completed. Results saved to comparison_results.csv")
    print("Comparison completed. Results saved to comparison_results.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare files between two folders and export results to a CSV file.")
    parser.add_argument("folder1", help="Path to the first folder")
    parser.add_argument("folder2", help="Path to the second folder")
    args = parser.parse_args()

    compare_folders(args.folder1, args.folder2)
