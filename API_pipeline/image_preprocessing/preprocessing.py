import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

class ImagePreprocessing:
    def __init__(self):
        self.new_width = 1000
        self.new_height = 1400
        self.x, self.y, self.w, self.h = 84, 161, 913 - 84, 1107 - 161
        self.dpi_threshold = 300
        self.width_threshold = 1500
        self.height_threshold = 1500
        self.clarity_threshold = 150
        self.noise_threshold = 200

    def process_pdf(self,pdf_path, output_folder, dpi):
        images = convert_from_path(pdf_path, dpi=dpi)
        _is_saved=True
        if not os.path.exists(output_folder):
           os.makedirs(output_folder)

        for i, img in enumerate(images):
            try:
               output_path = os.path.join(output_folder, f"Scanned_image.png")
               img.save(output_path, format="PNG")
               _is_saved=True
            except Exception as e:
                print(f"Error processing image: {e}")
                _is_saved=False
        return _is_saved
    
    def check_resolution(self, image):
        indicator = 0
        dpi=300
        height, width = image.shape[:2]

        # Calculate the actual DPI
        actual_dpi_x = width / (8.5 * 25.4) * 2.54 * 100
        actual_dpi_y = height / (11 * 25.4) * 2.54 * 100

        if actual_dpi_x < dpi or actual_dpi_y < dpi:
            print("Low image resolution (DPI).")
            indicator = 1
            # You can add code here to resize the image if you want to simulate higher DPI.
        else:
            print("Image resolution is acceptable.")

        return image, indicator 


    def check_dimensions(self, image):
        indicator = 0
        height, width = image.shape[:2]
        if width < self.width_threshold or height < self.height_threshold:
            print("Small image dimensions.")
            indicator = 1

        return indicator

    def check_clarity(self, image):
        indicator = 0
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        clarity_score = laplacian.var()

        if clarity_score < self.clarity_threshold:
            print("Low image clarity.")
            indicator = 1

        return indicator

    def check_noise(self, image):
        indicator = 0
        noise = np.mean(image)

        if noise > self.noise_threshold:
            print("Image contains noise.")
            indicator = 1

        return indicator

    def preprocess_invoice_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        enhanced_image = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        return enhanced_image
    

    def pil2cv(self,image):

        image_cv2 = np.array(image)
        if len(image_cv2.shape) == 3 and image_cv2.shape[-1] == 3:
            image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_RGB2BGR)
        return image_cv2
    def rotate_image(self, image, angle):
        mean_pixel = np.median(np.median(image, axis=0), axis=0)
        center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=mean_pixel)
        return result
    # Returns a small value if the horizontal histogram is sharp.
    # Returns a large value if the horizontal histogram is blurry.
    def eval_image(self,image: np.ndarray) -> float:
        hist = np.sum(np.mean(image, axis=1), axis=1)
        bef = 0
        aft = 0
        err = 0.
        assert(hist.shape[0] > 0)
        for pos in range(hist.shape[0]):
            if pos == aft:
               bef = pos
               while aft + 1 < hist.shape[0] and abs(hist[aft + 1] - hist[pos]) >= abs(hist[aft] - hist[pos]):
                  aft += 1
            err += min(abs(hist[bef] - hist[pos]), abs(hist[aft] - hist[pos]))
        assert(err > 0)
        return err

    # Measures horizontal histogram sharpness across many angles
    def sweep_angles(self,image: np.ndarray) -> np.ndarray:
        results = np.empty((81, 2))
        for i in range(81):
           angle = (i - results.shape[0] // 2) / 4.
           rotated = self.rotate_image(image, angle)
           err = self.eval_image(rotated)
           results[i, 0] = angle
           results[i, 1] = err
        return results
    
    # Find an angle that is a lot better than its neighbors
    def find_alignment_angle(self,image: np.ndarray) -> float:
        best_gain = 0
        best_angle = 0.
        results = self.sweep_angles(image)
        for i in range(2, results.shape[0] - 2):
            ave = np.mean(results[i-2:i+3, 1])
            gain = ave - results[i, 1]
            # print('angle=' + str(results[i, 0]) + ', gain=' + str(gain))
            if gain > best_gain:
               best_gain = gain
               best_angle = results[i, 0]
        return best_angle+0.78

    def align_image(self,image: np.ndarray) -> np.ndarray:
        angle = self.find_alignment_angle(image)
        return self.rotate_image(image, angle)
    
    def crop_image(self,image):
        
        # Crop the image using slicing
        cropped_image = image[self.y:self.y+self.h, self.x:self.x+self.w]

        return cropped_image


    def resize_image(self,image):

        # Resize the image using INTER_AREA interpolation method for best quality
        resized_image = cv2.resize(image, (self.new_width, self.new_height), interpolation=cv2.INTER_AREA)

        return resized_image      
    