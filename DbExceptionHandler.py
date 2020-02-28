

class DbExceptionHandler:


    def handle(self, exception):
        if str(exception[1])=="UNIQUE constraint failed: Asiakkaat.nimi":
            return 1
        elif str(exception[1])=="UNIQUE constraint failed: Paketit.nimi":
            return 2
        elif str(exception[1])=="Asiakasta ei loydy!":
            return 3
        elif str(exception[1])=="UNIQUE constraint failed: Paketit.seurantakoodi":
            return 4
        elif str(exception[1])=="Pakettia ei loydy!":
            return 5
        elif str(exception[1])=="Paikkaa ei loydy!":
            return 6
        elif str(exception[1])=="UNIQUE constraint failed: Paikat.nimi":
            return 7
        print("Tuntematon virhe:")
        print(exception)
