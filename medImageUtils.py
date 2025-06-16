# =============================================
# Author: Ibraheem Al-Dhamari ia@idhamari.com
#
#          Medical Image Tools
#
#  Useful uitlities for medical images using SimpleITK
#     - Resize image    
#     - Copy properties e.g. map an image to another
#     - extract 2D images from a 3D image
# Last update: 15.6.2025
# =============================================

import os, argparse, json, cv2
import numpy as np
import SimpleITK as sitk

def resize_image(image_path, new_size, output_path, output_format=None):
    # Read the image
    image = sitk.ReadImage(image_path)
    original_size = image.GetSize()
    original_spacing = image.GetSpacing()
    
    # Calculate new spacing to maintain physical dimensions
    new_spacing = [
        original_spacing[0] * (original_size[0] / new_size[0]),
        original_spacing[1] * (original_size[1] / new_size[1]),
        original_spacing[2] * (original_size[2] / new_size[2]) if len(new_size) > 2 else 1.0
    ]
    
    # Resize the image
    resized_image = sitk.Resample(
        image,
        new_size,
        sitk.Transform(),
        sitk.sitkLinear,
        image.GetOrigin(),
        new_spacing,
        image.GetDirection(),
        0.0,
        image.GetPixelID()
    )
    
    # Save metadata
    metadata = {
        "original_size": original_size,
        "original_spacing": original_spacing,
        "original_direction": image.GetDirection(),
        "original_origin": image.GetOrigin()
    }
    
    # Determine output path and format
    if output_format is None:
        output_format = os.path.splitext(image_path)[1][1:]
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_image_path = os.path.join(output_path, f"{base_name}_resized.{output_format}")
    output_meta_path = os.path.join(output_path, f"{base_name}_resized_meta.json")
    
    # Save the resized image and metadata
    sitk.WriteImage(resized_image, output_image_path)
    with open(output_meta_path, 'w') as f:
        json.dump(metadata, f)
    
    return output_image_path, output_meta_path

def extract_2d_slices(image_path, location=None, n=1, output_path=None):
    # Read the 3D image
    image = sitk.ReadImage(image_path)
    array = sitk.GetArrayFromImage(image)
    
    # If no location specified, use the center
    if location is None:
        location = [s//2 for s in array.shape]
    
    # Extract slices in three views
    slices = []
    views = ['axial', 'coronal', 'sagittal']
    
    for view in views:
        if view == 'axial':
            center = location[0]
            start = max(0, center - n//2)
            end = min(array.shape[0], center + n//2 + 1)
            for i in range(start, end):
                slices.append((f"{view}_{i}", array[i, :, :]))
        elif view == 'coronal':
            center = location[1]
            start = max(0, center - n//2)
            end = min(array.shape[1], center + n//2 + 1)
            for i in range(start, end):
                slices.append((f"{view}_{i}", array[:, i, :]))
        elif view == 'sagittal':
            center = location[2]
            start = max(0, center - n//2)
            end = min(array.shape[2], center + n//2 + 1)
            for i in range(start, end):
                slices.append((f"{view}_{i}", array[:, :, i]))
    
    # Save slices as PNG
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_files = []
    
    for name, slice_data in slices:
        # Normalize to 0-255
        slice_data = cv2.normalize(slice_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        output_file = os.path.join(output_path, f"{base_name}_{name}.png")
        cv2.imwrite(output_file, slice_data)
        output_files.append(output_file)
    
    return output_files

def main():
    parser = argparse.ArgumentParser(description="Medical Image Utilities")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Resize command
    resize_parser = subparsers.add_parser('resize', help='Resize medical images')
    resize_group = resize_parser.add_mutually_exclusive_group(required=True)
    resize_group.add_argument('--imagePath', help='Path to input image')
    resize_group.add_argument('--folderPath', help='Path to input folder')
    resize_parser.add_argument('--newSize', required=True, help='New size as [x,y,z]', type=json.loads)
    resize_parser.add_argument('--outputPath', required=True, help='Output directory')
    resize_parser.add_argument('--outputFormat', help='Output format (e.g., nii, mha)')
    
    # Extract 2D command
    extract_parser = subparsers.add_parser('extract2D', help='Extract 2D slices from 3D image')
    extract_group = extract_parser.add_mutually_exclusive_group(required=True)
    extract_group.add_argument('--imagePath', help='Path to input image')
    extract_group.add_argument('--folderPath', help='Path to input folder')
    extract_parser.add_argument('--location', help='Location as [x,y,z]', type=json.loads)
    extract_parser.add_argument('--N', type=int, default=1, help='Number of images to extract')
    extract_parser.add_argument('--outputPath', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    if args.command == 'resize':
        if args.imagePath:
            resize_image(args.imagePath, args.newSize, args.outputPath, args.outputFormat)
        else:
            for filename in os.listdir(args.folderPath):
                if filename.endswith(('.nii', '.nii.gz', '.mha', '.mhd')):
                    resize_image(os.path.join(args.folderPath, filename), 
                               args.newSize, args.outputPath, args.outputFormat)
    
    elif args.command == 'extract2D':
        if args.imagePath:
            extract_2d_slices(args.imagePath, args.location, args.N, args.outputPath)
        else:
            for filename in os.listdir(args.folderPath):
                if filename.endswith(('.nii', '.nii.gz', '.mha', '.mhd')):
                    extract_2d_slices(os.path.join(args.folderPath, filename), 
                                     args.location, args.N, args.outputPath)

if __name__ == "__main__":
    main()

