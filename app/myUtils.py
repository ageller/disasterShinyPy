import pandas as pd
import numpy as np
import plotly.graph_objects as go


def prepData():
    ''' 
    Function to read in and prep the data
    '''

    # Earthquakes : https://www.kaggle.com/datasets/thedevastator/uncovering-geophysical-insights-analyzing-usgs-e
    edf = pd.read_csv('data/usgs_main.csv')
    edf['time'] = pd.to_datetime(edf['time'])
    powmag = 10.**edf['mag']
    edf['Magnitude'] = np.nan_to_num((powmag - np.amin(powmag))/(np.amax(powmag) - np.amin(powmag))*1e3,0)
    edf['Depth (km)'] = np.nan_to_num(300.*(edf['depth'] - np.amin(edf['depth']))/(np.amax(edf['depth']) - np.amin(edf['depth'])),0)
    # a map between the normalized and regular columns so that I can plot histograms
    edfColMap = {'Magnitude':'mag', 'Depth (km)':'depth'}

    # Volcanoes : https://www.kaggle.com/datasets/jessemostipak/volcano-eruptions
    vdf = pd.read_csv('data/volcano.csv')
    vdf['Population Within 100km'] = np.nan_to_num((vdf['population_within_100_km'] - np.amin(vdf['population_within_100_km']))/(np.amax(vdf['population_within_100_km']) - np.amin(vdf['population_within_100_km']))*300., 0)
    vdf['Elevation (m)'] = np.nan_to_num(((vdf['elevation'] - np.amin(vdf['elevation']))/(np.amax(vdf['elevation']) - np.amin(vdf['elevation'])))**3.*300., 0)
    # a map between the normalized and regular columns so that I can plot histograms
    vdfColMap = {'Population Within 100km':'population_within_100_km', 'Elevation (m)':'elevation'}

    return edf, vdf, edfColMap, vdfColMap

def createMap(edf, vdf, edfColMap, vdfColMap, eSizeCol = 'Magnitude', vSizeCol = 'Population Within 100km'):
    '''
    Function to create the map
    '''

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