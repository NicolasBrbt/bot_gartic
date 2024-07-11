import time
from pynput import mouse # type: ignore
from pynput.mouse import Button, Controller # type: ignore
from PIL import ImageGrab
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import sys
import keyboard
from scipy.spatial import KDTree

numberColor = 26
nombreCoins = 2

colorPosition = []
colorColor = []
mouse2 = Controller()
grid = []
largeur = 0
hauteur = 0

def chargerImage(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    return image


def couleurPlusProche(colorColor, pixel):
    colorColor_np = np.array(colorColor)
    pixel_np = np.array(pixel)

    # Vérifier si la couleur exacte existe
    exact_match = np.where(np.all(colorColor_np == pixel_np, axis=1))[0]
    if len(exact_match) > 0:
        return colorColor_np[exact_match[0]]

    # Utiliser KDTree pour une recherche rapide du plus proche voisin
    tree = KDTree(colorColor_np)
    distance, index = tree.query(pixel_np)

    return colorColor_np[index]

def changerCouleur(colorColor, pixels):
    colorColor = np.array(colorColor)
    shape = pixels.shape
    pixels_flat = pixels.reshape(-1, pixels.shape[-1])

    for i in range(pixels_flat.shape[0]):
        pixel = pixels_flat[i][:3]
        pixels_flat[i][:3] = couleurPlusProche(colorColor, pixel)

    return pixels.reshape(shape)

def recupererCouleurPixel(x,y,couleurs):
    img = ImageGrab.grab(bbox=(int(x), int(y), int(x + 1), int(y +1)))
    couleurs.append(np.array(img.getpixel((0, 0)))[:3])


def recupererCouleurGarticPhone(positionsCouleur, couleurs):
    def getColorPosition(x, y, button, pressed):
        if pressed and len(positionsCouleur) < numberColor:
            positionsCouleur.append((x, y))
            recupererCouleurPixel(x, y, couleurs)
            if len(positionsCouleur) == numberColor:
                return False  # Stop listener when enough points are selected
            
    with mouse.Listener(on_click=getColorPosition) as listener:
        listener.join()
    print("Fin de la selection des couleurs.")
    
def recupererCoinsGrille(positionsCoins):
    def getGrid(x, y, button, pressed):
        if pressed and len(positionsCoins) < nombreCoins:
            positionsCoins.append((x, y))
            if len(positionsCoins) == nombreCoins:
                return False  # Stop listener when enough points are selected

    with mouse.Listener(on_click=getGrid) as listener:
        listener.join()
    print("Fin de la selection de la grille.")
    print("Positions grille:", positionsCoins)


def calculerDimensionsGrille(positionsCoins):
    largeur = abs(positionsCoins[0][0] - positionsCoins[1][0])
    hauteur = abs(positionsCoins[0][1] - positionsCoins[1][1])
    return largeur, hauteur

def dessiner(image, grid, couleurs, positionsCouleur, taillePixel=1):
    """
    Dessine un motif en ne dessinant que tous les 5 pixels sur la grille.
    
    Args:
    - image (numpy.ndarray): La matrice d'image représentant les pixels à dessiner.
    - grid (list of list of int): La position de départ sur la grille (x, y).
    - couleurs (list of list of int): Liste des couleurs à dessiner.
    - positionsCouleur (list of list of int): Liste des positions (x, y) pour chaque couleur.
    """
    couleurs_uniques = list(set(tuple(pixel) for row in image for pixel in row))
    couleurs_uniques = [np.array(couleur) for couleur in couleurs_uniques]  # Convertir en tableaux numpy pour comparaison
    mouse = Controller()
    
    for couleur in couleurs:
        idxCouleur = rechercherIndexCouleur(couleur, couleurs)
        if idxCouleur == -1:
            continue  # Ignorer si la couleur n'est pas trouvée dans la liste des couleurs

        xCouleur, yCouleur = positionsCouleur[idxCouleur]
        mouse.position = (xCouleur, yCouleur)
        mouse.click(Button.left, 1)

        for i in range(0, image.shape[0], taillePixel):  # Sauter de 5 pixels en 5 pixels en Y
            for j in range(0, image.shape[1], taillePixel):  # Sauter de 5 pixels en 5 pixels en X
                if np.array_equal(image[i][j], couleur):
                    if keyboard.is_pressed('q'):
                        print("Arrêt du script demandé.")
                        return
                    
                    # Dessiner sur la grille
                    x = grid[0][0] + j
                    y = grid[0][1] + i
                    mouse.position = (x, y)
                    mouse.click(Button.left, 1)
                    #time.sleep(0.002)  # Attendre un peu pour éviter les erreurs de clic


def matricePixelParCouleur(image, couleurs, grid):
    matriceTotale = []
    for couleur in couleurs:
        idx = rechercherIndexCouleur(couleur, couleurs)
        if idx == -1:
            print(f"La couleur {couleur} n'a pas été trouvée dans la liste des couleurs.")
            continue
        matricePixelParCouleur = []
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if np.array_equal(image[i][j], couleur):
                    matricePixelParCouleur.append((j + grid[0][0], i + grid[0][1], idx))
        matriceTotale.append(matricePixelParCouleur)
    return matriceTotale


def dessinerMatrice(images, couleurs, positionCouleur, grid):
    mouse = Controller()
    matrices = matricePixelParCouleur(images, couleurs, grid)
    
    for matrice in matrices:
        if keyboard.is_pressed('q'):
            print("Arrêt du script demandé.")
            return

        couleur_idx = matrice[0][2]
        mouse.position = (positionCouleur[couleur_idx][0], positionCouleur[couleur_idx][1])
        print("Couleur:", positionCouleur[couleur_idx])
        mouse.click(Button.left, 1)
        
        for pixel in matrice:
            if keyboard.is_pressed('q'):
                print("Arrêt du script demandé.")
                return
            
            x = pixel[0]
            y = pixel[1]
            mouse.position = (x, y)
            mouse.click(Button.left, 1)
            time.sleep(0.0008)



def rechercherIndexCouleur(couleur, couleurs):
    if np.array_equal(couleur, [255, 255, 255]):
        return -1
    for i in range(len(couleurs)):
        if np.all(couleur == couleurs[i]):
            return i
    return -1   
def main():
    try:
        # Charger l'image à partir d'une URL
        url = input("Entrez l'URL de l'image: ")
        image = chargerImage(url)

        # Cliquer sur les 2 premières couleurs de Gartic phone.
        print("Cliquez sur les couleurs de Gartic Phone.")
        positionCouleur = []
        couleurs = []
        recupererCouleurGarticPhone(positionCouleur, couleurs)
        print("Couleurs selectionnees:", couleurs)
        print("Positions selectionnees:", positionCouleur)

        # Cliquer sur les 2 coins de la grille
        print("Cliquez sur les coins de la grille.")
        grid = []
        recupererCoinsGrille(grid)

        # Calculer les dimensions de la grille
        largeur, hauteur = calculerDimensionsGrille(grid)
        print("Largeur:", largeur)
        print("Hauteur:", hauteur)

        # Modifier la taille de l'image
        print("Modification de la taille de l'image.")
        print("Taille de l'image:", image.size)
        image = image.resize((int(largeur), int(hauteur)))
        print("Nouvelle taille de l'image:", image.size)
        pixels = np.array(image)

        # Changer les couleurs
        changerCouleur(couleurs, pixels)

        new_image = Image.fromarray(pixels)
        new_image.save('image_modifiee.png')  # Sauvegarder l'image modifiée
        #new_image.show()

        # Dessiner sur Gartic Phone
        dessiner(pixels, grid, couleurs, positionCouleur,1)
        #dessinerOptimiser(pixels, grid, couleurs, positionCouleur)
        #dessinerMatrice(pixels, couleurs,positionCouleur, grid)


        

        return 0

    except KeyboardInterrupt:
        print("Programme interrompu par l'utilisateur.")
        return 1

    except Exception as e:
        print(f"Une erreur est survenue: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())



