'''
Working with earthquake and volcano data 

Downloaded from Kaggle : 
- https://www.kaggle.com/datasets/thedevastator/uncovering-geophysical-insights-analyzing-usgs-e
- https://www.kaggle.com/datasets/jessemostipak/volcano-eruptions


conda install shiny rsconnect-python pandas numpy matplotlib ipywidgets==7.7.3
pip install shinywidgets

run with 
shiny run --reload app.py

deploy using rsconnect-python , info here (note the available python versions): 
https://docs.posit.co/shinyapps.io/getting-started.html#working-with-shiny-for-python

For Python 3.9.13 this requires ipywidgets==7.7.3

'''

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, register_widget
import matplotlib.pyplot as plt

'''
Earthquakes

https://www.kaggle.com/datasets/thedevastator/uncovering-geophysical-insights-analyzing-usgs-e


'''
edf = pd.read_csv('data/usgs_main.csv')
edf['time'] = pd.to_datetime(edf['time'])
powmag = 10.**edf['mag']
edf['Magnitude'] = np.nan_to_num((powmag - np.amin(powmag))/(np.amax(powmag) - np.amin(powmag))*1e3,0)
edf['Depth (km)'] = np.nan_to_num(300.*(edf['depth'] - np.amin(edf['depth']))/(np.amax(edf['depth']) - np.amin(edf['depth'])),0)
# a map between the normalized and regular columns so that I can plot histograms
edfColMap = {'Magnitude':'mag', 'Depth (km)':'depth'}

'''
Volcanoes 

https://www.kaggle.com/datasets/jessemostipak/volcano-eruptions

'''
vdf = pd.read_csv('data/volcano.csv')
vdf['Population Within 100km'] = np.nan_to_num((vdf['population_within_100_km'] - np.amin(vdf['population_within_100_km']))/(np.amax(vdf['population_within_100_km']) - np.amin(vdf['population_within_100_km']))*300., 0)
vdf['Elevation (m)'] = np.nan_to_num(((vdf['elevation'] - np.amin(vdf['elevation']))/(np.amax(vdf['elevation']) - np.amin(vdf['elevation'])))**3.*300., 0)
# a map between the normalized and regular columns so that I can plot histograms
vdfColMap = {'Population Within 100km':'population_within_100_km', 'Elevation (m)':'elevation'}


'''
Function to create the map
'''
def createMap(eSizeCol = 'Magnitude', vSizeCol = 'Population Within 100km'):

    fig = go.FigureWidget(
        data = [
            go.Scattermapbox(
                lat = edf['latitude'],
                lon = edf['longitude'],
                mode = 'markers',
                marker = go.scattermapbox.Marker(
                    size = edf[eSizeCol].to_numpy(),
                    sizemin = 1.5,
                    sizemode = 'area',
                    color = '#0d6aff',
                    opacity = 0.7
                ),
                text = edf['place'] + '<br>' + eSizeCol +': ' + edf[edfColMap[eSizeCol]].astype('str')+ '<br>Date: ' + edf['time'].dt.strftime('%b %d, %Y'),
                hoverinfo = 'text'
            ),
            go.Scattermapbox(
                lat = vdf['latitude'],
                lon = vdf['longitude'],
                mode = 'markers',
                marker = go.scattermapbox.Marker(
                    size = vdf[vSizeCol].to_numpy(),
                    sizemin = 1.5,
                    sizemode = 'area',
                    color = '#ff1d0d',
                    opacity = 0.7
                ),
                text = vdf['volcano_name'] + '<br>' + vSizeCol +': ' + vdf[vdfColMap[vSizeCol]].astype('str') + '<br>Last Eruption Year: ' + vdf['last_eruption_year'].astype('str'),
                hoverinfo = 'text'
            )
        ],
        layout = dict(
            autosize = True,
            hovermode = 'closest',
            height = 500,
            width = 1000,
            margin = {"r":0,"t":0,"l":0,"b":0},
            mapbox = dict(
                style = 'carto-darkmatter',
                zoom = 0.9
            ),
            showlegend = False,
        )
    )

    return fig


    

'''
The Shiny app

working from this example https://shinylive.io/py/examples/#map
'''

app_ui = ui.page_fluid(
    # title
    ui.h1("Map of earthquakes and volcanoes"),
    ui.p("Earthquakes are plotted in blue; the data come from ", ui.a("here", href = "https://www.kaggle.com/datasets/thedevastator/uncovering-geophysical-insights-analyzing-usgs-e"), " and show all earthquakes from 2022.  Volcanoes are plotted in red; the data come from", ui.a("here", href = "https://www.kaggle.com/datasets/jessemostipak/volcano-eruptions"), " and show all recorded volcanoes."),
    ui.layout_sidebar(
        # UI
        ui.panel_sidebar(
            ui.h4("Use the buttons below to define how the data are plotted.", style = "margin-bottom:40px"),
            ui.input_checkbox_group(
                "toggle", "Show/Hide data", {"Earthquakes": "Earthquakes (blue)", "Volcanoes": "Volcanoes (red)"},
                selected = ["Earthquakes", "Volcanoes"]
            ),
            ui.input_radio_buttons(
                "eSizeCol", "Size attribute for earthquake (blue) data", {"Magnitude": "Magnitude", "Depth (km)": "Depth"}
            ),
            ui.input_radio_buttons(
                "vSizeCol", "Size attribute for volcano (red) data", {"Population Within 100km": "Population", "Elevation (m)": "Elevation"}
            ),
        ),

        # plot
        ui.panel_main(
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
            ),
        )
        
    ),
)


def server(input, output, session):
    # Initialize and display when the session starts 
    map = createMap()
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
