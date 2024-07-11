import time
from pynput import mouse
from pynput.mouse import Button, Controller
from PIL import ImageGrab
import requests
from PIL import Image
from io import BytesIO
import numpy as np

numberColor = 18
numberCorner = 2

colorPosition = []
colorColor = []
mouse2 = Controller()
grid = []
largeur = 0
hauteur = 0

def getColorPosition(x, y, button, pressed):
    if pressed and len(colorPosition) < numberColor:
        colorPosition.append((x, y))
        getColorColor(x, y, colorColor)
        if len(colorPosition) == numberColor:
            return False  # Stop listener when enough points are selected

def getGrid(x, y, button, pressed):
    if pressed and len(grid) < numberCorner:
        grid.append((x, y))
        if len(grid) == numberCorner:
            return False  # Stop listener when enough points are selected

def getColorColor(x,y, colorColor):
        # Capture the color of the pixel at the specified position
        img = ImageGrab.grab(bbox=(int(x), int(y), int(x + 1), int(y +1)))
        colorColor.append(np.array(img.getpixel((0, 0)))[:3])

def changerCouleur(colorColor,pixels):
    for i in range (pixels.shape[0]):
        for j in range(pixels.shape[1]):
            pixel = pixels[i,j][:3]
            pixels[i,j][:3] = couleurPlusProche(colorColor, pixel)
            

def couleurPlusProche(colorColor, pixel):
    distancePlusPetite = 10000
    couleurRemplacement = (0,0,0)

    for color in colorColor:
        if np.all(pixel == color):
            return color
        else:
            distance = np.linalg.norm(np.array(pixel) - np.array(color))
            if distance < distancePlusPetite:
                couleurRemplacement = color
                distancePlusPetite = distance

    return couleurRemplacement

# Listen for color positions
with mouse.Listener(on_click=getColorPosition) as listener:
    listener.join()
print("Fin de la selection des couleurs.")

# Wait briefly to avoid issues
time.sleep(3)

# Click at the color positions (if needed)
for position in colorPosition:
    mouse2.position = position
    mouse2.click(Button.left, 1)
    time.sleep(0.1)

# Listen for grid corners
with mouse.Listener(on_click=getGrid) as listener:
    listener.join()

# Calculate grid dimensions
if len(grid) == 2:
    largeur = abs(grid[0][0] - grid[1][0])
    hauteur = abs(grid[0][1] - grid[1][1])
    print("Largeur:", largeur)
    print("Hauteur:", hauteur)

print("Fin de la selection de la grille.")
print("Couleurs selectionnees:", colorColor)
image_url = "https://cdn-imgix.headout.com/media/images/c90f7eb7a5825e6f5e57a5a62d05399c-25058-BestofParis-EiffelTower-Cruise-Louvre-002.jpg"
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))
image = image.resize((int(largeur), int(hauteur)))
pixels = np.array(image)
print(pixels.shape)

changerCouleur(colorColor, pixels)
new_image = Image.fromarray(pixels)
new_image.save('image_modifiee.png')  # Sauvegarder l'image modifiée
new_image.show()  # Afficher l'image modifiée

