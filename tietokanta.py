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
            self.c.execute("INSERT INTO Paketit (asiakas_id, seurantakoodi) VALUES ((SELECT id FROM Asiakkaat WHERE nimi=?),?);",[asiakas,koodi])
        except:
            return self.handler.handle(sys.exc_info())
        return 0

    def lisaaTapahtuma(self, koodi, paikka, kuvaus, aika):
        try:
            self.c.execute("INSERT INTO Tapahtumat (paketti_id, paikka_id, kuvaus, aika) VALUES ((SELECT id FROM Paketit WHERE seurantakoodi=?),(SELECT id FROM Paikat WHERE nimi=?),?,DATETIME('now','localtime'))",[koodi, paikka, kuvaus])
        except:
            return self.handler.handle(sys.exc_info())
        return 0

    def getAsiakas(self, nimi):
        self.c.execute("SELECT id FROM Asiakkaat WHERE nimi = ?",[nimi])
        return int(self.c.fetchone()[0])

    def getPaketti(self, koodi):
        self.c.execute("SELECT id FROM Paketit WHERE seurantakoodi = ?",[koodi])
        return int(self.c.fetchone()[0])

    def getPaikka(self, nimi):
        self.c.execute("SELECT id FROM Paikat WHERE nimi = ?",[nimi])
        return int(self.c.fetchone()[0])

    def haeTapahtumatKoodilla(self, koodi):
        try:
            self.c.execute("SELECT aika, Paikat.nimi, kuvaus FROM Paikat LEFT JOIN Tapahtumat ON Paikat.id=paikka_id WHERE paketti_id=(SELECT id FROM Paketit WHERE seurantakoodi=?);",[koodi])
        except:
            return self.handler.handle(sys.exc_info())
        return self.c.fetchall(),["Aika","Paikka","Kuvaus"]

    def haeAsiakkaanPaketit(self, asiakas):
        try:
            self.c.execute("SELECT Paketit.seurantakoodi, COUNT((SELECT id FROM Tapahtumat TapA WHERE TapA.paketti_id=TapP.paketti_id)) FROM Paketit LEFT JOIN Tapahtumat TapP ON Paketit.id=TapP.paketti_id WHERE Paketit.asiakas_id=(SELECT id FROM Asiakkaat WHERE nimi=?)",[asiakas])
        except:
            return self.handler.handle(sys.exc_info())
        return self.c.fetchall(),["paketti", "tapahtumia"]

    def haePaikanTapahtumat(self, paikka, paiva):
        paikka_id=self.getPaikka(paikka)
        self.c.execute("SELECT COUNT(id) FROM Tapahtumat WHERE paikka_id=? AND DATE(aika)=DATE(?)",[paikka_id,paiva])
        print()
        print(paikka+":")
        self.tulostaTaulu(self.c.fetchall(),["Tapahtumia"])

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
        self.tulostaTaulu(self.c.fetchall(),["id","paketti_id", "paikka_id", "kuvaus", "aika"])

    def tulostaTaulu(self, taulu, otsikot):
        t=PrettyTable(otsikot)
        i=0
        while i<len(taulu):
            t.add_row(taulu[i])
            i=i+1
        print(t)

    def tehokkuustesti(self):
        self.deletedb()

        indeksoitu=bool(input("Käytetäänkö indeksointia? (true/false): "))
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

        tapahtumatq="INSERT INTO Tapahtumat (paketti_id, paikka_id, kuvaus, aika) VALUES ((SELECT id FROM Paketit WHERE seurantakoodi=?),(SELECT id FROM Paikat WHERE nimi=?),?,DATETIME('now','localtime'))"
        tapahtumatParams=[]
        while i<1000000:
            tapahtumatParams.append([str(random.randrange(1,1001,1)),"P"+str(random.randrange(1,1001,1)),"tapahtuma "+str(i)])
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
        self.c.executemany("INSERT INTO Tapahtumat (paketti_id, paikka_id, kuvaus, aika) VALUES ((SELECT id FROM Paketit WHERE seurantakoodi=?),(SELECT id FROM Paikat WHERE nimi=?),?,DATETIME('now','localtime'))", tapahtumatParams)
        print("Tapahtuminen lisäämisessä kesti: " + str(datetime.now()-alku))
        self.c.execute("COMMIT;")
