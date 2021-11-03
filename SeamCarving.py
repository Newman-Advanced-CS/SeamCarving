import cv2 as cv
import sys
from operator import itemgetter

def SobelEdges(img, kernelSize):
    # Apply sobel operator for x and y axis
    sobelX = cv.Sobel(img, cv.CV_64F, 1, 0, ksize=kernelSize)
    sobelY = cv.Sobel(img, cv.CV_64F, 0, 1, ksize=kernelSize)
    absX = cv.convertScaleAbs(sobelX)
    absY = cv.convertScaleAbs(sobelY)

    # Combine the two images
    edges = cv.addWeighted(absX, 0.5, absY, 0.5, 0)

    # Convert to grayscale (for easier use)
    edges = cv.cvtColor(edges, cv.COLOR_BGR2GRAY)
    return edges
    
def FindCarvingLine(img, x):
    # Get dimensions of image
    height, width = img.shape

    # Carving line coordinates
    carvingLine = [(0,x)]
    sum = 0

    # Iterate through the image rows
    for i in range(height-1):
        # Get pixel values of neighbours
        values = []
        for neighbourX in range(3):
            neighbourX = x + (neighbourX - 1)
            if neighbourX >= 0 and neighbourX < width:
                neighbourCoordinates = (i+1, neighbourX)
                neighbourValue = img[neighbourCoordinates]
                values.append([neighbourValue, neighbourX])
        
        # Choose neighbour with lowest value
        lowest = [255, -1]
        for neighbour in values:
            if neighbour[0] <= lowest[0]:
                lowest = neighbour
        
        # Add to sum
        sum = sum + lowest[0]

        # Repeat with new coordinates
        carvingLine.append((i+1, lowest[1]))
        x = lowest[1]
    
    # Return the line and the sum
    return carvingLine, sum

def ShiftPixels(x, y, width, img):
    if x+1 < width:
        img[y, x] = img[y, x+1]
        img = ShiftPixels(x+1, y, width, img)
    return img

def RemovePoints(line, img):
    # Create copy image
    copy = img.copy()

    # Get image dimensions
    height, width = img.shape[:2]

    # Get x,y of each point
    for point in line[0]:
        y = point[0]
        x = point[1]

        # Shift neighbouring pixels to the left (if applicable)
        copy = ShiftPixels(x,y,width,copy)
    
    # Remove last collumn
    copy = copy[0:height, 0:width-1]

    return copy

def Resize(img, newWidth):
    # Create copy so a comparison is possible
    img = img.copy()

    # Edge detection
    sobelEdges = SobelEdges(img, 3)
    cannyEdges = cv.Canny(img, 100, 200)
    edges = cv.addWeighted(sobelEdges, 0.5, cannyEdges, 0.5, 0)

    # Generate all carving lines
    imgWidth = edges.shape[1]
    carvingLines = []
    for x in range(imgWidth):
        line, sum = FindCarvingLine(edges, x)
        carvingLines.append((line, sum))

    # Sort by sum
    carvingLines = sorted(carvingLines, key=itemgetter(1))

    # Calculate the amount of lines needed to remove
    lineCount = imgWidth - newWidth

    #... and remove those lines from the picture
    for i in range(lineCount):
        img = RemovePoints(carvingLines[i], img)
    
    return img

if len(sys.argv) == 4:
    input = sys.argv[1]
    newWidth = int(sys.argv[2])
    output = sys.argv[3]

    inputImg = cv.imread(input)
    outputImg = Resize(inputImg, newWidth)
    cv.imwrite(output, outputImg)
else:
    print("USAGE: python3 SeamCarving.py pathToInput newWidth pathToOutput")
    