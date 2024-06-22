"""
Automate Cellulaire créé par Sidane Alp de la filière MP option info
Pour son TIPE sur la propagation des moustiques
"""

from tkinter import *
import time
from random import choice, randint
import numpy as np
import math
w,h=250,250 #Hauteur, largeur du canvas
c = 20#taille cellule
fen = Tk()

barreDeMenu = Menu(fen)
fen.config(menu=barreDeMenu)

model_grav = False
model_mous = False
def menu_callback():
    print("I'm in the menu callback!")
def submenu_callback():
    print("I'm in the submenu callback!")
submenu_widget = Menu(barreDeMenu, tearoff=False)
submenu_widget.add_command(label="Submenu Item1",
                           command=submenu_callback)
submenu_widget.add_command(label="Submenu Item2",
                           command=submenu_callback)
barreDeMenu.add_cascade(label="Fichier", menu=submenu_widget)
barreDeMenu.add_command(label="Configuration",
                        command=menu_callback)
#Le menu configuration donne l'accès à une fenêtre qui permet de modifier la taille des canvas
barreDeMenu.add_command(label="Aide",
                        command=menu_callback)

BMoustique = Frame(fen, borderwidth=2, relief = "raised")
fen.resizable(False, False)
BPop = Frame(fen,borderwidth=2, relief = "raised")
BpointDeau = Frame(fen,borderwidth=2, relief = "raised")
BTemp = Frame(fen,borderwidth=2, relief = "raised")
BOptions = Frame(fen, borderwidth = 2, relief = "raised")

BMoustique.grid(row = 1,column = 0)
BPop.grid(row = 1, column = 1)
BpointDeau.grid(row = 2, column = 0)
BTemp.grid(row=2, column = 1)
BOptions.grid(row =0, column = 2)

canMoustique = Canvas(BMoustique, bg = "White", width = w+c, height = h+c)
canPopulation = Canvas(BPop, bg = "White", width = w+c, height = h+c)
canEau = Canvas(BpointDeau, bg = "White", width = w+c, height = h+c)
canTemp = Canvas(BTemp, bg = "White", width = w+c, height = h+c)

lMoustique = Label(BMoustique, text = "Population de moustique")
lPopulation = Label(BPop, text = "Population humaine")
lEau = Label(BpointDeau, text = "Surface d'eau en m²")
lTemp = Label(BTemp, text = "Température moyenne")

Label(BMoustique, text = "Carte des moustiques").grid(column = 0, row = 0)
canMoustique.grid(column=0, row=1, rowspan = 5)
lMoustique.grid(column = 0, row = 6)



Label(BPop, text = "Carte de la population").grid(column = 0, row = 0)
canPopulation.grid(column = 0, row = 1, rowspan = 5)
lPopulation.grid(column = 0, row = 6)

Label(BpointDeau, text = "Carte des points d'eau").grid(column = 0, row = 0)
canEau.grid(column = 0, row = 1, rowspan = 5)
lEau.grid(column = 0, row = 6)

Label(BTemp, text = "Carte des températures").grid(column = 0, row = 0)
canTemp.grid(column = 0, row = 1, rowspan = 5)
lTemp.grid(column = 0, row = 6)

# VARIABLE CLES DE LA MODELISATIONS

SURFACE = 10000 # m² SURFACE D'UNE CASE

densite_population_humaine_maximale = 45 # par m²
densite_population_moustique_maximale = 80 # par m²
n_max = 100000 # Population  maximale pouvant être présente sur la SURFACE
nm_max = SURFACE*densite_population_moustique_maximale # Population maximale de moustiques pouvant vivre dans la surface? Si c'est dépassé, il y a overpopulation et les moustiques
me_max = SURFACE*(3/5) # Surface d'eau maximale atteinte lors d'inondations
me_stable = SURFACE*(2/5)  #Surface d'eau limite telle que les moustiques ont assez de point d'eau pour avoir une reproduction stable A préciser à l'aide de chiffre
n_stable = n_max*(2/5) #Population humaine seuil pour laquelle les moustiques ont un taux de reproduction normal
#Population moyenne de moustique à ny : 1200 pour 15m² soit 80 moustiques par m² à ny
temp_moyenne = 20 # Température moyenne
#https://www.researchgate.net/publication/5323088_Effectiveness_of_Mosquito_Traps_in_Measuring_Species_Abundance_and_Composition/link/53f7865e0cf24ddba7d84ca1/download
temp_maximale = 60
# A 10°C les moustiques meurent
#



def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

class Cellule () :
    def __init__(self,x,y,n) :
        self.pos = [x,y]
        self.n = n #population vivant sur la case
        self.nm = 0 #Population de moustique
        self.me = me_stable #Surface d'eau en m²
        self.t = 0 # Température moyenne de la parcelle

        self.color = ""
        self.balanceP = 255-int((self.n*255)/n_max)
        self.balanceM = 255
        self.balanceE = 255
        self.rectangleM = canMoustique.create_rectangle(x, y, x+c, y+c)
        self.rectangleP = canPopulation.create_rectangle(x, y, x+c, y+c)
        self.rectangleE = canEau.create_rectangle(x, y, x+c, y+c)
        self.rectangleT = canTemp.create_rectangle(x, y, x+c, y+c)

        self.remplir()
    def remplir(self, color = "") :
        self.balance = 255-int((self.n*255)/n_max)
        color = _from_rgb((self.balance, self.balance, self.balance))
        canPopulation.itemconfigure(self.rectangleP,fill = color)

        if self.nm > nm_max :
            color = _from_rgb((255,0,0))
            canMoustique.itemconfigure(self.rectangleM,fill = color)
        else :
            self.balanceM = int((self.nm*255)/nm_max)
            color = _from_rgb((255,255-self.balanceM,255-self.balanceM))
            canMoustique.itemconfigure(self.rectangleM,fill = color)

        self.balanceE = int((self.me*255/me_max))
        color = _from_rgb((255-self.balanceE,255-self.balanceE,255))
        canEau.itemconfigure(self.rectangleE, fill = color)

        self.balanceT = int((self.t*255/temp_maximale))
        tempo = 255-2*self.balanceT
        if tempo < 0 : tempo = 0
        color = _from_rgb((255,255-self.balanceT,tempo))
        canTemp.itemconfigure(self.rectangleT, fill = color)
    def survie(self) :
        if self.nm < nm_max :
            #Si on n'est pas dans un cas de surpopulation de moustique*
            self.nm = int(self.nm*((self.me/me_stable)*(self.n/n_stable)))
            if self.t < 15 or self.t > 40 :
                self.nm *= 0.75
    def get_n(self) :
        return self.n
    def get_t(self) :
        return self.t
    def set_n(self,a = 0) :
        "Modifie la population, population nulle si rien n'est renseigné"
        self.n = a
    def set_nm(self, a = 0) :
        "De même pour les moustiques"
        self.nm = a
        self.remplir()
    def up_me(self, a= 0) :
        self.me += a
        if self.me > me_max :
            self.me = me_max
        self.remplir()
    def get_pos(self) :
        return self.pos
    def moustique(self) :
        self.remplir("infecte")
    def reset_pop(self, pop = 0) :
        self.n = pop
        self.color = ""
        self.balanceP = 255-int((self.n*255)/n_max)
        self.remplir()
    def up_t(self, t=2):
        if self.t +t < temp_maximale :
            self.t+=t
        else :
            self.t = temp_maximale
        self.rafraichir()
    def reset_moustique(self, mous = 0) :
        self.nm = mous
        self.color = ""
        self.balanceM = 255
        self.remplir()
    def reset_eau(self, nb = 0) :
        self.me = nb
        self.remplir()
    def reset_temp(self) :
        self.t = temp_moyenne
        self.remplir()
    def kill_moustique(self) :
        self.remplir("White")
        self.nm= 0
    def get_nm(self) :
        return self.nm
    def get_me(self) :
        return self.me
    def up_nm(self, x) :
        self.nm += x
        if self.nm > nm_max :
            self.nm = nm_max
        elif self.nm < 0 :
            self.nm =0
        self.rafraichir()
    def up_n(self, x):
        self.n += x
        if self.n > n_max :
            self.n = n_max
        self.rafraichir()
    def rafraichir(self) :
        self.survie()
        self.remplir()
    def eau(self) :
        self.remplir("eau")
    def up_me(self, nb) :
        total = self.me+int(nb)
        if total < me_max :
            self.me= total
            self.rafraichir()
    def avancer(self) :
        if self.pos[0]< w and self.pos[1] <h :
            self.pos[0]+=c
            canMoustique.coords(self.rectangle, self.pos[0], self.pos[1], self.pos[0]+c, self.pos[1]+c)

def distance(cel1, cel2) :
    "Calcule la distance entre deux cellules"
    (x1,y1) = cel1.get_pos()
    x2,y2 = cel2.get_pos()
    return np.sqrt((x1**2)+(x2**2)+(y1**2)+(y2**2))
class Master_Grille() :
    def __init__(self) :
        self.tab = [[Cellule(x,y, randint(0,n_max)) for x in range(0,w,c)]  for y in range(0,w,c)]
        self.taille = len(self.tab)
        self.mode = "none"
        self.moustiquelache = 100
        self.populationlache = 100
        self.qtePluie = 100
        self.eaulachee = 100
        self.qteInsecticide = 100
        self.carteMoustique = np.array([[False]*self.taille]*self.taille)
        canMoustique.bind('<Button-1>', self.cliquefenM)
        canEau.bind('<Button-1>', self.cliquefenE)
        canPopulation.bind('<Button-1>', self.cliquefenP)
        canMoustique.bind('<Motion>', self.majInfoM)
        canPopulation.bind('<Motion>', self.majInfoP)
        canEau.bind('<Motion>', self.majInfoE)
        canTemp.bind('<Motion>', self.majInfoT)
        self.running = True
        self.degradee_temperature()
        self.rafraichir()
    def moustique(self) :
        self.mode = "moustique"
    def insecticide(self) :
        self.mode = "insecticide"
    def pop(self) :
        self.mode = "population"
    def set_moustiquelache(self, nb) :
        self.moustiquelache = int(nb)
    def set_poplache(self, nb) :
        self.populationlache = int(nb)
    def set_qteInsecticide(self, nb) :
        self.qteInsecticide = int(nb)
    def set_eaulachee(self, nb) :
        self.eaulachee = int(nb)
    def set_qtePluie(self, nb) :
        self.qtePluie = nb
    def pleuvoir(self) :
        for i in range(0, self.taille) :
            for j in range(0, self.taille) :
                self.tab[i][j].up_me(self.qtePluie)
    def majInfoM(self, event) :
        (x,y) = event.x, event.y
        if x<= w and y <= h :
            #◘ Si on veut afficher 8 chiffres
            nm = self.tab[y//c][x//c].get_nm()
            if nm == 0 :
                n = 8
            else :
                n = 8 - int(math.log10(nm))
            lMoustique.configure(text = "Population de moustique sur la case sélectionnée: " + n*"0" + str(self.tab[y//c][x//c].get_nm()))
    def majInfoP(self,event) :
        (x,y) = event.x, event.y
        if x <= w and y <= h :
            lPopulation.configure(text = "Population humaine sur la case sélectionnée: " + str(self.tab[y//c][x//c].get_n()))
    def majInfoE(self, event) :
        (x,y) = event.x, event.y
        if x <= w and y <= h :
            lEau.configure(text = "Surface d'eau stagnante sur la case sélectionnée : " + str(self.tab[y//c][x//c].get_me()))
    def majInfoT(self, event) :
        (x,y) = event.x, event.y
        if x <= w and y <= h :
            lTemp.configure(text = "Température moyenne sur la case sélectionnée: " + str(self.tab[y//c][x//c].get_t()))
    def desinfection(self) :
        "Retire toutes les cellules infectées"
        self.carteMoustique = np.array([[False]*self.taille]*self.taille)
        self.mode = "none"
        for i in range(0, self.taille) :
            for j in range(0, self.taille) :
                if self.carteMoustique[i][j] :
                    self.tab.kill_moustique()
                    self.carteMoustique[i][j] = False
    def pointdeau(self) :
        self.mode = "eau"
    def cliquefenM(self,event) :
        if self.mode == "moustique" :
            self.tab[event.y//c][event.x//c].up_nm(self.moustiquelache)
            self.carteMoustique[event.y//c][event.x//c] = True
        elif self.mode == "insecticide" :
            self.tab[event.y//c][event.x//c].up_nm(-self.qteInsecticide)
    def cliquefenE(self, event) :
        if self.mode == "eau" :
            self.tab[event.y//c][event.x//c].up_me(self.eaulachee)
    def cliquefenP(self, event) :
        if self.mode == "population" :
            self.tab[event.y//c][event.x//c].up_n(self.populationlache)
    def degradee_temperature(self) :
        for i in range(self.taille) :
            for j in range(self.taille) :
                self.tab[i][j].up_t(i*3)
    def rafraichir(self) :
        "Boucle principal"
        if self.mode == "run" :
            if model_grav :
                self.gegravity()
            if model_mous :
                self.moustiqueAI()
            for i in range(self.taille) :
                for j in range(self.taille) :
                    self.tab[i][j].rafraichir()
        if self.mode != "stop" :
            fen.after(150, self.rafraichir)
        else :
            self.running = False
            fen.after_cancel(100)
    def demarrer(self, grav = False, mous = False) :
        global model_mous, model_gravite
        "Démarre la simulation"
        self.mode = "run"
        if self.running == False :
            self.running = True
            model_gravite = grav
            model_mous = mous
            self.rafraichir()
    def get_cartemoustique(self) :
        return self.carteMoustique
    def stopper(self) :
        self.mode = 'stop'
    def reset(self, carte = "moustique") :
        "Reset la carte"
        for i in range(self.taille) :
            for j in range(self.taille) :
                if carte == "moustique" :
                    self.tab[i][j].reset_moustique()
                elif carte == "population" :
                    self.tab[i][j].reset_pop()
                elif carte == "eau" :
                    self.tab[i][j].reset_eau()
                elif carte == "temperature" :
                    self.tab[i][j].reset_temp()
                self.mode = "none"
    def aleatoire(self, carte = "moustique") :
         "Met une population aléatoire"
         for i in range(self.taille) :
            for j in range(self.taille) :
                if carte == "moustique" :
                    self.tab[i][j].reset_moustique(randint(0, nm_max))
                elif carte == "population" :
                    self.tab[i][j].reset_pop(randint(0, n_max))
                elif carte == "eau" :
                    self.tab[i][j].reset_eau(randint(0, me_max))
                self.mode = "none"
    def moustiqueAI(self) :
        "Détermine la propagation des moustiques de proche en proche"
        "1% des moustiques se propagent vers une case donné à chaque temps"
        # Capture des moustiques à l'instant T
        tampon = np.empty([self.taille, self.taille])
        # Propagation faible de proche en proche
        for i in range(self.taille) :
            for j in range(self.taille) :
                tampon[i][j] = self.tab[i][j].get_nm()
        for i in range(self.taille) :
            for j in range(self.taille) :
                m1 = -1
                m2 = 2
                n1 = -1
                n2 = 2
                if i == 0 :
                    m1 +=1
                elif i >= self.taille-1 :
                    m2 -= 1
                if j == 0 :
                    n1 += 1
                elif j >= self.taille-1 :
                    n2 -= 1
                for k1 in range(m1,m2) :
                    for k2 in range(n1,n2) :
                        self.tab[i][j].up_nm(int(0.1*tampon[i+k1][j+k2]))
        # A l'instant T+1
    def gegravity(self) :
        T = np.empty([self.taille, self.taille,self.taille,self.taille])
        #copie
        tampon = np.empty([self.taille, self.taille])
        for i in range(self.taille) :
            for j in range(self.taille) :
                tampon[i][j] = self.tab[i][j].get_n()
        k = 0.0000005
        a = 1.5
        b = 0.8
        y = 2
        for i1 in range(self.taille) :
            for i2 in range(self.taille) :
                "Pour chaque cellule"
                for j1 in range(self.taille) :
                    for j2 in range(self.taille) :
                        "On calcule l'influence de toutes les autres cellules"
                        if i1 != i2 or j1 != j2 :
                            d = distance(self.tab[i1][i2], self.tab[j1][j2])

                            T[i1][i2][j1][j2] = k*((self.tab[i1][i2].get_n()**a)*(self.tab[j1][j2].get_n()**b))/d
        for i1 in range(self.taille) :
            for i2 in range(self.taille) :
                "Pour chaque cellule"
                if i1 != i2 or j1 != j2 :
                    S1 = 0 # Population entrante
                    S2 = 0 # Population sortante
                    npop = self.tab[i1][i2].get_n()
                    for j1 in range(self.taille) :
                        for j2 in range(self.taille) :
                            "On calcule la nouvelle population de chaque cellule"
                            S1 += T[i1][i2][j1][j2]
                            S2 += T[j1][j2][i1][i2]
                    un = int(npop + S1 -S2)
                    if un <= n_max and 0<= un :
                        tampon[i1][i2] = un
                    elif 0<= un :
                        tampon[i1][i2] = n_max
                    else :
                        tampon[i1][i2] = 0
        for i in range(self.taille) :
            for j in range(self.taille) :
                self.tab[i][j].set_n(tampon[i][j])
    def pop_total(self) :
        s = 0
        for i in range(self.taille) :
            for j in range(self.taille) :
                s+=self.tab[i][j].get_n()


# Liste des modèles de comportements

g = Master_Grille()
bbool = False
def b1_action () :
    global model_mous
    if model_mous :
        model_mous = False
    else :
        model_mous = True
def b2_action () :
    global model_grav
    if model_grav :
        model_grav = False
    else :
        model_grav = True
def b_action() :
    global bbool
    if not(bbool) :
        bbool = True
        g.demarrer(grav = model_grav, mous = model_mous)
    else :
        g.stopper()
        bbool = False

b1 = Checkbutton(fen, text = "Activer la propagation des moustiques", command = b1_action)
b2 = Checkbutton(fen, text = "Activer le modèle à gravitation", command = b2_action)

b = Button(BOptions, text = "Activer", command = b_action)
b1.grid(row = 0, column = 0)
b2.grid(row = 0, column = 1)
b.grid(row = 0, column = 0)

bm1 = Button(BMoustique, text = "Reset", command = lambda : g.reset("moustique"))
bm2 = Button(BMoustique, text = "Population Moustique aléatoire", command = lambda : g.aleatoire("moustique"))
boitem1 = Frame(BMoustique, borderwidth=2, relief = "raised")

mousplace = 100

bm3 = Button(boitem1, text = "Placer Moustique", command = g.moustique)
fm3 = Scale(boitem1, orient=HORIZONTAL, to = nm_max, command = g.set_moustiquelache)


be1 = Button(BpointDeau, text = "Reset", command = lambda  : g.reset("eau"))
be2 = Button(BpointDeau, text = "Points d'eau aléatoire", command = lambda : g.aleatoire("eau"))
boitee1 = Frame(BpointDeau, borderwidth=2, relief = "raised")
be3 = Button(boitee1, text = "Faire pleuvoir", command = g.pleuvoir)
fe3 = Scale(boitee1, orient=HORIZONTAL, to = me_max, command = g.set_qtePluie)

boitee2 = Frame(BpointDeau, borderwidth=2, relief = "raised")
be4 = Button(boitee2, text = "Placer point d'eau", command=g.pointdeau)
fe4 = Scale(boitee2, orient=HORIZONTAL, to = me_max, command = g.set_eaulachee)

bp1 = Button(BPop, text = "Reset", command = lambda : g.reset("population"))
bp2 = Button(BPop, text = "Générer Population aléatoire", command = lambda : g.aleatoire("population"))
boitep1 = Frame(BPop, borderwidth=2, relief = "raised")
bp4 = Button(boitep1, text = "Placer une population donnée", command = g.pop)
fp4 = Scale(boitep1, orient=HORIZONTAL, to = n_max, command = g.set_poplache)


bt1 = Button(BTemp, text = "Reset", command = lambda : g.reset("temperature"))
bt2 = Button(BTemp, text = "Vague de Chaleur", command = g.degradee_temperature)
bt3 = Button(BTemp, text = "Point de chaleur")

bm1.grid(row=1, column = 1)
bm2.grid(row = 2, column = 1)
boitem1.grid(row = 3, column = 1)

bm3.pack()
fm3.pack()

bt1.grid(row = 1, column = 1)
bt2.grid(row = 2, column = 1)

be1.grid(row = 1, column = 1)
boitee1.grid(row=2, column = 1)
be2.grid(row = 3, column = 1)
boitee2.grid(row = 4, column = 1)
be3.pack()
fe3.pack()
be4.pack()
fe4.pack()


bp1.grid(row=1, column = 1)
bp2.grid(row = 2, column = 1)
boitep1.grid(row = 3, column = 1)
bp4.pack()
fp4.pack()
def fen_etat(state = 'active') :
    bm1["state"] = "disabled"
    bm2["state"] = "disabled"
    be1["state"] = "disabled"
    be2["state"] = "disabled"
    bp1["state"] = "disabled"

fen.mainloop()