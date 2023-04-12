'''
Working with earthquake and volcano data 

Downloaded from Kaggle : 
- https://www.kaggle.com/datasets/thedevastator/uncovering-geophysical-insights-analyzing-usgs-e
- https://www.kaggle.com/datasets/jessemostipak/volcano-eruptions


conda create --name shinyTest python=3.9.13
conda install shiny rsconnect-python pandas plotly numpy matplotlib ipywidgets==7.7.3
pip install shinywidgets

run with 
shiny run --reload app.py

deploy using rsconnect-python, info here (note the available python versions): 
https://docs.posit.co/shinyapps.io/getting-started.html#working-with-shiny-for-python

For Python 3.9.13 this requires ipywidgets==7.7.3

'''

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, register_widget
import matplotlib.pyplot as plt

# myUtils.py contains two functions that I wrote
from myUtils import prepData, createMap
    
# read in and prepare the data
edf, vdf, edfColMap, vdfColMap = prepData()

'''
The Shiny app

working from examples here https://shinylive.io/py/examples/
'''

app_ui = ui.page_fluid(

    # title
    ui.h1("Map of earthquakes and volcanoes"),
    ui.p("Earthquakes are plotted in blue; the data come from the USGS (downloaded from ", ui.a("here", href = "https://www.kaggle.com/datasets/thedevastator/uncovering-geophysical-insights-analyzing-usgs-e"), ") and show all earthquakes from 2022.  Volcanoes are plotted in red; the data come from The Smithsonian Institute (downloaded from ", ui.a("here", href = "https://www.kaggle.com/datasets/jessemostipak/volcano-eruptions"), ") and show all recorded volcanoes.  In the map, marker sizes are scaled using the marker diameter.  When scaling by Magnitude, the sizes reflect 10^Magnitude; scaling by all other attributes is linear.", style = "max-width:1000px"),
    ui.h4("Use the buttons below to define how the data are plotted."),

    # UI
    ui.panel_well(
        ui.row(
            ui.column(3, 
                ui.input_checkbox_group(
                    "toggle", "Show/Hide data", {"Earthquakes": "Earthquakes (blue)", "Volcanoes": "Volcanoes (red)"},
                    selected = ["Earthquakes", "Volcanoes"]
                ),
            ),
            ui.column(4, 
                ui.input_radio_buttons(
                    "eSizeCol", "Size attribute for earthquake data", {"Magnitude": "Magnitude", "Depth (km)": "Depth"}
                ),
            ),
            ui.column(4, 
                ui.input_radio_buttons(
                    "vSizeCol", "Size attribute for volcano data", {"Population Within 100km": "Population", "Elevation (m)": "Elevation"}
                ),
            )
        ),
        style = "margin-bottom:10px; max-width:1000px"
    ),

    # plots
    ui.row(
        output_widget("map")        
    ),
    ui.row(
        ui.column(
            6, 
            ui.panel_conditional(
                "input.toggle.includes('Earthquakes')",
                    ui.output_plot("ehist"),
            )
        ),
        ui.column(
            6,
            ui.panel_conditional(
                "input.toggle.includes('Volcanoes')",
                    ui.output_plot("vhist"),
            )
        ),
        style = "max-width:1000px",
    ),

        

)


def server(input, output, session):
    # Initialize and display when the session starts 
    map = createMap(edf, vdf, edfColMap, vdfColMap)
    register_widget("map", map)

    # # When the radio buttons change, update the map
    @reactive.Effect
    def _():
        showE = 'Earthquakes' in input.toggle()
        showV = 'Volcanoes' in input.toggle()
        map.data[0].visible = showE
        map.data[1].visible = showV
        map.data[0].marker.size = edf[input.eSizeCol()].to_numpy()
        map.data[1].marker.size = vdf[input.vSizeCol()].to_numpy()
        map.data[0].text = edf['place'] + '<br>' + input.eSizeCol() +': ' + edf[edfColMap[input.eSizeCol()]].astype('str') + '<br>Date: ' + edf['time'].dt.strftime('%b %d, %Y')
        map.data[1].text = vdf['volcano_name'] + '<br>' + input.vSizeCol() +': ' + vdf[vdfColMap[input.vSizeCol()]].astype('str') + '<br>Last Eruption Year: ' + vdf['last_eruption_year'].astype('str')

    @output
    @render.plot()
    def ehist():
        showE = 'Earthquakes' in input.toggle()
        fig, ax = plt.subplots()
        ax.hist(edf[edfColMap[input.eSizeCol()]], bins = 25, color = [13/255., 106/255., 255/255.])
        ax.set_ylabel('N')
        ax.set_xlabel(f'Earthquake {input.eSizeCol()}')
        return fig
    
    @output
    @render.plot()
    def vhist():
        showV = 'Volcanoes' in input.toggle()
        fig, ax = plt.subplots()
        ax.hist(vdf[vdfColMap[input.vSizeCol()]], bins = 25, color = [255/255., 29/255., 13/255.])
        ax.set_ylabel('N')
        ax.set_xlabel(f'Volcano {input.vSizeCol()}')
        return fig  

    
app = App(app_ui, server)
