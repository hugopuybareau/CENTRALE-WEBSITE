import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import json
import os
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as pltd
from datetime import datetime
import sqlite3
import matplotlib.dates as mdates
from matplotlib.dates import MonthLocator, DateFormatter


class hydro:
    def __init__(self,db):
        self.bibliotheque=db
        self.__conn=sqlite3.connect(db)
    
    
    #Fonction pour extraire le nom, lat et lon d'une station    
    def get_all(self):
        curseur = self.__conn.cursor()
        info=[]
        for i in range(1,260):
            l={'n' : i}
            curseur.execute("SELECT Y FROM Stationhydro WHERE n == {};".format(i))
            line1=curseur.fetchone()
            if line1==None : 
                pass
            else :
                l.update({'lat': float(str(line1).lstrip("('").rstrip("',)"))})
                
            curseur.execute("SELECT X FROM Stationhydro WHERE n == {};".format(i))
            line2=curseur.fetchone()
            if line1==None : 
                pass
            else :
                l.update({'lon' : float(str(line2).lstrip("('").rstrip("',)"))})
            
            curseur.execute("SELECT LbStationHydro FROM Stationhydro WHERE n == {};".format(i))
            line3=curseur.fetchone()
            l.update({'nom': str(line3)})
            info.append(l)
        return(info)    


      # = Fonction pour recueillir les informations d'une station quand on appuie sur un marker
      
    def get_info(self):
        curseur = self.__conn.cursor()
        info=[]
        for i in range(1,260):
            l={'n' : i}
            curseur.execute("SELECT CdCommune FROM StationHydro WHERE n == {};".format(i))
            line1=curseur.fetchone()
            if line1==None : 
                pass
            else :
                l.update({'Commune' : str(line1).lstrip("('").rstrip("',)")})
            
            curseur.execute("SELECT NomIntervenant FROM StationHydro WHERE n == {};".format(i))
            line2=curseur.fetchone()
            if line2==None : 
                pass
            else :
                l.update({'Intervenant' : str(line2).lstrip("('").rstrip("',)")})
                
            curseur.execute("SELECT LbStationHydro FROM StationHydro WHERE n == {};".format(i))
            line2=curseur.fetchone()
            if line2==None : 
                pass
            else :
                l.update({'Nom' : str(line2).lstrip("('").rstrip("',)")})
            
            curseur.execute("SELECT DtFermetureStationHydro FROM StationHydro WHERE n == {};".format(i))
            line3=curseur.fetchone()
            if line3 == (None,):
                l.update({"etat" : "Toujours ouverte"})
            else: 
                l.update({"etat" :  "Fermée depuis " + str(line3).lstrip("('").rstrip("',)")})
                
            curseur.execute("SELECT Y FROM StationHydro WHERE n == {};".format(i))
            line4=curseur.fetchone()
            if line4==None : 
                pass
            else :
                l.update({'lat': float(str(line4).lstrip("('").rstrip("',)"))})
                
            curseur.execute("SELECT CdStationHydroAncienRef FROM StationHydro WHERE n == {};".format(i))
            line4=curseur.fetchone()
            if line4==None : 
                pass
            else :
                l.update({'codeStation': str(line4).lstrip("('").rstrip("',)")})
            
            curseur.execute("SELECT X FROM StationHydro WHERE n == {};".format(i))
            line5=curseur.fetchone()
            if line4==None : 
                pass
            else :
                l.update({'lon' : float(str(line5).lstrip("('").rstrip("',)"))})
            info.append(l)
        return(info)
    
    
def courbe(self,Nstation,h,debut1, fin1):
    #On change le format des dates
    debut2 = datetime.strptime(debut1, "%Y-%m-%d")
    debut = debut2.strftime("%d-%m-%Y")
    fin2 = datetime.strptime(fin1, "%Y-%m-%d")
    fin = fin2.strftime("%d-%m-%Y")
    
    #On fait appel à la base de donnée
    conn = sqlite3.connect("HydrométrieBretagne.db")
    curseur = conn.cursor()
    
    #on récupère les dates comprises entre les deux limites indiqués et pour la station donnée
    curseur.execute("SELECT Date  from Hydrometrie  WHERE CodesiteHydro3= '{}' AND date(substr(Date, 7, 4) || '-' || substr(Date, 4, 2) || '-' || substr(Date, 1, 2))BETWEEN '{}' AND '{}';".format(Nstation,debut1,fin1))
    dates = curseur.fetchall()
    dates = [str(date).lstrip("('").rstrip("',)") for date in dates]
    dates = [datetime.strptime(date, "%d/%m/%Y") for date in dates]
    
    #on récupère les données demandées pour les dates comprises entre les deux limites indiqués et pour la station donnée
    curseur.execute("SELECT {}  from Hydrometrie  WHERE CodesiteHydro3= '{}' AND date(substr(Date, 7, 4) || '-' || substr(Date, 4, 2) || '-' || substr(Date, 1, 2))BETWEEN '{}' AND '{}';".format(h.replace('true',''),Nstation,debut1,fin1))

                    
    V_list = curseur.fetchall()
    V_list = [float(str(vf).lstrip("('").rstrip("',)")) if str(vf).lstrip("('").rstrip("',)") != "None" else None for vf in V_list]
    
    dates_datetime = [mdates.datestr2num(date.strftime('%d-%m-%Y')) for date in dates]
    # Conversion des dates au format "yyyy/mm"
    dates_formatted = [mdates.num2date(date).strftime('%Y/%m') for date in dates_datetime]
    
    #Cas ou il n'y a pas de données
    if len(V_list) == 0 or V_list.count(None) == len(V_list): 
        plt.switch_backend('Agg')
        plt.figtext(0.5, 0.5, 'Pas de données pour cette station à ces dates', fontsize=12, ha='center')
        plt.savefig("client/courbe/Figure{}_{}_{}{}.png".format(h.replace('true',''),Nstation,debut1,fin1))
    #Sinon, on trace la courbe et on l'enregistre
    else:
        plt.switch_backend('Agg')
        plt.plot(dates, V_list)
        plt.title('Évolution de la donnée ' + str(h.replace('true','')))
        plt.xticks(rotation=25)
        plt.grid()
        plt.savefig("client/courbe/Figure{}_{}_{}{}.png".format(h.replace('true',''),Nstation,debut1,fin1)) 
    return
#
# Définition du nouveau handler
#
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  #
  # On surcharge la méthode qui traite les requêtes GET
  #
  def do_GET(self):

    # On récupère les étapes du chemin d'accès
    self.init_params()

    # le chemin d'accès commence par /location
    if self.path_info[0] == 'location':
      self.send_location()
   
     # le chemin d'accès commence par /info
    elif self.path_info[0] == 'info':
      self.send_info()
      
    # le chemin d'accès commence par /courbes
    elif self.path_info[0] == 'courbes':
      self.send_courbes()
      
    # ou pas...
    else:
      self.send_static()
  #
  # On surcharge la méthode qui traite les requêtes HEAD
  #
  def do_HEAD(self):
    self.send_static()

  #
  # On envoie le document statique demandé
  #
  def send_static(self):

    # on modifie le chemin d'accès en insérant un répertoire préfixe
    self.path = self.static_dir + self.path

    # on appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)
  
  #     
  # on analyse la requête pour initialiser nos paramètres
  #
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
      elif ctype == 'application/json' :
        self.params = json.loads(self.body)
    else:
      self.body = ''
   
    # traces
    print('info_path =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)
    
  #
  # On envoie un document avec l'heure
  #
  def send_location(self):
    
    
    Station = hydro('StationHydro_bretagne1.db')
    data = Station.get_all() 
    #On supprime les images du cache quand on lance le site
    
    #dossier où sont les images
    dossier_images = 'client/courbe'
    
    # Liste des extensions d'images prises en compte
    extensions_images = ['.jpg', '.jpeg', '.png', '.gif']
    
    # Parcourir tous les fichiers du dossier
    for fichier in os.listdir(dossier_images):
        chemin_fichier = os.path.join(dossier_images, fichier)
        # Vérifier si le fichier a une extension d'image
        if os.path.isfile(chemin_fichier) and os.path.splitext(fichier)[1].lower() in extensions_images:
            # Supprimer le fichier
            os.remove(chemin_fichier)
    self.send_json(data)

  #
  # On génère et on renvoie la liste des régions et leur coordonnées (version TD3, §5.1)
  #
  def send_info(self):
      
    #On supprime les images du cache quand on clique sur un marker
    dossier_images = 'client/courbe'
    
    # Liste des extensions d'images prises en compte
    extensions_images = ['.jpg', '.jpeg', '.png', '.gif']
    
    # Parcourir tous les fichiers du dossier
    for fichier in os.listdir(dossier_images):
        chemin_fichier = os.path.join(dossier_images, fichier)
        # Vérifier si le fichier a une extension d'image
        if os.path.isfile(chemin_fichier) and os.path.splitext(fichier)[1].lower() in extensions_images:
            # Supprimer le fichier
            os.remove(chemin_fichier)
            
            
    SHydro = hydro('StationHydro_bretagne1.db')
    data = SHydro.get_info() 
    print(data[0])
    for c in data:
      if c['n'] == int(self.path_info[1]):
        self.send_json(c)
        break

  #
  # On génère et on renvoie un graphique de ponctualite (cf. TD1)
  #
  def send_courbes(self):

    reponse =   self.query_string
    liste = reponse.split("&")
    print('liste' , liste)
    debut = ""
    fin = ""
    id_station = ""
    key = ""
    for mot in liste : 
        if "debut" in mot : 
            debut = mot 
            debut = debut.lstrip("debut=")
        elif "fin" in mot :
            fin = mot
            fin = fin.lstrip("fin=")
        elif "id_station" in mot :
            id_station = mot
            id_station = id_station.lstrip("id_station=")
        elif "key" in mot :
            key = mot
            key = key.lstrip("key=")
        

    graphe = courbe(self,id_station, key, debut, fin) 
    

            
    
  #
  # On envoie les entêtes et le corps fourni
  #
  
  def send_json(self,data,headers=[]):
    body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
    self.send_response(200)
    self.send_header('Content-Type','application/json')
    self.send_header('Content-Length',int(len(body)))
    [self.send_header(*t) for t in headers]
    self.end_headers()
    self.wfile.write(body) 
    
    
  def send(self,body,headers=[]):

    # on encode la chaine de caractères à envoyer
    encoded = bytes(body, 'UTF-8')

    # on envoie la ligne de statut
    self.send_response(200)

    # on envoie les lignes d'entête et la ligne vide
    [self.send_header(*t) for t in headers]
    self.send_header('Content-Length',int(len(encoded)))
    self.end_headers()

    # on envoie le corps de la réponse
    self.wfile.write(encoded)

 
#
# Instanciation et lancement du serveur
#
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()

