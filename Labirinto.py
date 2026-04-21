
"""
Labirinto


Descrizione:
    Generazione di un labirinto “perfect maze” con visita in profondità (DFS) iterativa
    e backtracking esplicito.
    Le celle sono identificate da coordinate complesse (x + y*1j).
    Ogni cella contiene: [id_visita, posizione, muri, direzioni_possibili]
    dove l’ordine dei muri è: [Est, Nord, Ovest, Sud] (1 = muro presente, 0 = muro aperto),
    e l’ordine delle direzioni è: [Est, Nord, Ovest, Sud]
    (1 = direzione ammessa, 0 = direzione non ammessa).

    Nota:
    L’algoritmo presenta analogie con una visita in profondità (Depth-First Search, DFS)
    nella sua versione iterativa, ma non deriva da implementazioni preesistenti.
    È stato sviluppato in modo indipendente come costruzione logica autonoma,
    basata sull'idea di avanzare finché esistono direzioni ammesse e tornare
    alla cella precedente quando non ve ne sono, fino a completare la copertura del reticolo.

Algoritmo (sintesi):
    - Partenza da una cella sul perimetro (bordo aperto in ingresso) scelta in modo casuale
      e setup del muro sul perimetro.
    - Uscita: cella speculare rispetto all’ingresso e setup del muro sul perimetro.
    - Scelta casuale di una direzione ammessa, apertura dei muri condivisi,
      marcatura e avanzamento alla cella successiva.
    - Se non ci sono direzioni disponibili: backtrack alla cella precedente.

Parametri:
    XCOLONNE, YRIGHE  → dimensioni della griglia (1-based).

Visualizzazione:
    - Matplotlib: rendering dei muri con LineCollection.
    - Stampa testuale: elenco delle celle come liste:
      [id, (x+yj), [E, N, O, S], …] su stdout (per debug/analisi).



Autore: Alessio Severi
Licenza: MIT License

MIT License

Copyright (c) 2025 Alessio Severi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""



import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import random as rn



# ======================
# CONFIGURAZIONE
# =====================


# Dimensioni reticolo
XCOLONNE = 50
YRIGHE = XCOLONNE



# ======================
# FUNZIONI PRINCIPALI
# ======================

def setupReticolo() -> tuple[list, list, list, list, list, list, list]:

    # per ogni cella: [id_visita, posizione_cella, muri := [est := 1, nord := 1, ovest:= 1, sud := 1],
    # direzioni_possibili := [est := 1, nord := 1, ovest:= 1, sud := 1]]
    reticolo_interno = [[None, complex(x, y), [1, 1, 1, 1], [1, 1, 1, 1]] for x in range(2,XCOLONNE) for y in range(2,YRIGHE) ]

    lato_up = [[None, complex(x, YRIGHE), [1, 1, 1, 1], [1, 0, 1, 1]] for x in range(2, XCOLONNE)]
    lato_down = [[None, complex(x, 1), [1, 1, 1, 1], [1, 1, 1, 0]] for x in range(2, XCOLONNE)]
    lato_left = [[None, complex(1, y), [1, 1, 1, 1], [1, 1, 0, 1]] for y in range(2, YRIGHE)]
    lato_right = [[None, complex(XCOLONNE, y), [1, 1, 1, 1], [0, 1, 1, 1]] for y in range(2, YRIGHE)]
    top_left= [None, complex(1, YRIGHE), [1, 1, 1, 1], [1, 0, 0, 1]]
    top_right= [None, complex(XCOLONNE, YRIGHE), [1, 1, 1, 1], [0, 0, 1, 1]]
    bottom_left= [None, complex(1, 1), [1, 1, 1, 1], [1, 1, 0, 0]]
    bottom_right= [None, complex(XCOLONNE, 1), [1, 1, 1, 1], [0, 1, 1, 0]]

    # settaggio iniziale e definizione del reticolo
    reticolo= [*reticolo_interno, *(perimetro_reticolo := [*lato_up, *lato_down, *lato_right, *lato_left,
                                                        top_left, top_right, bottom_left, bottom_right])]
    
    return reticolo, lato_right, lato_left, lato_down, bottom_left, bottom_right, perimetro_reticolo




def indicizzatore(lab: list) -> callable:

    # mappatura: posizione complessa -> cella
    by_pos = {c[1]: c for c in lab}

    # mappatura: id -> cella (verrà costruito durante il settaggio del labirinto
    # nella funzione setMuri)
    by_id = {}

    def trova(per = None, valore = None):

        # lookup O(1) per posizione (complex)
        if per == "pos":
            return by_pos.get(valore)
        
        # lookup O(1) per id (dopo l’assegnazione)
        elif per == "id":
            return by_id.get(valore)
        
        # registra/aggiorna mappatura id->cella
        elif per == "aggiorna":
            by_id[valore[0]] = valore

        else:
            return None

    return trova



def openInOut(cellaStart: list, lato_right: list, lato_left: list, lato_down: list, 
              bottom_left: list, bottom_right: list, trova: callable) -> complex:

    # settaggio id_visita - enumerazione della cella start
    cellaStart[0]= 1


    # scelta della cella end: riflessione speculare rispetto la cella start
    xyCellaEnd = complex(XCOLONNE + 1, YRIGHE + 1) - cellaStart[1]

    # ingresso: bordo destro → apertura muro est della cella start
    if cellaStart in lato_right:
        cellaStart[2][0] = 0

        # apertura muro ovest della cella end
        muro_out = 2

    # ingresso: bordo basso → apertura muro sud della cella start
    elif cellaStart in [*lato_down, bottom_left, bottom_right]:
        cellaStart[2][3] = 0

        # apertura muro nord della cella end
        muro_out = 1

    # ingresso: bordo sinistro → apertura muro ovest della cella start
    elif cellaStart in lato_left:
        cellaStart[2][2] = 0

        # apertura muro est della cella end
        muro_out = 0

    # ingresso: bordo top → apertura muro nord della cella start
    else:
        cellaStart[2][1] = 0

        # apertura muro sud della cella end
        muro_out = 3

    # settaggio muro della cella end
    c = trova(per = "pos", valore = xyCellaEnd)
    c[2][muro_out] = 0

    # opzionale, se si vuol sapere dove si trova l’uscita
    return xyCellaEnd



# settaggio muri del reticolo, escluso il perimetro
def setMuri(cellaStart: list, trova: callable) -> list:


    # temp id max della cella visitata quando si ritorna ad una cella già visitata
    enum = 0

    # lista costante di sistema
    COL = list(range(1,5))


    while(True):

        # Caso base: quando tutte le celle del labirinto sono visitate tutti i muri sono stati settatati
        if cellaStart[0] == YRIGHE * XCOLONNE:
            return cellaStart
        

        # se la somma dei valori associati alle direzioni ammesse
        # della cella corrente è non nulla allora si può andare avanti con l'esplorazione
        if  sum(cellaStart[3]):
        
            # calcolo implicitamente le direzioni possibili e quindi anche il muro candidato per essere abbattuto
            interval = [(a * b) -1 for a, b in zip(cellaStart[3], COL) if a]

            # scelgo una direzione sapendo che per costruzione è presente un muro candidato per essere abbattuto
            var = rn.choice(interval)

            # calcolo le coordinate nel piano di Gauss della cella adiacente che posso esplorare
            xyCellaNext = cellaStart[1] + (complex(0,1) ** var)
            
            
            # ricerca della cella successiva (adiacente a quella corrente) del reticolo sapendo
            # le sue coordinate nel piano di Gauss
            cellaNext = trova(per = "pos", valore = xyCellaNext)
            
            # considero se la cella adiacente a quella corrente non è mai stata visitata
            if not cellaNext[0]:
                
                # l'id riparte dall'ultima cella esplorata (con id max)
                if not enum:
                    cellaNext[0] = cellaStart[0] +1

                # l'id prosegue dall'ultima cella esplorata
                else:
                    cellaNext[0] = enum +1
                    enum = 0

                # aggiorna la mappatura id→cella per lookup O(1)
                trova(per = "aggiorna", valore = cellaNext)

            
                # si effettua la xor fra i due valori in binario e il risultato lo esprimo in decimale
                # per abbattere/settare il muro della cella adiacente
                cellaNext[2][var ^ 2] = 0

                # poiché ora il muro è aperto non è possibile esplorare verso quella direzione
                cellaNext[3][var ^ 2] = 0

                # setto/abbatto il muro della cella corrente
                cellaStart[2][var] = 0

                # poiché ora il muro è aperto non è possibile esplorare verso quella direzione
                cellaStart[3][var] = 0

            # se la cella adiacente a quella corrente è già stata visitata
            # non è possibile andare in quella direzione
            else:
                cellaStart[3][var] = 0

                # la cella successiva rimane quella corrente
                # cellaNext = cellaStart
                continue

                
        # poiché non posso andare in avanti con l'esplorazione torno indietro alla cella precedente
        else:

            # ricerca della cella precedete nel reticolo
            cellaNext = trova(per = "id", valore = cellaStart[0] - 1)
           
            # salvo l'id massimo della cella corrente tra quelle esplorate
            # in modo da ripartire da questo valore quando esploro il reticolo
            if enum < cellaNext[0] + 1:
                enum = cellaNext[0] + 1

                
        cellaStart = cellaNext



# rendering del reticolo
def rendering(celle: list) -> list:

    segments = []

    # per ogni cella viene creata una lista dei segmenti,
    # corrispondenti ai muri del labirinto:
    # sapendo le coordinate di ogni cella, derivanti dal numero complesso associato,
    # del vertice in alto a destra del quadrato (cella) e sapendo se un muro (lato su di esso)
    # è presente o abbattuto grazie alla lista
    # muri := [est := 1, nord := 1, ovest:= 1, sud := 1] ove
    # 1 rappresenta muro presente e 0 muro non presente (abbattuto)
    for cella in celle:
        x, y = int(round(cella[1].real)), int(round(cella[1].imag))
       
        # Nord
        if cella[2][1]:
            segments.append([(x-1, y), (x, y)])

        # Est
        if cella[2][0]:
            segments.append([(x, y-1), (x, y)])

        # Ovest: solo bordo sinistro (x = 1)
        if x == 1 and cella[2][2]:
            segments.append(((0, y-1), (0, y)))

        # Sud: solo bordo basso (y = 1)
        if y == 1 and cella[2][3]:
            segments.append(((x-1, 0), (x, 0)))


    # crea la figura (area di disegno interna destinata ai contenuti grafici, 8x8 pollici)
    # e il piano cartesiano su cui vine disegnato il labirinto (AxesSubplot)
    fig, ax = plt.subplots(figsize=(8, 8))

    # settaggio titolo
    fig.canvas.manager.set_window_title("Labirinto")

    # crea la collezione di linee
    lc = LineCollection(
            segments,
            linewidths = 2,
            colors = 'black',
            capstyle = 'projecting',   # (square) estende la linea oltre l’endpoint
            joinstyle = 'miter',       # spigolo vivo agli angoli
            antialiased = False        # evita filini bianchi da smoothing
            )

    # aggiunge ad ax
    ax.add_collection(lc)

    # imposta proporzioni
    ax.set_aspect("equal", adjustable="box")

    # padding per evitare il clipping del bordo
    eps = 0.5

    # imposta limiti
    ax.set_xlim(-eps, XCOLONNE + eps)
    ax.set_ylim(-eps, YRIGHE + eps)

    # assi non visibili
    ax.axis('off')

    # visualizzazione:
    # in ambienti headless (come Replit) non è possibile aprire una finestra grafica;
    # il grafico viene quindi salvato come immagine .png.
    plt.savefig("labirinto.png", dpi=300, bbox_inches="tight")
    print("✅ Labirinto salvato come 'labirinto.png' (usa plt.show() in locale per visualizzarlo).")

    # in locale puoi decommentare la riga seguente per visualizzare la finestra interattiva:
    # plt.show()

    return celle




# ======================
# PUNTO DI INGRESSO
# ======================

if __name__ == "__main__":

    # setup iniziale: reticolo_interno, lati, angoli, perimetro, reticolo finale
    _reticolo, _lato_right, _lato_left, _lato_down, _bottom_left, _bottom_right, _perimetro_reticolo = setupReticolo()
    
    # scelta della cella iniziale
    _cellaStart = rn.choice(_perimetro_reticolo)

    # ottimizzazione per la ricerca di una cella nel reticolo
    func = indicizzatore(_reticolo)

    # apertura del muro che insiste sul perimetro del labirinto della cella iniziale
    # e della cella finale (speculare alla cella iniziale)
    openInOut( _cellaStart, _lato_right, _lato_left, _lato_down, _bottom_left, _bottom_right, func)

    # genera il labirinto
    setMuri(_cellaStart, func)

    # Stampa testuale: elenco delle celle come liste:
    # [id, (x+yj), [E, N, O, S], …] su stdout (per debug/analisi).
    print(_reticolo)

    # disegno del labirinto
    rendering(_reticolo)


