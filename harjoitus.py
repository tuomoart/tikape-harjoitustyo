import sqlite3
from prettytable import PrettyTable
from datetime import datetime
import tietokanta
import sys
import os

def timeFormatHelper(aika):
    aika=int(aika)
    if (aika<10):
        return "0"+str(aika)
    return str(aika)

def formatTime(aika):
    try:
        palat=aika.split(".")
        palat[1]=timeFormatHelper(palat[1])
        palat[0]=timeFormatHelper(palat[0])
        uusiAika=""
        i=len(palat)-1
        while i>=0:
            uusiAika=uusiAika+palat[i]
            if i!=0:
                uusiAika=uusiAika+"-"
            i=i-1
        return uusiAika
    except:
        return -1

def tulostaOhjeet():
    print("Valitse toiminto (1-9):")
    print("0:  Lopeta")
    print("1:  Luo tietokanta")
    print("2:  Lisää paikka")
    print("3:  Lisää asiakas")
    print("4:  Lisää paketti")
    print("5:  Lisää tapahtuma")
    print("6:  Hae paketin tapahtumat")
    print("7:  Hae asiakkaan paketit")
    print("8:  Hae paikan tapahtumien määrä")
    print("9:  Suorita tehokkuustesti")
    if unlocked:
        print("10: Poista tietokanta")
        print("12: Tulosta taulu 'Paikat'")
        print("13: Tulosta taulu 'Asiakkaat'")
        print("14: Tulosta taulu 'Paketit'")
        print("15: Tulosta taulu 'Tapahtumat'")

def tulostaTaulu(taulu, otsikot):
    t=PrettyTable(otsikot)
    i=0
    while i<len(taulu):
        t.add_row(taulu[i])
        i=i+1
    print(t)

def main():
    tk=tietokanta.Tietokanta("database.db")
    clear = lambda: os.system('clear')
    clear()
    while True:
        tulostaOhjeet()
        inp=input("syötä komento: ")
        print()
        if inp=="":
            clear()
            continue
        elif inp=="0":
            print("heihei")
            break
        elif inp=="1":
            tk.createdb(True)
            print("Tietokanta luotu")
        elif inp=="2":
            nimi=input("Paikan nimi: ")
            status=tk.lisaaPaikka(nimi)
            if status==0:
                print("Paikka lisätty!")
            elif status==7:
                print("Paikka on jo lisätty!")
        elif inp=="3":
            nimi=input("Asiakkaan nimi: ")
            status=tk.lisaaAsiakas(nimi)
            if status==0:
                print("Asiakas lisätty!")
            elif status==1:
                print("Asiakas on jo lisätty!")
        elif inp=="4":
            nimi=input("Asiakkaan nimi: ")
            koodi=input("Seurantakoodi: ")
            status=tk.lisaaPaketti(nimi,koodi)
            if status==0:
                print("Paketti lisätty!")
            elif status==3:
                print("Asiakasta ei löydy!")
            elif status==4:
                print("Paketti on jo olemassa!")
        elif inp=="5":
            koodi = input("Anna seurantakoodi: ")
            paikka=input("Anna paikka: ")
            kuvaus=input("Anna kuvaus: ")
            aika=datetime.now()
            status=tk.lisaaTapahtuma(koodi, paikka, kuvaus, aika)
            if status==0:
                print("Tapahtuma lisätty!")
            elif status==5:
                print("Pakettia ei löydy!")
            elif status==6:
                print("Paikkaa ei löydy!")
        elif inp=="6":
            koodi=input("Anna seurantakoodi: ")
            status=tk.haeTapahtumatKoodilla(koodi)
            if status==665:
                print("Pakettia ei löytynyt!")
            else:
                tulostaTaulu(status[0],status[1])
        elif inp=="7":
            nimi=input("Asiakkaan nimi: ")
            status=tk.haeAsiakkaanPaketit(nimi)
            if status==664:
                print("Asiakasta ei löytynyt!")
            else:
                tulostaTaulu(status[0],status[1])
        elif inp=="8":
            paikka=input("Anna paikka: ")
            while True:
                paiva=input("Anna paiva (pp.kk.vvvv): ")
                paiva=formatTime(paiva)
                if paiva==-1:
                    print("Virheellinen päivämäärän muoto!")
                    continue
                break
            status=tk.haePaikanTapahtumat(paikka,paiva)
            if status==666:
                print("Paikkaa ei löytynyt!")
            elif len(status)>1:
                tulostaTaulu(status[0],status[1])
        elif inp=="9":
            tkt=tietokanta.Tietokanta("testbase.db")
            tkt.tehokkuustesti()
        elif inp=="10" and unlocked:
            tk.deletedb()
            print("Tietokanta poistettu")
        elif inp=="12" and unlocked:
            print("Paikat:")
            tk.tulostaPaikat()
        elif inp=="13" and unlocked:
            print("Asiakkaat:")
            tk.tulostaAsiakkaat()
        elif inp=="14" and unlocked:
            print("Paketit:")
            tk.tulostaPaketit()
        elif inp=="15" and unlocked:
            print("Tapahtumat:")
            tk.tulostaTapahtumat()
        else:
            print("Virheellinen komento!")
        input("Paina enter jatkaaksesi")
        clear()


if len(sys.argv)>1:
    unlocked=True
else:
    unlocked=False

main()
