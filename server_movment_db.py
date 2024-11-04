import socket 
import time
import sqlite3
from threading import Thread
import alphabot #importo la classe AlphaBot
#indirizzo del server e della porta diversa per i due socket
MY_ADDRESS = ("192.168.1.126", 9090)			#socket per il ricevimento dei comandi
HEART_BEAT_ADDRESS = ("192.168.1.126",9091)		#socket per il controllo della connessione
BUFFER_SIZE = 4096

lista_comandi = ["w","d","s","a","W","A","S","D"]

#funzione per il continuo controllo della connessione
def heartbeat_recive(heartbeat, alpha):
    
    #setta un timer di 2 secondi sul socket
    heartbeat.settimeout(2)
    
    #controlla che non ci siano problemi nella connessione
    try:
        while True:
            try:
                
                #riceve il messaggio dal client
                data = heartbeat.recv(BUFFER_SIZE).decode()
                
                #controlla che il messaggio non sia vuoto
                if not data:
                    break
                
            #eccezione nel caso in cui il timer di 2 secondi sul socket scade prima che riceva un messaggio
            except socket.timeout:
                print("FERMA TUTTO")
                alpha.stop()	#ferma i motori così si evita che continui ad andare avanti all'infinito
                
            #eccezione nel caso di un errore nella comunicazione
            except Exception as e:
                print(f"Errore {e}")
    #se ci sono probremi nella connessione o riceve un messaggio vuoto si chiude la connessione
    finally:
        heartbeat.close()

def movement(comando, alpha):
    if comando == "F":
        print("avanti")
        alpha.forward()
    elif comando == "B":
        print("indietro")
        alpha.backward()
    elif comando == "L":
        print("sinistra")
        alpha.left()
    elif comando == "R":
        print("destra")
        alpha.right()

def main():
    #crea l'oggetto alphabot
    alpha = alphabot.AlphaBot()
    #ferma i motori perché nel costruttore sono attivi
    alpha.stop()
    
    #creo il collegamento tramite socket tra pc e alphabot per l'invio dei dei comandi
    command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command.bind(MY_ADDRESS)
    command.listen(1)
    
    #crea il collegamento tramite socket tra pc e alphabot per il controllo della connessione.
    #se la connessione si interrompe e l'alphabot si stava muovendo si blocca e non continua il muovimento
    heartbeat_recived = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    heartbeat_recived.bind(HEART_BEAT_ADDRESS)
    heartbeat_recived.listen(1)
    
    #accetta entrambe le connessioni
    recive_heartbeat, _ = heartbeat_recived.accept() #bloccante
    command, client_address = command.accept() #bloccante
    
    print(f"Il client {client_address} si è connesso")
    
    #crea il thread per il controllo della connessione tra pc e alphabot tramite la funzione heartbeat_recive
    thread_heartbeat = Thread(target=heartbeat_recive, args=(recive_heartbeat,alpha))
    thread_heartbeat.start()
    
    conn = sqlite3.connect('mio_database.db')
    cur = conn.cursor()
    #ciclo while True in cui c'è il continuo ricevimento dei comandi inviati dal pc
    while True:
        #riceve il comando e lo decodifico
        message = command.recv(BUFFER_SIZE)
        direz_decode = message.decode()
        if direz_decode in lista_comandi:
            #controllo sul comando ricevuto ed esecuzione dalla funzione 
            #dell'oggetto alpha corrispondente al comando ricevuto
            if direz_decode == "w":
                print("avanti")
                alpha.forward()
            elif direz_decode == "s":
                print("indietro")
                alpha.backward()
            elif direz_decode == "a":
                print("sinistra")
                alpha.left()
            elif direz_decode == "d":
                print("destra")
                alpha.right()
            #se un qualsiasi tasto di quelli precedenti viene rilasciato si ferma
            elif direz_decode.isupper(): #controlla se è maiuscola perché nel client trasforma 
                print("stop")			 #la lettera rilasciata per differenziarla dai comandi (minuscoli)
                alpha.stop()
        else:
            #query per la lettura dei comandi nel db
            cur.execute(f'''SELECT str_mov
                        FROM Comandi
                        WHERE tasto = "{direz_decode}"
                ''')

            conn.commit()
            tupla_com_db = cur.fetchall() #lettura dei dati presi dal db
            print(tupla_com_db)
            try:
                com_db = tupla_com_db[0][0]
                #controlla se allinterno del messaggio ci sono più comandi
                if "," in com_db:
                    #divide i diversi comandi
                    com_db = com_db.split(",")
                    #li invia uno alla volta alla funzione per il movimento
                    for i in com_db:
                        comando = i[0]
                        durata = i[1:]
                        movement(comando, alpha)
                        time.sleep(int(durata)/100) #durata movimento in centesimi di secondi
                        alpha.stop()
                else:
                    comando = com_db[0]
                    durata = com_db[1:]
                    movement(comando, alpha)
                    time.sleep(int(durata)/100) #durata movimento in centesimi di secondi
                    alpha.stop()
            except:
                pass
    s.close()

if __name__ == "__main__":
    main()