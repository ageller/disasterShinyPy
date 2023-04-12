# Disaster ShinyPy

A Python Shiny app showing earthquakes and volcanoes.  

Earthquake data come from the USGS and were downloaded [here](https://www.kaggle.com/datasets/thedevastator/uncovering-geophysical-insights-analyzing-usgs-e), and volcano data come The Simithsonian Institute and were downloaded from [here](https://www.kaggle.com/datasets/jessemostipak/volcano-eruptions).

A live version of this app is available on [shinyapps.io here](https://ageller.shinyapps.io/disasterpy/).

Please also see my companion [blog post](https://sites.northwestern.edu/researchcomputing/2023/04/12/experimenting-with-shiny-for-python/) about creating this app.

## Running locally

If you want to run this app locally, you can clone this repo and follow these steps:

1. I recommend creating a conda environment.  I am using Python version 3.9.13 because that is currently one of the (few) available version on shinyapps.io.  Note that for the plotly widget to work with this version of Python, you need to specify the version of ipywidgets. (Otherwise, the app will encounter an error.  See some discussion [here](https://github.com/rstudio/py-shinywidgets/issues/79). Perhaps this will be fixed in a future version of py-shinywidgets):
```
conda create --name shinyTest python=3.9.13
conda activate shinyTest
conda install shiny pandas numpy matplotlib plotly ipywidgets==7.7.3
pip install shinywidgets
```

2. Run  the app with 
```
cd app
shiny run --reload app.py
```

3. Point your browser to http://127.0.0.1:8000/ to view your app.
