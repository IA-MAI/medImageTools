#          Medical Image Tools

Useful uitlities for medical images using SimpleITK

 - Resize image    
 - extract 2D images from a 3D image
 - Copy properties e.g. map an image to another


## How to use:

- Install requirements:

    pip install SimpleITK opencv-python 


### Resize medical images

     python medImageUtils.py --resize < --imagePath <image path> | --folderPath <folder path> --newSize <[x,y,z]> --outputPath <outputPath> --outputFormat <format>
  
  The tools will resize the image or all the images in a folder to the new size depends on the input. 
  
  The result will be saved in the same path with the same name with "_resized" at the end. 
  
  The result will be saved in the same format unless a format was provided. 
  
  Note that the spacing will be changed to match the new size, otherwise the pixel location will be wrong. 

  A meta file will be added to the result image that contains the original size and other information. This can be used to reverse the operation. e.g.  

  python medImageUtils.py --resize <metaFilePath>

  The tool assume that the image file has the same path as the metaFile

##   Extract 2D images from a 3D image 

python medImageUtils.py --extract2D < --imagePath <image path> | --folderPath <folder path> --location <[x,y,z]> --N <number of images>--outputPath <outputPath> 

This is useful for simple visualization purposes. The tools will extract the center N images in 3 views as PNG unless a location is provided. If N =2 the output will be 2x3 = 6 2D images 

