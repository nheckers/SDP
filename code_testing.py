import cv2
import numpy as np

# Create a blank 300x300 black image
blank_image = np.zeros((300, 300, 3), dtype=np.uint8)

cv2.imshow("Blank Image", blank_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
