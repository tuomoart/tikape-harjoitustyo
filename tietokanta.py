import DbExceptionHandler
import sqlite3
from prettytable import PrettyTable
from datetime import datetime
import random
import sys

class Tietokanta:
    def __init__(self, tietokanta):
        self.db=sqlite3.connect(tietokanta)
        self.db.isolation_level = None

        self.c=self.db.cursor()

        self.handler = DbExceptionHandler.DbExceptionHandler()

    def createdb(self, indeksoitu):
        queries = ["CREATE TABLE IF NOT EXISTS Asiakkaat (id INTEGER PRIMARY KEY, nimi TEXT UNIQUE);",
                    "CREATE TABLE IF NOT EXISTS Paikat (id INTEGER PRIMARY KEY, nimi TEXT UNIQUE);",
                    "CREATE TABLE IF NOT EXISTS Paketit (id INTEGER PRIMARY KEY, asiakas_id INTEGER, seurantakoodi TEXT UNIQUE);",
                    "CREATE TABLE IF NOT EXISTS Tapahtumat (id INTEGER PRIMARY KEY, paketti_id INTEGER, paikka_id INTEGER, kuvaus TEXT, aika DATE);",
                    "CREATE TRIGGER IF NOT EXISTS asiakas_ei_loydy_lisatessa_paketti BEFORE INSERT ON Paketit BEGIN SELECT CASE WHEN NEW.asiakas_id IS NULL THEN RAISE(ABORT,'Asiakasta ei loydy!') END; END;",
                    "CREATE TRIGGER IF NOT EXISTS paketti_ei_loydy_lisatessa_tapahtuma BEFORE INSERT ON Tapahtumat BEGIN SELECT CASE WHEN NEW.paikka_id IS NULL THEN RAISE(ABORT, 'Paikkaa ei loydy!') END; END;",
                    "CREATE TRIGGER IF NOT EXISTS paikka_ei_loydy_lisatessa_tapahtuma BEFORE INSERT ON Tapahtumat BEGIN SELECT CASE WHEN NEW.paketti_id IS NULL THEN RAISE(ABORT, 'Pakettia ei loydy!') END; END;"]

        for query in queries:
            try:
                self.c.execute(query)
            except:
                self.handler.handle(sys.exc_info())

        if indeksoitu:
            self.indeksoi()

    def deletedb(self):
        self.c.execute("DROP TABLE IF EXISTS Asiakkaat;")
        self.c.execute("DROP TABLE IF EXISTS Paikat;")
        self.c.execute("DROP TABLE IF EXISTS Paketit;")
        self.c.execute("DROP TABLE IF EXISTS Tapahtumat;")

    def indeksoi(self):
        try:
            self.c.execute("CREATE INDEX idx_asiakkaat ON Asiakkaat (nimi);")
            self.c.execute("CREATE INDEX idx_Paikat ON Paikat (nimi);")
            self.c.execute("CREATE INDEX idx_paketit ON Paketit (seurantakoodi);")
            self.c.execute("CREATE INDEX idx_paketit_asiakas_id ON Paketit (asiakas_id)")
            self.c.execute("CREATE INDEX idx_tapahtumat_paketti_id ON Tapahtumat (paketti_id)")
            self.c.execute("CREATE INDEX idx_tapahtumat_paikka_id ON Tapahtumat (paikka_id)")
        except:
            self.handler.handle(sys.exc_info())

    def lisaaPaikka(self, paikka):
        try:
            self.c.execute("INSERT INTO Paikat (nimi) VALUES (?);",[paikka])
        except:
            return self.handler.handle(sys.exc_info())
        return 0

    def lisaaAsiakas(self, nimi):
        try:
            self.c.execute("INSERT INTO Asiakkaat (nimi) VALUES (?);",[nimi])
        except:
            return self.handler.handle(sys.exc_info())
        return 0

    def lisaaPaketti(self, asiakas, koodi):
        try:
            self.c.execute("INSERT INTO Paketit (asiakas_id, seurantakoodi) VALUES ((SELECT id FROM Asiakkaat WHERE nimi=?),?);", [asiakas,koodi])
        except:
            return self.handler.handle(sys.exc_info())
        return 0

    def lisaaTapahtuma(self, koodi, paikka, kuvaus, aika):
        try:
            self.c.execute("INSERT INTO Tapahtumat (paketti_id, paikka_id, kuvaus, aika) VALUES ((SELECT id FROM Paketit WHERE seurantakoodi=?),(SELECT id FROM Paikat WHERE nimi=?),?, DATETIME('now','localtime'))",[koodi, paikka, kuvaus])
        except:
            return self.handler.handle(sys.exc_info())
        return 0

    def getAsiakas(self, nimi):
        self.c.execute("SELECT id FROM Asiakkaat WHERE nimi = ?",[nimi])
        tulos = self.c.fetchone()
        if tulos==None:
            return -1
        return int(tulos[0])

    def getPaketti(self, koodi):
        self.c.execute("SELECT id FROM Paketit WHERE seurantakoodi = ?",
        [koodi])
        tulos = self.c.fetchone()
        if tulos==None:
            return -1
        return int(tulos[0])

    def getPaikka(self, nimi):
        self.c.execute("SELECT id FROM Paikat WHERE nimi = ?",[nimi])
        tulos=self.c.fetchone()
        if (tulos==None):
            return -1
        return int(tulos[0])

    def haeTapahtumatKoodilla(self, koodi):
        if self.getPaketti(koodi)==-1:
            return 665
        try:
            self.c.execute("SELECT aika, Paikat.nimi, kuvaus FROM Paikat LEFT JOIN Tapahtumat ON Paikat.id=paikka_id WHERE paketti_id=(SELECT id FROM Paketit WHERE seurantakoodi=?);",[koodi])
        except:
            return self.handler.handle(sys.exc_info())
        return self.c.fetchall(),["Aika","Paikka","Kuvaus"]

    def haeAsiakkaanPaketit(self, asiakas):
        if self.getAsiakas(asiakas)==-1:
            return 664
        try:
            self.c.execute("SELECT Paketit.seurantakoodi, COUNT(TapP.id) FROM Paketit LEFT JOIN Tapahtumat TapP ON Paketit.id=TapP.paketti_id WHERE Paketit.asiakas_id=(SELECT id FROM Asiakkaat WHERE nimi=?) GROUP BY Paketit.seurantakoodi ;",[asiakas])
        except:
            return self.handler.handle(sys.exc_info())
        return self.c.fetchall(),["paketti", "tapahtumia"]

    def haePaikanTapahtumat(self, paikka, paiva):
        if(self.getPaikka(paikka)==-1):
            return 666
        try:
            self.c.execute("SELECT COUNT(id) FROM Tapahtumat WHERE paikka_id=(SELECT id FROM Paikat WHERE nimi=?) AND DATE(aika)=DATE(?)",[paikka,paiva])
        except:
            return self.handler.handle(sys.exc_info())
        return self.c.fetchall(),["tapahtumia"]


    def tulostaPaikat(self):
        self.c.execute("SELECT * FROM Paikat;")
        self.tulostaTaulu(self.c.fetchall(),[])

    def tulostaAsiakkaat(self):
        self.c.execute("SELECT * FROM Asiakkaat;")
        self.tulostaTaulu(self.c.fetchall(),[])

    def tulostaPaketit(self):
        self.c.execute("SELECT * FROM Paketit;")
        self.tulostaTaulu(self.c.fetchall(),[])

    def tulostaTapahtumat(self):
        self.c.execute("SELECT * FROM Tapahtumat;")
        self.tulostaTaulu(self.c.fetchall(),["id","paketti_id", "paikka_id",
        "kuvaus", "aika"])

    def tulostaTaulu(self, taulu, otsikot):
        t=PrettyTable(otsikot)
        i=0
        while i<len(taulu):
            t.add_row(taulu[i])
            i=i+1
        print(t)

    def tehokkuustesti(self):
        print()
        print("Ilman indeksointia:")
        print()
        self.tehokkuustestiSuoritus(False)

        print()
        print()
        print("Indeksoituna:")
        print()
        self.tehokkuustestiSuoritus(True)

    def tehokkuustestiSuoritus(self, indeksoitu):
        self.deletedb()

        self.createdb(indeksoitu)

        alku=datetime.now()

        paikat = []
        asiakkaat = []
        paketit = []

        i=1
        while i<=1000:
            paikat.append(["P"+str(i)])
            asiakkaat.append(["A"+str(i)])
            paketit.append([i,i])

            i+=1

        i=0

        tapahtumatq="INSERT INTO Tapahtumat (paketti_id, paikka_id, kuvaus, aika) VALUES ((SELECT id FROM Paketit WHERE seurantakoodi=?), (SELECT id FROM Paikat WHERE nimi=?),?,DATETIME('now','localtime'))"
        tapahtumatParams=[]
        while i<1000000:
            tapahtumatParams.append([str(random.randrange(1,1001,1)),
            "P"+str(random.randrange(1,1001,1)),"tapahtuma "+str(i)])
            i+=1
        self.c.execute("BEGIN TRANSACTION;")
        alku=datetime.now()
        self.c.executemany("INSERT INTO Paikat (nimi) VALUES (?)", paikat)
        print("Paikkojen lisäämisessä kesti: " + str(datetime.now()-alku))
        alku=datetime.now()
        self.c.executemany("INSERT INTO Asiakkaat (nimi) VALUES (?)", asiakkaat)
        print("Asiakkaiden lisäämisessä kesti: " + str(datetime.now()-alku))
        alku=datetime.now()
        self.c.executemany("INSERT INTO Paketit (asiakas_id, seurantakoodi) VALUES (?,?)", paketit)
        print("Pakettien lisäämisessä kesti: " + str(datetime.now()-alku))
        alku=datetime.now()
        self.c.executemany("INSERT INTO Tapahtumat (paketti_id, paikka_id, kuvaus, aika) VALUES ((SELECT id FROM Paketit WHERE seurantakoodi=?),(SELECT id FROM Paikat WHERE nimi=?),?, DATETIME('now','localtime'))", tapahtumatParams)
        print("Tapahtumien lisäämisessä kesti: " + str(datetime.now()-alku))
        self.c.execute("COMMIT;")

        i=0

        alku=datetime.now()
        while i<1000:
            self.c.execute("SELECT COUNT(id) FROM Paketit WHERE asiakas_id = (SELECT id FROM Asiakkaat WHERE nimi=?)",asiakkaat[i])
            i+=1
        print("Asiakkaiden pakettien määrän hakemisessa meni: "
        +str(datetime.now()-alku))

        i=0
        alku = datetime.now()
        while i<2000:
            self.c.execute("SELECT COUNT(paketti_id) FROM Tapahtumat WHERE paketti_id = (SELECT id FROM Paketit WHERE seurantakoodi = ?)", [str(i)])
            i+=2

        print("Pakettien tapahtumien määrän hakemisessa meni: "
        +str(datetime.now()-alku))
