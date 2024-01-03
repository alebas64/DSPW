"""
Questo microservizio serve per interagire con il bot telegram. Il suo unico scopo
è leggere tutti i messaggi che riceve e passarli ai microservizi che li devono
gestire/elaborare
"""

import requests
api_url = "https://api.telegram.org/bot"
api_token = "6860123323:AAFxGrDJ4tjaPS0mnkRgNmjNTG6CYBxH1AI"
api_request = api_url + api_token +"/"

def getUpdates():
    request_url = api_request+"getUpdates"
    params = {
        "offset": 0,
        "limit": 15
    }
    while True:
        response = requests.get(request_url,params).json()
        results = response["result"]
        if len(results) == 0:
            break
        else:
            params["offset"]=results[0]["update_id"]+len(results)
        return_value = 0
        for x in results:
            x = x["message"]
            elements = x["text"].split(" ")
            match elements[0]:
                case "/start":
                    return_value = checkNewRegisteredUser(x)
                    if return_value != False:
                        #funzione di notifica che l'utente è nuovo
                        #bisogna aggiornare il database
                        send_message(return_value["chat_id"],"Ciao e benvenuto!")
                    break

                case "/listConstraint":
                    listConstraint(x["from"]["username"],x["from"]["id"])

                case "addConstraint":
                    addConstraint(x["from"]["username"],elements[1],elements[2],elements[3],elements[4])
                    
                case "/deleteConstraint":
                    deleteConstraint(x["from"]["username"],elements[1])
                    
                case _:
                    break

#microservizio per aggiungere un nuovo contraint per le
#notifiche dell'utente
#parametry: username utente, città, giorno attuale o prossimo per la previsione, valore
def addConstraint(username,city,day,value):
    pass

# rimozione di un constraint di un utente
def deleteConstraint(username, id_constraint):
    pass


def listConstraint(username,chat_id):
    #conterrà il messaggio da restituire all'utente
    message_to_send=""
    constraint_list=getConstraintsList(username)

    if len(constraint_list) == 0:
        message_to_send = "Nessun constraint presente"
    else:
        
        message_to_send=""
    send_message(chat_id,message_to_send)


# tramite questa funzione viene restituita una lista contenente tutti i constraint
# Note: impostare la query mysql in modo che restituisca un array di array configurato in questo modo
# [id sottoscrizione, città, codice legenda, valore(null se non previsto)]
def getConstraintsList(username):
    legend_value
    pass

#questo microservizio restituisce una lista degli utenti che sono registrati
#al bot
def getRegisteredUsers():
    registeredUsers = set()
    #accesso al database per ottenere gli utenti attualmente registrati
    #aggiunta di valori al set() degli utenti registrati
    return registeredUsers

#questo microservizio dovrebbe controllare se l'utente che ha scritto start
#non ha mai utilizzato l'applicazione oppure ha scritto nuovamente il comando
def checkNewRegisteredUser(x):
    #aggiungere funzione per ottenere gli user attualmente registrati
    tmp = getRegisteredUsers()
    newUser = False 
    if x["from"]["username"] not in tmp:
        newUser = {
                "nome":x["from"]["first_name"],
                "cognome":x["from"]["last_name"],
                "username":x["from"]["username"],
                "chat_id":x["from"]["id"]
        }
    return newUser
