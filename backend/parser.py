import cv2
import numpy as np
import pytesseract
import os
import matplotlib.pyplot as plt

# Set Tesseract path (update this to your actual Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(img):
    # Resize for better resolution (assuming 72 DPI originally, aim for ~300 DPI)
    scale_factor = 4
    img_resized = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # Slight contrast adjustment
    gray = cv2.convertScaleAbs(gray, alpha=1.1, beta=10)
    
    # Binary thresholding instead of adaptive (better for printed text)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def show_image(img, title="Image"):
    # Convert from BGR to RGB (OpenCV uses BGR by default)
    if len(img.shape) == 3:  # Color image
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:  # Grayscale image
        img_rgb = img
    # Display image using Matplotlib
    plt.figure()
    plt.imshow(img_rgb, cmap='gray' if len(img.shape) == 2 else None)
    plt.title(title)
    plt.axis('off')  # Hide axis
    plt.show()

def extract_text_from_image(img_path):
    try:
        # Verify Tesseract is accessible
        if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            raise Exception(f"Tesseract executable not found at: {pytesseract.pytesseract.tesseract_cmd}")
        
        # Read image
        img = cv2.imread(img_path)
        if img is None:
            raise Exception(f"Failed to load image from: {img_path}")
            
        # Preprocess image
        processed_img = preprocess_image(img)
        
        # Save preprocessed image for debugging
        cv2.imwrite("processed_test.jpg", processed_img)
        # Display preprocessed image using Matplotlib
        show_image(processed_img, title="Processed Image")
        
        # Configure Tesseract with custom parameters
        custom_config = r'--oem 3 --psm 3 -l eng'  # PSM 3 for automatic segmentation, English language
        
        # Extract text using Tesseract on processed image
        text_processed = pytesseract.image_to_string(processed_img, config=custom_config)
        
        # Extract text and bounding boxes using image_to_data
        data = pytesseract.image_to_data(processed_img, config=custom_config, output_type=pytesseract.Output.DICT)
        
        # Highlight the text on the original image
        for i in range(len(data['text'])):
            text = data['text'][i]
            if text.strip():  # Only consider non-empty text
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                # Adjust coordinates back to original image scale
                x, y, w, h = int(x / 4), int(y / 4), int(w / 4), int(h / 4)  # scale_factor = 4
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Display the image with highlighted text
        show_image(img, title="Image with Detected Text")
        
        # Save extracted text to file
        with open('extracted_text.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n\n=== Text from {img_path} ===\n")
            f.write(text_processed)
        
        print(f"Extracted text from {img_path}:")
        print(text_processed)
        
        return text_processed
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

def process_image_or_directory(path):
    if os.path.isdir(path):
        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)
            if os.path.isfile(full_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"Processing {filename}...")
                text = extract_text_from_image(full_path)
                print("-" * 50)
    elif os.path.isfile(path):
        print(f"Processing single image: {path}")
        text = extract_text_from_image(path)
    else:
        print("Invalid path specified")

# Test with your image
if __name__ == "__main__":
    image_path = "./test.jpg"
    process_image_or_directory(image_path)