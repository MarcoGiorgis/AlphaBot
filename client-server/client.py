import socket
from pynput import keyboard
from threading import Thread
import time

#indirizzo del server e della porta diversa per i due socket
SERVER_ADDRESS = ("192.168.1.126", 9090)    #socket per l'invio  dei comandi
HEARTBEAT_ADDRESS = ("192.168.1.126", 9091) #socket per il controllo della connessione
BUFFER_SIZE = 4096

lista_comandi = [""]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(SERVER_ADDRESS)

def heartbeat_send(): #funzione per il controllo della comunicazione con il server
    send_heartbeat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_heartbeat.connect(HEARTBEAT_ADDRESS)
    while True:
        try:
            #invio continuo del messaggio per tenere la connessione attiva
            send_heartbeat.sendall("Ciao".encode())
            time.sleep(1)
        except Exception as e:
            #se c'è un errore blocca tutto
            print(f"Error: {e}")
            break
    send_heartbeat.close()

def on_press(key): #funzione di invio dei tasti premuti
    try:
        # Controlla se il tasto ha un attributo 'char' con la funzione hasattr
        if hasattr(key, 'char') and key.char != lista_comandi[-1]:  #controllo per permette al server di ricervere un solo comando alla volta per tasto
            lista_comandi.append(key.char.lower())  #il comando vinene inserito nella lista per evitare che venga continuamente inviato congestionando la comunicazione
            s.sendall(key.char.lower().encode())    #invio del comando con .lower() che serve a differenziare i comandi di movimento da quelli di stop
        if hasattr(key, 'char') and key.char == "w":
            print("press w")
        elif hasattr(key, 'char') and key.char == "s":
            print("press s")
        elif hasattr(key, 'char') and key.char == "a":
            print("press a")
        elif hasattr(key, 'char') and key.char == "d":
            print("press d")
    except AttributeError: #se si premono tasti speciali CTRL,ALT o SHIFT non blocca il codice
        pass


def on_release(key): #funzione tasti rilasciati
    global lista_comandi
    try:
        # Controlla se il tasto ha un attributo 'char' con la funzione hasattr
        if hasattr(key, 'char') and key.char == "w":
            print("release w")
        elif hasattr(key, 'char') and key.char == "s":
            print("release s")
        elif hasattr(key, 'char') and key.char == "a":
            print("release a")
        elif hasattr(key, 'char') and key.char == "d":
            print("release d")
        lista_comandi = [""]    #la lista per il controllo dei tasti già inviati si svuota in modo che dopo che viene rilasciato in modo che possa essere ripremuto
        if hasattr(key, 'char'):
            s.sendall(key.char.upper().encode()) #invio del comando con .upper() che serve a differenziare i comandi di stop da quelli di movimento
    except AttributeError: #se si premono tasti speciali CTRL,ALT o SHIFT non blocca il codice
        pass
    
def start_listener():
    #funzione ascoltatore degli eventi della tastiera
    with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
        listener.join() #oggetto ascoltatore
        
def main():
    t = Thread(target=heartbeat_send) #thread per controllo temporaneo sull'heartbeat
    t.start()   #parte il thread
    start_listener()
    while True:
        pass
    s.close()

if __name__ == "__main__":
    main()