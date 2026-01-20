import pygame
import random


def creer_fichier_record():
    #attention : si le fichier record.txt existe déjà ça l'écrase (remet à zéro)
    with open("record.txt", "w") as f:
        f.write("0")
    print("Le fichier record.txt a été créé !")

#pour le premier lancement:(a commenter ensuite)
# creer_fichier_record()

# --- CONFIGURATION ----------------------------------------------------------------------------------------
LARGEUR_ECRAN, HAUTEUR_ECRAN = 1500, 900
LARGEUR_COLONNE =10
NB_COLONNES = LARGEUR_ECRAN // LARGEUR_COLONNE
FPS = 60
pente_actuelle = 0







# --- INITIALISATION ---------------------------------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
clock = pygame.time.Clock()




#création du fond d'écran coloré
trounoir = pygame.image.load("trounoir.jpg").convert()
trounoir = pygame.transform.scale(trounoir, (LARGEUR_ECRAN, HAUTEUR_ECRAN))


#--------------------------
#---création du vaisseau---
#--------------------------
image_vaisseau = pygame.image.load("vaisseau3.png").convert_alpha()#.alpha pour qu'il n'y ait pas de rectangle autour
image_vaisseau = pygame.transform.rotate(image_vaisseau, -90)#on met le vaisseau dans le bon sens
image_vaisseau = pygame.transform.scale(image_vaisseau, (80, 70))#on le met à l'échelle
vaisseau_y=450
centre_vaisseau=(250,450)
#initialisation des variables
angle_vaisseau=0
niveau_surchauffe = 0
surchauffe = False # Si True l'arme est bloquée jusqu'à refroidissement complet



#chargement des images d'astéroides
asteroide1=pygame.image.load("asteroide1.png").convert_alpha()
asteroide3=pygame.image.load("asteroide3.png").convert_alpha()
asteroide1=pygame.transform.scale(asteroide1, (100,100))
asteroide3=pygame.transform.scale(asteroide3, (100,100))


#Création du tunnel initial
#structure du tunnel: tunnel=[[y_plafond, largeur_tunnel],...]
tunnel = []
liste_etoiles=[]
liste_obstacles=[]
for i in range(NB_COLONNES + 2):
    tunnel.append([250, 400])


#________________________________________________________________________________________________________________
#__fonctions_________________________________________________________________________________________________
#________________________________________________________________________________________________________________
def reinitialiser_jeu():
    #on s'autorise le global car on utilise que peu de fonctions ici donc pas de risques que les variables buguent
    global tunnel, liste_etoiles, centre_vaisseau, angle_vaisseau,pente_actuelle, action, liste_obstacles, score, compteur_frames,niveau_surchauffe,surchauffe,best_score

    if score > best_score:#on vérifie si on a battu le record
        best_score = score
        sauvegarder_record(best_score)
        print(f"Nouveau Record enregistré : {best_score} !")
    #on vide et recrée le tunnel
    tunnel = []
    for i in range(NB_COLONNES):
        tunnel.append([250, 400])
    pente_actuelle = 0

    #on remet le vaisseau à sa place
    centre_vaisseau = (250, 450)
    angle_vaisseau = 0


    #on annule tous les statuts d'actions
    action = {"tir": False, "RIGHT": False, "LEFT": False, "LOSTUP": False, "LOSTDOWN": False}

    #suppression des obstacles
    liste_obstacles = []

    #remise à zéro du score
    score = 0
    compteur_frames = 0

    #remise à zéro de la surchauffe
    niveau_surchauffe = 0
    surchauffe = False


# ---GESTION DU RECORD ---

def charger_record():
    with open("record.txt", "r") as f:
        return int(f.read())

def sauvegarder_record(nouveau_record):
    #on écrit le nouveau chiffre dans le fichier
    with open("record.txt", "w") as f:
        f.write(str(nouveau_record))


best_score = charger_record() #on récupère le meilleur score en mémoire

#________________________________________________________________________________________________________________
# --- JEU -----------------------------------------------------------------------------------------------------
#________________________________________________________________________________________________________________

running = True


action={"tir":False,"RIGHT":False,"LEFT":False,"LOSTUP":False,"LOSTDOWN":False}
police = pygame.font.SysFont("Arial", 30, bold=True)
score = 0
compteur_frames = 0  #pour compter jusqu'à 60


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()#on récupère la touche préssée

    if keys[pygame.K_LEFT]:#actions de tourner gauche et droite
        for i in range(len(tunnel)): tunnel[i][0] += 4#on descend le tunnel
        action["LEFT"]=True
    if keys[pygame.K_RIGHT]:
        for i in range(len(tunnel)): tunnel[i][0] -= 4#on monte le tunnel
        action["RIGHT"]=True


    #_____TIR_________
    if keys[pygame.K_UP] and surchauffe == False:#pour le tir on doit vérifier que le laser ne soit pas en "surchauffe"
        action["tir"] = True
        tir_actif = True
        niveau_surchauffe += 3  #vitesse de chauffe
    else:
        #si on ne tire pas, ça refroidit
        niveau_surchauffe -= 1.5  #vitesse de refroidissement

        #on empêche de descendre sous 0
    if niveau_surchauffe < 0:
        niveau_surchauffe = 0
        surchauffe = False  # L'arme est réparée quand elle est froide !

        #on empêche de dépasser 100
    if niveau_surchauffe >= 100:
        niveau_surchauffe = 100
        surchauffe = True  #l'arme surchauffe et se bloque
        action["tir"] = False #on arrête le tir


    #mise à jour du tunnel
    #on retire la première colonne (celle qui sort à gauche)
    tunnel.pop(0)

    #variation de la hauteur (le tunnel monte ou descend)
    #on change la pente
    pente_actuelle += random.uniform(-0.7, 0.7)
    if pente_actuelle > 5: pente_actuelle = 5
    if pente_actuelle < -5: pente_actuelle = -5
    nouveau_plafond = tunnel[-1][0] + pente_actuelle


    #variation de la largeur (le tunnel se resserre ou s'élargit)
    #on change la largeur moins souvent pour éviter un effet "stroboscope"
    changement_largeur = random.choice([-2,-2,-1,0,1,1,1,1])
    nouvelle_largeur = tunnel[-1][1] + changement_largeur


    if nouvelle_largeur < 250:
        nouvelle_largeur = 250  #largeur min
    if nouvelle_largeur > 600:
        nouvelle_largeur = 600  #largeur max



    #ajout de la nouvelle colonne
    tunnel.append([nouveau_plafond, nouvelle_largeur])

    #______________________________________________________ETOILES_____________________________________________________

    nb_nouvelles_etoiles = random.choice([1,2, 3, 4])

    for _ in range(nb_nouvelles_etoiles):
        #configuration aléatoire pour la profondeur
        vitesse = random.choice([2, 3, 5, 8])  # Différentes vitesses

        #taille et couleur selon la vitesse (plus vite = plus gros/clair)
        if vitesse == 2:
            taille = 1
            couleur = (100, 100, 100)
        elif vitesse == 3:
            taille = 2
            couleur = (150, 150, 150)
        elif vitesse == 5:
            taille = 3
            couleur = (200, 200, 200)
        else:
            taille = 5
            couleur = (255, 255, 255)

        #on ajoute l'étoile, elle part de la droite (LARGEUR_ECRAN)
        #"y" est aléatoire sur toute la hauteur
        liste_etoiles.append([LARGEUR_ECRAN, random.randint(-500, 1400), vitesse, taille, couleur])

    #______________________________________________________OBSTACLES____________________________________________________

    if compteur_frames==0 or compteur_frames==40 or compteur_frames==20:#les obstacles n'apparaissent pas tout le temps
        nb_obstacles = random.choice([0,1,2])

        for _ in range(nb_obstacles):
            image_choisie = random.choice([asteroide1, asteroide3])
            vitesse=random.choice([1,2,3,4,5])
            taille=random.randint(75,150)
            #on ajoute l'obstacle
            # "y" est aléatoire sur toute la hauteur
            liste_obstacles.append([LARGEUR_ECRAN, random.randint(0, 900), vitesse, taille, image_choisie])



    #---collisions---
    #on va récupérer les corrdonnées du sol et du plafond au niveau du vaisseau
    index_vaisseau = (250 // LARGEUR_COLONNE)
    plafond = tunnel[index_vaisseau][0]
    sol = tunnel[index_vaisseau][0] + tunnel[index_vaisseau][1]  # plafond + largeur

    if vaisseau_y < (plafond+10):
        action["LOSTUP"] = True
    elif vaisseau_y > (sol-10):
        action["LOSTDOWN"] = True

    for obstacle in liste_obstacles:
        if (obstacle[0]<=250 and obstacle[0]>=240) and (obstacle[1]>=(440-obstacle[3]) and obstacle[1]<=460):#on vérifie que l'obstacle n'entre pas en collision avec le vaisseau
            action["LOSTUP"] = True



# Dessin du fond
    screen.blit(trounoir, (0, 0))  # Fond noir

    #DESSIN DU TUNNEL (AVEC TRANSPARENCE)
    for i in range(len(tunnel)):
        x = i * LARGEUR_COLONNE
        plafond = tunnel[i][0]
        largeur = tunnel[i][1]
        sol = plafond + largeur
        hauteur_rect_bas = HAUTEUR_ECRAN - sol

        # --- RECTANGLE DU HAUT ---
        # Les if évitent les bugs quand le tunnel sort de l'écran
        if plafond > 0:
            s_haut = pygame.Surface((LARGEUR_COLONNE, int(plafond)))
            s_haut.set_alpha(70)#on regle la transparence
            s_haut.fill((223, 115, 255))
            screen.blit(s_haut, (x, 0))

        # --- RECTANGLE DU BAS ---
        if hauteur_rect_bas > 0:
            s_bas = pygame.Surface((LARGEUR_COLONNE, int(hauteur_rect_bas)))
            s_bas.set_alpha(70)
            s_bas.fill((223, 115, 255))
            screen.blit(s_bas, (x, sol))

#Dessin des étoiles
    for etoile in liste_etoiles:
        #etoile = [x, y, vitesse, taille, couleur]
        #Déplacement
        etoile[0] -= etoile[2]
        etoile[1] += angle_vaisseau//4
        # Dessin ou suppression
        if etoile[0] <=0:
            liste_etoiles.remove(etoile)

        else:
            pygame.draw.rect(screen, etoile[4], (etoile[0], etoile[1], etoile[3], etoile[3]))

#Dessin des obstacles
    for obstacle in liste_obstacles:
        # obstacle = [x, y, vitesse, taille, couleur]
        #  Déplacement
        obstacle[0] -= obstacle[2]
        obstacle[1] += angle_vaisseau//7
        # Dessin ou suppression
        if obstacle[0] <=0:
            liste_obstacles.remove(obstacle)

        else:
            screen.blit(obstacle[4], (obstacle[0], obstacle[1]))

    #___________AFFICHAGE DES LASERS________________________________________

        if action["tir"] == True:
            #On crée une liste qui contient les coordonnées de nos 2 lasers
            #chaque laser est un couple : (point_depart, point_arrivee)
            lasers = []

            if angle_vaisseau >= 3:  # Tir vers le HAUT
                lasers.append(((257, 430), (1500, 250)))
                lasers.append(((257, 470), (1500, 290)))

            elif angle_vaisseau <= -3:  # Tir vers le BAS
                lasers.append(((257, 430), (1500, 650)))
                lasers.append(((257, 470), (1500, 690)))

            else:  # Tir TOUT DROIT
                lasers.append(((257, 430), (1500, 430)))
                lasers.append(((257, 470), (1500, 470)))

            # DESSIN ET COLLISIONS

            # On dessine d'abord les lasers pour l'effet visuel
            for depart, arrivee in lasers:
                pygame.draw.line(screen, (255, 0, 0), depart, arrivee, 4)
                pygame.draw.line(screen, (255, 200, 200), depart, arrivee, 2)

            # On vérifie les collisions
            # On parcourt la liste des obstacles À L'ENVERS (step = -1)
            # range(debut, fin, pas) -> De la taille-1 jusqu'à -1 (pour inclure 0)
            for i in range(len(liste_obstacles) - 1, -1, -1):
                obstacle = liste_obstacles[i]

                # On crée le rectangle de l'obstacle pour tester
                rect_obstacle = pygame.Rect(obstacle[0], obstacle[1], obstacle[3], obstacle[3])

                obstacle_touche = False

                # On vérifie si UN des 2 lasers touche cet obstacle
                for depart, arrivee in lasers:
                    if rect_obstacle.clipline(depart, arrivee):
                        obstacle_touche = True

                # Si touché, on supprime proprement avec l'index i
                if obstacle_touche == True:
                    del liste_obstacles[i]  # 'del' supprime l'élément à l'index i
                    score += 10  # On ajoute le score

            action["tir"] = False


    if action["RIGHT"]==True:
        if angle_vaisseau>-10:
            angle_vaisseau -=3
        action["RIGHT"]=False

    if action["LEFT"]==True:
        if angle_vaisseau<10:
            angle_vaisseau += 3
        action["LEFT"]=False

    # Si aucune touche n'est active, on revient doucement vers 0
    if not action["RIGHT"] and not action["LEFT"]:
        if angle_vaisseau > 0:
            angle_vaisseau -= 1  # On redescend
        elif angle_vaisseau < 0:
            angle_vaisseau += 1  # On remonte


    if action["LOSTUP"]==True:
        screen.blit(trounoir, (0, 0))

        x,y=centre_vaisseau
        x-=3
        centre_vaisseau = (x, y)
        angle_vaisseau += 10
        if x <-30:
            print("Fin de partie - Relance !")
            reinitialiser_jeu()
            pygame.time.delay(300)

    if action["LOSTDOWN"]==True:
        screen.blit(trounoir, (0, 0))  # Fond noir

        x, y = centre_vaisseau
        x -= 3
        centre_vaisseau = (x, y)
        angle_vaisseau -= 10
        if x <-30:
            print("Fin de partie - Relance !")
            reinitialiser_jeu()
            pygame.time.delay(300)


    if not action["LOSTUP"] and not action["LOSTDOWN"]:
        compteur_frames += 1
        if compteur_frames >= 60:  # Tous les 60 tours de boucle
            score += 1  # On gagne 1 point
            compteur_frames = 0  # On remet le compteur à 0



    # On crée une NOUVELLE image temporaire en tournant l'ORIGINALE
    image_a_afficher = pygame.transform.rotate(image_vaisseau, angle_vaisseau)
    # On récupère le rectangle de cette nouvelle image
    rect_a_afficher = image_a_afficher.get_rect()
    rect_a_afficher.center = centre_vaisseau
    # DESSIN
    screen.blit(image_a_afficher, rect_a_afficher)


    #SCORE
    image_score = police.render(f"SCORE: {score}", True, (255, 255, 255))
    # Affichage en haut à gauche (x=20, y=20)
    screen.blit(image_score, (20, 20))
    texte_best = police.render(f"BEST: {best_score}", True, (255, 255, 255))
    screen.blit(texte_best, (1300, 20))



    # -------BARRE DE SURCHAUFFE------------
    #On définit les variables de position pour que ce soit plus lisible
    x_barre = 20
    y_barre = 840
    largeur_max = 400
    hauteur_barre = 40
    pygame.draw.rect(screen, (50, 50, 50), (x_barre, y_barre, largeur_max, hauteur_barre))
    #Couleur de la barre
    if surchauffe:
        couleur_barre = (255, 0, 0)
    else:
        vert = int(255 - (niveau_surchauffe * 2.55))
        if vert < 0: vert = 0
        couleur_barre = (255, vert, 0)
    #dessin de la barre
    longueur_barre = (niveau_surchauffe / 100) * largeur_max
    pygame.draw.rect(screen, couleur_barre, (x_barre, y_barre, longueur_barre, hauteur_barre))
    pygame.draw.rect(screen, (255, 255, 255), (x_barre, y_barre, largeur_max, hauteur_barre), 3)



    #la vitesse du jeu augmente jusqu'à 130 fps
    bonus_vitesse = (score ** 0.5)*3 #la progression est de moins en moins rapide(courbe de racine carré)
    FPS = 60+ int(bonus_vitesse)
    if FPS > 130:
        FPS = 130

    pygame.display.flip()
    clock.tick(FPS)
    #Affiche les FPS réels dans la console
    if compteur_frames == 0:
        print(clock.get_fps())

pygame.quit()