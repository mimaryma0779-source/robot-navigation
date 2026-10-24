import random
import pygame
from collections import deque

# --- Réglages ---
TAILLE_CASE = 90       # taille d'une case en pixels
HAUTEUR_BARRE = 80     # hauteur de la barre du bas
VITESSE = 3            # vitesse du robot (pixels par image)
DELAI_ALEATOIRE = 1000 # un obstacle apparaît/disparaît toutes les 1000 ms (mode aléatoire)
DENSITE_MAX = 0.35     # au-delà, le mode aléatoire ne fait que retirer des obstacles

# --- La grille : 0 = case libre, 1 = obstacle ---
grille = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
]

depart = (0, 0)        # (ligne, colonne) du robot
destination = (5, 7)   # (ligne, colonne) de l'arrivée

# --- Couleurs ---
SOL_1 = (248, 250, 248)
SOL_2 = (212, 224, 212)
LIGNE_GRILLE = (90, 105, 95)
BRIQUE = (160, 72, 50)
MORTIER = (215, 205, 195)
CORPS = (60, 120, 215)
TETE = (205, 215, 230)
CONTOUR = (40, 50, 70)
ROUE = (45, 45, 50)
YEUX = (80, 220, 255)
LAMPE = (255, 200, 40)
MAT = (110, 75, 40)
DRAPEAU = (225, 50, 50)
BASE = (70, 170, 90)
CHEMIN = (255, 140, 0)
BARRE = (35, 40, 55)
TEXTE = (240, 240, 240)
TEXTE_DISCRET = (170, 178, 195)
BOUTON = (50, 160, 90)
BOUTON_SURVOL = (70, 190, 110)
BOUTON_GRIS = (110, 115, 125)
BOUTON_ALEA = (190, 110, 40)
BOUTON_ALEA_SURVOL = (215, 135, 60)

nb_lignes = len(grille)
nb_colonnes = len(grille[0])
LARGEUR = nb_colonnes * TAILLE_CASE
HAUTEUR_GRILLE = nb_lignes * TAILLE_CASE


def rect(x, y, largeur, hauteur):
    """Crée un rectangle avec des nombres entiers."""
    return pygame.Rect(int(x), int(y), int(largeur), int(hauteur))


# ------------------------------------------------------------
# Recherche du chemin (BFS)
# ------------------------------------------------------------
def trouver_chemin(grille, depart, arrivee):
    """Renvoie la liste des cases du départ à l'arrivée (liste vide si impossible)."""
    file = deque([depart])
    precedent = {depart: None}   # pour chaque case : d'où on vient

    while file:
        actuel = file.popleft()
        if actuel == arrivee:
            break
        ligne, colonne = actuel
        for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nl, nc = ligne + dl, colonne + dc
            voisin = (nl, nc)
            if (0 <= nl < nb_lignes and 0 <= nc < nb_colonnes
                    and grille[nl][nc] == 0 and voisin not in precedent):
                precedent[voisin] = actuel
                file.append(voisin)

    if arrivee not in precedent:
        return []   # aucun chemin trouvé

    chemin = []
    case = arrivee
    while case is not None:
        chemin.append(case)
        case = precedent[case]
    chemin.reverse()
    return chemin


# ------------------------------------------------------------
# Dessin
# ------------------------------------------------------------
def dessiner_sol(fenetre, x, y, ligne, colonne):
    couleur = SOL_1 if (ligne + colonne) % 2 == 0 else SOL_2
    pygame.draw.rect(fenetre, couleur, rect(x, y, TAILLE_CASE, TAILLE_CASE))


def dessiner_mur(fenetre, x, y):
    t = TAILLE_CASE
    pygame.draw.rect(fenetre, BRIQUE, rect(x, y, t, t))
    hauteur = t // 4
    for rang in range(4):
        yy = y + rang * hauteur
        pygame.draw.line(fenetre, MORTIER, (x, yy), (x + t, yy), 2)
        decalage = 0 if rang % 2 == 0 else t // 4
        for k in range(-1, 3):
            vx = x + decalage + k * (t // 2)
            if x < vx < x + t:
                pygame.draw.line(fenetre, MORTIER, (vx, yy), (vx, yy + hauteur), 2)
    pygame.draw.rect(fenetre, MORTIER, rect(x, y, t, t), 2)


def dessiner_drapeau(fenetre, x, y):
    t = TAILLE_CASE
    pygame.draw.ellipse(fenetre, BASE, rect(x + t * 0.2, y + t * 0.78, t * 0.5, t * 0.14))
    pygame.draw.line(fenetre, MAT, (x + t * 0.35, y + t * 0.15), (x + t * 0.35, y + t * 0.85), 4)
    pointes = [
        (x + t * 0.35, y + t * 0.15),
        (x + t * 0.82, y + t * 0.30),
        (x + t * 0.35, y + t * 0.45),
    ]
    pygame.draw.polygon(fenetre, DRAPEAU, pointes)
    pygame.draw.polygon(fenetre, CONTOUR, pointes, 2)


def dessiner_robot(fenetre, x, y):
    t = TAILLE_CASE
    pygame.draw.rect(fenetre, ROUE, rect(x + t * 0.15, y + t * 0.78, t * 0.22, t * 0.15), border_radius=4)
    pygame.draw.rect(fenetre, ROUE, rect(x + t * 0.63, y + t * 0.78, t * 0.22, t * 0.15), border_radius=4)
    corps = rect(x + t * 0.2, y + t * 0.45, t * 0.6, t * 0.38)
    pygame.draw.rect(fenetre, CORPS, corps, border_radius=8)
    pygame.draw.rect(fenetre, CONTOUR, corps, 2, border_radius=8)
    pygame.draw.circle(fenetre, LAMPE, (int(x + t * 0.5), int(y + t * 0.64)), int(t * 0.07))
    pygame.draw.line(fenetre, CONTOUR, (x + t * 0.5, y + t * 0.18), (x + t * 0.5, y + t * 0.07), 3)
    pygame.draw.circle(fenetre, DRAPEAU, (int(x + t * 0.5), int(y + t * 0.07)), int(t * 0.045))
    tete = rect(x + t * 0.25, y + t * 0.18, t * 0.5, t * 0.3)
    pygame.draw.rect(fenetre, TETE, tete, border_radius=8)
    pygame.draw.rect(fenetre, CONTOUR, tete, 2, border_radius=8)
    pygame.draw.circle(fenetre, YEUX, (int(x + t * 0.39), int(y + t * 0.33)), int(t * 0.06))
    pygame.draw.circle(fenetre, YEUX, (int(x + t * 0.61), int(y + t * 0.33)), int(t * 0.06))


def dessiner_lignes_grille(fenetre):
    """Traits bien visibles entre les cases."""
    for c in range(nb_colonnes + 1):
        x = c * TAILLE_CASE
        pygame.draw.line(fenetre, LIGNE_GRILLE, (x, 0), (x, HAUTEUR_GRILLE), 2)
    for l in range(nb_lignes + 1):
        y = l * TAILLE_CASE
        pygame.draw.line(fenetre, LIGNE_GRILLE, (0, y), (LARGEUR, y), 2)


def dessiner_chemin(fenetre, points):
    if len(points) < 2:
        return
    pygame.draw.lines(fenetre, CHEMIN, False, points, 6)
    for point in points[1:]:
        pygame.draw.circle(fenetre, CHEMIN, point, 6)


def centre_case(ligne, colonne):
    return (colonne * TAILLE_CASE + TAILLE_CASE // 2,
            ligne * TAILLE_CASE + TAILLE_CASE // 2)


def dessiner_bouton(fenetre, police, bouton, texte, couleur):
    pygame.draw.rect(fenetre, couleur, bouton, border_radius=10)
    pygame.draw.rect(fenetre, TEXTE, bouton, 2, border_radius=10)
    label = police.render(texte, True, TEXTE)
    fenetre.blit(label, label.get_rect(center=bouton.center))


def dessiner_barre(fenetre, police, petite_police, message, info,
                   texte_bouton, actif, survol, bouton,
                   texte_alea, survol_alea, bouton_alea):
    pygame.draw.rect(fenetre, BARRE, rect(0, HAUTEUR_GRILLE, LARGEUR, HAUTEUR_BARRE))

    image = police.render(message, True, TEXTE)
    fenetre.blit(image, (15, HAUTEUR_GRILLE + 12))
    image2 = petite_police.render(info, True, TEXTE_DISCRET)
    fenetre.blit(image2, (15, HAUTEUR_GRILLE + 46))

    if not actif:
        couleur = BOUTON_GRIS
    elif survol:
        couleur = BOUTON_SURVOL
    else:
        couleur = BOUTON
    dessiner_bouton(fenetre, police, bouton, texte_bouton, couleur)

    couleur_alea = BOUTON_ALEA_SURVOL if survol_alea else BOUTON_ALEA
    dessiner_bouton(fenetre, police, bouton_alea, texte_alea, couleur_alea)


# ------------------------------------------------------------
# Programme principal
# ------------------------------------------------------------
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR_GRILLE + HAUTEUR_BARRE))
pygame.display.set_caption("Robot - Navigation dynamique (Niveau 2)")
horloge = pygame.time.Clock()
police = pygame.font.SysFont("arial", 20, bold=True)
petite_police = pygame.font.SysFont("arial", 14)

bouton = pygame.Rect(LARGEUR - 185, HAUTEUR_GRILLE + 17, 170, 46)
bouton_alea = pygame.Rect(LARGEUR - 185 - 10 - 170, HAUTEUR_GRILLE + 17, 170, 46)

# États possibles : "attente", "en_route", "arrive", "bloque"
etat = "attente"
chemin = []
index = 0               # case que le robot est en train de rejoindre (chemin[index])
case_courante = depart  # dernière case atteinte par le robot
bloque_en_route = False # True : le robot va juste se mettre à l'abri, aucun chemin n'existe
nb_replanifications = 0
mode_aleatoire = False
dernier_evenement = 0

# Position du robot en pixels (coin haut-gauche)
robot_x = depart[1] * TAILLE_CASE
robot_y = depart[0] * TAILLE_CASE


# ------------------------------------------------------------
# Gestion des obstacles dynamiques
# ------------------------------------------------------------
def cases_protegees():
    """Cases où l'on ne peut pas poser d'obstacle : robot, case visée, destination."""
    protegees = {case_courante, destination}
    if etat == "en_route" and index < len(chemin):
        protegees.add(chemin[index])
    return protegees


def chemin_bloque():
    """Vrai si une case restante du chemin est devenue un obstacle."""
    return any(grille[l][c] == 1 for (l, c) in chemin[index:])


def replanifier():
    """Recalcule un chemin quand le robot est en mouvement et que son chemin est coupé.
    Le robot est entre case_courante et chemin[index]. Il peut :
      1) terminer son pas vers chemin[index] (si cette case est libre) puis repartir,
      2) sinon faire demi-tour vers case_courante puis repartir,
      3) s'il n'existe aucun chemin, aller se mettre à l'abri et attendre."""
    global chemin, index, bloque_en_route, nb_replanifications, etat
    cible = chemin[index]

    if grille[cible[0]][cible[1]] == 0:
        nouveau = trouver_chemin(grille, cible, destination)
        if nouveau:
            chemin = [case_courante] + nouveau
            index = 1
            bloque_en_route = False
            nb_replanifications += 1
            return

    nouveau = trouver_chemin(grille, case_courante, destination)
    if nouveau:
        chemin = [cible] + nouveau        # chemin[1] = case_courante : demi-tour
        index = 1
        bloque_en_route = False
        nb_replanifications += 1
        return

    # Aucun chemin : le robot rejoint une case libre et attend
    if grille[cible[0]][cible[1]] == 0:
        chemin = [case_courante, cible]
    else:
        chemin = [cible, case_courante]
    index = 1
    bloque_en_route = True


def reessayer_depuis_arret():
    """Robot à l'arrêt (état 'bloque') : un obstacle a changé, on retente."""
    global chemin, index, etat, nb_replanifications
    nouveau = trouver_chemin(grille, case_courante, destination)
    if nouveau:
        chemin = nouveau
        index = 1
        etat = "en_route"
        nb_replanifications += 1


def apres_changement():
    """À appeler après chaque apparition/disparition d'obstacle."""
    if etat == "en_route" and chemin_bloque():
        replanifier()
    elif etat == "bloque":
        reessayer_depuis_arret()


def basculer_obstacle(ligne, colonne):
    if (ligne, colonne) in cases_protegees():
        return
    grille[ligne][colonne] = 1 - grille[ligne][colonne]
    apres_changement()


def evenement_aleatoire():
    """Fait apparaître ou disparaître un obstacle au hasard."""
    protegees = cases_protegees()
    libres = [(l, c) for l in range(nb_lignes) for c in range(nb_colonnes)
              if grille[l][c] == 0 and (l, c) not in protegees]
    murs = [(l, c) for l in range(nb_lignes) for c in range(nb_colonnes)
            if grille[l][c] == 1]
    densite = len(murs) / (nb_lignes * nb_colonnes)
    if murs and (densite > DENSITE_MAX or not libres or random.random() < 0.4):
        l, c = random.choice(murs)
    elif libres:
        l, c = random.choice(libres)
    else:
        return
    grille[l][c] = 1 - grille[l][c]
    apres_changement()


continuer = True
while continuer:
    souris = pygame.mouse.get_pos()
    maintenant = pygame.time.get_ticks()

    # --- Événements ---
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            continuer = False
        elif evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            x_clic, y_clic = evenement.pos
            if bouton.collidepoint(evenement.pos):
                if etat == "attente":
                    chemin = trouver_chemin(grille, depart, destination)
                    case_courante = depart
                    nb_replanifications = 0
                    if chemin:
                        etat = "en_route"
                        index = 1
                    else:
                        etat = "bloque"
                elif etat in ("arrive", "bloque"):
                    # Recommencer
                    etat = "attente"
                    chemin = []
                    index = 0
                    bloque_en_route = False
                    case_courante = depart
                    grille[depart[0]][depart[1]] = 0
                    robot_x = depart[1] * TAILLE_CASE
                    robot_y = depart[0] * TAILLE_CASE
            elif bouton_alea.collidepoint(evenement.pos):
                mode_aleatoire = not mode_aleatoire
                dernier_evenement = maintenant
            elif y_clic < HAUTEUR_GRILLE:
                # Clic sur la grille : ajouter / retirer un obstacle
                basculer_obstacle(y_clic // TAILLE_CASE, x_clic // TAILLE_CASE)

    # --- Obstacles aléatoires ---
    if mode_aleatoire and maintenant - dernier_evenement >= DELAI_ALEATOIRE:
        dernier_evenement = maintenant
        evenement_aleatoire()

    # --- Déplacement du robot ---
    if etat == "en_route":
        cible_x = chemin[index][1] * TAILLE_CASE
        cible_y = chemin[index][0] * TAILLE_CASE
        dx = cible_x - robot_x
        dy = cible_y - robot_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance <= VITESSE:
            robot_x, robot_y = cible_x, cible_y
            case_courante = chemin[index]
            index += 1
            if index >= len(chemin):
                etat = "bloque" if bloque_en_route else "arrive"
                bloque_en_route = False
        else:
            robot_x += VITESSE * dx / distance
            robot_y += VITESSE * dy / distance

    # --- Dessin ---
    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            x = colonne * TAILLE_CASE
            y = ligne * TAILLE_CASE
            if grille[ligne][colonne] == 1:
                dessiner_mur(fenetre, x, y)
            else:
                dessiner_sol(fenetre, x, y, ligne, colonne)
    dessiner_lignes_grille(fenetre)

    # La ligne va toujours du robot jusqu'à la destination (mise à jour à chaque replanification)
    if etat == "en_route" and not bloque_en_route:
        points = [(int(robot_x + TAILLE_CASE / 2), int(robot_y + TAILLE_CASE / 2))]
        for (l, c) in chemin[index:]:
            points.append(centre_case(l, c))
        dessiner_chemin(fenetre, points)

    dessiner_drapeau(fenetre, destination[1] * TAILLE_CASE, destination[0] * TAILLE_CASE)
    dessiner_robot(fenetre, robot_x, robot_y)

    # --- Barre du bas ---
    if etat == "attente":
        message, texte_bouton, actif = "Cliquez sur Démarrer", "Démarrer", True
    elif etat == "en_route":
        message, texte_bouton, actif = "Le robot se déplace...", "En cours...", False
    elif etat == "arrive":
        message, texte_bouton, actif = "Destination atteinte !", "Recommencer", True
    else:
        message, texte_bouton, actif = "Aucun chemin : en attente...", "Recommencer", True

    info = "Clic sur une case = obstacle | Replanifications : " + str(nb_replanifications)
    texte_alea = "Aléatoire : " + ("OUI" if mode_aleatoire else "NON")

    survol = actif and bouton.collidepoint(souris)
    survol_alea = bouton_alea.collidepoint(souris)
    dessiner_barre(fenetre, police, petite_police, message, info,
                   texte_bouton, actif, survol, bouton,
                   texte_alea, survol_alea, bouton_alea)

    pygame.display.flip()
    horloge.tick(60)

pygame.quit()
