from flask import Blueprint, jsonify
from itertools import zip_longest
from app.database.tables import BinRecord, Bin
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import csv
import os
from flasgger import swag_from
import traceback
from app.utils.utils import Utils


fbprophet_blueprint = Blueprint(
    "fbprophet", __name__, template_folder="templates", url_prefix="/pred"
)


@fbprophet_blueprint.route("/")
def main():
    return "<h1>FbProphet</h1>"


def getprevision(apartment_name=None, tipologia=None):

    if tipologia is not None and apartment_name is not None:
        if Bin.query.filter(Bin.tipologia == tipologia).filter(Bin.apartment_ID == apartment_name).first() == None:
            return jsonify({"error": "tipology or apartment name not valid"}), 401

    if apartment_name is not None:
        if Bin.query.filter(Bin.apartment_ID == apartment_name).first() == None:
            return jsonify({"error": "Apartment name not valid or it doesn't have any bin"}), 402

    array_pred = []

    if tipologia is None and apartment_name is None:
        bins = Bin.query.all()
    if tipologia is not None:
        bins = Bin.query.filter(Bin.tipologia == tipologia)
    if apartment_name is not None:
        bins = Bin.query.filter(Bin.apartment_ID == apartment_name)
    if apartment_name is not None and tipologia is not None:
        bins = Bin.query.filter(Bin.apartment_ID == apartment_name).filter(
            Bin.tipologia == tipologia)

    for bin in bins:
        file = pd.read_csv(
            f"./predictions_file/{bin.apartment_ID}/riempimento_{bin.tipologia}.csv")

        predictions = file["y"]
        dates = pd.to_datetime(file["ds"])

        json_bin = {"bin": bin.id_bin, "tipologia": bin.tipologia,
                    "apartment": bin.apartment_ID, "previsioni": None}

        values_and_dates = []
        for i in range(len(predictions)):
            array = {}
            array["value"] = predictions[i]
            array["date"] = dates[i]
            values_and_dates.append(array)
        json_bin["previsioni"] = values_and_dates
        array_pred.append(json_bin)

    return jsonify({"fbprophet": array_pred}), 200


def createprevision(time, apartment_name=None, tipologia=None):

    if time < 0:
        return jsonify({"error": "time not correct"}), 401

    if apartment_name is not None:
        if tipologia is not None and Bin.query.filter(Bin.tipologia == tipologia).filter(Bin.apartment_ID == apartment_name).first() == None:
            return jsonify({"error": "Apartment or tipology not valid"}), 402

        if Bin.query.filter(Bin.apartment_ID == apartment_name).first() == None:
            return jsonify({"error": "Apartment not valid"}), 403

    util = Utils()

    if time == 0:  # se tempo non inserito(0), default 5 giorni
        time = 5

    if apartment_name is None and tipologia is None:
        bins = Bin.query.all()

    if apartment_name is not None:
        if tipologia is not None:
            bins = Bin.query.filter(Bin.tipologia == tipologia).filter(
                Bin.apartment_ID == apartment_name)
        else:
            bins = Bin.query.filter(Bin.apartment_ID == apartment_name)

    for bin in bins:  # per ogni bidone creo una previsione temporale
        bin_records = BinRecord.query.filter(
            BinRecord.associated_bin == bin.id_bin
        ).order_by(BinRecord.timestamp.desc())[:50]

        apartment_name = bin.apartment_ID
        tipologia = bin.tipologia

        if len(bin_records) >= 2:
            timestamps = []
            filling = []

            for bin_record in bin_records:
                timestamps.append(bin_record.timestamp)
                filling.append(bin_record.riempimento)

            path = "./predictions_file/" + apartment_name
            if not os.path.exists(path):
                os.makedirs(path)

            with open(f"./predictions_file/{apartment_name}/riempimento_{tipologia}.csv", "w") as csvfile:
                filewriter = csv.writer(
                    csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
                )
                filewriter.writerow(["ds", "y"])
                for tp, fl in zip_longest(timestamps, filling):
                    filewriter.writerow([tp, fl])

            df = pd.read_csv(
                f"./predictions_file/{apartment_name}/riempimento_{tipologia}.csv")

            df.columns = ["ds", "y"]
            df["ds"] = pd.to_datetime(df["ds"])

            # plotting the actual values
            plt.plot(df.ds, df.y)

           # plt.title(
           #     f"Dati attuali di riempimento {tipologia} dell'appartamento {apartment_name}")
            plt.xlabel("Date")
            plt.ylabel("Filling")

            path = "./predictions/" + apartment_name + "/" + tipologia
            if not os.path.exists(path):
                os.makedirs(path)

            plt.savefig(
                f"./predictions/{apartment_name}/{tipologia}/dati_attuali.png", format="png")

            try:
                m = Prophet()
                m.fit(df)

            except Exception as e:
                print('Prophet error: ' + str(e))

            future = m.make_future_dataframe(periods=time, freq="d")
            future.tail()

            forecast = m.predict(future)
            forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail()
            forecast.to_csv(
                f"./predictions/{apartment_name}/prediction_{tipologia}.csv")

            # Plotting the generated forecast
            m.plot(forecast, uncertainty=True)

            plt.title(
                f"Previsioni di riempimento {tipologia} dell'appartamento {apartment_name}")
            plt.xlabel("Data")
            plt.ylabel("Livello di riempimento")

            path = "./predictions/" + apartment_name + "/" + tipologia
            if not os.path.exists(path):
                os.makedirs(path)

            plt.savefig(
                f"./predictions/{apartment_name}/{tipologia}/forecast.png", format="png")

            # Plotting the forecast components.
            m.plot_components(forecast)
            plt.savefig(
                f"./predictions/{apartment_name}/{tipologia}/components.png", format="png")

            prediction = forecast[["yhat"]].values
            dates = forecast[["ds"]].values
            date_riempimento = ""

            for i in range(len(dates)):
                try:
                    next_status = util.calcolastatus(
                        bin.id_bin, prediction[i], prophet=True)
                    if (next_status == 2):
                        date_riempimento = dates[i][0] if dates[i] is not None else ''
                except Exception as e:
                    traceback.print_exc()

            if str(date_riempimento) != "":
                Utils.set_previsione_status(bin.id_bin, str(date_riempimento))

    return jsonify({"msg": "Previsioni correttamente create"}), 200


@fbprophet_blueprint.route("/getprevision")
@swag_from('docs/predizioni.yml')
def prevision():
    """
    questo endpoint prende le previsioni temporali di riempimento dei bidoni 
    precedentemente create e ritorna un json con le relative previsioni
    """
    return getprevision(None, None)


@fbprophet_blueprint.route("/getprevision/<string:apartment_name>")
@swag_from('docs/predizioni2.yml')
def prevision2(apartment_name):
    """
    questo endpoint prende le previsioni temporali di riempimento dei bidoni di uno specifico appartamento
    precedentemente create e ritorna un json con le previsioni di tutti i bidoni dell'appartamento
    """
    return getprevision(apartment_name, None)


@fbprophet_blueprint.route("/getprevision/<string:apartment_name>&<string:tipologia>")
@swag_from('docs/predizioni3.yml')
def prevision3(apartment_name, tipologia):
    """
    questo endpoint prende le previsioni temporali di riempimento dei bidoni di uno specifico appartamento 
    e di una specifica tipologia precedentemente create e ritorna un json con le relative previsioni 
    """
    return getprevision(apartment_name=apartment_name, tipologia=tipologia)


@fbprophet_blueprint.route("/createprevision/<int:time>")
@swag_from('docs/createpredizioni.yml')
def createprevision1(time):
    """
    questo end point crea previsioni temporali di riempimento dei bidoni per un certo periodo di tempo, 
    se l'input è uguale a 0, di defaul si assume 5 giorni
    """
    return createprevision(time, None, None)


@fbprophet_blueprint.route("/createprevision/<string:apartment_name>&<int:time>")
@swag_from('docs/createpredizioni2.yml')
def createprevision2(apartment_name, time):
    """
    questo end point crea previsioni temporali di riempimento dei bidoni per un certo periodo di tempo, 
    per un appartamento specifico
    se l'input è uguale a 0, di defaul si assume 5 giorni
    """
    return createprevision(time, apartment_name=apartment_name, tipologia=None)


@fbprophet_blueprint.route("/createprevision/<string:apartment_name>&<string:tipologia>&<int:time>")
@swag_from('docs/createpredizioni3.yml')
def createprevision3(apartment_name, tipologia, time):
    """
    questo end point crea previsioni temporali di riempimento dei bidoni per un certo periodo di tempo, 
    per un appartamento specifico e per una tipologia di bidoni specifica
    se l'input è uguale a 0, di defaul si assume 5 giorni
    """
    return createprevision(time, apartment_name=apartment_name, tipologia=tipologia)
