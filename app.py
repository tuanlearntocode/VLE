import os
import requests
import pandas as pd
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

# main function
from Distill.distill import Distill

UPLOAD_FOLDER = "./data/"
ALLOWED_EXTENSIONS = {"xlsx"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# path to data file

file = os.listdir(UPLOAD_FOLDER)
path = UPLOAD_FOLDER + "data.xlsx"


@app.route("/")
def home_page():
    compositions = get_all_composition(path)
    initial_data = {
        "xw": 0,
        "xf": 0,
        "xd": 0,
        "yf": 0,
        "yf_vapor": 0,
        "R_min": 0,
        "R": 0,
        "t_stage": 0,
    }
    return render_template("root.html", compositions=compositions, **initial_data)


@app.route("/getdata", methods=["POST"])
def getGSheetLink():
    url = request.form.get("url")
    sheetId = getId(url)
    outDir = UPLOAD_FOLDER
    outFileName = "data.xlsx"
    getGoogleSeet(sheetId, outDir, outFileName)
    return redirect(url_for("home_page"))


@app.route("/processed", methods=["POST"])
def initial_data():
    # path = UPLOAD_FOLDER + filename[0]

    xw = request.form.get("xw")
    xf = request.form.get("xf")
    xd = request.form.get("xd")

    compositions = request.form.get("compositions")

    data_entry = tuple(map(float, (xf, xd, xw)))

    myProblem = Distill(data_entry, path, compositions)
    myProblem.calculation()

    data = {
        "xw": xw,
        "xf": xf,
        "xd": xd,
        "yf": myProblem.yf,
        "yf_vapor": myProblem.yf_vapor,
        "R": myProblem.R,
        "R_min": myProblem.R_min,
        "t_stage": myProblem.t_stage,
        "liquid": myProblem.liquid.tolist(),
        "vapor": myProblem.vapor.tolist(),
        "stair_x": myProblem.stair_x.tolist(),
        "stair_y": myProblem.stair_y.tolist(),
        "this_compositions": compositions,
    }

    compositions = get_all_composition(path)

    return render_template("root.html", compositions=compositions, **data)


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/how_to_use", methods=["GET"])
def how_to_use():
    return render_template("tutorial.html")


def blank_folder(path):
    try:
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All file deleted")
    except OSError:
        print("Delete Error")


def get_all_composition(file_path):
    df = pd.ExcelFile(file_path)
    sheets = df.sheet_names
    return sheets


def getGoogleSeet(spreadsheet_id, outDir, outFile):
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx"
    response = requests.get(url)
    if response.status_code == 200:
        filepath = os.path.join(outDir, outFile)

        with open(filepath, "wb") as f:
            f.write(response.content)
            print("XLSX file saved to: {}".format(filepath))
    else:
        print(f"Error downloading Google Sheet: {response.status_code}")


def getId(url):
    delimiters = ["/d/", "/edit?"]
    for delimiter in delimiters:
        url = " ".join(url.split(delimiter))

    sheetId = url.split()[1]
    return sheetId  # this is the id


if __name__ == "__main__":
    app.run(debug=False)
