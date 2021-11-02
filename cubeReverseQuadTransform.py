from PIL import Image
import cv2
import numpy

def reverse_quad_transform(image, quad_to_map_to, alpha):
  # forward mapping, for simplicity

  result = Image.new("RGBA",image.size)
  result_pixels = result.load()

  width, height = result.size

  for y in range(height):
    for x in range(width):
      result_pixels[x,y] = (0,0,0,0)

  p1 = (quad_to_map_to[0],quad_to_map_to[1])
  p2 = (quad_to_map_to[2],quad_to_map_to[3])
  p3 = (quad_to_map_to[4],quad_to_map_to[5])
  p4 = (quad_to_map_to[6],quad_to_map_to[7])

  p1_p2_vec = (p2[0] - p1[0],p2[1] - p1[1])
  p4_p3_vec = (p3[0] - p4[0],p3[1] - p4[1])

  for y in range(height):
    for x in range(width):
      pixel = image.getpixel((x,y))

      y_percentage = y / float(height)
      x_percentage = x / float(width)

      # interpolate vertically
      pa = (p1[0] + p1_p2_vec[0] * y_percentage, p1[1] + p1_p2_vec[1] * y_percentage) 
      pb = (p4[0] + p4_p3_vec[0] * y_percentage, p4[1] + p4_p3_vec[1] * y_percentage)

      pa_to_pb_vec = (pb[0] - pa[0],pb[1] - pa[1])

      # interpolate horizontally
      p = (pa[0] + pa_to_pb_vec[0] * x_percentage, pa[1] + pa_to_pb_vec[1] * x_percentage)

      try:
        result_pixels[p[0],p[1]] = (pixel[0],pixel[1],pixel[2],min(int(alpha * 255),pixel[3]))
      except Exception:
        pass

  return result
  
im = Image.open("hello.jpg")
width = 100
height = 100
ress = reverse_quad_transform(im, [0, 0, width, 0, 0, height, width, height], 0.5)
print(ress)
ress.show()
open_cv_image = numpy.array(ress) 
# Convert RGB to BGR 
open_cv_image = open_cv_image[:, :, ::-1].copy() 

cv2.imshow("n", open_cv_image)
cv2.waitKey(0)
