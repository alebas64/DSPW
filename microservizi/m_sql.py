"""
Questo microservizio serve per interagire con il server mysql, salvando, modificando
e visualizzando i dati utente
"""
import requests
import mysql.connector
geo_api_url = "http://api.openweathermap.org/geo/1.0/direct"

geo_params = {
    'q':'',
    'limit': 5,
    'appid': '241cf7e334517a031d31287144b10f1a'
}

def coords(city,country_code="IT"):
    geo_params["q"] = '{'+city+'},{'+country_code+'}'
    json_response = requests.get(geo_api_url,geo_params).json()
    city_selected = json_response[0]
    for x in json_response:
        if x["country"] == country_code:
            city_selected = x
            city_selected.pop("country",None)
            city_selected.pop("state",None)
            city_selected.pop("local_names",None)
            break
    return city_selected

def database_connection():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dsds"
    )
    return mydb

def database_cursor():
    return mydb.cursor()

def close(mycursor,mydb):
    mycursor.close()
    mydb.close()

# salva un nuovo utente nel database mysql
def addUser(mydb,mycursor,nome,cognome,telegram,chat_id=0):
    if chat_id == 0:
        sql = "INSERT INTO utente (nome,cognome,telegram) VALUES (%s,%s,%s)"
        val = (nome,cognome,telegram)
    else:
        sql = "INSERT INTO utente (nome,cognome,telegram,id_chat) VALUES (%s,%s,%s,%s)"
        val = (nome,cognome,telegram,str(chat_id))
    mycursor.execute(sql,val)
    mydb.commit()

# questa funzione serve per aggiungere l'identificatore della chat che un utente
# ha con il bot telegram al record personale di mysql (qualora sia cambiata la chat
# oppure non era stata creata in precedenza)
def alterUserID(mydb,mycursor,telegram,chat_id):
    sql = "UPDATE utente SET id_chat = %s WHERE utente.telegram = %s"
    val=(str(chat_id),telegram)
    mycursor.execute(sql,val)
    mydb.commit()

# questa funzione aggiunge una notifica di un evento 
# metereologico per un determinato utente
def addConstraint(mydb,mycursor,telegram,citta,cod_legenda,valore="NULL"):
    #sql principale per inserire un nuova sottoscrizione a un servizio
    #sql_citta="SELECT id FROM citta WHERE nome = %s"
    sql_citta="SELECT id FROM citta WHERE nome = '"+citta+"'"
    #val_citta=tuple(citta)
    #mycursor.execute(sql_citta,val_citta)
    mycursor.execute(sql_citta)
    
    if mycursor.rowcount == 0:
        # in questo caso la città non è mai stata richiesta da nessuno
        # bisogna richiedere le coordinate alla api di openweather
        sql_citta_new = "INSERT INTO citta"
        pass
    
    if valore=="NULL":
        sql_sub = "INSERT INTO constraints (cod_citta,cod_constraint,cod_utente) VALUES (%s,%s,%s)"
    else:
        pass
    

# questa funzione rimuove una notifica specifica di un evento 
# metereologico per un determinato utente
def removeConstraint(mydb,mycursor):
    pass

# questa funzione restituisce tutte le notifiche degli eventi 
# metereologici di un determinato utente
def listAllConstraint(mydb,mycursor):
    pass


# -----------------------------------------------------------
# I codici sottostanti sono test per verificare il corretto
# funzionamento delle funzioni sviluppate 
# -----------------------------------------------------------

if __init__ == '__main__':    
    debug_procedures() # solo per debug. Non sarà presente nella versione definitiva

def debug_procedures():
    mydb = database_connection()
    mycursor = database_cursor()
    #print(mydb)

    mycursor.execute("SELECT * from legenda")
    for x in mycursor:
        print(x)

    # sql = "INSERT INTO legenda (nome,descrizione) VALUES (%s,%s)"
    # val = ("testing","valore inserito da python per testing")
    # mycursor.execute(sql,val)
    # mydb.commit()

    #addUser(mydb,mycursor,"Aracno","Fobico","fifatantaa")
    #addUser(mydb,mycursor,"Aracno","Fobico","fifatantaaa",43)

    #alterUserID(mydb,mycursor,"fifatantaa",463572)

    addConstraint(mydb,mycursor,"alebas64","Roma","3")
    addConstraint(mydb,mycursor,"alebas64","Siracusa","3")

    close(mycursor,mydb)

    #coords("Syracuse","US")
    #coords("Siracusa")
    #coords("Milano","IT")
    #coords("Parigi","USA")