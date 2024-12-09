import os
import cv2
import numpy as np

def apply_blur(image, blur_levels):
    blurred_images = []
    for blur_level in blur_levels:
        ksize = int(blur_level * 10) * 2 + 1
        blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
        blurred_images.append((f'blur_{blur_level}', blurred))
    return blurred_images

def apply_noise(image, noise_levels):
    noisy_images = []
    for noise_level in noise_levels:
        noise = np.random.randn(*image.shape) * noise_level * 255
        noisy = np.clip(image + noise, 0, 255).astype(np.uint8)
        noisy_images.append((f'noise_{noise_level}', noisy))
    return noisy_images

def apply_compression(image, compression_levels):
    compressed_images = []
    for compression_level in compression_levels:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), compression_level]
        is_success, encoded_img = cv2.imencode('.jpg', image, encode_param)
        compressed = cv2.imdecode(encoded_img, 1)
        compressed_images.append((f'compression_{compression_level}', compressed))
    return compressed_images

def save_images(images, output_base_folder, transformation_type, original_filename):
    for label, img in images:
        subfolder = f'{transformation_type}/{label}'
        output_folder = os.path.join(output_base_folder, subfolder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_path = os.path.join(output_folder, original_filename)
        cv2.imwrite(output_path, img)

def process_images(input_folder, output_base_folder):
    blur_levels = [0.3, 0.5, 0.7]
    noise_levels = [0.1, 0.2, 0.3]
    compression_levels = [20, 30, 50]

    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = cv2.imread(image_path)
            
            blurred_images = apply_blur(image, blur_levels)
            noisy_images = apply_noise(image, noise_levels)
            compressed_images = apply_compression(image, compression_levels)

            save_images(blurred_images, output_base_folder, 'blur', filename)
            save_images(noisy_images, output_base_folder, 'noise', filename)
            save_images(compressed_images, output_base_folder, 'compression', filename)


input_folder = '/media/NAS/DATASET/LOLI_ACCV/test/high'
output_folder = '/media/NAS/DATASET/LOLI_ACCV/test/processed'
process_images(input_folder, output_folder)