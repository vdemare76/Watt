from flask import flash, render_template, redirect, url_for, request, g, session, json, jsonify
from flask_appbuilder import ModelView, BaseView, expose, has_access, action
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy.exc import SQLAlchemyError

from flask_appbuilder.fieldwidgets import Select2AJAXWidget, Select2SlaveAJAXWidget
from flask_appbuilder.fields import AJAXSelectField
from wtforms import validators

from .import appbuilder, db
from .models import AnnoAccademico, CorsoDiStudio, AttivitaDidattica, Docente, Aula, NumerositaAnniCorso, Offerta, \
                    LogisticaDocente, Modulo, Giorno, Slot, OrarioTestata, OrarioDettaglio, Chiusura

from flask.templating import render_template
from .util import svuotaDb, caricaDati7Cds, caricaDati13Cds, caricaDatiBase, getAttributiLDap, getOrarioCorrente, getChiusureOrarioCorrente
from .esse3_to_watt import getAnniAccademici, getCorsiInOfferta, importDatiEsse3
from .solver import AlgoritmoCalcolo

class AnniAccademiciView(ModelView):
    datamodel = SQLAInterface(AnnoAccademico)
    list_title = 'Anni accademici'
    add_title = 'Nuovo anno accademico'
    show_title = 'Anno accademico'
    edit_title = 'Modifica anno accademico'
    label_columns = {"anno":"Anno accademico",
                     "anno_esteso":"Anno accademico esteso"}
    list_columns = ["anno",
                    "anno_esteso"]


class SlotView(ModelView):
    datamodel = SQLAInterface(Slot)
    list_title = 'Slot orari'
    add_title = 'Nuovo slot orario'
    show_title = 'Slot orario'
    edit_title = 'Modifica slot orario'
    label_columns = {"descrizione":"Descrizione"}
    list_columns = ["descrizione"]


class GiorniView(ModelView):
    datamodel = SQLAInterface(Giorno)
    list_title = 'Giorni disponibili'
    add_title = 'Nuovo giorno'
    show_title = 'Giorno'
    edit_title = 'Modifica Giorno'
    label_columns = {"descrizione":"Descrizione"}
    list_columns = ["descrizione"]


class CorsiDiStudioView(ModelView):
    datamodel = SQLAInterface(CorsoDiStudio)
    list_title = 'Corsi di studio'
    add_title = 'Nuovo corso di studio'
    show_title = 'Corso di studio'
    edit_title = 'Modifica corso di studio'
    label_columns = {"codice":"Codice CdS",
                     "descrizione":"Descrizione",
                     "cfu":"Cfu",
                     "durata_legale":"Durata legale"}
    list_columns = ["codice", 
                    "descrizione", 
                    "cfu", 
                    "durata_legale"]


class AttivitaDidatticheView(ModelView):
    datamodel = SQLAInterface(AttivitaDidattica)
    list_title = 'Attività didattiche'
    add_title = 'Nuova attività didattica'
    show_title = 'Attività didattica'
    edit_title = 'Modifica attività didattica'
    label_columns = {"codice":"Codice AD",
                     "Descrizione":"Descrizione",
                     "cfu":"Cfu",
                     "colore":"Colore"}
    list_columns = ["codice", 
                    "descrizione", 
                    "cfu",
                    "colore"]


class AuleView(ModelView):
    datamodel = SQLAInterface(Aula)
    list_title = 'Aule'
    add_title = 'Nuova aula'
    show_title = 'Aula'
    edit_title = 'Modifica aula'
    label_columns = {"codice":"Codice aula",
                     "descrizione":"Descrizione",
                     "capienza":"Capienza",
                     "tipo_aula":"Tipo aula"}
    list_columns = ["codice", 
                    "descrizione", 
                    "capienza",
                    "tipo_aula"]


class NumerositaAnniCorsoView(ModelView):
    datamodel = SQLAInterface(NumerositaAnniCorso)
    list_title = 'Numerosità anni di corso'
    add_title = 'Nuova numerosità anno di corso'
    show_title = 'Numerosità anno di corso'
    edit_title = 'Modifica numerosità anno di corso'
    label_columns = {"codice_corso":"Corso di studio",
                     "anno_di_corso":"Anno di corso",
                     "numerosita":"Numerosità"}
    list_columns = ["codice_corso",
                    "anno_di_corso",
                    "numerosita"]


class DocentiView(ModelView):
    datamodel = SQLAInterface(Docente)
    list_title = 'Docenti'
    add_title = 'Nuovo docente'
    show_title = 'Docente'
    edit_title = 'Modifica docente'
    label_columns = {"codice_fiscale":"Codice fiscale",
                     "cognome":"Cognome",
                     "nome":"Nome"}
    list_columns = ["codice_fiscale", 
                    "cognome", 
                    "nome"]
    search_filters = ["codice_fiscale", 
                    "cognome", 
                    "nome"] 


class OffertaView(ModelView):
    datamodel = SQLAInterface(Offerta)
    list_title = 'Offerta didattica'
    add_title = 'Nuova voce di offerta'
    show_title = 'Voce di offerta didattica'
    edit_title = 'Modifica voce di offerta didattica'
    label_columns = {"anno_accademico.anno_esteso":"Anno accademico",
                     "corso_di_studio.descrizione":"Corso di studio",
                     "attivita_didattica.descrizione":"Attività didattica",
                     "docente.cognome":"Cognome docente",
                     "docente.nome":"Nome docente",
                     "anno_di_corso":"Anno di corso",
                     "semestre":"Semestre",
                     "max_studenti":"Numerosità studenti"}
    list_columns = ["anno_accademico.anno_esteso",
                    "corso_di_studio.descrizione",
                    "attivita_didattica.descrizione",
                    "docente.cognome","docente.nome",
                    "anno_di_corso",
                    "semestre",
                    "max_studenti"]


class ModuliView(ModelView):
    datamodel = SQLAInterface(Modulo)
    list_title = 'Moduli di attività didattica'
    add_title = 'Nuovo modulo'
    show_title = 'Modulo di attività didattica'
    edit_title = 'Modifica modulo'
    label_columns = {"codice":"Codice modulo",
                     "descrizione":"Descrizione",
                     "offerta.anno_accademico":"A.A. Offerta",
                     "offerta.corso_di_studio":"C.d.S Offerta",
                     "offerta.attivita_didattica":"AD Offerta",
                     "tipo_aula":"Tipo aula",
                     "docente.cognome":"Cognome docente",
                     "docente.nome":"Nome docente",
                     "numero_sessioni":"Numero di sessioni",
                     "durata_sessioni":"Durata sessioni",
                     "max_studenti":"Numerosità massima studenti"}
    list_columns = ["codice",
                    "descrizione",
                    "offerta.anno_accademico",
                    "offerta.corso_di_studio",
                    "offerta.attivita_didattica",
                    "tipo_aula",
                    "docente.cognome",
                    "docente.nome",
                    "numero_sessioni",
                    "durata_sessioni",
                    "max_studenti"]
    order_columns = ["codice",
                    "descrizione",
                    "tipo_aula",
                    "docente.cognome",
                    "docente.nome",
                    "numero_sessioni",
                    "durata_sessioni",
                    "max_studenti"]


class ChiusuraView(ModelView):
    datamodel = SQLAInterface(Chiusura)
    list_title = 'Periodi di chiusura'
    add_title = 'Nuova chiusura'
    show_title = 'Periodo di chiusura'
    edit_title = 'Modifica periodo di chiusura'
    label_columns = {"orario_testata.descrizione":"Descrizione orario",
                     "data_inizio":"Data chiusura",
                     "data_fine":"Data fine",
                     "nota":"Nota"}
    list_columns = ["testata",
                    "data_inizio",
                    "data_fine",
                    "nota"]


class LogisticaDocentiView(ModelView):
    datamodel = SQLAInterface(LogisticaDocente)
    list_title = 'Logistiche docenti'
    add_title = 'Nuova logistica'
    show_title = 'Logistica docente'
    edit_title = 'Modifica logistica'
    label_columns = {"offerta.attivita_didattica":"Offerta",
                     "modulo.descrizione":"Modulo",
                     "slot.descrizione":"Slot",
                     "giorno.descrizione":"Giorno"}
    
    list_columns = ["offerta.attivita_didattica",
                    "modulo.descrizione",
                    "slot.descrizione",
                    "giorno.descrizione"]
       
    add_form_extra_fields = {
         "offerta": AJAXSelectField(
            "Offerta",
            datamodel = datamodel,
            validators = [validators.DataRequired()],
            col_name = "offerta",
            widget = Select2AJAXWidget(
                endpoint = "/logisticadocentiview/api/column/add/offerta"
            ),
        ),
        "modulo": AJAXSelectField(
            "Modulo",
            datamodel = datamodel,
            validators = [validators.DataRequired()],
            col_name = "modulo",
            widget = Select2SlaveAJAXWidget(
                master_id = "offerta",
                endpoint = "/logisticadocentiview/api/column/add/modulo?_flt_0_offerta_id={{ID}}",
            )
        )
    }
    
    edit_form_extra_fields = add_form_extra_fields 


class OrariGeneratiView(ModelView):
    datamodel = SQLAInterface(OrarioTestata)
    list_title = 'Orari generati'
    show_title = 'Orario generato'
    edit_title = 'Modifica dati di testata dell\'orario generato'
    label_columns = {"id":"identificativo",
                     "descrizione":"Descrizione",
                     "anno_accademico.anno_esteso":"Anno Accademico",
                     "semestre":"Semestre",
                     "data_creazione":"Data creazione",
                     "note_creazione":"Note",
                     "stato_orario.descrizione":"Stato"}
    list_columns = ["id",
                    "descrizione",
                    "anno_accademico.anno_esteso",
                    "semestre",
                    "data_creazione",
                    "note_creazione",
                    "stato_orario.descrizione"]
    edit_exclude_columns = ["id",
                            "anno_accademico",
                            "semestre",
                            "data_creazione",
                            "note_creazione"]

    @action("cancella", "Elimina", "Vuoi eliminare gli orari selezionati?", "fa-trash-alt", single=False)
    def cancella(self, items):
        for i in items:
            try:
                db.session.query(OrarioDettaglio).filter(OrarioDettaglio.testata_id == i.id).delete()
                db.session.query(OrarioTestata).filter(OrarioTestata.id == i.id).delete()
                db.session.commit()
            except SQLAlchemyError:
                db.sessione.rollback()
                flash("Errore durante la cancellazione degli orari selezionati","danger")
                return -1
        return redirect(self.get_redirect())

    @action("carica_schema", "Carica orario", "Carico lo schema orario selezionato?", "fa-trash-alt", multiple=False, single=True)
    def carica_schema(self, item):
        tst=db.session.query(OrarioTestata).filter(OrarioTestata.id==item.id).first()
        # Dati dell'orario corrente caricato in memoria
        session["annoAccademico"] = tst.anno_accademico_id
        session["semestre"] = tst.semestre
        session["testataId"] = item.id
        session["chkSessioneUnica"] = int(tst.vincolo_sessione_unica)
        session["chkSessioniConsecutive"] = int(tst.vincolo_sessioni_consecutive)
        if tst.vincolo_max_slot>0:
            session["chkMaxOre"] = 1
        else:
            session["chkMaxOre"] = 0
        session["selMaxOre"] = int(tst.vincolo_max_slot)
        session["chkPreferenzeDocenti"] = int(tst.vincolo_logistica_docenti)

        flash('Orario caricato correttamente! (Puoi visualizzarlo con Orario -> Schema settimanale', 'success')
        return redirect(self.get_redirect())


class UtilitaView(BaseView):
    default_view = "srv_home"

    @expose("/srv_home/", methods=["GET","POST"])
    @has_access
    def srv_home(self):
        return render_template("utility.html", base_template = appbuilder.base_template, appbuilder = appbuilder)

    @expose("/srv_svuotadb/", methods=["GET","POST"])
    @has_access
    def srv_svuotadb(self):
        svuotaDb()
        return render_template("utility.html", base_template=appbuilder.base_template, appbuilder=appbuilder)

    @expose("/srv_carica_dati_base/", methods=["GET","POST"])
    @has_access
    def srv_carica_dati_base(self):
        caricaDatiBase()
        return render_template("utility.html", base_template=appbuilder.base_template, appbuilder=appbuilder)

    @expose("/srv_carica_dati_7cds1/", methods=["GET","POST"])
    @has_access
    def srv_carica_dati_7cds1(self):
        caricaDati7Cds("1")
        return render_template("utility.html", base_template=appbuilder.base_template, appbuilder=appbuilder)

    @expose("/srv_carica_dati_7cdsn/", methods=["GET","POST"])
    @has_access
    def srv_carica_dati_7cdsn(self):
        caricaDati7Cds("N")
        return render_template("utility.html", base_template=appbuilder.base_template, appbuilder=appbuilder)

    @expose("/srv_carica_dati_13cds/", methods=["GET","POST"])
    @has_access
    def srv_carica_dati_13cds(self):
        caricaDati13Cds("1")
        return render_template("utility.html", base_template=appbuilder.base_template, appbuilder=appbuilder)


class UtilitaEsse3View(BaseView):
    default_view = "srv_esse3_home"

    @expose("/srv_esse3_home/")
    @has_access
    def srv_esse3_home(self, name=None):
        return render_template("utility_esse3.html", base_template = appbuilder.base_template, appbuilder = appbuilder)

    @expose("/srv_esse3_util", methods=["GET","POST"])
    @has_access
    def srv_esse3_util(self):
        target=request.form.get("target")

        if target == "caricaAnniAccademici":
            session["anniAccademici"] = getAnniAccademici()
            return render_template("utility_esse3.html",
                                   base_template = appbuilder.base_template,
                                   appbuilder = appbuilder,
                                   annoAccademicoSelezionato = 1000,
                                   anniAccademici = session["anniAccademici"])

        elif target == "caricaCorsiOffertaFormativa":
            try:
                anniAccademici = session["anniAccademici"]
                session["corsiInOfferta"] = getCorsiInOfferta(request.form.get("anniAccademici"))
                return render_template("utility_esse3.html",
                                       base_template = appbuilder.base_template,
                                       appbuilder = appbuilder,
                                       anniAccademici = anniAccademici,
                                       annoAccademicoSelezionato = request.form.get("anniAccademici"),
                                       corsiInOfferta = session["corsiInOfferta"])
            except:
                flash("Non sono stati caricati gli anni accademici per cui è disponibile un'offerta didattica!","danger")

        elif target == "caricaDatiCorsi":
            try:
                anniAccademici=session["anniAccademici"]
                corsiInOfferta=session["corsiInOfferta"]

            except:
                flash("Bisogna effettuare almeno una selezione nelle precedenti sezioni!", "warning")

            if len(request.form.getlist("corsi"))>0:
                importDatiEsse3(request.form.get("anniAccademici"),request.form.getlist("corsi"), request.form.get("semestre"),
                            request.form.get("cbSovrDatiCorsi"),request.form.get("cbSovrDatiAD"), request.form.get("cbSovrDatiDocenti"),
                            request.form.get("cbSovrDatiOfferta"),request.form.get("cbImportaADObbligatorie"),request.form.get("cbImportaDatiIncompleti"),
                            request.form.get("moduli"))
            else:
                flash("Selezionare almeno un corso da importare!", "warning")

            return render_template("utility_esse3.html",
                                   base_template=appbuilder.base_template,
                                   appbuilder=appbuilder,
                                   anniAccademici=anniAccademici,
                                   annoAccademicoSelezionato=request.form.get("anniAccademici"),
                                   corsiInOfferta=corsiInOfferta)

        return render_template("utility_esse3.html", base_template=appbuilder.base_template, appbuilder=appbuilder)


class GeneraOrarioView(BaseView):
    default_view = "prf_home"

    @expose("/prf_home/", methods=["GET","POST"])
    @has_access
    def prf_home(self):
        anni_accademici=db.session.query(AnnoAccademico.id, AnnoAccademico.anno, AnnoAccademico.anno_esteso)\
        .join(Offerta, Offerta.anno_accademico_id==AnnoAccademico.id).distinct()
        semestri=db.session.query(Offerta.semestre).distinct()
        return render_template("generator.html",
                                base_template=appbuilder.base_template,
                                appbuilder=appbuilder,
                                anni_accademici=anni_accademici,
                                semestri=semestri)

    @expose("/prf_calc/", methods=["GET","POST"])
    @has_access
    def prf_calc(self):
        try:
            dati = json.loads(request.data)
            vincoli={"chkSessioneUnica": dati["chkSessioneUnica"],
                     "chkSessioniConsecutive": dati["chkSlotSessioniConsecutive"],
                     "chkMaxOre": dati["chkMaxOre"],
                     "selMaxOre": int(dati["selMaxOre"]),
                     "chkPreferenzeDocenti": dati["chkPreferenzeDocenti"],
                     "posizioniFisse": None}
            algoritmo=AlgoritmoCalcolo()
            ris=algoritmo.genera_orario(dati["aa"], dati["semestre"], dati["txtDescOrario"], True, vincoli, -1)
            data = {"status": ris}
            return data, 200
        except:
            data = {"status": "Verifica fallita"}
            return data, 200

class SchemaSettimanaleView(BaseView):
    default_view = "wsk_home"

    @expose("/wsk_home/", methods=["GET","POST"])
    @has_access
    def wsk_home(self):
        if "testataId" in session:
            slot=db.session.query(Slot).all()
            return render_template("timetable.html",
                                   base_template=appbuilder.base_template,
                                   appbuilder=appbuilder,
                                   slot=slot,
                                   orario=getOrarioCorrente())
        else:
            flash("Caricare un orario generato come base su cui lavorare: Orari Generati -> Carica", "danger")
        return redirect(self.get_redirect())

class CalendarioView(BaseView):
    default_view = "cld_home"

    @expose("/cld_home/")
    @has_access
    def cld_home(self):
        if "testataId" in session:
            session["orarioCorrente"] = getOrarioCorrente()
            session["chiusure"] = getChiusureOrarioCorrente()

            orarioCorrente = session["orarioCorrente"]
            chiusureOrarioCorrente = []
            token, role = getAttributiLDap(g.user.username)
            corsiOrarioCorrente = []
            anniCorsoOrarioCorrente = []

            if role!="wattStud":
                for o in orarioCorrente:
                    risCorsi = list(filter(lambda ocr: ocr['corso_id'] == o["corso_id"], corsiOrarioCorrente))
                    if len(risCorsi)==0:
                       corsiOrarioCorrente.append({"corso_id":o["corso_id"], "codice_corso":o["codice_corso"], "descrizione_corso":o["descrizione_corso"]})
                    corsiOrarioCorrente = sorted(corsiOrarioCorrente, key=lambda k: (k["descrizione_corso"]))
                    risAnniCorso = list(filter(lambda ocr: ocr["corso_id"] == o["corso_id"] and ocr["anno_corso"] == o["anno_corso"], anniCorsoOrarioCorrente))
                    if len(risAnniCorso)==0:
                       anniCorsoOrarioCorrente.append({"corso_id": o["corso_id"], "codice_corso": o["codice_corso"], "anno_corso": o["anno_corso"]})
                    anniCorsoOrarioCorrente = sorted(anniCorsoOrarioCorrente, key=lambda k: (k["anno_corso"]))

            return render_template("calendar.html",
                                   base_template=appbuilder.base_template,
                                   appbuilder=appbuilder,
                                   corsi=corsiOrarioCorrente,
                                   anni_corso=anniCorsoOrarioCorrente,
                                   orario=orarioCorrente,
                                   chiusure=chiusureOrarioCorrente)
        else:
            flash("Caricare un orario generato come base su cui lavorare: Orari Generati -> Carica", "danger")
            return redirect(self.get_redirect())

    @expose("/cld_load/", methods=["POST"])
    @has_access
    def cld_load(self):
        session["orarioCorrente"] = getOrarioCorrente()
        session["chiusure"] = getChiusureOrarioCorrente()

        data = {"orario": session["orarioCorrente"],
                "chiusure": session["chiusure"]}
        return data, 200

    @expose("/cld_upd/", methods=["POST"])
    @has_access
    def cld_upd(self):
        data = {"orario": session["orarioCorrente"],
                "chiusure": session["chiusure"]}
        return data, 200

    @expose("/cld_mod/", methods=["POST"])
    @has_access
    def cld_mod(self):
        global tipo_conflitto
        global descrizione_conflitto
        dati = json.loads(request.data)
        orarioCorrente = session["orarioCorrente"]
        eventoOld = dati["eventoOld"]
        tipo_variazione = dati["tipo_variazione"]

        slotNew = db.session.query(Slot).filter(Slot.ora_slot_cal == dati["slotNew"]).first()
        giornoNew = db.session.query(Giorno).filter(Giorno.id == dati["giornoNew"]).first()
        aulaNew = db.session.query(Aula).filter(Aula.id == dati["aulaNew"]).first()

        if tipo_variazione=="slot":
            conflittiAula = list(filter(lambda ocr: ocr["slot_id"] == slotNew.id and
                                                    ocr["giorno_id"] == giornoNew.id and
                                                    ocr["aula_id"] == aulaNew.id,
                                                    orarioCorrente))

            conflittiDocente = list(filter(lambda ocr: ocr["slot_id"] == slotNew.id and
                                                       ocr["giorno_id"] == giornoNew.id and
                                                       ocr["docente_id"] == eventoOld["extendedProps"]["docente_id"],
                                                       orarioCorrente))

        if (tipo_variazione == "slot" and len(conflittiAula) > 0) :
            tipo_conflitto = "A"
            descrizione_conflitto = conflittiAula[0]["codice_corso"] + " - " + conflittiAula[0]["descrizione_corso"] + \
                                    " - (Anno di corso: " + str(conflittiAula[0]["anno_corso"]) + ")"
        elif (tipo_variazione == "slot" and len(conflittiDocente) > 0) :
            tipo_conflitto = "D"
            descrizione_conflitto = conflittiDocente[0]["codice_corso"] + " - " + conflittiDocente[0]["descrizione_corso"] + \
                                    " - (Anno di corso: " + str(conflittiDocente[0]["anno_corso"]) + ")"
        else:
            tipo_conflitto = "N"
            descrizione_conflitto = "Nessun conflitto"
            for row in orarioCorrente:
                if (row["corso_id"] == eventoOld["extendedProps"]["corso_id"] and
                        row["modulo_id"] == eventoOld["extendedProps"]["modulo_id"] and
                        row["aula_id"] == eventoOld["extendedProps"]["aula_id"] and
                        row["giorno_id"] == eventoOld["extendedProps"]["giorno_id"] and
                        row["slot_id"] == eventoOld["extendedProps"]["slot_id"]):
                    row["giorno_id"] = dati["giornoNew"]
                    row["slot_id"] = slotNew.id
                    row["descrizione_slot"] = slotNew.descrizione
                    row["giorno"] = giornoNew.descrizione
                    row["aula_id"] = aulaNew.id
                    row["aula"] = aulaNew.descrizione
                    row["capienza_aula"] = aulaNew.capienza
                    break;

            session["orarioCorrente"] = orarioCorrente

        data = {"tipo_conflitto": tipo_conflitto,
                "descrizione_conflitto": descrizione_conflitto,
                "orario": session["orarioCorrente"],
                "chiusure": session["chiusure"]}

        return data, 200

    @expose("/cld_room/", methods=["POST"])
    @has_access
    def cld_room(self):
        dati = json.loads(request.data)
        aula = db.session.query(Aula).filter(Aula.id == dati["aula"]).first()

        auleOccupate = []
        orarioCorrente = session['orarioCorrente']
        for o in orarioCorrente:
            if o["giorno_id"] == dati["giorno"] and o["slot_id"] == dati["slot"]:
                auleOccupate.append(o["aula_id"])
        aule = db.session.query(Aula) \
            .filter(Aula.id != dati["aula"]).filter(Aula.capienza >= dati["numerosita"]) \
            .filter(Aula.id.notin_(auleOccupate)).filter(Aula.tipo_aula == aula.tipo_aula) \
            .order_by(Aula.descrizione).all()

        vAule = []
        for a in aule:
            vAule.append(a.to_dict())

        data = {"aule": vAule}
        return data, 200

    @expose("/cld_ver/", methods=["POST"])
    @has_access
    def cld_ver(self):
        try:
            dati = json.loads(request.data)
            orarioCorrente = session["orarioCorrente"]
            vincoli = {"chkSessioneUnica": int(session["chkSessioneUnica"]),
                       "chkSessioniConsecutive": int(session["chkSessioniConsecutive"]),
                       "chkMaxOre": int(session["chkMaxOre"]),
                       "selMaxOre": int(session["selMaxOre"]),
                       "chkPreferenzeDocenti": int(session["chkPreferenzeDocenti"]),
                       "posizioniFisse": orarioCorrente}
            algoritmo = AlgoritmoCalcolo()
            if dati["tipoVerifica"] == -1:
                ris = algoritmo.genera_orario(session["annoAccademico"], session["semestre"], "Verifica Orario",
                                            False, vincoli, -1)
            else:
                ris = algoritmo.genera_orario(session["annoAccademico"], session["semestre"], "Verifica Orario",
                                              False, vincoli, dati["tipoVerifica"])
            data = {"status": ris}
            return data, 200
        except:
            data = {"status": "Verifica fallita"}
            return data, 200

    @expose("/cld_app/", methods=["POST"])
    @has_access
    def cld_app(self):
        if "orarioCorrente" in session:
            orarioCorrente = session["orarioCorrente"]
            db.session.query(OrarioDettaglio).filter(OrarioDettaglio.testata_id == orarioCorrente[0]["testata_id"]).delete()
            for o in orarioCorrente:
                row = OrarioDettaglio(
                    testata_id = o["testata_id"],
                    corso_di_studio_id = o["corso_id"],
                    modulo_id = o["modulo_id"],
                    slot_id = o["slot_id"],
                    giorno_id = o["giorno_id"],
                    aula_id = o["aula_id"])
                db.session.add(row)
            db.session.commit()
            flash("Orario salvato correttamente!", "success")
        else:
            flash("Caricare un orario generato come base su cui lavorare: Orari Generati -> Carica", "danger")

        data = {"esito": "ok"}
        return data, 200

db.create_all()

appbuilder.add_view(SlotView, "Slot", icon = "fa-clock-o", category = "Tabelle di base")

appbuilder.add_view(GiorniView, "Giorni", icon = "fa-calendar-check-o", category = "Tabelle di base")

appbuilder.add_separator("Tabelle di base")

appbuilder.add_view(AnniAccademiciView, "Anni Accademici", icon = "fa-font", category = "Tabelle di base")

appbuilder.add_view(AuleView, "Aule", icon = "fa-th", category = "Tabelle di base")

appbuilder.add_view(CorsiDiStudioView, "Corsi di Studio", icon = "fa-pencil", category = "Didattica")

appbuilder.add_view(NumerositaAnniCorsoView, "Numerosità anni corso", icon = "fa-users", category = "Didattica")

appbuilder.add_view(DocentiView, "Docenti", icon = "fa-user-circle", category = "Didattica")

appbuilder.add_view(AttivitaDidatticheView, "Attività didattiche", icon = "fa-book", category = "Didattica")

appbuilder.add_view(OffertaView, "Offerta", icon = "fa-university", category = "Offerta didattica")

appbuilder.add_view(ModuliView, "Moduli", icon = "fa-puzzle-piece", category = "Offerta didattica")

appbuilder.add_view(LogisticaDocentiView, "Logistica docenti", icon = "fa-hand-o-up", category = "Offerta didattica")

appbuilder.add_view(UtilitaView, "Funzioni utilità",  icon = "fa-briefcase", category = "Utilità")

appbuilder.add_view(UtilitaEsse3View, "Connettore Esse3",  icon = "fa-share-square", category = "Utilità")

appbuilder.add_view(GeneraOrarioView, "Elaborazione orario",  icon = "fa-cogs", category = "Orario")

appbuilder.add_view(OrariGeneratiView, "Orari generati",  icon = "fa-table", category = "Orario")

appbuilder.add_view(ChiusuraView, "Imposta chiusure", icon = "fa-home", category = "Orario")

appbuilder.add_view(SchemaSettimanaleView, "Schema settimanale",  icon = "fa-calendar", category = "Orario")

appbuilder.add_view(CalendarioView, "Calendario orario",  icon = "fa-clipboard", category = "Orario")
