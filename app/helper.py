import pandas as pd
from flask import flash
from matplotlib.figure import Figure
import base64
import numpy as np
from io import BytesIO
from sklearn.preprocessing import StandardScaler


def preprocess(file):
    df = pd.read_csv(file)
    drop_cols = ['Well Name']
    df = df.drop(drop_cols, axis=1)

    sc = StandardScaler()
    _df = sc.fit_transform(df)

    return _df


def predict(file, model):
    _df = preprocess(file)
    y_pred = model.predict(_df)
    result = np.argmax(y_pred, axis=1) + 1
    return result


def combine_result(file, prediction):
    logs = pd.read_csv(file)
    logs['Prediction'] = prediction
    return logs


def make_facies_log_plot(file):
    logs = pd.read_csv(file)
    # make sure logs are sorted by depth
    try:
        logs = logs.sort_values(by='Depth')

        ztop = logs.Depth.min()
        zbot = logs.Depth.max()

        fig = Figure(figsize=(15, 10))
        ax = fig.subplots(nrows=1, ncols=5)
        ax[0].plot(logs.GR, logs.Depth, '-g')
        ax[1].plot(logs.ILD_log10, logs.Depth, '-')
        ax[2].plot(logs.DeltaPHI, logs.Depth, '-', color='0.40')
        ax[3].plot(logs.PHIND, logs.Depth, '-', color='r')
        ax[4].plot(logs.PE, logs.Depth, '-', color='black')

        for i in range(len(ax) - 1):
            ax[i].set_ylim(ztop, zbot)
            ax[i].invert_yaxis()
            ax[i].grid()
            ax[i].locator_params(axis='x', nbins=3)

        ax[0].set_xlabel("GR")
        ax[0].set_xlim(logs.GR.min(), logs.GR.max())
        ax[1].set_xlabel("ILD_log10")
        ax[1].set_xlim(logs.ILD_log10.min(), logs.ILD_log10.max())
        ax[2].set_xlabel("DeltaPHI")
        ax[2].set_xlim(logs.DeltaPHI.min(), logs.DeltaPHI.max())
        ax[3].set_xlabel("PHIND")
        ax[3].set_xlim(logs.PHIND.min(), logs.PHIND.max())
        ax[4].set_xlabel("PE")
        ax[4].set_xlim(logs.PE.min(), logs.PE.max())

        ax[1].set_yticklabels([])
        ax[2].set_yticklabels([])
        ax[3].set_yticklabels([])
        ax[4].set_yticklabels([])
        fig.suptitle('Well: %s' % logs.iloc[0]['Well Name'], fontsize=14, y=0.94)

        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode('ascii')
        return f"<img class='img-fluid' src='data:image/png;base64,{data}'/>"
    except:
        flash("You uploaded incorrect well logs file. Try again!", category='error')


def csv_df_to_html(file, describe):
    """Convert a csv file to DataFrame and render to HTML"""
    df = pd.read_csv(file)
    if describe:
        html = df.describe().to_html()
    else:
        html = df.head(10).to_html()
    return html
