![VVVVID-Downloader](https://socialify.git.ci/CoffeeStraw/VVVVID-Downloader/image?description=1&descriptionEditable=Un%20piccolo%20script%20in%20Python3%20per%20scaricare%20contenuti%20multimediali%20(non%20a%20pagamento)%20offerti%20da%20VVVVID&font=KoHo&forks=1&issues=1&language=1&owner=1&pattern=Charlie%20Brown&stargazers=1&theme=Dark)

---

## 📚 Descrizione
**VVVVID Downloader** è una comoda soluzione per scaricare dei contenuti dal noto sito **VVVVID**, tutto ciò di cui necessita è il **link** alla serie/film o ad un singolo episodio, al resto ci penserà lui.
 In particolare, sono distinguibili due casistiche per i link:
- Link a **singolo episodio**: lo script scaricherà da quell'episodio in poi, solamente gli episodi di quella stagione.
- Link a **pagina di un film/anime** con lista episodi: lo script scaricherà tutti gli episodi di tutte le stagioni disponibili o il singolo film.

Durante lo sviluppo si è scelto di adottare queste convenzioni poiché sono risultate essere quelle più comode per l'uso quotidiano. Il progetto è comunque aperto a soluzioni alternative ed è possibile discuterne aprendo una issue.

## ⚙️ Installazione
### Release (Windows)
*NON ANCORA FUNZIONANTE, per il momento riferirsi a **Per developer**.*

Scaricate [l'ultima release](https://github.com/CoffeeStraw/VVVVID-Downloader/releases). Vi ritroverete con un *.zip*, che dovrete scompattare. Per avviare il programma basterà quindi lanciare l'eseguibile.

### Docker
Per installare ed utilizzare il software tramite **Docker**, basterà lanciare il file ```vvvvvid-downloader.sh```. Esso si occuperà di lanciare il container e monterà la cartella dei *Downloads* come volume esterno.

### Per Developer
Ovviamente la prima cosa da fare è scaricare il progetto, usando `git clone` oppure scaricandone lo zip e poi estraendolo dove più vi è comodo. Dopodiché:

1. Lo script richiede Python3, [scaricabile qui](https://www.python.org/downloads/). **Nota per gli utenti Windows**: è necessario che durante l'installazione sia aggiunto Python3 al PATH. Una possibile guida per l'installazione è consultabile [qui](https://realpython.com/installing-python/).
2. Vanno installate le librerie esterne. Per farlo, recatevi nella cartella del progetto ed utilizzate pip (oppure pip3 nel caso non vada) per installarle: 
```sh
pip install -r requirements.txt
```
3. A questo punto basterà avviare il programma: 
```sh
python main.py
```

## 🎮 Utilizzo
Per poter utilizzare VVVVID Downloader, tutto quello che dovrete fare è porre il link a ciò che desiderate scaricare da VVVVID all'interno del file **downloads_list.txt**, che contiene già degli esempi.
## ℹ️ Note:
- Se avete più link, vanno posizionati ognuno su una linea a parte.
- Le linee che cominciano con **#** saranno ignorate, può tornare utile se volete ignorare temporaneamente qualcosa ad esempio.
- Per motivi di copyright VVVVID non è disponibile all'estero, per cui è necessario possedere un indirizzo IP italiano.

## 🧭 Licenza
Il presente software è distribuito sotto licenza MIT. Si legga il file `LICENSE` per ulteriori informazioni.
