import ast
import math
import os
import statistics
import sys
import time
import copy
import pygame


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    dim_celula = None
    display = None
    zero_img = None
    x_img = None
    celuleGrid = None
    NR_LINII = None
    NR_COLOANE = None
    JMIN = None
    JMAX = None
    GOL = '#'
    PONDERI = None
    ADANCIME_MAX = None

    def __init__(self, tabla=None, lin=None, col=None):
        if lin is not None and col is not None:
            Joc.NR_LINII = lin
            Joc.NR_COLOANE = col
        self.matr = tabla or [Joc.GOL] * self.NR_LINII * self.NR_COLOANE

    @classmethod
    def initializeaza(cls, display, dim_celula):
        # pentru a centra pe verticala tabla, trebuie sa adaugam la pozitia patratelor valoarea:
        dim = (900 - 60 * Joc.NR_COLOANE) / 2
        poz_y = (750 - 60 * Joc.NR_LINII - 100) / 2

        cls.display = display
        cls.dim_celula = dim_celula
        cls.x_img = pygame.image.load('x_roz_deschis.png')
        cls.x_img = pygame.transform.scale(cls.x_img, (
            dim_celula, math.floor(dim_celula * cls.x_img.get_height() / cls.x_img.get_width())))
        cls.zero_img = pygame.image.load('zero_galben.png')
        cls.zero_img = pygame.transform.scale(cls.zero_img, (
            dim_celula, math.floor(dim_celula * cls.zero_img.get_height() / cls.zero_img.get_width())))
        cls.celuleGrid = []  # este lista cu patratelele din grid
        for linie in range(Joc.NR_LINII):
            cls.celuleGrid.append([])
            for coloana in range(Joc.NR_COLOANE):
                patr = pygame.Rect(dim + coloana * dim_celula, poz_y + linie * dim_celula, dim_celula, dim_celula)
                cls.celuleGrid[linie].append(patr)

    def deseneaza_grid(self, marcaj=None):
        dim = (900 - 60 * Joc.NR_COLOANE) / 2
        poz_min = Joc.pozitii_patrate_completate(self, Joc.JMIN)
        poz_max = Joc.pozitii_patrate_completate(self, Joc.JMAX)

        culoare_roz = (255, 194, 212)
        culoare_galben = (255, 240, 194)

        culoare_min = culoare_roz if len(poz_min) > 0 and self.matr[list(poz_min)[0]] == 'x' else culoare_galben
        culoare_max = culoare_roz if len(poz_max) > 0 and self.matr[list(poz_max)[0]] == 'x' else culoare_galben
        poz_y = (750 - 60 * Joc.NR_LINII - 100) / 2
        for linie in range(Joc.NR_LINII):
            for coloana in range(Joc.NR_COLOANE):
                ind = linie * Joc.NR_COLOANE + coloana
                if ind in poz_min:
                    culoare = culoare_min
                elif ind in poz_max:
                    culoare = culoare_max
                elif (linie + coloana) % 2 == 0 and self.matr[ind] == Joc.GOL:
                    culoare = (152, 185, 243)
                else:
                    culoare = (73, 123, 254)
                pygame.draw.rect(self.__class__.display, culoare,
                                 self.__class__.celuleGrid[linie][coloana])
                if self.matr[linie * Joc.NR_COLOANE + coloana] == 'x':
                    self.__class__.display.blit(self.__class__.x_img,
                                                (dim + coloana * self.__class__.dim_celula,
                                                 poz_y + linie * self.__class__.dim_celula +
                                                 (self.__class__.dim_celula - self.__class__.x_img.get_height()) // 2))

                elif self.matr[linie * Joc.NR_COLOANE + coloana] == '0':
                    self.__class__.display.blit(self.__class__.zero_img,
                                                (dim + coloana * self.__class__.dim_celula,
                                                 poz_y + linie * self.__class__.dim_celula +
                                                 (self.__class__.dim_celula - self.__class__.zero_img.get_height()) // 2))

        pygame.display.update()

    @classmethod
    def jucator_opus(cls, jucator):
        # val_true if conditie else val_false
        return cls.JMAX if jucator == cls.JMIN else cls.JMIN

    def final(self):
        # daca nu s-au completat toate pozitiile posibile, atunci jocul nu s-a terminat
        # jucatorii pot plasa simboluri doar în pozițiile în care indicii liniei, il și coloanei, ic,
        # ale poziției respective îndeplinesc conđiția il+ic să fie număr par
        # Jocul se termina cand nu mai sunt spatii libere in grid
        for i in range(0, Joc.NR_LINII):
            for j in range(0, Joc.NR_COLOANE):
                if self.matr[i * Joc.NR_COLOANE + j] == Joc.GOL and (i + j) % 2 == 0:
                    return False
        scorMAX = self.calculeaza_scor(Joc.JMAX)
        scorMIN = self.calculeaza_scor(Joc.JMIN)

        if scorMAX > scorMIN:
            return Joc.JMAX
        elif scorMAX < scorMIN:
            return Joc.JMIN
        return "remiza"

    def mutari(self, jucator):  # jucator = simbolul jucatorului care muta
        """
        Functia genereaza toate mutarile posibile din starea curenta a jocului
        Se parcurge matricea si se verifica fiecare pozitie in parte
        O pozitie este valida daca nu a fost deja completata si daca suma dintre indecsii liniei si coloanei este para
        :returns: lista de stari ce reprezinta mutarile posibile
        """
        l_mutari = []
        for l in range(Joc.NR_LINII):
            for c in range(Joc.NR_COLOANE):
                indice = l * Joc.NR_COLOANE + c
                if (l + c) % 2 == 0 and self.matr[indice] == Joc.GOL:
                    copie_matr = copy.deepcopy(self.matr)
                    copie_matr[indice] = jucator
                    l_mutari.append(Joc(copie_matr))
        return l_mutari

    def pozitii_patrat(self, lin, col, jucator):
        """
        Determina pozitiile din matrice care fac parte dintr-un patrat completat cu coltul din stanga sus in pozitia (lin, col)
        :returns: lista pozitiilor
        """
        poz = [0, 0, 0, 0]
        lista_pozitii = []
        for latura in range(2, Joc.NR_LINII - lin, 2):
            poz[0] = lin * Joc.NR_COLOANE + col
            poz[1] = lin * Joc.NR_COLOANE + col + latura
            poz[2] = (lin + latura) * Joc.NR_COLOANE + col
            poz[3] = (lin + latura) * Joc.NR_COLOANE + col + latura
            # daca lin+latura sau col+latura depasesc dimensiunile matricei, atunci nu mai are rost sa verificam
            if lin + latura >= Joc.NR_LINII or col + latura >= Joc.NR_COLOANE:
                continue
            nr_simboluri_juc = 0
            for i in range(4):
                if poz[i] < (Joc.NR_COLOANE * Joc.NR_LINII) and self.matr[poz[i]] == jucator:
                    nr_simboluri_juc += 1
            if nr_simboluri_juc == 4:
                lista_pozitii.append(poz[:])
            poz = [0, 0, 0, 0]
        return lista_pozitii

    def pozitii_patrate_completate(self, jucator):
        """
        Returneaza un set cu toate pozitiile din matrice care fac parte dintr-un patrat completat
        """
        pozitii = set()
        for linie in range(Joc.NR_LINII):
            for col in range(Joc.NR_COLOANE):
                indice = linie * Joc.NR_COLOANE + col
                if self.matr[indice] == jucator:
                    # folosim functia pozitii_patrat pentru a verifica daca exista patrate cu coltul din stanga sus in pozitia curenta
                    lista_pozitii = self.pozitii_patrat(linie, col, jucator)
                    for poz in lista_pozitii:
                        pozitii.update(poz)
        return pozitii

    def calculeaza_scor(self, jucator):
        scor = 0
        for linie in range(Joc.NR_LINII):
            for col in range(Joc.NR_COLOANE):
                indice = linie * Joc.NR_COLOANE + col
                if self.matr[indice] == jucator:
                    # daca am gasit in matrice un element al jucatorului
                    # verificam daca exista patrate cu coltul din stanga sus in pozitia curenta
                    for col2 in range(col + 1, Joc.NR_COLOANE):
                        if self.matr[linie * Joc.NR_COLOANE + col2] == jucator:
                            latura = col2 - col  # dimensiunea laturii unui patrat pe care il cautam
                            ind1 = (linie + latura) * Joc.NR_COLOANE + col
                            ind2 = (linie + latura) * Joc.NR_COLOANE + col2
                            if ((linie + latura) < Joc.NR_LINII and self.matr[ind1] == jucator and self.matr[
                                ind2] == jucator):
                                scor += 1
        return scor

    def patrat_deschis(self, lin, col, jucator):
        """
        Verifica daca exista un patrat deschis de orice dimensiune pentru jucatorul primit ca parametru,
         avand coltul din stanga sus in pozitia (lin, col)
        :returns: suma ponderilor pentru toate patratele deschise
        """
        nr_patrate = 0
        suma_ponderi = 0
        # initializez o lista de 4 elemente cu 0
        poz = [0, 0, 0, 0]
        for latura in range(2, Joc.NR_LINII - lin, 2):
            poz[0] = lin * Joc.NR_COLOANE + col
            poz[1] = lin * Joc.NR_COLOANE + col + latura
            poz[2] = (lin + latura) * Joc.NR_COLOANE + col
            poz[3] = (lin + latura) * Joc.NR_COLOANE + col + latura
            nr = 0
            # daca lin+latura sau col+latura depasesc dimensiunile matricei, atunci nu mai are rost sa verificam
            if lin + latura >= Joc.NR_LINII or col + latura >= Joc.NR_COLOANE:
                continue
            nr_simboluri_juc = 0
            for i in range(4):
                # pentru fiecare colt al patratului se verifica daca este in matrice si daca este gol sau simbolul jucatorului
                if poz[i] < Joc.NR_COLOANE * Joc.NR_LINII and (
                        self.matr[poz[i]] == jucator or self.matr[poz[i]] == Joc.GOL):
                    nr += 1
                    nr_simboluri_juc += (1 if self.matr[poz[i]] == jucator else 0)

            # doar daca toate cele 4 pozitii sunt in matrice si sunt goluri sau simboluri ale jucatorului se poate forma un patrat
            if nr == 4:
                nr_patrate += 1
                # pentru fiecare simbol al jucatorului din patrat, se adauga ponderea corespunzatoare
                # daca clasa Joc nu are ponderi, orice patrat deschis este considerat de valoare 1
                suma_ponderi += (Joc.PONDERI[nr_simboluri_juc] if Joc.PONDERI is not None else 1)
            poz = [0, 0, 0, 0]

        # daca nu se primeste nicio pondere, suma_ponderi este egal cu numarul de patrate deschise
        return suma_ponderi

    def patrate_deschise(self, jucator):
        """
        Calculeaza suma ponderilor pentru toate patratele deschise pentru jucatorul primit ca parametru
        """
        suma_ponderi = 0
        # cream un set pentru a retine toate pozitiile din matrice care fac parte dintr-un patrat completat
        pozitii = set()
        for linie in range(Joc.NR_LINII):
            for col in range(Joc.NR_COLOANE):
                indice = linie * Joc.NR_COLOANE + col
                if (linie + col) % 2 == 0 and (self.matr[indice] == Joc.GOL or self.matr[indice] == jucator):
                    suma_ponderi += self.patrat_deschis(linie, col, jucator)
        return suma_ponderi

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        if t_final == self.__class__.JMAX:  # self.__class__ referinta catre clasa instantei
            return (99 + adancime)
        elif t_final == self.__class__.JMIN:
            return (-99 - adancime)
        elif t_final == 'remiza':
            return 0
        else:
            # numarul de patrate deschise ale calculatorului sunt avantajoase pentru el
            # numarul de patrate deschise ale jucatorului scad scorul calculatorului
            return (self.patrate_deschise(self.__class__.JMAX) - self.patrate_deschise(self.__class__.JMIN))

    def sirAfisare(self):
        sir = "  |"
        sir += " ".join([str(i) for i in range(self.NR_COLOANE)]) + "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        for i in range(self.NR_LINII):  # itereaza prin linii
            sir += str(i) + " |" + " ".join(
                [str(x) for x in self.matr[self.NR_COLOANE * i: self.NR_COLOANE * (i + 1)]]) + "\n"
        return sir

    def __str__(self):
        return self.sirAfisare()

    def __repr__(self):
        sir = f"N={self.NR_LINII}\nM={self.NR_COLOANE}\nJMIN={self.JMIN}\nJMAX={self.JMAX}\nPONDERI={self.PONDERI}\n" \
              f"ADANCIME_MAX={self.ADANCIME_MAX}\nTABLA={self.matr}\n"
        return sir


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    O instanta din clasa stare este un nod din arborele minimax
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, estimare=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # estimarea favorabilitatii starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.estimare = estimare

        # lista de mutari posibile (tot de tip Stare) din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        # e de tip Stare (cel mai bun succesor)
        self.stare_aleasa = None
        self.parinte = parinte

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)  # lista de informatii din nodurile succesoare
        juc_opus = Joc.jucator_opus(self.j_curent)

        # mai jos calculam lista de noduri-fii (succesori)
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir

    def __repr__(self):
        sir = f"JCURENT={self.j_curent}\nADANCIME={self.adancime}\nESTIMARE={self.estimare}\n"
        sir += self.tabla_joc.__repr__()
        return sir



""" Algoritmul MinMax """
# declaram o variabila globala pentru a numara nodurile generate in algoritmul minimax
nr_noduri_min_max = 0


def min_max(stare):
    # daca sunt la o frunza in arborele minimax sau la o stare finala
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    # actualizam numarul de noduri generate, adaugand lungimea listei de mutari posibile
    global nr_noduri_min_max
    nr_noduri_min_max += len(stare.mutari_posibile)

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutariCuEstimare = [min_max(x) for x in
                        stare.mutari_posibile]  # expandez(constr subarb) fiecare nod x din mutari posibile

    # sortare mutari cu estimare in functie de jucator
    # mutariCuEstimare.sort(key=lambda x: x.estimare, reverse=stare.j_curent == Joc.JMAX)

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu estimarea maxima
        stare.stare_aleasa = max(mutariCuEstimare, key=lambda x: x.estimare)  # def f(x): return x.estimare -----> key=f
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu estimarea minima
        stare.stare_aleasa = min(mutariCuEstimare, key=lambda x: x.estimare)

    stare.estimare = stare.stare_aleasa.estimare
    return stare


nr_noduri_alpha_beta = 0


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()
    # mutarile ar trebui sortate crescator daca e randul lui JMIN si descrescator daca e randul lui JMAX
    stare.mutari_posibile.sort(key=lambda x: x.tabla_joc.estimeaza_scor(stare.adancime - 1),
                               reverse=stare.j_curent == Joc.JMAX)

    # actualizam numarul de noduri generate, adaugand lungimea listei de mutari posibile
    global nr_noduri_alpha_beta
    nr_noduri_alpha_beta += len(stare.mutari_posibile)

    if stare.j_curent == Joc.JMAX:
        estimare_curenta = float('-inf')  # in aceasta variabila calculam maximul

        for mutare in stare.mutari_posibile:
            # calculeaza estimarea pentru starea noua, realizand subarborele
            stare_noua = alpha_beta(alpha, beta, mutare)  # aici construim subarborele pentru stare_noua

            if (estimare_curenta < stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if (alpha < stare_noua.estimare):
                alpha = stare_noua.estimare
                if alpha >= beta:  # interval invalid
                    break

    elif stare.j_curent == Joc.JMIN:
        estimare_curenta = float('inf')
        # completati cu rationament similar pe cazul stare.j_curent==Joc.JMAX
        for mutare in stare.mutari_posibile:
            # calculeaza estimarea
            stare_noua = alpha_beta(alpha, beta, mutare)  # aici construim subarborele pentru stare_noua

            if (estimare_curenta > stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if (beta > stare_noua.estimare):
                beta = stare_noua.estimare
                if alpha >= beta:
                    break

    stare.estimare = stare.stare_aleasa.estimare

    return stare


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()  # metoda final() returneaza "remiza" sau castigatorul ("x" sau "0") sau False daca nu e stare finala
    if (final):
        if (final == "remiza"):
            print("Remiza!")
        else:
            print("A castigat " + final)
        return True
    return False


# clasa Buton folosita pentru a desena butoanele
class Buton:
    def __init__(self, display=None, left=0, top=0, w=0, h=0, culoareFundal=(73, 123, 254),
                 culoareFundalSel=(255, 95, 150), text="", font="comicsansms", fontDimensiune=20, culoareText=(255, 255, 255),
                 valoare=""):
        self.display = display
        self.culoareFundal = culoareFundal
        self.culoareFundalSel = culoareFundalSel
        self.text = text
        self.font = font
        self.w = w
        self.h = h
        self.selectat = False
        self.fontDimensiune = fontDimensiune
        self.culoareText = culoareText
        # creez obiectul font
        fontObj = pygame.font.SysFont(font, fontDimensiune)
        self.textRandat = fontObj.render(self.text, True, self.culoareText)
        self.dreptunghi = pygame.Rect(left, top, w, h)
        # aici centram textul
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)
        self.valoare = valoare

    def selecteaza(self, sel):
        self.selectat = sel
        self.deseneaza()

    def selecteazaDupacoord(self, coord):
        if self.dreptunghi.collidepoint(coord):
            self.selecteaza(True)
            return True
        return False

    def updateDreptunghi(self):
        self.dreptunghi.left = self.left
        self.dreptunghi.top = self.top
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)

    def deseneaza(self):
        culoareF = self.culoareFundalSel if self.selectat else self.culoareFundal
        pygame.draw.rect(self.display, culoareF, self.dreptunghi, border_radius=7)
        self.display.blit(self.textRandat, self.dreptunghiText)


class GrupButoane:
    def __init__(self, listaButoane=[], indiceSelectat=0, spatiuButoane=40, left=0, top=0):
        self.listaButoane = listaButoane
        self.indiceSelectat = indiceSelectat
        self.listaButoane[self.indiceSelectat].selectat = True
        self.top = top
        self.left = left
        leftCurent = self.left
        for b in self.listaButoane:
            b.top = self.top
            b.left = leftCurent
            b.updateDreptunghi()
            leftCurent += (spatiuButoane + b.w)

    def selecteazaDupacoord(self, coord):
        for ib, b in enumerate(self.listaButoane):
            if b.selecteazaDupacoord(coord):
                self.listaButoane[self.indiceSelectat].selecteaza(False)
                self.indiceSelectat = ib
                return True
        return False

    def deseneaza(self):
        # atentie, nu face wrap
        for b in self.listaButoane:
            b.deseneaza()

    def getValoare(self):
        return self.listaButoane[self.indiceSelectat].valoare


def deseneaza_alegeri(display):
    # scrierea textului (optiunile)

    dim = 70
    imgx = pygame.image.load("x_roz_deschis.png")
    img0 = pygame.image.load("zero_galben.png")
    imgx = pygame.transform.smoothscale(imgx, (dim, dim))
    img0 = pygame.transform.smoothscale(img0, (dim, dim))
    display.blit(imgx, (365, 50))
    display.blit(img0, (465, 50))

    culoareText = (255, 255, 255)
    fontObj = pygame.font.SysFont("comicsansms", 25)
    pozitie_y = 150
    pozitie_x = 150
    textAlgortim = fontObj.render("Algoritm:", True, culoareText)
    display.blit(textAlgortim, (pozitie_x, pozitie_y + 30))
    textJucator = fontObj.render("Jucător:", True, culoareText)
    display.blit(textJucator, (pozitie_x, pozitie_y + 100))
    textTip = fontObj.render("Tip joc:", True, culoareText)
    display.blit(textTip, (pozitie_x, pozitie_y + 170))
    textDificultate = fontObj.render("Dificultate:", True, culoareText)
    display.blit(textDificultate, (pozitie_x, pozitie_y + 240))
    textDimensiune = fontObj.render("Număr linii:", True, culoareText)
    display.blit(textDimensiune, (pozitie_x, pozitie_y + 310))
    textDimensiune = fontObj.render("Număr coloane:", True, culoareText)
    display.blit(textDimensiune, (pozitie_x, pozitie_y + 380))

    poz_butoane = 400
    btn_alg = GrupButoane(
        top=pozitie_y + 30,
        left=poz_butoane,
        listaButoane=[
            Buton(display=display, w=120, h=40, text="MiniMax", valoare="1"),
            Buton(display=display, w=120, h=40, text="AlphaBeta", valoare="2")
        ],
        indiceSelectat=1)
    btn_juc = GrupButoane(
        top=pozitie_y + 100,
        left=poz_butoane,
        listaButoane=[
            Buton(display=display, w=50, h=40, text="X", valoare="x"),
            Buton(display=display, w=50, h=40, text="0", valoare="0")
        ],
        indiceSelectat=0)
    btn_tip = GrupButoane(
        top=pozitie_y + 170,
        left=poz_butoane,
        listaButoane=[
            Buton(display=display, w=80, h=40, text="J vs J", valoare="1"),
            Buton(display=display, w=80, h=40, text="J vs C", valoare="2"),
            Buton(display=display, w=80, h=40, text="C vs C", valoare="3")
        ],
        indiceSelectat=1)
    btn_dif = GrupButoane(
        top=pozitie_y + 240,
        left=poz_butoane,
        listaButoane=[
            Buton(display=display, w=120, h=40, text="Începător", valoare="1"),
            Buton(display=display, w=100, h=40, text="Mediu", valoare="2"),
            Buton(display=display, w=100, h=40, text="Avansat", valoare="3")
        ],
        indiceSelectat=0)

    dim = 40
    distanta = 200
    minus_img_lin = pygame.image.load("minus.png")
    minus_img_lin = pygame.transform.smoothscale(minus_img_lin, (dim, dim))
    minus_rect_lin = minus_img_lin.get_rect(topleft=(poz_butoane, pozitie_y + 310))
    display.blit(minus_img_lin, (poz_butoane, pozitie_y + 310))

    plus_img_lin = pygame.image.load("plus.png")
    plus_img_lin = pygame.transform.smoothscale(plus_img_lin, (dim, dim))
    plus_rect_lin = plus_img_lin.get_rect(topleft=(poz_butoane + distanta, pozitie_y + 310))
    display.blit(plus_img_lin, (poz_butoane + distanta, pozitie_y + 310))

    nrLinii = Buton(display=display, top=pozitie_y+310, left=poz_butoane+100, w=50, h=40, text="4", valoare="4", culoareFundal=(73, 123, 254))
    nrLinii.deseneaza()

    minus_img_col = pygame.image.load("minus.png")
    minus_img_col = pygame.transform.smoothscale(minus_img_col, (dim, dim))
    minus_rect_col = minus_img_col.get_rect(topleft=(poz_butoane, pozitie_y + 380))
    display.blit(minus_img_col, (poz_butoane, pozitie_y + 380))

    plus_img_col = pygame.image.load("plus.png")
    plus_img_col = pygame.transform.smoothscale(plus_img_col, (dim, dim))
    plus_rect_col = plus_img_col.get_rect(topleft=(poz_butoane + distanta, pozitie_y + 380))
    display.blit(plus_img_col, (poz_butoane + distanta, pozitie_y + 380))

    nrColoane = Buton(display=display, top=pozitie_y+380, left=poz_butoane+100, w=50, h=40, text="4", valoare="4", culoareFundal=(73, 123, 254))
    nrColoane.deseneaza()

    start = pygame.image.load("start.png")
    start = pygame.transform.smoothscale(start, (187, 50))
    start_rect = start.get_rect(topleft=(356, pozitie_y + 480))
    display.blit(start, (356, pozitie_y + 480))
    btn_alg.deseneaza()
    btn_juc.deseneaza()
    btn_tip.deseneaza()
    btn_dif.deseneaza()
    culoareText = (255, 255, 255)
    fontObj = pygame.font.SysFont("comicsansms", 20)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if minus_rect_lin.collidepoint(pos):
                    val = int(nrLinii.valoare) - 1
                    if val < 4:
                        val = 4
                    nrLinii.valoare = val
                    nrLinii.textRandat = fontObj.render(str(nrLinii.valoare), True, culoareText)
                    nrLinii.deseneaza()
                elif plus_rect_lin.collidepoint(pos):
                    val = int(nrLinii.valoare) + 1
                    if val > 10:
                        val = 10
                    nrLinii.valoare = val
                    nrLinii.textRandat = fontObj.render(str(nrLinii.valoare), True, culoareText)
                    nrLinii.deseneaza()
                elif minus_rect_col.collidepoint(pos):
                    val = int(nrColoane.valoare) - 1
                    if val < 4:
                        val = 4
                    nrColoane.valoare = val
                    nrColoane.textRandat = fontObj.render(str(nrColoane.valoare), True, culoareText)
                    nrColoane.deseneaza()
                elif plus_rect_col.collidepoint(pos):
                    val = int(nrColoane.valoare) + 1
                    if val > 10:
                        val = 10
                    nrColoane.valoare = val
                    nrColoane.textRandat = fontObj.render(str(nrColoane.valoare), True, culoareText)
                    nrColoane.deseneaza()
                if not btn_alg.selecteazaDupacoord(pos):
                    if not btn_juc.selecteazaDupacoord(pos):
                        if not btn_tip.selecteazaDupacoord(pos):
                            if not btn_dif.selecteazaDupacoord(pos):
                                # if start.selecteazaDupacoord(pos):
                                if start_rect.collidepoint(pos):
                                    # display.fill((0, 0, 0))  # stergere ecran
                                    # tabla_curenta.deseneaza_grid()
                                    return btn_juc.getValoare(), btn_alg.getValoare(), btn_tip.getValoare(), \
                                        btn_dif.getValoare(), nrLinii.valoare, nrColoane.valoare
        pygame.display.update()


def main():
    # folosire cod salvat
    raspuns_valid = False
    folosire_joc_salvat = False
    while not raspuns_valid:
        raspuns = input("Incarcati un joc salvat? (raspundeti cu 1 sau 2)\n 1.Da\n 2.Nu\n ")
        if raspuns in ['1', '2']:
            raspuns_valid = True
            folosire_joc_salvat = True if raspuns == '1' else False
        else:
            print("Nu ati ales o varianta corecta.")
    if folosire_joc_salvat:
        listaFisiere = os.listdir("salvari")
        print("Lista de jocuri salvate: ")
        for i in range(len(listaFisiere)):
            print(i,"-", listaFisiere[i])
        raspuns_valid = False
        while not raspuns_valid:
            raspuns = input("Alegeti un joc salvat: ")
            if raspuns in [str(i) for i in range(len(listaFisiere))]:
                raspuns_valid = True
                fisier = listaFisiere[int(raspuns)]
                print("Ati ales jocul salvat:", fisier)
            else:
                print("Nu ati ales o varianta corecta.")
        with open("salvari/" + fisier, "r") as f:
            sir = f.read()
            val = [elem.split("=")[1] for elem in sir.split('\n')]
            jcurent, adancime, estimare, N, M, JMIN, JMAX, ponderi, admax, tabla, tip_algoritm, tip_joc = val[:12]
            Joc.N = int(N)
            Joc.M = int(M)
            matr = ast.literal_eval(tabla)
            PONDERI = ast.literal_eval(ponderi)
            Joc.JMIN = JMIN
            Joc.JMAX = JMAX
            Joc.ADANCIME_MAX = int(admax)
            Joc.PONDERI = PONDERI
            tabla_curenta = Joc(tabla=matr, lin=int(N), col=int(M))
            adancime = 0 if adancime == 'None' else int(adancime)
            estimare = 0 if estimare == 'None' else float(estimare)
            stare_curenta = Stare(tabla_curenta, jcurent, adancime, estimare)
            ecran = pygame.display.set_mode(size=(900, 750))

            # statistici
            mutari_calculator, mutari_utilizator, minim_timp, maxim_timp = [float(elem) for elem in val[12:16]]
            minim_noduri, maxim_noduri, timp_total = [float(elem) for elem in val[16:19]]
            timpi = ast.literal_eval(val[19])
            noduri = ast.literal_eval(val[20])
            mediu_timp = sum(timpi)
            mediu_noduri = sum(noduri)
            # cand se va scadea timpul de start din timpul final,
            # -(-timp_total) = + timp_total (deci se va aduna)
            t_joc_start = int(round(time.time() * 1000)) - timp_total
            ecran = pygame.display.set_mode(size=(900, 750))
            pygame.display.set_caption('Udrea Iulia - X și 0')
            ecran.fill((0, 82, 192))
            pygame.font.init()
    else:
        ecran = pygame.display.set_mode(size=(900, 750))
        pygame.display.set_caption('Udrea Iulia - X și 0')
        ecran.fill((0, 83, 191))
        pygame.font.init()
        Joc.JMIN, tip_algoritm, tip_joc, dificultate, N, M = deseneaza_alegeri(ecran)
        print(Joc.JMIN, tip_algoritm, tip_joc, dificultate, N, M)
        Joc.N = int(N)
        Joc.M = int(M)
        Joc.JMAX = '0' if Joc.JMIN == 'x' else 'x'

        # alegerea ponderilor pentru a doua estimare
        PONDERI = [0.1, 0.3, 1, 2, 5]
        Joc.PONDERI = PONDERI
        Joc.ADANCIME_MAX = int(dificultate)

        tabla_curenta = Joc(lin=Joc.N, col=Joc.M)
        print("Tabla initiala")
        print(str(tabla_curenta))

        stare_curenta = Stare(tabla_curenta, 'x', Joc.ADANCIME_MAX)

        # initizare variabile pentru statistici
        mutari_calculator = mutari_utilizator = 0
        timpi = []
        noduri = []
        minim_timp = minim_noduri = float('inf')
        maxim_timp = maxim_noduri = float('-inf')
        mediu_timp = mediu_noduri = 0
        t_joc_start = int(round(time.time() * 1000))

    # setari interf grafica
    ecran.fill((0, 82, 192))
    dim_celula = 60
    Joc.initializeaza(ecran, dim_celula)
    tabla_curenta.deseneaza_grid()
    ok = True

    # afisarea scorului in interfata grafica
    dim = 30
    pozy = (750 - 60 * Joc.NR_LINII - 100) / 2 + 60 * Joc.NR_LINII + 40
    img_x = pygame.image.load("x_roz_deschis.png")
    img_x = pygame.transform.smoothscale(img_x, (dim, dim))
    ecran.blit(img_x, (330, pozy))

    img_0 = pygame.image.load("zero_galben.png")
    img_0 = pygame.transform.smoothscale(img_0, (dim, dim))
    ecran.blit(img_0, (540, pozy))

    font = pygame.font.SysFont("comicsansms", 30)
    titlu = font.render("- Scor -", True, (255, 255, 255))

    if Joc.JMAX == 'x':
        scx = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)
        sc0 = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)
    else:
        sc0 = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)
        scx = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)

    scorx = Buton(display=ecran, left=330, top= pozy + 40, w=dim, h=dim, culoareFundal=(0, 82, 192), text=str(scx), culoareText=(255, 255, 255), font="comicsansms", fontDimensiune=30)
    scor0 = Buton(display=ecran, left=540, top= pozy + 40, w=dim, h=dim, culoareFundal=(0, 82, 192), text=str(sc0), culoareText=(255, 255, 255), font="comicsansms", fontDimensiune=30)
    scorx.deseneaza()
    scor0.deseneaza()
    ecran.blit(titlu, (400, pozy - 10))
    pygame.display.update()

    def afisareStatistici():
        t_joc_final = int(round(time.time() * 1000))
        print(f"Timpii de gandire ai calculatorului: minim: {minim_timp}, maxim: {maxim_timp},"
              f" mediu: {mediu_timp / mutari_calculator if mutari_calculator > 0 else 0},"
              f" mediana: {statistics.median(timpi) if len(timpi) > 0 else 0}")
        print(f"Numarul de noduri generate de calculator: minim: {minim_noduri}, maxim: {maxim_noduri},"
              f" mediu: {mediu_noduri / mutari_calculator if mutari_calculator > 0 else 0},"
              f" mediana: {statistics.median(noduri) if len(noduri) > 0 else 0}")
        print(f"Numarul de mutari ale calculatorului: {mutari_calculator}")
        print(f"Numarul de mutari ale utilizatorului: {mutari_utilizator}")
        print(f"Timpul total de joc: {t_joc_final - t_joc_start} milisecunde")

    def reseteazaStatistici():
        nonlocal mutari_calculator, mutari_utilizator, timpi, noduri, minim_timp
        nonlocal minim_noduri, maxim_timp, maxim_noduri, mediu_timp, mediu_noduri, t_joc_start
        t_joc_start = int(round(time.time() * 1000))
        mutari_calculator = mutari_utilizator = 0
        timpi = []
        noduri = []
        minim_timp = minim_noduri = float('inf')
        maxim_timp = maxim_noduri = float('-inf')
        mediu_timp = mediu_noduri = 0

    def mutareCalculator():
        nonlocal stare_curenta, mutari_calculator, timpi, noduri, minim_timp, minim_noduri
        nonlocal maxim_timp, maxim_noduri, mediu_timp, mediu_noduri, ok
        print("Acum muta calculatorul cu simbolul", stare_curenta.j_curent)

        # preiau timpul in milisecunde de dinainte de mutare
        t_inainte = int(round(time.time() * 1000))

        # resetarea variabilelor globale nr_noduri_min_max si nr_noduri_alpha_beta
        global nr_noduri_min_max
        nr_noduri_min_max = 0
        global nr_noduri_alpha_beta
        nr_noduri_alpha_beta = 0

        noduri_generate = None
        # stare actualizata e starea mea curenta in care am setat stare_aleasa (mutarea urmatoare)
        if tip_algoritm == '1':
            stare_actualizata = min_max(stare_curenta)
            noduri_generate = nr_noduri_min_max
        else:  # tip_algoritm==2
            stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            noduri_generate = nr_noduri_alpha_beta

        stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc  # aici se face de fapt mutarea !!!

        if Joc.JMAX == 'x':
            scx = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)
            sc0 = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)
        else:
            sc0 = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)
            scx = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)
        scorx.textRandat = font.render(str(scx), 1, (255, 255, 255))
        scor0.textRandat = font.render(str(sc0), 1, (255, 255, 255))
        scorx.deseneaza()
        scor0.deseneaza()

        print("Tabla dupa mutarea calculatorului")

        print(str(stare_curenta))
        stare_curenta.tabla_joc.deseneaza_grid()
        t_dupa = int(round(time.time() * 1000))
        print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")

        print("Estimarea calculata de calculator este: " + str(stare_actualizata.estimare))
        print("Numarul de noduri generate de algoritm este: " + str(noduri_generate))

        # actualizare timp minim, maxim si mediu
        timp = t_dupa - t_inainte
        timpi.append(timp)
        if timp < minim_timp:
            minim_timp = timp
        if timp > maxim_timp:
            maxim_timp = timp
        mediu_timp += timp

        # actualizare noduri generate minim, maxim si mediu
        noduri.append(noduri_generate)
        if noduri_generate < minim_noduri:
            minim_noduri = noduri_generate
        if noduri_generate > maxim_noduri:
            maxim_noduri = noduri_generate
        mediu_noduri += noduri_generate

        print(f"Scorul este c:{stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)} - "
              f"u:{stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)}")

        mutari_calculator += 1
        if (afis_daca_final(stare_curenta)):
            castigator = stare_curenta.tabla_joc.final()
            # daca jocul s-a terminat, se afiseaza in interfata
            if castigator != 'remiza':
                mesaj = font.render("A câștigat jucătorul", True, (255, 255, 255))
                ecran.blit(mesaj, (270, pozy+80))
                if castigator == 'x':
                    img = img_x
                else:
                    img = img_0
                ecran.blit(img, (560, pozy+90))
            else:
                mesaj = font.render("Remiza!", True, (255, 255, 255))
                ecran.blit(mesaj, (400, pozy+80))
            pygame.display.flip()
            afisareStatistici()
            ok = False

        # S-a realizat o mutare. Jucatorul cu cel opus
        stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)

    def salveaza_stare(stare):
        nonlocal mutari_calculator, mutari_utilizator, timpi, noduri, minim_timp, tip_algoritm
        nonlocal minim_noduri, maxim_timp, maxim_noduri, mediu_timp, mediu_noduri, t_joc_start, tip_joc
        nume_fisier = input("Introduceti numele fisierului in care doriti sa salvati jocul: ")
        with open("salvari/" + nume_fisier, 'w') as f:
            f.write(stare.__repr__())
            sir = f"TIPALG={tip_algoritm}\nTIPJOC={tip_joc}\nMCALC={mutari_calculator}\nMUTIL={mutari_utilizator}\n" \
                  f"MINTIMP={minim_timp}\nMAXTIMP={maxim_timp}\nMINNOD={minim_noduri}\nMAXNOD={maxim_noduri}\n" \
                  f"TIMP={int(round(time.time() * 1000)) - t_joc_start}\nTIMPI={timpi}\nNODURI={noduri}"
            f.write(sir)

    def mutareJucator(simbol=Joc.JMIN):
        nonlocal stare_curenta, mutari_utilizator, ok
        # preiau timpul in milisecunde de dinainte de mutare
        t_inainte = int(round(time.time() * 1000))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # inchide fereastra
                # daca nu s-a terminat jocul, afisez statisticile, altfel se vor afisa oricum la ultima mutare
                if not stare_curenta.tabla_joc.final():
                    afisareStatistici()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # jocul se reseteaza dar se pastreaza informatiile cerute la inceput
                    stare_curenta = Stare(Joc(lin=Joc.N, col=Joc.M), 'x', Joc.ADANCIME_MAX)
                    reseteazaStatistici()
                    Joc.initializeaza(ecran, dim_celula)
                    stare_curenta.tabla_joc.deseneaza_grid()
                elif event.key == pygame.K_s:
                    # se salveaza starea curenta a jocului
                    salveaza_stare(stare_curenta)
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:  # click
                pos = pygame.mouse.get_pos()  # coordonatele clickului
                for linie in range(Joc.NR_LINII):
                    for coloana in range(Joc.NR_COLOANE):
                        # verifica daca punctul cu coord pos se afla in dreptunghi(celula)
                        if ((linie + coloana) % 2 == 0 and stare_curenta.tabla_joc.matr[
                            linie * Joc.NR_COLOANE + coloana] == Joc.GOL
                                and Joc.celuleGrid[linie][coloana].collidepoint(pos)):
                            # plasez simbolul pe "tabla de joc"
                            stare_curenta.tabla_joc.matr[linie * Joc.NR_COLOANE + coloana] = simbol
                            stare_curenta.tabla_joc.deseneaza_grid()
                            # afisarea starii jocului in urma mutarii utilizatorului
                            print("\nTabla dupa mutarea jucatorului")
                            print(str(stare_curenta))

                            t_dupa = int(round(time.time() * 1000))
                            print("Utilizatorul a \"gandit\" timp de " + str(
                                t_dupa - t_inainte) + " milisecunde.")

                            mutari_utilizator += 1
                            if Joc.JMAX == 'x':
                                scx = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)
                                sc0 = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)
                            else:
                                sc0 = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)
                                scx = stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)
                            scorx.textRandat = font.render(str(scx), 1, (255, 255, 255))
                            scor0.textRandat = font.render(str(sc0), 1, (255, 255, 255))
                            scorx.deseneaza()
                            scor0.deseneaza()
                            pygame.display.update()

                            print(f"Scorul este c:{stare_curenta.tabla_joc.calculeaza_scor(Joc.JMAX)} - "
                                  f"u:{stare_curenta.tabla_joc.calculeaza_scor(Joc.JMIN)}")

                            # testez daca jocul a ajuns intr-o stare finala
                            # si afisez un mesaj corespunzator in caz ca da
                            if (afis_daca_final(stare_curenta)):
                                castigator = stare_curenta.tabla_joc.final()
                                # daca jocul s-a terminat, se afiseaza in interfata
                                if castigator != 'remiza':
                                    mesaj = font.render("A câștigat jucătorul", True, (255, 255, 255))
                                    ecran.blit(mesaj, (270, pozy + 80))
                                    if castigator == 'x':
                                        img = img_x
                                    else:
                                        img = img_0
                                    ecran.blit(img, (560, pozy + 90))
                                else:
                                    mesaj = font.render("Remiza!", True, (255, 255, 255))
                                    ecran.blit(mesaj, (400, pozy + 80))
                                pygame.display.flip()
                                afisareStatistici()
                                ok = False
                                break

                            # S-a realizat o mutare. Schimb jucatorul cu cel opus
                            stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)

    if tip_joc == '1':
        # jucator vs jucator
        Joc.JMAX = 'x'
        Joc.JMIN = '0'
        stare_curenta.j_curent = Joc.JMAX
        while ok:
            if stare_curenta.j_curent == Joc.JMIN:
                mutareJucator(Joc.JMIN)
            else:
                mutareJucator(Joc.JMAX)
    elif tip_joc == '2':
        # jucator vs calculator
        while ok:
            if stare_curenta.j_curent == Joc.JMIN:
                mutareJucator()
            else:
                mutareCalculator()
    elif tip_joc == '3':
        # calculator vs calculator
        Joc.JMAX = 'x'
        Joc.JMIN = '0'
        stare_curenta.j_curent = Joc.JMAX
        jucator = 'x'
        while ok:
            # calculator vs calculator
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            if jucator == 'x':
                Joc.JMAX = 'x'
                Joc.JMIN = '0'
                Joc.PONDERI = None
                mutareCalculator()
                time.sleep(0.5)
                jucator = '0'
            else:
                Joc.JMAX = '0'
                Joc.JMIN = 'x'
                Joc.PONDERI = PONDERI
                mutareCalculator()
                time.sleep(0.5)
                jucator = 'x'


if __name__ == "__main__":
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
