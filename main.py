import pygame
from collections import deque

# --- Réglages ---
TAILLE_CASE = 90       # taille d'une case en pixels
HAUTEUR_BARRE = 70     # hauteur de la barre du bas (bouton + message)
VITESSE = 4            # vitesse du robot (pixels par image)

# --- La grille : 0 = case libre, 1 = obstacle ---
grille = [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
]

depart = (0, 0)        # (ligne, colonne) du robot
destination = (3, 4)   # (ligne, colonne) de l'arrivée

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
BOUTON = (50, 160, 90)
BOUTON_SURVOL = (70, 190, 110)
BOUTON_GRIS = (110, 115, 125)

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


def dessiner_barre(fenetre, police, message, texte_bouton, actif, survol, bouton):
    pygame.draw.rect(fenetre, BARRE, rect(0, HAUTEUR_GRILLE, LARGEUR, HAUTEUR_BARRE))
    image = police.render(message, True, TEXTE)
    fenetre.blit(image, (15, HAUTEUR_GRILLE + (HAUTEUR_BARRE - image.get_height()) // 2))

    if not actif:
        couleur = BOUTON_GRIS
    elif survol:
        couleur = BOUTON_SURVOL
    else:
        couleur = BOUTON
    pygame.draw.rect(fenetre, couleur, bouton, border_radius=10)
    pygame.draw.rect(fenetre, TEXTE, bouton, 2, border_radius=10)
    label = police.render(texte_bouton, True, TEXTE)
    fenetre.blit(label, label.get_rect(center=bouton.center))


# ------------------------------------------------------------
# Programme principal
# ------------------------------------------------------------
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR_GRILLE + HAUTEUR_BARRE))
pygame.display.set_caption("Robot - Navigation")
horloge = pygame.time.Clock()
police = pygame.font.SysFont("arial", 20, bold=True)

bouton = pygame.Rect(LARGEUR - 175, HAUTEUR_GRILLE + 12, 160, 46)

# États possibles : "attente", "en_route", "arrive", "bloque"
etat = "attente"
chemin = []
index = 0   # prochaine case à atteindre dans le chemin

# Position du robot en pixels (coin haut-gauche de sa case)
robot_x = depart[1] * TAILLE_CASE
robot_y = depart[0] * TAILLE_CASE

continuer = True
while continuer:
    souris = pygame.mouse.get_pos()

    # --- Événements ---
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            continuer = False
        elif evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            if bouton.collidepoint(evenement.pos):
                if etat == "attente":
                    chemin = trouver_chemin(grille, depart, destination)
                    if chemin:
                        etat = "en_route"
                        index = 1
                    else:
                        etat = "bloque"
                elif etat in ("arrive", "bloque"):
                    # Recommencer
                    etat = "attente"
                    chemin = []
                    robot_x = depart[1] * TAILLE_CASE
                    robot_y = depart[0] * TAILLE_CASE

    # --- Déplacement du robot ---
    if etat == "en_route":
        cible_x = chemin[index][1] * TAILLE_CASE
        cible_y = chemin[index][0] * TAILLE_CASE
        dx = cible_x - robot_x
        dy = cible_y - robot_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance <= VITESSE:
            robot_x, robot_y = cible_x, cible_y
            index += 1
            if index >= len(chemin):
                etat = "arrive"
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

    # La ligne va du robot jusqu'à la destination (visible seulement après le clic)
    if etat == "en_route":
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
        message, texte_bouton, actif = "Aucun chemin possible", "Recommencer", True

    survol = actif and bouton.collidepoint(souris)
    dessiner_barre(fenetre, police, message, texte_bouton, actif, survol, bouton)

    pygame.display.flip()
    horloge.tick(60)

pygame.quit()
