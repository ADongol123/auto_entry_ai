import cv2
import numpy as np
import pytesseract
import os
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from mongodb import save_to_mongodb

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_image(img):
    """Enhanced image preprocessing for better OCR results"""
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    kernel = np.ones((1, 1), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=1)
    thresh = cv2.erode(thresh, kernel, iterations=1)

    return thresh


def extract_structured_data(text):
    """Extract specific fields from bill text"""
    data = {
        "raw_text": text,
        "date": None,
        "total": None,
        "items": [],
        "vendor": None,
        "processing_date": datetime.now().isoformat()
    }

    date_patterns = [
        r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(?:\d{4}[/-]\d{2}[/-]\d{2})"
    ]

    total_patterns = [
        r"(?:Total|TOTAL|Amount Due)[:\s]*\$?(\d+\.?\d{2})",
        r"\$?(\d+\.?\d{2})\s*(?:Total|TOTAL)"
    ]

    for pattern in date_patterns:
        date_match = re.search(pattern, text)
        if date_match:
            data["date"] = date_match.group(0)
            break

    for pattern in total_patterns:
        total_match = re.search(pattern, text, re.IGNORECASE)
        if total_match:
            data["total"] = float(total_match.group(1))
            break

    lines = text.split('\n')
    if lines and lines[0].strip():
        data["vendor"] = lines[0].strip()

    item_pattern = r"(.+?)\s+(\d+\.?\d{2})"
    for line in lines:
        item_match = re.search(item_pattern, line)
        if item_match:
            data["items"].append({
                "description": item_match.group(1).strip(),
                "price": float(item_match.group(2))
            })

    return data


def process_single_image(file_path):
    """Process a single image file"""
    try:
        img = cv2.imread(file_path)
        if img is None:
            raise Exception(f"Failed to load image: {file_path}")

        processed_img = preprocess_image(img)
        custom_config = r'--oem 3 --psm 6 -l eng'
        text = pytesseract.image_to_string(processed_img, config=custom_config)

        if text.strip():
            structured_data = extract_structured_data(text)
            structured_data["source_file"] = file_path
            structured_data["page_number"] = 1

            # Save to MongoDB
            save_to_mongodb(file_path, structured_data)

            # Save processed image for verification
            output_path = f"processed_{os.path.basename(file_path)}"
            cv2.imwrite(output_path, processed_img)

            return structured_data
        return None

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None


def process_all_images(directory_path, max_workers=4):
    """Process all images in directory using parallel processing"""
    # Create output directory for processed images
    output_dir = os.path.join(directory_path, "processed")
    os.makedirs(output_dir, exist_ok=True)

    # Get list of image files
    image_extensions = ('.png', '.jpg', '.jpeg')
    image_files = [
        os.path.join(directory_path, f) for f in os.listdir(directory_path)
        if f.lower().endswith(image_extensions)
    ]

    print(f"Found {len(image_files)} images to process")

    # Process images in parallel
    successful = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all processing tasks
        future_to_file = {
            executor.submit(process_single_image, file_path): file_path
            for file_path in image_files
        }

        # Collect results as they complete
        for future in future_to_file:
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    successful += 1
                    print(f"Successfully processed: {os.path.basename(file_path)}")
                    print(f"Extracted data: {result}")
                else:
                    print(f"Failed to extract data from: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
            print("-" * 50)

    print(f"Processing complete: {successful}/{len(image_files)} images processed successfully")
    return successful


if __name__ == "__main__":
    # Specify your directory containing the 20 images
    images_directory = "./images"  # Replace with your actual directory path

    # Process all images
    successful_count = process_all_images(images_directory)