import random
import traceback


class Zasobnik(list):
    """
    hrací pole, ukládají se sem žetony
    """
    def __init__(self, nazev=None):
        self._nazev = nazev

    def je_volno(self, hrac) -> bool:
        return not ((len(self) > 1 and self[-1].get_colour != hrac.id))

    def add_stone(self, stone):
        stone.save_pos(self._nazev)
        self.append(stone)

    def odeber_stone(self):
        self.pop(len(self) - 1)

    def last_stone(self):
        return None if len(self) == 0 else self[-1]

    def ascii_obsahu(self):
        output = ""
        for kamen in self.obsah:
            output += f"{kamen.get_colour} "
        return output

    @property
    def nazev(self):
        return self._nazev

    @property
    def obsah(self):
        return self


class Dicebasket:
    """
    kelímek s kostkami
    """
    def __init__(self, dicecount):
        self.dicecount = dicecount
        self.dicevalue = []

    def throw(self):
        for i in range(self.dicecount):
            self.dicevalue.append(random.randint(1, 6))
        """
        kontrola stejného hodu a přidání stejných hodnot
        """
        if len(set(self.dicevalue)) == 1:
            for i in range(self.dicecount):
                self.dicevalue.append(self.dicevalue[0])
        return self.dicevalue


class Stone:
    """
    herní kámen
    """
    def __init__(self, colour):
        self._colour = colour
        self._pos_list = []

    def save_pos(self, pos):
        self._pos_list.append(pos)

    @property
    def get_colour(self):
        return self._colour


class Deska:
    """
    herní deska, obsahuje herní pole(zásobníky)
    """
    def __init__(self, delka):
        self._delka = delka
        self._obsah = []

    def pridej_pole(self, pole):
        self._obsah.append(pole)

    @property
    def obsah(self):
        return self._obsah

    @property
    def delka(self):
        return self._delka


class Tah:
    """
    třída pro tah, poskytuje informace o tahu
    """
    def __init__(self, start, cil, dice):
        self._start = start
        self._cil = cil
        self._kostka = dice

    @property
    def zacatek(self):
        return self._start

    @property
    def cil(self):
        return self._cil

    @property
    def dice(self):
        return self._kostka


class Hrac:
    """
    poskytuje informace o hráči
    """
    def __init__(self, id, jmeno, strana):
        self._id = id
        self._strana = strana
        self._jmeno = jmeno
        self._home = 0

    @property
    def id(self):
        return self._id

    @property
    def strana(self):
        return self._strana

    @property
    def jmeno(self):
        return self._jmeno

    @property
    def home(self):
        return self._home

    @home.setter
    def home(self, value):
        self._home = value


class Logika:
    """
    samostatná třída pro zpracování hry
    """
    def __init__(self):
        self._deska = Deska(24)
        self._dice = Dicebasket(2)
        self.dohrano = False
        self._hraci = []
        self._bar = Zasobnik()
        self._aktivni_kostka = []
        self._mozne_tahy = []
        self._aktivni_hrac = None
        self.nova_hra()

    def nova_hra(self):
        self.inicializace()
        self.nove_kolo()

    def inicializace(self):
        """
        připraví hru
        """
        self.vytvor_hrace()
        self.napln_desku()
        self.zakladni_kameny()
        self._aktivni_hrac = self._hraci[0]

    def print_current_state(self):
        """
        metoda pro vypsání stavu hry
        """
        i = 0
        for pole in self._deska.obsah:
            print(f"[{pole._nazev + 1}]: {pole.ascii_obsahu()}")
        print(f"Hraje: {self._aktivni_hrac.jmeno}({self._aktivni_hrac.id})")
        print(f"Tvůj hod: {self._aktivni_kostka}")
        for tah in self._mozne_tahy:
            if type(tah.zacatek) == str:
                print(f"[{i}]: pro hod {tah.dice} z pozice {tah.zacatek} na {tah.cil + 1}")

            elif type(tah.cil) == str:
                print(f"[{i}]: pro hod {tah.dice} z pozice {tah.zacatek + 1} na {tah.cil}")

            elif type(tah.zacatek) == str and type(tah.cil) == str:
                print(f"[{i}]: pro hod {tah.dice} z pozice {tah.zacatek} na {tah.cil}")

            else:
                print(f"[{i}]: pro hod {tah.dice} z pozice {tah.zacatek + 1} na {tah.cil + 1}")
            i += 1

    def hod_kostky(self):
        self._aktivni_kostka = self._dice.throw()

    def vytvor_tahy(self):
        self._mozne_tahy = self.tahy_hrace(self._aktivni_hrac)
        if len(self._mozne_tahy) < 1:
            self.vymen_hrace()

    def nove_kolo(self):
        if self.win_check():
            return
        self.vytvor_tahy()
        if len(self._aktivni_kostka) < 1 or len(self._mozne_tahy) < 1:
            self.vymen_hrace()
        self.print_current_state()

    def tah_zadani(self, input):
        try:
            if input == "konec":
                self.ukonci_hru()
            else:
                zadani = int(input)
                if zadani < 0 or zadani > len(self._mozne_tahy):
                    print("zadej validní číslo")
                    return
                self.tah_provedeni(self._mozne_tahy[zadani])
        except Exception as e:
            print(e)
            traceback.print_exc()

    def tah_provedeni(self, tah):
        if tah.zacatek == "bar":
            self.proved_tah_bar(tah)
        elif tah.cil == "domek":
            self.proved_tah_home(tah)
        else:
            self.proved_tah_normal(tah)
        self._aktivni_kostka = self.zbyvajici_hody(self._aktivni_kostka, tah.dice)
        self.nove_kolo()

    def ukonci_hru(self):
        print("konec hry")
        self.dohrano = True

    def vymen_hrace(self):
        self._aktivni_hrac = self._hraci[
            (self._hraci.index(self._aktivni_hrac) + 1) % len(self._hraci)]  # swapuje [0] a [1]
        self.hod_kostky()
        self.vytvor_tahy()

    def win_check(self):
        """
        hlídá počet kamenů ve hře, když není žádný -> výhra
        :return: bool
        """
        if len(self.hracovi_figurky(self._aktivni_hrac)) == 0:
            self.ukonci_hru()
            return True
        return False


    def proved_tah_bar(self, tah):
        """
        provede tah  z a do baru
        :param tah: tah
        """
        kamen = None
        for zet in self._bar:
            if zet.get_colour == self._aktivni_hrac.id:
                kamen = zet
        pole_nove = self.najdi_pole(tah.cil)
        if len(pole_nove.obsah) > 0 and pole_nove.last_stone().get_colour != self._aktivni_hrac.id:
            self._bar.append(pole_nove.last_stone())
            pole_nove.odeber_stone()
        self._bar.remove(kamen)
        pole_nove.add_stone(kamen)

    def proved_tah_home(self, tah):
        """
        provede tah do domku
        :param tah: tah
        """
        zet = self.najdi_kamen(tah.zacatek)
        self.najdi_hrace(zet.get_colour).home += 1
        self.najdi_pole(tah.zacatek).odeber_stone()

    def proved_tah_normal(self, tah):
        """
        provede normální tah
        :param tah: tah
        """
        kamen = self.najdi_kamen(tah.zacatek)
        pole_puvodni = self.najdi_pole(tah.zacatek)
        pole_nove = self.najdi_pole(tah.cil)
        if pole_nove.je_volno(self.najdi_hrace(kamen.get_colour)):
            pole_puvodni.odeber_stone()
            if len(pole_nove.obsah) > 0 and pole_nove.last_stone().get_colour != kamen.get_colour:
                self._bar.append(pole_nove.last_stone())
                pole_nove.last_stone().save_pos("bar")
                pole_nove.odeber_stone()
            pole_nove.add_stone(kamen)

    def tahy_hrace(self, hrac):
        """
        nabídka tahů
        :param hrac: hráč
        :return: list tahů
        """
        for kamen in self._bar:
            if kamen.get_colour == hrac.id:
                return self.bar_tahy(hrac)
        vse = []
        if self.home_check(hrac):
            vse += self.home_tahy(hrac)
        vse += self.overall_tahy(hrac)
        return vse

    def bar_tahy(self, hrac):
        """
        nabídka tahů baru
        :param hrac: hráč
        :return: list tahů
        """
        vysledek = []
        for cislo in set(self._aktivni_kostka):
            if (hrac.strana == "nahoru"):
                pol = self.najdi_pole(24 - cislo)
            else:
                pol = self.najdi_pole(-1 + cislo)
            if pol.je_volno(hrac):
                vysledek.append(Tah("bar", pol._nazev, cislo))
        return vysledek

    def home_tahy(self, hrac):
        """
        nabídka tahů do domečku
        :param hrac: hráč
        :return: list tahů
        """
        vysledek = []
        for cislo in set(self._aktivni_kostka):
            for pole in self._deska.obsah:
                if pole.last_stone() != None and pole.last_stone().get_colour == hrac.id:
                    if (hrac.strana == "nahoru"):
                        if pole._nazev - cislo < 0:
                            vysledek.append(Tah(pole._nazev, "domek", cislo))
                    else:
                        if pole._nazev + cislo > 23:
                            vysledek.append(Tah(pole._nazev, "domek", cislo))
        return vysledek

    def overall_tahy(self, hrac):
        """
        nabídka tahů
        :param hrac: hráč
        :return: list tahů
        """
        vysledek = []
        for cislo in set(self._aktivni_kostka):
            for pole in self._deska.obsah:
                if pole.last_stone() != None and pole.last_stone().get_colour == hrac.id:
                    if ((pole._nazev - cislo > -1) and hrac.strana == "nahoru") or (
                            (pole._nazev + cislo < 24) and hrac.strana == "dolu"):  # pokud to je na desce
                        if (hrac.strana == "nahoru"):
                            pol = self.najdi_pole(pole._nazev - cislo)
                        else:
                            pol = self.najdi_pole(pole._nazev + cislo)
                        if pol.je_volno(hrac):
                            vysledek.append(Tah(pole._nazev, pol._nazev, cislo))
        return vysledek

    def home_check(self, hrac):
        """
        kontroluje, zda je kámen na prvních šeti, resp. posledních šeti polích
        :param hrac: hráč
        :return: true, když kámen je na pozici, kdy může táhnout do domku
        """
        for pole in self._deska.obsah:
            if hrac.strana == "nahoru":
                if pole._nazev > 5 and pole.last_stone() != None and pole.last_stone().get_colour == hrac.id:
                    return False
            else:
                if pole._nazev < 18 and pole.last_stone() != None and pole.last_stone().get_colour == hrac.id:
                    return False
        return True

    def hracovi_figurky(self, hrac):
        """
        přidává kameny na desce do listu, potřeba pro kontrolu výhry
        :param hrac: hráč
        :return: list kamenů
        """
        kameny = []
        for pole in self._deska.obsah:
            for kamen in pole.obsah:
                if kamen.get_colour == hrac.id:
                    kameny.append(kamen)
        return kameny

    def najdi_pole(self, nazev):
        """
        :param nazev: cislo pole
        :return: herní pole
        """
        for pole in self._deska.obsah:
            if pole._nazev == nazev:
                return pole

    def najdi_kamen(self, nazev):
        """
        :param nazev: cislo pole
        :return: poslení kámen v poli
        """
        return self.najdi_pole(nazev).last_stone()

    def zbyvajici_hody(self, kostka, hod):
        """
        smaže použitý hod
        :param kostka: aktivní kostka
        :param hod: číslo hodu, který se odehrál
        :return: zbylé hody
        """
        vys = kostka
        vys.pop(kostka.index(hod))
        print(f"zbyvající hody: {vys}")
        return vys

    def najdi_hrace(self, id):
        for hrac in self._hraci:
            if hrac.id == id:
                return hrac
        return None

    def napln_desku(self):
        for i in range(self._deska.delka):
            self._deska.pridej_pole(Zasobnik(i))

    def zakladni_kameny(self):
        ids = []
        for hrac in self._hraci:
            ids.append(hrac.id)
        self.napln_pole(0, 2, ids[0])
        self.napln_pole(11, 5, ids[0])
        self.napln_pole(16, 3, ids[0])
        self.napln_pole(18, 5, ids[0])
        self.napln_pole(5, 5, ids[1])
        self.napln_pole(12, 5, ids[1])
        self.napln_pole(7, 3, ids[1])
        self.napln_pole(23, 2, ids[1])

    def napln_pole(self, pozice, pocet, id_hrac):
        for pole in self._deska.obsah:
            if pole._nazev == pozice:
                for _ in range(pocet):
                    pole.obsah.append(Stone(id_hrac))

    def vytvor_hrace(self):
        self._hraci.append(Hrac("\u25CB", "Hráč 1", "dolu"))
        self._hraci.append(Hrac("\u25CF", "Hráč 2", "nahoru"))


def main():
    hra = Logika()

    while not hra.dohrano:
        player_input = input("Zadej číslo vypsaného tahu: ")
        hra.tah_zadani(player_input)


if __name__ == "__main__":
    main()