import streamlit as st
import pandas as pd
import numpy as np
import requests
import altair as alt
import pydeck as pdk
import os

st.set_page_config( layout='wide')
os.environ['MAPBOX_API_KEY'] = 'pk.eyJ1Ijoia3NoaXRpamdhbWJoaXIiLCJhIjoiY2tsY3dyZWJ5MXh1bTJvbnB5aXA3d3k5cSJ9.e3cwTQ9HmShzDArWLro9Lg'

# Other Functions
def share_of_services_sheet(TENANT, services):
    if TENANT == 'trondheim':
        ranges = [25,50,80]
    else:
        ranges = [50,80]    
        
    def percentage_services(low, high, services):
        return len(services[(services.fill_before_serviced >= low) & (services.fill_before_serviced < high)])/len(services)
     
    output = []
    diffs = pd.Series([[ranges[i], ranges[i + 1]] for i in range(len(ranges) - 1)])
    if len(services) > 0:
        
         
        output.append({f"<{ranges[0]}%":percentage_services(0, ranges[0], services)})
        diffs.apply(lambda row: output.append({f"{row[0]}%-{row[1]}%": percentage_services(row[0], row[1], services)}))
        output.append({f">{ranges[-1]}%": percentage_services(ranges[-1], 101, services)})
        
    else:
        output.append({f"<{ranges[0]}%":""})
        diffs.apply(lambda row: output.append({f"{row[0]}%-{row[1]}%": ""}))
        output.append({f">{ranges[-1]}%": ""})

    final_output = []
    for i in range(len(output)):
        final_output += list(output[i].items())
    
    final_output = [dict(final_output)]
    
    return pd.DataFrame(final_output)

def wt_loc_share(services, wt):

    df_list = []

    for i in services.location.unique():
        df = share_of_services_sheet('borough-of-hillingdon', services[(services.location == i) & (services.content_type == wt)])
        df.insert(loc=0, column = 'Location', value="")
        df.at[0, 'Location'] = i

        df_list.append(df)

    key_df = pd.concat(list(df_list), ignore_index = True)

    return key_df
    


def flatten(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten(i))
        else: rt.append(i)
    return rt

def clean(list_of_lists):
    """Flatten list of lists and remove 'nan' values
    """
    flat_list = list(flatten(list_of_lists))
    clean_list = [item for item in flat_list if str(item) != 'nan']
    return clean_list


def create_wt_loc_report_sheet(services):
    report_list = []
    for i in services.location.unique():
        report_list.append(
                            (i, len(services[services.location == i].serial_no.unique()), 
                            len(services[services.location == i]), 
                            sum(services[services.location == i]['volume_emptied']),
                            np.mean(services[services.location == i]['fill_before_serviced']/100),
                            np.mean(clean(services[services.location == i]['time_diff_days'])), 
                            np.mean(clean(services[services.location == i]['fill_rate_per_day'])),
                            np.mean(clean(services[services.location == i]['days_to_full'])),
                            np.mean(clean(services[services.location == i]['days_overflowing'])))
                          )
        
    report_sheet_list = []
    for tup in report_list:
        report_sheet_list.append({'Location': tup[0], 'Number of Containers': tup[1], 'Number of Services': tup[2],
                                    'Total Volume Emptied': tup[3], 'Avg Fill at Service': tup[4], 
                                    'Avg Days Between Services': tup[5], 'Avg Daily Fill Rate': tup[6],
                                    'Avg Days to Full': tup[7], 
                                    'Avg Days Overflowing': tup[8]})
    return pd.DataFrame(report_sheet_list)



@st.cache(show_spinner = False)
def location_center_coords(madrid_locations):
    coordslist = []
    for i in madrid_locations:
        try:
            response = requests.get(f'https://nominatim.openstreetmap.org/search?q={i},%20madrid&format=json&polygon=1&addressdetails=1')
            data_dict = response.json()
            coordslist.append((i, float(f'{data_dict[0]["lat"]}'), float(f'{data_dict[0]["lon"]}')))
        except:
            pass
    return pd.DataFrame(coordslist, columns = ['Location', 'c_lat', 'c_long'])

tenant = st.sidebar.radio("Select Tenant", ['Borough of Hillingdon', 'Madrid'])
st.title(tenant)

if tenant == 'Borough of Hillingdon':
    # Read Data
        #  Nov 2020
    hil_loc_report_nov = pd.read_csv('Data/hil_loc_report_nov.csv', sep = ";", decimal = ",")
    hil_wt_report_nov = pd.read_csv('Data/hil_wt_report_nov.csv', sep = ";", decimal = ",")
    hil_loc_share_nov = pd.read_csv('Data/hil_loc_share_nov.csv', sep = ";", decimal = ",")
    hil_wt_share_nov = pd.read_csv('Data/hil_wt_share_nov.csv', sep = ";", decimal = ",")
    hil_services_nov = pd.read_csv('Data/hil_services_nov.csv', sep = ";", decimal = ",")
    

        # Dec 2020
    hil_loc_report_dec = pd.read_csv('Data/hil_loc_report_dec.csv', sep = ";", decimal = ",")
    hil_wt_report_dec = pd.read_csv('Data/hil_wt_report_dec.csv', sep = ";", decimal = ",")
    hil_loc_share_dec = pd.read_csv('Data/hil_loc_share_dec.csv', sep = ";", decimal = ",")
    hil_wt_share_dec = pd.read_csv('Data/hil_wt_share_dec.csv', sep = ";", decimal = ",")
    hil_services_dec = pd.read_csv('Data/hil_services_dec.csv', sep = ";", decimal = ",")
    
        # Jan 2021
    hil_loc_report_jan = pd.read_csv('Data/hil_loc_report_jan.csv', sep = ";", decimal = ",")
    hil_wt_report_jan = pd.read_csv('Data/hil_wt_report_jan.csv', sep = ";", decimal = ",")
    hil_loc_share_jan = pd.read_csv('Data/hil_loc_share_jan.csv', sep = ";", decimal = ",")
    hil_wt_share_jan = pd.read_csv('Data/hil_wt_share_jan.csv', sep = ";", decimal = ",")
    hil_services_jan = pd.read_csv('Data/hil_services_jan.csv', sep = ";", decimal = ",")
   

    timerange = st.sidebar.select_slider('Select Time Range', ['Nov 2020', 'Dec 2020', 'Jan 2021'])
    months = {'Nov 2020': [hil_loc_report_nov, hil_wt_report_nov, hil_loc_share_nov, hil_wt_share_nov, hil_services_nov], 
              'Dec 2020': [hil_loc_report_dec, hil_wt_report_dec, hil_loc_share_dec, hil_wt_share_dec, hil_services_dec],
              'Jan 2021': [hil_loc_report_jan, hil_wt_report_jan, hil_loc_share_jan, hil_wt_share_jan, hil_services_jan]}

    report_type = st.sidebar.radio('Select Report Type:', ['Location', 'Waste-Type', 'Both'])


    if report_type == 'Location':
    
        st.header('Location-Based Data')
        st.write('Click on the bars to see more information')
        Location = []
        category = []
        value = []
        for i in range(len(months[timerange][2])):
            Location.extend([months[timerange][2].at[i, 'Location']] * 3)
            category.extend(['<50%', '50%-80%', '>80%'])
            value.extend([months[timerange][2].at[i, '<50%'], months[timerange][2].at[i, '50%-80%'], months[timerange][2].at[i, '>80%']])    
        #value = np.char.replace(value, ",", ".").astype('float').tolist()
        locs_share_chart_data = pd.DataFrame(list(zip(Location,category,value)), columns = ['Location', 'category', 'value'])

        data = pd.merge(months[timerange][0], locs_share_chart_data, on='Location')

        locs_chart = st.empty()
        locs_chart_height = st.sidebar.slider('Chart Height', min_value = 300, max_value = 1000, value = 500)
        locs_chart_width = st.sidebar.slider('Chart Width', min_value = 500, max_value = 2000, value = 1000)

        selector = alt.selection_single(empty='all', fields=['Location'])

        top = alt.Chart(months[timerange][0],
                                   height = locs_chart_height,
                                   width = locs_chart_width).mark_bar(
        ).encode(
            alt.X('Location', title = 'Location', axis = alt.Axis(labelAngle=-45, labelFontSize = 15, titleFontSize = 15)),
            alt.Y('Total Volume Emptied', title = "Volume Emptied [L]", axis = alt.Axis(titleFontSize = 15)),
            tooltip = [alt.Tooltip('Number of Containers', title = 'Number of Containers'),
                       alt.Tooltip('Number of Services', title = 'Number of Services'), 
                       alt.Tooltip('Total Volume Emptied', title = 'Volume Emptied [L]')],
            color = alt.value("#294269"),
            opacity = alt.condition(selector, alt.value(1.0), alt.value(0.3))
        ).add_selection(selector)
        

        bottom = alt.Chart(locs_share_chart_data).mark_bar().properties(width = locs_chart_width).encode(
                        alt.X('value:Q', title = 'Share of Services', axis = alt.Axis(format='%'), scale=alt.Scale(domain=(0, 1))),
                        alt.Y('category:O', sort = None, title = 'Group'),
                        color=alt.Color('category:N', legend = None, scale = alt.Scale(domain=['<50%', '50%-80%', '>80%'],
                                                                        range = ['#71D1A7', '#5E6773', '#294269']))
                    ).transform_filter(selector)
        
        locs_chart.altair_chart(alt.vconcat(top,bottom), use_container_width=True)

    if report_type == 'Waste-Type':
        st.header('Waste-Type Data')
        st.write('Click on the bars to see more information')
        ContentType = []
        category = []
        value = []
        for i in range(len(months[timerange][3])):
            ContentType.extend([months[timerange][3].at[i, 'ContentType']] * 3)
            category.extend(['<50%', '50%-80%', '>80%'])
            value.extend([months[timerange][2].at[i, '<50%'], months[timerange][3].at[i, '50%-80%'], months[timerange][2].at[i, '>80%']])    
        #value = np.char.replace(value, ",", ".").astype('float').tolist()
        wt_share_chart_data = pd.DataFrame(list(zip(ContentType,category,value)), columns = ['ContentType', 'category', 'value'])

        data = pd.merge(months[timerange][1], wt_share_chart_data, on='ContentType')

        wt_chart = st.empty()
        wt_chart_height = st.sidebar.slider('Chart Height', min_value = 300, max_value = 1000, value = 500)
        wt_chart_width = st.sidebar.slider('Chart Width', min_value = 500, max_value = 2000, value = 1000)

        selector = alt.selection_single(empty='all', fields=['ContentType'])

        top = alt.Chart(months[timerange][1],
                                   height = wt_chart_height,
                                   width = wt_chart_width).mark_bar(size=20
        ).encode(
            alt.X('ContentType', title = 'Waste-Type', axis = alt.Axis(labelAngle=0, labelFontSize = 15, titleFontSize = 15)),
            alt.Y('Total Volume Emptied', title = "Volume Emptied [L]", axis = alt.Axis(titleFontSize = 15)),
            tooltip = [alt.Tooltip('Number of Containers', title = 'Number of Containers'),
                       alt.Tooltip('Number of Services', title = 'Number of Services'), 
                       alt.Tooltip('Total Volume Emptied', title = 'Volume Emptied [L]')],
            color = alt.value("#294269"),
            opacity = alt.condition(selector, alt.value(1.0), alt.value(0.3))
        ).add_selection(selector)
        
        bottom = alt.Chart(wt_share_chart_data).mark_bar().properties(width = wt_chart_width).encode(
                        alt.X('value:Q', title = 'Share of Services', axis = alt.Axis(format='%'), scale=alt.Scale(domain=(0, 1))),
                        alt.Y('category:O', sort = None, title = 'Group'),
                        color=alt.Color('category:N', legend = None, scale = alt.Scale(domain=['<50%', '50%-80%', '>80%'],
                                                                        range = ['#71D1A7', '#5E6773', '#294269']))
                    ).transform_filter(selector)
        
        wt_chart.altair_chart(alt.vconcat(top,bottom), use_container_width=True)

    
    if report_type == 'Both':
        waste_type = st.radio('Select Waste-Type', ['General Waste', 'Recycling Waste'])

        if waste_type == 'General Waste':

            services = months[timerange][4][months[timerange][4].content_type == 'General Waste']
            report = create_wt_loc_report_sheet(services)
            share_prelim = wt_loc_share(services, 'General Waste')

            Location = []
            category = []
            value = []
            for i in range(len(share_prelim)):
                Location.extend([share_prelim.at[i, 'Location']] * 3)
                category.extend(['<50%', '50%-80%', '>80%'])
                value.extend([share_prelim.at[i, '<50%'], share_prelim.at[i, '50%-80%'], share_prelim.at[i, '>80%']])    

            share = pd.DataFrame(list(zip(Location,category,value)), columns = ['Location', 'category', 'value'])

            data = pd.merge(report, share, on='Location')

            both_chart = st.empty()
            both_chart_height = st.sidebar.slider('Chart Height', min_value = 300, max_value = 1000, value = 500)
            both_chart_width = st.sidebar.slider('Chart Width', min_value = 500, max_value = 2000, value = 1000) 

            selector = alt.selection_single(empty='all', fields=['Location'])

            top = alt.Chart(report,
                                   height = both_chart_height,
                                   width = both_chart_width).mark_bar(
            ).encode(
                alt.X('Location', title = 'Location', axis = alt.Axis(labelAngle=-45, labelFontSize = 15, titleFontSize = 15)),
                alt.Y('Total Volume Emptied', title = "Volume Emptied [L]", axis = alt.Axis(titleFontSize = 15)),
                tooltip = [alt.Tooltip('Number of Containers', title = 'Number of Containers'),
                        alt.Tooltip('Number of Services', title = 'Number of Services'), 
                        alt.Tooltip('Total Volume Emptied', title = 'Volume Emptied [L]')],
                color = alt.value("#294269"),
                opacity = alt.condition(selector, alt.value(1.0), alt.value(0.3))
            ).add_selection(selector)

            bottom = alt.Chart(share).mark_bar().properties(width = both_chart_width).encode(
                            alt.X('value:Q', title = 'Share of Services', axis = alt.Axis(format='%'), scale=alt.Scale(domain=(0, 1))),
                            alt.Y('category:O', sort = None, title = 'Group'),
                            color=alt.Color('category:N', legend = None, scale = alt.Scale(domain=['<50%', '50%-80%', '>80%'],
                                                                            range = ['#71D1A7', '#5E6773', '#294269']))
                        ).transform_filter(selector)

            both_chart.altair_chart(alt.vconcat(top,bottom), use_container_width=True)
        
        if waste_type == 'Recycling Waste':

            services = months[timerange][4][months[timerange][4].content_type == 'Recycling Waste']
            report = create_wt_loc_report_sheet(services)
            share_prelim = wt_loc_share(services, 'Recycling Waste')

            Location = []
            category = []
            value = []
            for i in range(len(share_prelim)):
                Location.extend([share_prelim.at[i, 'Location']] * 3)
                category.extend(['<50%', '50%-80%', '>80%'])
                value.extend([share_prelim.at[i, '<50%'], share_prelim.at[i, '50%-80%'], share_prelim.at[i, '>80%']])    

            share = pd.DataFrame(list(zip(Location,category,value)), columns = ['Location', 'category', 'value'])

            data = pd.merge(report, share, on='Location')

            both_chart = st.empty()
            both_chart_height = st.sidebar.slider('Chart Height', min_value = 300, max_value = 1000, value = 500)
            both_chart_width = st.sidebar.slider('Chart Width', min_value = 500, max_value = 2000, value = 1000) 

            selector = alt.selection_single(empty='all', fields=['Location'])

            top = alt.Chart(report,
                                   height = both_chart_height,
                                   width = both_chart_width).mark_bar(
            ).encode(
                alt.X('Location', title = 'Location', axis = alt.Axis(labelAngle=-45, labelFontSize = 15, titleFontSize = 15)),
                alt.Y('Total Volume Emptied', title = "Volume Emptied [L]", axis = alt.Axis(titleFontSize = 15)),
                tooltip = [alt.Tooltip('Number of Containers', title = 'Number of Containers'),
                        alt.Tooltip('Number of Services', title = 'Number of Services'), 
                        alt.Tooltip('Total Volume Emptied', title = 'Volume Emptied [L]')],
                color = alt.value("#294269"),
                opacity = alt.condition(selector, alt.value(1.0), alt.value(0.3))
            ).add_selection(selector)

            bottom = alt.Chart(share).mark_bar().properties(width = both_chart_width).encode(
                            alt.X('value:Q', title = 'Share of Services', axis = alt.Axis(format='%'), scale=alt.Scale(domain=(0, 1))),
                            alt.Y('category:O', sort = None, title = 'Group'),
                            color=alt.Color('category:N', legend = None, scale = alt.Scale(domain=['<50%', '50%-80%', '>80%'],
                                                                            range = ['#71D1A7', '#5E6773', '#294269']))
                        ).transform_filter(selector)

            both_chart.altair_chart(alt.vconcat(top,bottom), use_container_width=True)

            


if tenant == 'Madrid':
    
    madrid_dec_services = pd.read_csv('Data/madrid_dec_services.csv', sep = ";", decimal = ",")
    madrid_jan_services = pd.read_csv('Data/madrid_jan_services.csv', sep = ";", decimal = ",")

    madrid_location_report_dec = pd.read_csv('Data/madrid_location_report_dec.csv', sep = ";", decimal = ",")
    madrid_location_report_jan = pd.read_csv('Data/madrid_location_report_jan.csv', sep = ";", decimal = ",")

    madrid_location_share_dec = pd.read_csv('Data/madrid_location_share_dec.csv', sep = ";", decimal = ",")
    madrid_location_share_jan = pd.read_csv('Data/madrid_location_share_jan.csv', sep = ";", decimal = ",")

    madrid_locations = list(madrid_location_report_dec.Location.unique())

    coords_load_status = st.empty()
    coords_load_status.info('Retrieving Location Coordinates')
    madrid_location_coords = location_center_coords(madrid_locations)
    coords_load_status.success('Location Coordinates Retrieved')
    coords_load_status.empty()

    madrid_location_report_dec = madrid_location_report_dec.merge(madrid_location_coords, on='Location', how='left')
    madrid_location_report_jan = madrid_location_report_jan.merge(madrid_location_coords, on='Location', how='left')

    months = {'Dec 2020': [madrid_dec_services, madrid_location_report_dec, madrid_location_share_dec], 
              'Jan 2021': [madrid_jan_services, madrid_location_report_jan, madrid_location_share_jan]}
    timerange = st.sidebar.select_slider('Select Time Range', ['Dec 2020', 'Jan 2021'])
    
    st.header('Services by Location')
    map_plot = st.empty()
    map_height = st.slider('Map Height', min_value = 300, max_value = 1000, value = 500)
    scale = st.slider('Map Bar Scale', min_value = 0.005, max_value = 0.05, value = 0.005)

    # Figure
    months[timerange][1]['TVL'] = months[timerange][1]['Total Volume Emptied'].apply(round)

    layer = pdk.Layer(
        'ColumnLayer', 
        months[timerange][1],
        radius = 350,
        get_position='[c_long, c_lat]',
        get_elevation = 'TVL',
        get_fill_color = ["0.00013281305338772246 * TVL", "0.00013281305338772246 * TVL", "0.00013281305338772246 * TVL", 255],
        auto_highlight=True,
        elevation_scale=scale,
        pickable=True)

    # Set the viewport location
    view_state = pdk.ViewState(
        longitude= -3.703790,
        latitude = 40.416775,
        zoom=10.5,
        min_zoom=5,
        max_zoom=15,
        pitch=60,
        bearing=-25,
        height = map_height)
    map_plot.write(pdk.Deck(map_style = 'mapbox://styles/mapbox/light-v9', layers=[layer], initial_view_state=view_state, 
                tooltip = {
                         "text": "Location: {Location}\n Volume Emptied [L]: {TVL}\n Services: {Number of Services}"
                       }
                ))


    st.header('Location-Based Data')
    st.write('Click on the bars to see more information')
    Location = []
    category = []
    value = []
    for i in range(len(months[timerange][2])):
        Location.extend([months[timerange][2].at[i, 'Location']] * 3)
        category.extend(['<50%', '50%-80%', '>80%'])
        value.extend([months[timerange][2].at[i, '<50%'], months[timerange][2].at[i, '50%-80%'], months[timerange][2].at[i, '>80%']])    

    locs_share_chart_data = pd.DataFrame(list(zip(Location,category,value)), columns = ['Location', 'category', 'value'])
    
    data = pd.merge(months[timerange][1], locs_share_chart_data, on='Location')

    locs_chart = st.empty()
    locs_chart_height = st.slider('Chart Height', min_value = 300, max_value = 1000, value = 500)
    locs_chart_width = st.slider('Chart Width', min_value = 500, max_value = 2000, value = 1000)

    selector = alt.selection_single(empty='all', fields=['Location'])

    top = alt.Chart(months[timerange][1],
                                height = locs_chart_height,
                                width = locs_chart_width).mark_bar(
    ).encode(
        alt.X('Location', title = 'Location', axis = alt.Axis(labelAngle=-45, labelFontSize = 15, titleFontSize = 15)),
        alt.Y('Total Volume Emptied', title = "Volume Emptied [L]", axis = alt.Axis(titleFontSize = 15)),
        tooltip = [alt.Tooltip('Number of Containers', title = 'Number of Containers'),
                    alt.Tooltip('Number of Services', title = 'Number of Services'), 
                    alt.Tooltip('Total Volume Emptied', title = 'Volume Emptied [L]')],
        color = alt.value("#294269"),
        opacity = alt.condition(selector, alt.value(1.0), alt.value(0.3))
    ).add_selection(selector)

    bottom = alt.Chart(locs_share_chart_data).mark_bar().properties(width = locs_chart_width).encode(
                    alt.X('value:Q', title = 'Share of Services', axis = alt.Axis(format='%'), scale=alt.Scale(domain=(0, 1))),
                    alt.Y('category:O', sort = None, title = 'Group'),
                    color=alt.Color('category:N', legend = None, scale = alt.Scale(domain=['<50%', '50%-80%', '>80%'],
                                                                        range = ['#71D1A7', '#5E6773', '#294269']))
                ).transform_filter(selector)
    
    locs_chart.altair_chart(alt.vconcat(top,bottom), use_container_width=True)




