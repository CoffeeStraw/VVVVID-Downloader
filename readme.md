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
Scaricate [l'ultima release](https://github.com/CoffeeStraw/VVVVID-Downloader/releases). Vi ritroverete con un *.zip*, che dovrete scompattare. Per avviare il programma basterà quindi lanciare "VVVVID Downloader.bat".

### Docker
Per installare ed utilizzare il software tramite **Docker**, basterà lanciare il file ```vvvvvid-downloader.sh```. Esso si occuperà di lanciare il container e monterà la cartella dei *Downloads* come volume esterno.

## 🎮 Utilizzo
Per poter utilizzare VVVVID Downloader, tutto quello che dovrete fare è porre il link a ciò che desiderate scaricare da VVVVID all'interno del file **downloads_list.txt**, che contiene già degli esempi.
## ℹ️ Note:
- Se avete più link, vanno posizionati ognuno su una linea a parte.
- Le linee che cominciano con **#** saranno ignorate, può tornare utile se volete ignorare temporaneamente qualcosa ad esempio.
- Per motivi di copyright VVVVID non è disponibile all'estero, per cui è necessario possedere un indirizzo IP italiano.

## 👨‍💻 Developers - Release Windows
Per creare l'eseguibile Windows viene utilizzato **pyinstaller**. I passaggi sono i seguenti:
- Creare un ambiente virtuale con ```venv``` ed attivarlo;
- Installare i requirements ed installare ```pyinstaller``` con **pip**;
- Produrre l'eseguibile col comando:
```sh
pyinstaller -F main.py
```
- Affiancare all'eseguibile i file ```downloads_list.txt``` e ```VVVVID Downloader.bat```, che potete trovare nelle release vecchie;
- Spostare l'eseguibile in una nuova cartella denominata ```bin/```;
- Includere nella cartella ```bin/``` anche l'eseguibile di ```ffmpeg```.

## 🧭 Licenza
Il presente software è distribuito sotto licenza MIT. Si legga il file `LICENSE` per ulteriori informazioni.
