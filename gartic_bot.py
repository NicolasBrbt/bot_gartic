import time
from pynput import mouse # type: ignore
from pynput.mouse import Button, Controller # type: ignore
from PIL import ImageGrab
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import sys

def chargerImage(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    return image


def draw_line(tupleCoordonnees, initialCoordonate):
    mouse = Controller()
    x1 = tupleCoordonnees[0][0] + initialCoordonate[0]
    x2 = tupleCoordonnees[1][0] + initialCoordonate[0]

    y1 = tupleCoordonnees[0][1] + initialCoordonate[1]
    y2 = tupleCoordonnees[1][1] + initialCoordonate[1]

    mouse.position = (x1, y1)
    time.sleep(0.008)
    mouse.press(Button.left)
    mouse.position = (x2, y2)
    time.sleep(0.008)
    mouse.release(Button.left)

def dessiner(initalCoordonate, listeDessin,positionCouleur ):
    mouse = Controller()
    mouse.position = positionCouleur
    time.sleep(0.05)
    mouse.click(Button.left, 1)
    time.sleep(0.05)

    for trait in listeDessin:
        draw_line(trait, initalCoordonate)
    return


def recupererCouleurPixel(x,y,couleurs):
    img = ImageGrab.grab(bbox=(int(x), int(y), int(x + 1), int(y +1)))
    couleurs.append(np.array(img.getpixel((0, 0)))[:3])

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

def changerCouleur(colorColor, pixels):
    colorColor = np.array(colorColor)
    shape = pixels.shape
    pixels_flat = pixels.reshape(-1, pixels.shape[-1])

    for i in range(pixels_flat.shape[0]):
        pixel = pixels_flat[i][:3]
        pixels_flat[i][:3] = couleurPlusProche(colorColor, pixel)

    return pixels.reshape(shape)

def recurerPaletteCouleurs(positionsCouleurs, nbCouleurs, couleurs):
    nbCouleurs = int(nbCouleurs)
    def getColor(x, y, button, pressed):
        nonlocal nbCouleurs
        if pressed and len(positionsCouleurs) < nbCouleurs:
            recupererCouleurPixel(x, y, couleurs)
            positionsCouleurs.append((int(x), int(y)))
            if len(positionsCouleurs) == nbCouleurs:
                print("Fin de la selection de la palette de couleurs.")
                return False
    
    with mouse.Listener(on_click=getColor) as listener:
        listener.join()
    print("Fin de la selection de la palette de couleurs.")


def recupererCoinsGrille(positionsCoins):
    def getGrid(x, y, button, pressed):
        if pressed and len(positionsCoins) < 2:
            positionsCoins.append((int(x), int(y)))
            if len(positionsCoins) == 2:
                return False  # Stop listener when enough points are selected

    with mouse.Listener(on_click=getGrid) as listener:
        listener.join()
    print("Fin de la selection de la grille.")
    print("Positions grille:", positionsCoins)



def calculerDimensionsGrille(positionsCoins):
    largeur = abs(positionsCoins[0][0] - positionsCoins[1][0])
    hauteur = abs(positionsCoins[0][1] - positionsCoins[1][1])
    return largeur, hauteur


def generateMatricesCouleurs(couleurs, pixels, matriceExistance):
    matricesCouleurs = []
    for couleur in couleurs:
        if(np.all(couleur != [255,255,255])):
            matrice = np.zeros((pixels.shape[0], pixels.shape[1]))
            for i in range (len(pixels)):
                for j in range(pixels.shape[1]):
                    if np.any(pixels[i][j] == couleur) and matriceExistance[i][j] == 0:
                        matrice[i][j] = 1
                        matriceExistance[i][j] = 1
            matricesCouleurs.append(matrice)
    return matricesCouleurs


def ajouterColonnes0(matrices):
    colonne_zero = np.zeros((matrices[0].shape[0], 1))
    for i in range (len(matrices)):
        matrices[i] = np.hstack((matrices[i], colonne_zero))
        matrices[i] = np.hstack((colonne_zero,matrices[i]))
    return matrices


def epurerMatricesCouleurs(matrices):
    for matrice in matrices:
        for i in range(matrice.shape[0]):
            for j in range(matrice.shape[1]):
                if matrice[i][j] == 1:
                    if i > 0 and j > 0 and i < matrice.shape[0]-1 and j < matrice.shape[1]-1:
                        if ((matrice[i-1][j] == 0 and matrice[i+1][j] == 0) or (matrice[i][j-1] == 0 and matrice[i][j+1] == 0)):
                            matrice[i][j] = 0
    return matrices



def calculGradientMatrices(matrices):
    matricesGradient = []
    for matrice in matrices : 
        gradient = np.zeros_like(matrice)
        for i in range (0, matrice.shape[1]-1):
            gradient[:,i] = np.abs(matrice[:,i+1] - matrice[:,i])
        matricesGradient.append(gradient)
    return matricesGradient


def calculListesDessin(matricesGradient):
    listesDessin = []
    for matrice in matricesGradient:
        listeDessin = []
        for i in range(len(matrice)):
            line = []
            for j in range(len(matrice[0])):
                if matrice[i][j] == 1 and len(line) == 0:
                    line.append([j,i])
                elif matrice[i][j] == 1 and len(line) == 1:
                    line.append([j,i])
                    listeDessin.append((line[0],line[1]))
                    line = []
        listesDessin.append(listeDessin)
    return listesDessin


def main():
    try:
        nbCouleurs = 0
        positionsCouleurs = []
        couleurs = []

        url = input("Entrez l'URL de l'image: ")
        image = chargerImage(url)
        image.load()
        image2 = Image.new('RGB', image.size, (255, 255, 255))
        image2.paste(image, None)

        nbCouleurs = input("Veuillez entrer le nombre de couleurs souhaitées :")

        print("Veuillez cliquer sur les {nbCouleurs} couleurs de la palette.".format(nbCouleurs=nbCouleurs))
        recurerPaletteCouleurs(positionsCouleurs, nbCouleurs, couleurs)
        nbCouleurs = len(couleurs)
        print("Positions couleurs:", positionsCouleurs)
        print("Couleurs:", couleurs)

        positionsCoins = []
        print("Veuillez cliquer sur les deux coins opposés de la grille.")
        recupererCoinsGrille(positionsCoins)

        largeur, hauteur = calculerDimensionsGrille(positionsCoins)
        print("Dimensions grille:", largeur, hauteur)

        print("nbCouleurs",nbCouleurs)

        print("Modification de la taille de l'image ... ")
        image2 = image2.resize((largeur, hauteur))
        pixels = np.array(image2)

        print("Calcul des nouvelles couleurs ...")
        pixels = changerCouleur(couleurs, pixels)

        print("Generation des matrices de couleurs ...")
        matriceExistance = np.zeros((pixels.shape[0], pixels.shape[1]))
        matrices = generateMatricesCouleurs(couleurs, pixels, matriceExistance)

        print("Epuration des matrices de couleurs ...")
        matrices = epurerMatricesCouleurs(matrices)

        print("Calcul des gradients ...")
        matricesGradient = calculGradientMatrices(matrices)

        print("Calcul des matrices de dessin ...")
        listesDessin = calculListesDessin(matricesGradient)
        for i in range(len(listesDessin) - 1, -1, -1):
            # Vérifie si la longueur de la liste de dessin est inférieure à 30
            if len(listesDessin[i]) < 1:
                # Supprime les couleurs qui ne sont pas assez présentes
                listesDessin[i] = []
                # Affiche un message pour indiquer qu'une couleur a été supprimée
                print("Couleur supprimée")

        for i in range(len(couleurs) - 1, -1, -1):
            if np.all(couleurs[i] == [255,255,255]):
                couleurs.pop(i)
                positionsCouleurs.pop(i)

        time.sleep(1)
        for i in range(0,len(listesDessin)):
            dessiner(positionsCoins[0], listesDessin[i], positionsCouleurs[i])

        return 0

    except KeyboardInterrupt:
        print("Programme interrompu par l'utilisateur.")
        return 1

    except Exception as e:
        print(f"Une erreur est survenue: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())



