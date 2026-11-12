import streamlit as st
import pandas as pd
from datetime import date
import os
from fpdf import FPDF

st.set_page_config(
    page_title="Scheda osservazione atleta",
    page_icon="⛵",
    layout="wide"
)

def crea_pdf_valutazione(nome, classe, data_val, istruttore, media_pesata, esito, pesi_aree, medie_aree, dettagli_comp, note_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Intestazione PDF
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, "MATRICE DI VALUTAZIONE PONDERATA - VELA FIV", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Passaggio da Preagonismo ad Agonismo", ln=True, align="C")
    pdf.ln(4)
    
    # Dati Anagrafici (larghezza totale 190mm)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "DATI SESSIONE", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(95, 6, f" Allievo: {nome}", border=1)
    pdf.cell(95, 6, f" Classe: {classe}", border=1, ln=True)
    pdf.cell(95, 6, f" Data: {data_val.strftime('%d/%m/%Y')}", border=1)
    pdf.cell(95, 6, f" Istruttore: {istruttore}", border=1, ln=True)
    pdf.ln(4)
    
    # Sintesi Risultato
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "SINTESI PUNTEGGIO", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(95, 6, f" Media Ponderata Finale: {media_pesata:.2f} / 5.0", border=1)
    pdf.cell(95, 6, f" Esito Complessivo: {esito}", border=1, ln=True)
    pdf.ln(5)
    
    colonne_voto = [1, 2, 3, 4, 5, "NE"]
    
    # Tabelle a matrice per ogni Macro-Area (124mm Skill + 6 colonne da 11mm = 190mm)
    for cat, items in dettagli_comp.items():
        # Riga Titolo Macro-Area con peso e media di area
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(220, 225, 230)
        peso_cat = pesi_aree[cat]
        media_cat = medie_aree.get(cat)
        media_str = f"{media_cat:.2f}/5" if media_cat is not None else "N.E."
        cat_clean = cat.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(190, 6, f"  {cat_clean} (Peso: {peso_cat}% - Media area: {media_str})", border=1, ln=True, fill=True)
        
        # Riga Intestazione Colonne: Skill | 1 | 2 | 3 | 4 | 5 | NE
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(124, 6, " Skill / Obiettivo", border=1, fill=True)
        for idx_c, col_val in enumerate(colonne_voto):
            pdf.cell(11, 6, str(col_val), border=1, align="C", fill=True, ln=(idx_c == len(colonne_voto) - 1))
        
        # Righe delle singole Skills con la 'X' nella colonna corrispondente al voto
        for item, voto in items:
            item_clean = item.encode('latin-1', 'replace').decode('latin-1')
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(124, 6, f"  {item_clean}", border=1)
            
            for idx_c, col_val in enumerate(colonne_voto):
                is_last = (idx_c == len(colonne_voto) - 1)
                if voto == col_val:
                    pdf.set_font("Helvetica", "B", 10)
                    if col_val == "NE":
                        pdf.set_fill_color(235, 235, 235)  # Grigio chiaro per NE
                    else:
                        pdf.set_fill_color(200, 225, 250)  # Azzurro chiaro per voto 1-5
                    pdf.cell(11, 6, "X", border=1, align="C", fill=True, ln=is_last)
                else:
                    pdf.set_font("Helvetica", "", 9)
                    pdf.cell(11, 6, "", border=1, align="C", fill=False, ln=is_last)
        pdf.ln(3)
        
    # Note e Obiettivi
    if note_text:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, "NOTE E OBIETTIVI DELL'ISTRUTTORE", ln=True)
        pdf.set_font("Helvetica", "", 9)
        note_clean = note_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 5, note_clean, border=1)
        
    return bytes(pdf.output())

st.title("Scheda di osservazione atleta per passaggio da preagonismo ad agonismo")
tab_val, tab_sto = st.tabs(["📋 Checklist di osservazione", "📊 Storico e Medie"])

with tab_val:
    st.sidebar.header("Dati Osservazione")
    nome_allievo = st.sidebar.text_input("Nome e Cognome Allievo", value="Mario Rossi")
    classe_vela = st.sidebar.selectbox("Classe / Imbarcazione", ["Optimist", "Laser", "RS Feva", "420", "29er", "Altro"])
    data_valutazione = st.sidebar.date_input("Data osservazione", value=date.today())
    nome_istruttore = st.sidebar.text_input("Istruttore", value="")

    # Macro-aree con pesi e skills
    macro_aree = {
        "1. A Terra": {
            "peso": 0.30,
            "skills": [
                "Saper armare la barca",
                "Nomenclatura di base",
                "Nomenclatura specifica",
                "Attenzione al briefing/spiegazione",
                "Indipendenza varo/alaggio barca",
                "Nodi principali",
                "Cura del materiale e puntualità"
            ]
        },
        "2. In acqua, conoscenze di base": {
            "peso": 0.40,
            "skills": [
                "Scuffia e raddrizzamento barca",
                "Sicurezza in mare",
                "Posizione, postura, equilibrio",
                "Mantenimento della rotta",
                "Esecuzione percorso",
                "Mantenimento rotta senza riferimenti",
                "Sapersi collocare rispetto al vento",
                "Cambio direzione con regolazione delle vele",
                "Esecuzione andature",
                "Virata semplice",
                "Abbattuta semplice",
                "Attenzione in situazioni normali"
            ]
        },
        "3. In acqua, conoscenze intermedie": {
            "peso": 0.30,
            "skills": [
                "Saper fare e mantenere barca ferma",
                "Sapersi disporre autonomamente al traino",
                "Conduzione con vele di prua",
                "Issata/ammainata vele di prua",
                "Regolare vangh, cunningham, base",
                "Nozione di vento apparente"
            ]
        },
        "4. In acqua, conoscenze avanzate": {
            "peso": 0.15,
            "skills": [
                "Virata con rollio",
                "Abbattuta con rollio",
                "Nozione di scarroccio",
                "Nozione di corrente e deriva",
                "Concetto di vento pulito",
                "Concetto di portanza",
                "Variazione del vento in raffica con regolazioni",
                "Tensioni sartie",
                "Regolazione carrello o archetto",
            ]
        },
        "4. Avvicinamento alla regata": {
            "peso": 0.10,
            "skills": [
                "Saper fare barca ferma sulla linea",
                "Senso linea",
                "Lettura del campo (buchi e raffiche)",
                "Scelta del posizionamento in linea",
                "Navigare con vento libero",
                "Copertura avversari",
                "Concetto di velocità al vento"
            ]
        },
        "5. Aspetti fisici e mentali": {
            "peso": 0.25,
            "skills": [
                "Tenuta cinghie/trapezio prolungata",
                "Agilità e rapidità nei movimenti in mare",
                "Agilità e rapidità nei movimenti a terra",
                "Intesa equipaggio (doppi)",
                "Capacità di accettazione dell'errore",
                "Apertura a correzioni e consigli",
                "Partecipazione e spirito di squadra",
                "Interesse ed entusiasmo mostrato"
            ]
        },
    }

    pesi_dict = {cat: int(round(data["peso"] * 100)) for cat, data in macro_aree.items()}
    
    dettagli_valutazione = {}
    medie_aree = {}

    st.markdown("Legenda: **[1]** Non acquisito | **[2]** Da sviluppare | **[3]** Base | **[4]** Autonomo | **[5]** Agonista | **[NE]** Non Esaminato")
    st.markdown("---")

    for categoria, info in macro_aree.items():
        n_skills = len(info["skills"])
        with st.expander(f"📌 {categoria} — Peso: {int(round(info['peso']*100))}% ({n_skills} skills)", expanded=True):
            voti_numerici_area = []
            dettagli_valutazione[categoria] = []
            
            for idx, item in enumerate(info["skills"]):
                r_col1, r_col2 = st.columns([3, 2])
                r_col1.write(item)
                
                voto = r_col2.radio(
                    item,
                    options=[1, 2, 3, 4, 5, "NE"],
                    index=2,  # Default su 3 (Base)
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"mat_{categoria}_{idx}"
                )
                
                # cosi escludo gli Ne
                if isinstance(voto, int):
                    voti_numerici_area.append(voto)
                    
                dettagli_valutazione[categoria].append((item, voto))
            
            # media di ongi area
            if len(voti_numerici_area) > 0:
                media_area = sum(voti_numerici_area) / len(voti_numerici_area)
                medie_aree[categoria] = media_area
                st.caption(f"Media di area: **{media_area:.2f} / 5.0** *(calcolata su {len(voti_numerici_area)}/{n_skills} skills esaminate)*")
            else:
                medie_aree[categoria] = None
                st.caption("Media di area: **N.E.** *(nessuna skill esaminata in questa area)*")

    # Calcolo media ponderata totale:
    # Ogni area contribuisce in proporzione al suo peso (indipendentemente dal numero di skills dentro).
    # Se un'area è interamente "NE", il suo peso viene ridistribuito proporzionalmente sulle altre aree valutate.
    somma_pesata = 0.0
    peso_totale_valutato = 0.0
    for cat, info in macro_aree.items():
        if medie_aree[cat] is not None:
            somma_pesata += medie_aree[cat] * info["peso"]
            peso_totale_valutato += info["peso"]

    media_ponderata_totale = (somma_pesata / peso_totale_valutato) if peso_totale_valutato > 0 else 0.0

    # Soglie di ammissione calibrate su 5.0
    if peso_totale_valutato == 0:
        esito_testo = "NON VALUTABILE"
    elif media_ponderata_totale >= 3.20:
        esito_testo = "IDONEO"
    elif media_ponderata_totale >= 2.50:
        esito_testo = "IN VALUTAZIONE"
    else:
        esito_testo = "PREAGONISMO"

    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Punteggio calcolato")
        st.metric(label="Media Ponderata Finale", value=f"{media_ponderata_totale:.2f} / 5.0")
        st.progress(min(media_ponderata_totale / 5.0, 1.0))

    with col2:
        st.subheader("Esito")
        if esito_testo == "IDONEO":
            st.success("🟢 **FUTURO AGONISTA!:** Pronto per la squadra agonistica!")
        elif esito_testo == "IN VALUTAZIONE":
            st.warning("🟡 **MANCA POCO:** Richiede consolidamento, ancora una stagione in preagonistica, con possibilità di fare qualche allenamento con l'agonismo.")
        elif esito_testo == "PREAGONISMO":
            st.error("🔴 **PREAGONISTA:** Continuare la formazione di base.")
        else:
            st.info("⚪ **NON VALUTABILE:** Tutte le voci risultano 'NE'.")

    st.subheader("Altro da aggiungere")
    note = st.text_area("Osservazioni specifiche:", height=100)

    c_salva, c_pdf = st.columns(2)
    file_csv = "valutazioni_matrice_allievi.csv"

    with c_salva:
        if st.button("💾 Aggiungi allo storico", use_container_width=True):
            dati_sessione = {
                "Data": data_valutazione,
                "Allievo": nome_allievo,
                "Classe": classe_vela,
                "Istruttore": nome_istruttore,
                "Media_Ponderata": round(media_ponderata_totale, 2),
                "Esito": esito_testo,
                "Note": note
            }
            df_nuovo = pd.DataFrame([dati_sessione])
            if not os.path.isfile(file_csv):
                df_nuovo.to_csv(file_csv, index=False, encoding="utf-8-sig")
            else:
                df_nuovo.to_csv(file_csv, mode="a", header=False, index=False, encoding="utf-8-sig")
            st.toast(f"Valutazione di {nome_allievo} salvata!")

    with c_pdf:
        pdf_data = crea_pdf_valutazione(
            nome_allievo, classe_vela, data_valutazione, nome_istruttore,
            media_ponderata_totale, esito_testo, pesi_dict, medie_aree, dettagli_valutazione, note
        )
        st.download_button(
            label="📄 Scarica PDF",
            data=pdf_data,
            file_name=f"Scheda_osservazione{nome_allievo.replace(' ', '_')}_{data_valutazione}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

with tab_sto:
    st.header("📊 Storico Osservazioni")
    if os.path.exists(file_csv):
        df_storico = pd.read_csv(file_csv)
        allievi_unici = ["Tutti"] + list(df_storico["Allievo"].unique())
        allievo_selezionato = st.selectbox("Filtra per Allievo:", allievi_unici)
        
        if allievo_selezionato != "Tutti":
            df_filtrato = df_storico[df_storico["Allievo"] == allievo_selezionato]
        else:
            df_filtrato = df_storico
            
        st.dataframe(df_filtrato, use_container_width=True)
        
        if allievo_selezionato != "Tutti" and len(df_filtrato) > 1:
            st.subheader(f"📈 Andamento punteggi medi di {allievo_selezionato}")
            df_filtrato["Data"] = pd.to_datetime(df_filtrato["Data"])
            st.line_chart(df_filtrato.set_index("Data")["Media_Ponderata"])
    else:
        st.info("Nessuna valutazione salvata finora.")