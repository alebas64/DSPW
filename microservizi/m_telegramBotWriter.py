"""
Questo microservizio serve per interagire con gli utenti 
tramite i messaggi del bot telegram
"""

# funzione per invio di messaggi a un utente registrato
# tramite bot telegram 
def send_message(chat_id, text):
    request_url = api_request + "sendMessage"
    params = {
        'chat_id' : str(chat_id),
        'text' : text
    }
    response = requests.get(request_url,params)
    return response.json()

