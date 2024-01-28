import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import PIL
import io 

# Path to files:
country_data_path = "Data_Fanning_et_al_2021_shartfallofnations.xlsx"
column_name_lst = ["CO2 Emissions", "Land-System Change", "Material Footprint"]


# Read the CSV file
df = pd.read_excel(country_data_path, sheet_name=1)
iso_name = "adm0_a3"
eco_data = df.rename(columns={"iso3c": iso_name})

lst_all_years = sorted(eco_data["date"].unique())
political_countries_url = './political_world_map.geojson'
gdf = gpd.read_file(political_countries_url)
eco_data = gdf.merge(eco_data, on=iso_name)


column_name = "CO2 Emissions"

for column_name in column_name_lst:
    # Add traces, one for each slider step
    fig = go.Figure()
    for step in lst_all_years:
        tmp_df = eco_data.loc[(eco_data["date"] == step)]
        fig.add_trace(
            go.Choropleth(
                locations=tmp_df[iso_name], # Spatial coordinates
                z=tmp_df[column_name].astype(float), # Data to be color-coded
                locationmode='ISO-3', # set of locations match entries in `locations`
                colorscale="OrRd",
                zmin=0,
                zmax=5,
                name=str(step),
                visible=False if lst_all_years.index(step) > 0 else True
                
            )
        )
    frames = [go.Frame(data=[go.Choropleth(
                locations=eco_data.loc[(eco_data["date"] == step)][iso_name],
                z=eco_data.loc[(eco_data["date"] == step)][column_name].astype(float),
                locationmode='ISO-3',
                colorscale="OrRd",
                zmin=0,
                zmax=6,
                name=str(step)
            )], name=str(step)) for step in lst_all_years]

    updatemenus = [{
        'buttons': [{
            'label': 'Play',
            'method': 'animate',
            'args': [None, {'frame': {'duration': 50, 'redraw': True}, 'fromcurrent': True, 'transition': {'duration': 50, 'easing': 'quadratic-in-out'}}]
        }, 
        {
            'label': 'Pause',
            'method': 'animate',
            'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}]
        }],
        'direction': 'left',
        'showactive': False,
        'type': 'buttons',
        'pad': {'r': 10, 't': 70},
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }]

    sliders = [{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 12},
            'prefix': 'Year: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': [{'args': [[f.name], {'frame': {'duration': 100, 'redraw': True},
                                        'mode': 'immediate',
                                        'transition': {'duration': 100}}],
                    'label': f.name, 'method': 'animate'} for f in frames]
    }]

    fig.frames = frames
    gif_frames = []
    for s, fr in enumerate(fig.frames):
        # set main traces to appropriate traces within plotly frame
        fig.update(data=fr.data)
        fig.update_layout(title=dict(text=f"{column_name} {lst_all_years[s]}", x=0.5, xanchor='center'), annotations=[dict(
            text="Data from https://goodlife.leeds.ac.uk/", 
            x=0.02,
            y=0,
            xref="paper",
            yref="paper",
            showarrow=False)])
        gif_frames.append(PIL.Image.open(io.BytesIO(fig.to_image(format="png"))))

    # append duplicated last image more times, to keep animation stop at last status
    for i in range(3):
        gif_frames.append(gif_frames[-1])

    # create animated GIF
    gif_frames[0].save(
            f"gifs/{column_name}_animated.gif",
            save_all=True,
            append_images=gif_frames[1:],
            optimize=False,
            duration=500,
            loop=0,
        )

    fig.update_layout(
        updatemenus=updatemenus, 
        sliders=sliders, 
        title_text=f"{column_name} Overshoot by Country", 
        annotations=[dict(
            text="Data from https://goodlife.leeds.ac.uk/", 
            x=0.02,
            y=0,
            xref="paper",
            yref="paper",
            showarrow=False)])
    # Save as HTML
    fig.write_html(f'html_files/{column_name}_interactive.html')
    
print("Done!")