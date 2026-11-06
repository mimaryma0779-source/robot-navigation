import heapq
import math
import random
from collections import deque
from time import perf_counter

import pygame

# ------------------------------------------------------------
# Réglages
# ------------------------------------------------------------
TAILLE_CASE = 56
HAUTEUR_BARRE = 70
LARGEUR_PANNEAU = 290
VITESSE = 4
SQRT2 = math.sqrt(2)

# Limites de temps de calcul proposées (en millisecondes)
LIMITES_MS = [0.05, 1, 5, 20, 100, 1000]

NOMS_ALGOS = ["BFS", "Dijkstra", "A*", "Glouton"]
BFS, DIJKSTRA, ASTAR, GLOUTON = 0, 1, 2, 3

# 0 = libre, 1 = obstacle
PLAN = [
    "..............",
    ".####..#####..",
    ".#..#..#...#..",
    ".#..#..#.#.#..",
    ".#.....#.#....",
    ".#######.####.",
    "..........#...",
    ".########.#.#.",
    "........#...#.",
    "####.##...#...",
]
grille = [[1 if ch == "#" else 0 for ch in ligne] for ligne in PLAN]

depart = (0, 0)
destination = (9, 13)

nb_lignes = len(grille)
nb_colonnes = len(grille[0])
LARGEUR_GRILLE = nb_colonnes * TAILLE_CASE
HAUTEUR_GRILLE = nb_lignes * TAILLE_CASE
LARGEUR = LARGEUR_GRILLE + LARGEUR_PANNEAU
HAUTEUR = HAUTEUR_GRILLE + HAUTEUR_BARRE

# ------------------------------------------------------------
# Couleurs
# ------------------------------------------------------------
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
CHEMIN_PARTIEL = (170, 60, 200)
BARRE = (35, 40, 55)
PANNEAU = (28, 32, 44)
TEXTE = (240, 240, 240)
TEXTE_DISCRET = (160, 170, 185)
BOUTON = (50, 160, 90)
BOUTON_SURVOL = (70, 190, 110)
BOUTON_GRIS = (110, 115, 125)
BOUTON_PANNEAU = (60, 70, 95)
BOUTON_ACTIF = (60, 120, 215)


def rect(x, y, largeur, hauteur):
    return pygame.Rect(int(x), int(y), int(largeur), int(hauteur))


# ------------------------------------------------------------
# Outils sur la grille
# ------------------------------------------------------------
def libre(ligne, colonne):
    return (0 <= ligne < nb_lignes and 0 <= colonne < nb_colonnes
            and grille[ligne][colonne] == 0)


def voisins(case, diagonales):
    """Cases voisines accessibles, avec le coût du pas (1 ou racine de 2).
    Une diagonale est interdite si elle 'coupe le coin' d'un obstacle."""
    ligne, colonne = case
    for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if libre(ligne + dl, colonne + dc):
            yield (ligne + dl, colonne + dc), 1.0
    if diagonales:
        for dl, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (libre(ligne + dl, colonne + dc)
                    and libre(ligne + dl, colonne)
                    and libre(ligne, colonne + dc)):
                yield (ligne + dl, colonne + dc), SQRT2


def pas_valide(a, b):
    """Le pas a -> b est-il toujours possible avec la grille actuelle ?"""
    if not libre(b[0], b[1]):
        return False
    if a[0] != b[0] and a[1] != b[1]:   # pas diagonal : pas de coin coupé
        return libre(a[0], b[1]) and libre(b[0], a[1])
    return True


def chemin_valide(chemin, debut):
    """Vérifie les pas de chemin[debut-1] jusqu'à la fin."""
    for i in range(max(debut, 1), len(chemin)):
        if not pas_valide(chemin[i - 1], chemin[i]):
            return False
    return True


def heuristique(case, but, diagonales):
    """Distance estimée jusqu'au but (ne surestime jamais -> A* optimal)."""
    dl = abs(case[0] - but[0])
    dc = abs(case[1] - but[1])
    if diagonales:
        return (dl + dc) + (SQRT2 - 2) * min(dl, dc)   # distance « octile »
    return dl + dc                                      # distance de Manhattan


def cout_chemin(chemin):
    total = 0.0
    for i in range(1, len(chemin)):
        total += math.hypot(chemin[i][0] - chemin[i - 1][0],
                            chemin[i][1] - chemin[i - 1][1])
    return total


# ------------------------------------------------------------
# Recherche du chemin : BFS / Dijkstra / A* / Glouton
# avec un temps de calcul borné
# ------------------------------------------------------------
def rechercher(algo, source, but, diagonales, limite_ms):
    """
    Renvoie un dictionnaire :
      chemin   : liste de cases (vide si aucun chemin)
      cout     : longueur du chemin
      explores : nombre de cases développées
      temps    : temps de calcul en ms
      statut   : "ok" (chemin complet), "partiel" (temps dépassé) ou "aucun"
      zone     : ensemble des cases développées (pour l'affichage)
    Si le temps est dépassé, on renvoie le chemin vers la case développée
    la plus proche du but : le robot avance quand même, puis on recalcule.
    """
    t0 = perf_counter()
    limite = limite_ms / 1000.0

    precedent = {source: None}
    g = {source: 0.0}
    developpees = set()
    trouve = False
    statut = "ok"
    compteur = 0   # départage les égalités dans le tas

    if algo == BFS:
        ouvert = deque([source])
    else:
        ouvert = [(0.0, 0, source)]

    while ouvert:
        if perf_counter() - t0 > limite:
            statut = "partiel"
            break

        if algo == BFS:
            actuel = ouvert.popleft()
        else:
            _, _, actuel = heapq.heappop(ouvert)
            if actuel in developpees:
                continue
        developpees.add(actuel)

        if actuel == but:
            trouve = True
            break

        for voisin, pas in voisins(actuel, diagonales):
            nouveau_g = g[actuel] + pas
            if algo == BFS:
                if voisin not in precedent:
                    precedent[voisin] = actuel
                    g[voisin] = nouveau_g
                    ouvert.append(voisin)
            else:
                if voisin in g and (algo == GLOUTON or nouveau_g >= g[voisin] - 1e-12):
                    continue
                g[voisin] = nouveau_g
                precedent[voisin] = actuel
                h = heuristique(voisin, but, diagonales)
                if algo == DIJKSTRA:
                    priorite = nouveau_g
                elif algo == ASTAR:
                    priorite = nouveau_g + h
                else:
                    priorite = h
                compteur += 1
                heapq.heappush(ouvert, (priorite, compteur, voisin))

    temps = (perf_counter() - t0) * 1000.0

    if trouve:
        fin = but
    elif statut == "partiel":
        if developpees:
            fin = min(developpees, key=lambda c: (heuristique(c, but, diagonales), g[c]))
        else:
            fin = source
    else:
        return {"chemin": [], "cout": 0.0, "explores": len(developpees),
                "temps": temps, "statut": "aucun", "zone": developpees}

    chemin = []
    case = fin
    while case is not None:
        chemin.append(case)
        case = precedent[case]
    chemin.reverse()
    return {"chemin": chemin, "cout": cout_chemin(chemin),
            "explores": len(developpees), "temps": temps,
            "statut": statut, "zone": developpees}


def comparer_algos(source, but, diagonales, limite_ms, repetitions=20):
    """Lance les 4 algorithmes sur la grille actuelle (temps moyen sur plusieurs essais)."""
    resultats = []
    for algo in range(4):
        total = 0.0
        res = None
        for _ in range(repetitions):
            res = rechercher(algo, source, but, diagonales, limite_ms)
            total += res["temps"]
        resultats.append((NOMS_ALGOS[algo], total / repetitions,
                          res["cout"], res["explores"], res["statut"]))
    print("\n--- Comparaison (diagonales : %s, limite : %s ms) ---" % (diagonales, limite_ms))
    print("%-10s %10s %10s %10s  %s" % ("Algo", "Temps ms", "Longueur", "Explorees", "Statut"))
    for nom, t, c, e, s in resultats:
        print("%-10s %10.3f %10.2f %10d  %s" % (nom, t, c, e, s))
    return resultats


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
    pointes = [(x + t * 0.35, y + t * 0.15), (x + t * 0.82, y + t * 0.30), (x + t * 0.35, y + t * 0.45)]
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
    for c in range(nb_colonnes + 1):
        x = c * TAILLE_CASE
        pygame.draw.line(fenetre, LIGNE_GRILLE, (x, 0), (x, HAUTEUR_GRILLE), 2)
    for l in range(nb_lignes + 1):
        y = l * TAILLE_CASE
        pygame.draw.line(fenetre, LIGNE_GRILLE, (0, y), (LARGEUR_GRILLE, y), 2)


def dessiner_chemin(fenetre, points, couleur):
    if len(points) < 2:
        return
    pygame.draw.lines(fenetre, couleur, False, points, 6)
    for point in points[1:]:
        pygame.draw.circle(fenetre, couleur, point, 6)


def centre_case(ligne, colonne):
    return (colonne * TAILLE_CASE + TAILLE_CASE // 2,
            ligne * TAILLE_CASE + TAILLE_CASE // 2)


def dessiner_bouton(fenetre, police, zone, texte, couleur):
    pygame.draw.rect(fenetre, couleur, zone, border_radius=8)
    pygame.draw.rect(fenetre, TEXTE, zone, 1, border_radius=8)
    label = police.render(texte, True, TEXTE)
    fenetre.blit(label, label.get_rect(center=zone.center))


# ------------------------------------------------------------
# Initialisation
# ------------------------------------------------------------
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Robot - Navigation (niveau 3)")
horloge = pygame.time.Clock()
police = pygame.font.SysFont("arial", 20, bold=True)
police_petite = pygame.font.SysFont("arial", 15)
police_petite_gras = pygame.font.SysFont("arial", 15, bold=True)

bouton = pygame.Rect(LARGEUR - 175, HAUTEUR_GRILLE + 12, 160, 46)

# Boutons du panneau (x relatif au panneau)
PX = LARGEUR_GRILLE + 15
boutons_panneau = {}
for i in range(4):
    boutons_panneau["algo%d" % i] = pygame.Rect(PX, 40 + i * 32, 260, 28)
boutons_panneau["diag"] = pygame.Rect(PX, 175, 260, 28)
boutons_panneau["zone"] = pygame.Rect(PX, 208, 260, 28)
boutons_panneau["comparer"] = pygame.Rect(PX, 241, 125, 28)
boutons_panneau["alea"] = pygame.Rect(PX + 135, 241, 125, 28)
boutons_panneau["moins"] = pygame.Rect(PX + 170, 280, 40, 26)
boutons_panneau["plus"] = pygame.Rect(PX + 220, 280, 40, 26)

# Paramètres modifiables
algo = ASTAR
diagonales = False
montrer_zone = True
indice_limite = 3          # 20 ms par défaut
comparaison = []

# État du robot
etat = "attente"           # "attente", "en_route", "coince", "arrive"
chemin = []
index = 1
stats = None               # résultat de la dernière recherche
zone_explorée = set()
robot_x = depart[1] * TAILLE_CASE
robot_y = depart[0] * TAILLE_CASE


def limite_ms():
    return LIMITES_MS[indice_limite]


def appliquer_resultat(res):
    """Mémorise le résultat d'une recherche pour l'affichage."""
    global stats, zone_explorée
    stats = res
    zone_explorée = res["zone"]


def reinitialiser():
    """Remet le robot au départ et recalcule le chemin."""
    global etat, chemin, index, robot_x, robot_y
    robot_x = depart[1] * TAILLE_CASE
    robot_y = depart[0] * TAILLE_CASE
    res = rechercher(algo, depart, destination, diagonales, limite_ms())
    appliquer_resultat(res)
    chemin = res["chemin"] if res["statut"] != "aucun" else []
    index = 1
    etat = "attente"


def remplacer_trajet(res, quittee):
    """Adopte un nouveau trajet : [case quittée] + chemin trouvé depuis la case visée."""
    global chemin, index
    appliquer_resultat(res)
    chemin = [quittee] + res["chemin"]
    index = 1


def obstacles_aleatoires(densite=0.25):
    for l in range(nb_lignes):
        for c in range(nb_colonnes):
            if (l, c) in (depart, destination):
                grille[l][c] = 0
            else:
                grille[l][c] = 1 if random.random() < densite else 0


def action_panneau(nom):
    global algo, diagonales, montrer_zone, indice_limite, comparaison
    if nom == "zone":
        montrer_zone = not montrer_zone
        return
    if nom == "comparer":
        comparaison = comparer_algos(depart, destination, diagonales, limite_ms())
        return
    if etat == "en_route":
        return   # on ne change pas la configuration pendant le déplacement
    if nom.startswith("algo"):
        algo = int(nom[4])
    elif nom == "diag":
        diagonales = not diagonales
    elif nom == "moins":
        indice_limite = max(0, indice_limite - 1)
    elif nom == "plus":
        indice_limite = min(len(LIMITES_MS) - 1, indice_limite + 1)
    elif nom == "alea":
        obstacles_aleatoires()
    comparaison = []
    reinitialiser()


reinitialiser()

# ------------------------------------------------------------
# Boucle principale
# ------------------------------------------------------------
continuer = True
while continuer:
    souris = pygame.mouse.get_pos()

    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            continuer = False

        elif evenement.type == pygame.KEYDOWN:
            if evenement.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4):
                action_panneau("algo%d" % (evenement.key - pygame.K_F1))
            elif evenement.key == pygame.K_d:
                action_panneau("diag")
            elif evenement.key == pygame.K_c:
                action_panneau("comparer")
            elif evenement.key == pygame.K_e:
                action_panneau("zone")
            elif evenement.key == pygame.K_r:
                action_panneau("alea")
            elif evenement.key == pygame.K_UP:
                action_panneau("plus")
            elif evenement.key == pygame.K_DOWN:
                action_panneau("moins")

        elif evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            # ----- Bouton principal -----
            if bouton.collidepoint(evenement.pos):
                if etat == "attente":
                    if len(chemin) > 1:
                        etat = "en_route"
                        index = 1
                elif etat in ("arrive", "coince"):
                    reinitialiser()

            # ----- Panneau de droite -----
            elif evenement.pos[0] >= LARGEUR_GRILLE and evenement.pos[1] < HAUTEUR_GRILLE:
                for nom, zone in boutons_panneau.items():
                    if zone.collidepoint(evenement.pos):
                        action_panneau(nom)
                        break

            # ----- Clic sur la grille : ajouter / retirer un obstacle -----
            elif evenement.pos[0] < LARGEUR_GRILLE and evenement.pos[1] < HAUTEUR_GRILLE:
                colonne = evenement.pos[0] // TAILLE_CASE
                ligne = evenement.pos[1] // TAILLE_CASE
                case = (ligne, colonne)

                protegees = {depart, destination}
                if etat in ("en_route", "coince"):
                    a, b = chemin[index - 1], chemin[index]
                    protegees.update([a, b])
                    if a[0] != b[0] and a[1] != b[1]:   # segment diagonal en cours
                        protegees.update([(a[0], b[1]), (b[0], a[1])])

                if case not in protegees:
                    grille[ligne][colonne] = 1 - grille[ligne][colonne]
                    est_obstacle = (grille[ligne][colonne] == 1)
                    comparaison = []

                    if etat in ("attente", "arrive"):
                        reinitialiser()

                    elif etat in ("en_route", "coince"):
                        quittee = chemin[index - 1]
                        visee = chemin[index]
                        coupe = not chemin_valide(chemin, index)

                        if coupe or etat == "coince":
                            # Le chemin est coupé (ou le robot est bloqué) : recalcul obligatoire
                            res = rechercher(algo, visee, destination, diagonales, limite_ms())
                            if res["statut"] != "aucun":
                                remplacer_trajet(res, quittee)
                                etat = "en_route"
                            else:
                                appliquer_resultat(res)
                                etat = "coince"
                        elif not est_obstacle:
                            # Un obstacle a disparu : un chemin plus court existe peut-être
                            res = rechercher(algo, visee, destination, diagonales, limite_ms())
                            if res["statut"] != "aucun":
                                reste = cout_chemin(chemin[index:])
                                chemin_incomplet = chemin[-1] != destination
                                meilleur = (res["statut"] == "ok"
                                            and res["cout"] < reste - 1e-9)
                                if meilleur or (chemin_incomplet and res["statut"] == "ok"):
                                    remplacer_trajet(res, quittee)

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
                if chemin[-1] == destination:
                    etat = "arrive"
                else:
                    # Chemin partiel (temps dépassé) : on recalcule depuis ici
                    res = rechercher(algo, chemin[-1], destination, diagonales, limite_ms())
                    if res["statut"] != "aucun" and len(res["chemin"]) > 1:
                        remplacer_trajet(res, chemin[-1])
                    else:
                        appliquer_resultat(res)
                        etat = "coince"
        else:
            robot_x += VITESSE * dx / distance
            robot_y += VITESSE * dy / distance

    # --- Dessin de la grille ---
    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            x = colonne * TAILLE_CASE
            y = ligne * TAILLE_CASE
            if grille[ligne][colonne] == 1:
                dessiner_mur(fenetre, x, y)
            else:
                dessiner_sol(fenetre, x, y, ligne, colonne)

    if montrer_zone and zone_explorée:
        voile = pygame.Surface((TAILLE_CASE, TAILLE_CASE), pygame.SRCALPHA)
        voile.fill((80, 140, 255, 80))
        for (l, c) in zone_explorée:
            if grille[l][c] == 0:
                fenetre.blit(voile, (c * TAILLE_CASE, l * TAILLE_CASE))

    dessiner_lignes_grille(fenetre)

    if etat in ("attente", "en_route") and chemin:
        points = [(int(robot_x + TAILLE_CASE / 2), int(robot_y + TAILLE_CASE / 2))]
        for (l, c) in chemin[index:]:
            points.append(centre_case(l, c))
        partiel = chemin[-1] != destination
        dessiner_chemin(fenetre, points, CHEMIN_PARTIEL if partiel else CHEMIN)

    dessiner_drapeau(fenetre, destination[1] * TAILLE_CASE, destination[0] * TAILLE_CASE)
    dessiner_robot(fenetre, robot_x, robot_y)

    # --- Panneau de droite ---
    pygame.draw.rect(fenetre, PANNEAU, rect(LARGEUR_GRILLE, 0, LARGEUR_PANNEAU, HAUTEUR_GRILLE))
    fenetre.blit(police_petite_gras.render("Algorithme (F1 à F4)", True, TEXTE), (PX, 14))
    for i in range(4):
        couleur = BOUTON_ACTIF if algo == i else BOUTON_PANNEAU
        dessiner_bouton(fenetre, police_petite, boutons_panneau["algo%d" % i], NOMS_ALGOS[i], couleur)
    dessiner_bouton(fenetre, police_petite, boutons_panneau["diag"],
                    "Diagonales (D) : " + ("oui" if diagonales else "non"), BOUTON_PANNEAU)
    dessiner_bouton(fenetre, police_petite, boutons_panneau["zone"],
                    "Cases explorées (E) : " + ("oui" if montrer_zone else "non"), BOUTON_PANNEAU)
    dessiner_bouton(fenetre, police_petite, boutons_panneau["comparer"], "Comparer (C)", BOUTON_PANNEAU)
    dessiner_bouton(fenetre, police_petite, boutons_panneau["alea"], "Aléatoire (R)", BOUTON_PANNEAU)

    fenetre.blit(police_petite.render("Limite de calcul : %s ms" % limite_ms(), True, TEXTE), (PX, 285))
    dessiner_bouton(fenetre, police_petite, boutons_panneau["moins"], "-", BOUTON_PANNEAU)
    dessiner_bouton(fenetre, police_petite, boutons_panneau["plus"], "+", BOUTON_PANNEAU)

    y = 322
    fenetre.blit(police_petite_gras.render("Dernière recherche", True, TEXTE), (PX, y))
    if stats:
        lignes = [
            "Statut : %s" % stats["statut"],
            "Temps : %.3f ms" % stats["temps"],
            "Longueur : %.2f" % stats["cout"],
            "Cases explorées : %d" % stats["explores"],
        ]
        for k, texte in enumerate(lignes):
            fenetre.blit(police_petite.render(texte, True, TEXTE_DISCRET), (PX, y + 20 + k * 18))

    y = 430
    if comparaison:
        fenetre.blit(police_petite_gras.render("Comparaison (départ -> arrivée)", True, TEXTE), (PX, y))
        fenetre.blit(police_petite.render("Algo     ms      long.   expl.", True, TEXTE_DISCRET), (PX, y + 20))
        for k, (nom, t, c, e, s) in enumerate(comparaison):
            ligne_txt = "%-8s %-7.3f %-7.2f %d%s" % (nom, t, c, e, "" if s == "ok" else " (%s)" % s)
            fenetre.blit(police_petite.render(ligne_txt, True, TEXTE), (PX, y + 40 + k * 18))
    else:
        fenetre.blit(police_petite.render("Clic sur la grille : obstacle", True, TEXTE_DISCRET), (PX, y))
        fenetre.blit(police_petite.render("Violet = chemin partiel (temps dépassé)", True, TEXTE_DISCRET), (PX, y + 20))

    # --- Barre du bas ---
    pygame.draw.rect(fenetre, BARRE, rect(0, HAUTEUR_GRILLE, LARGEUR, HAUTEUR_BARRE))
    if etat == "attente":
        if len(chemin) > 1:
            if chemin[-1] != destination:
                message = "Chemin partiel (limite de temps atteinte)"
            else:
                message = "Cliquez sur Démarrer"
            texte_bouton, actif = "Démarrer", True
        else:
            message, texte_bouton, actif = "Aucun chemin possible", "Démarrer", False
    elif etat == "en_route":
        message, texte_bouton, actif = "Le robot se déplace...", "En cours...", False
    elif etat == "coince":
        message, texte_bouton, actif = "Chemin bloqué !", "Recommencer", True
    else:
        message, texte_bouton, actif = "Destination atteinte !", "Recommencer", True

    image = police.render(message, True, TEXTE)
    fenetre.blit(image, (15, HAUTEUR_GRILLE + (HAUTEUR_BARRE - image.get_height()) // 2))
    survol = actif and bouton.collidepoint(souris)
    couleur = BOUTON_GRIS if not actif else (BOUTON_SURVOL if survol else BOUTON)
    dessiner_bouton(fenetre, police, bouton, texte_bouton, couleur)

    pygame.display.flip()
    horloge.tick(60)

pygame.quit()