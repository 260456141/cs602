'''
Name:    Haoze Tan
CS602:   Section 1
Data:    Volcanic Eruptions
URL:     https://share.streamlit.io/260456141/cs602/main/HTProject.py

Description:
This program depends on the volcanoes data, to develop a website by using python and streamlit.
let users custom filter to show the data, concluding show the dataFrame, making map, and plotting charts.
'''

import numpy as np
import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import pydeck as pdk
import altair as alt
import csv


@st.cache
# Read file by using and returning pandas data frame, and also deleted the colums which are not will be used.
def readFile(fileName):
    data = pd.read_csv(fileName, encoding = 'ISO-8859-1')
    dataFrame = pd.DataFrame(data, columns =['Volcano Name', 'Country', 'Primary Volcano Type', 'Activity Evidence', 'Last Known Eruption', 'Region', 'Latitude', 'Longitude', 'Elevation (m)', 'Link'])
    return dataFrame


# Filter main part in sidebar:
def filter(originalData):
    # Find the closest value of a numberList depends on the specificValue by using lambda.
    # This function is used to adjust the Elevation (m) in the filter.
    def findClosest(NumbersList, specificValue):
        return NumbersList[min(range(len(NumbersList)), key = lambda number: abs(NumbersList[number] - specificValue))]


    # set data frame
    dataFrame = pd.DataFrame(originalData)

    st.sidebar.header('Filter')

    #1 filterPrimaryChoice
    primaryDefault = '-- Select a type for search --'
    primaryList = dataFrame.columns.values.tolist()
    deleteList = ['Latitude', 'Longitude', 'Link']
    for column in deleteList:
        primaryList.remove(column)
    primaryList.insert(0, primaryDefault)
    primaryChoice = st.sidebar.selectbox('How would you like to search?', primaryList)

    #2 filterSecondaryChoice
    if primaryChoice != primaryDefault: 
        secondaryDefault = '-- Select '+ primaryChoice + ' --'
        secondaryList = sorted(dataFrame[primaryChoice].unique())
        secondaryList.insert(0, secondaryDefault)
        # special 1: Elevation (m)
        if primaryChoice == 'Elevation (m)':
            maxElevation = dataFrame['Elevation (m)'].max()
            minElevation = dataFrame['Elevation (m)'].min()
            secondaryChoice = st.sidebar.slider('Please select an elevation', int(minElevation), int(maxElevation), 670, 10)
            elevationList = sorted(dataFrame[primaryChoice].unique())
            if secondaryChoice not in elevationList:
                st.sidebar.info(f'Oops! There is no data with the elevation = {str(secondaryChoice)}.')
                adjust = int(findClosest(elevationList, secondaryChoice))
                secondaryChoice = st.sidebar.slider('This is the closest result after adjustment.', int(minElevation), int(maxElevation), adjust, 10)
        # special 2: Activity Evidence
        elif primaryChoice == 'Activity Evidence':
            secondaryList.remove(secondaryList[0])
            secondaryChoice = st.sidebar.radio("Select an Activity Evidence: ", secondaryList)
        # others (no special)
        else: 
            secondaryChoice = st.sidebar.selectbox('Which ' + primaryChoice.lower() + ' you are searching?', secondaryList)
        
        # setting new data and return to main
        filteredData = dataFrame[dataFrame[primaryChoice] == secondaryChoice]
        return filteredData, primaryChoice, secondaryChoice

    return None, primaryChoice, None


# All Data check box.
def allDataCheck():
    return st.sidebar.checkbox('All Volcanoes', False)


# Display page with no data filter or data filtering incomplete.
def welcomePage(showTitle, primaryChoice):
    # Display page with no data filter.
    if showTitle:
        col1, col2, col3 = st.beta_columns([1, 8, 1])
        with col1:
            st.write('')
        with col2:
            st.title('Volcanoes Data Demonstration')
        with col3:
            st.write('')
        st.write("This volcano doesn't look like it's going to erupt. Try to change the filter and look for erupting volcanoes!")
        image1Link = 'https://en.wikipedia.org/wiki/Mount_Sinabung#/media/File:Sinabung-Gundaling-20100913.JPG'
        image1 = Image.open('volcano ne.jpg')
        st.image(image1, caption = 'Mount Sinabung')
        col1, col2 = st.beta_columns([4, 1])
        with col2:
            st.write(f'[Picture from]({str(image1Link)})')
    # Display page with data filtering incomplete.
    else:
        st.title('Almost Erupt!')
        st.subheader(f'Please continue selecting a {str(primaryChoice)}.')
        video = open('volcano.mov', 'rb')
        videoLink = 'https://www.youtube.com/watch?v=VNGUdObDoLk'
        videoBytes = video.read()
        st.video(videoBytes)
        col1, col2 = st.beta_columns([4, 1])
        with col2:
            st.write(f'[Video from]({str(videoLink)})')
        st.write('*This video may not load on Chrome. Please try it on Safari or Edge.')


# pivotTable to show the average elevation of the volcanoes
def pivotTable(data, sideBar):
    dataFrame = pd.DataFrame(data)
    if len(dataFrame) > 1 and sideBar[0] != 'Elevation (m)': 
        # Making pivot table:
        st.write('This is the pivot table for max, min, and mean of elevation.')
        table = pd.pivot_table(dataFrame, values = ['Elevation (m)'], 
                                            index = [sideBar[0]], 
                                            aggfunc = {'Elevation (m)': [min,max,np.mean]})
        st.write(table)
        st.write(f'{len(table)} {sideBar[0]}(s).')


# Show map part:
def map(data, sideBar):
    # HEX color convert to RGB:
    def convertColor(HEX = '#ffff33'):
        # read file to avoid hardcoding, and make sure use dictionary in this project.
        fileName = 'hexadecimal.csv'
        with open(fileName, mode = 'r') as f:
            data = csv.DictReader(f)
            HEXDict = {}
            for line in data:
                hexadecimal = line['hexadecimal']
                decimal = line['decimal']
                if hexadecimal not in HEXDict.keys():
                    HEXDict[hexadecimal] = decimal
        RGB = []
        index = 0
        start = 1
        # loop 3 times for adding 3 numbers of RGB.
        for times in range(3):
            result = 0
            number = 0
            # loop the string to identify the letters or numbers.
            for i in HEX[start:start+2]:
                if i in list(HEXDict.keys()):
                    number = HEXDict[i]
                else:
                    number = i
                if index % 2 == 0:
                    result += int(number) * 16
                else:
                    result += int(number)
                index += 1
            RGB.append(result)
            start += 2
        return RGB


    # Setting title and data.
    if sideBar[2]:
        st.subheader('This is the map of all Volcanoes.')
    else:
        st.subheader(f'This is the map of {sideBar[0]}: {sideBar[1]}.')
    dataFrame = pd.DataFrame(data)
    # Making map.
    # custom expander with: 1,Map Mode. 2,zoom factor. 3,Font. 4,radius. 5,color
    expander = st.beta_expander(label='Map Setting')
    with expander:
        mode = st.selectbox('Mode',['Dark', 'Light', 'Streets', 'Satellite-Streets'])
        customMode = f'mapbox://styles/mapbox/{mode.lower()}-v10'
        customFont = st.radio('Font',["Cursive", "Monospace", "Times New Roman"])
        if sideBar[2]:
            customZoom = st.slider('Zoom Factor', min_value = 0, max_value = 7, value = 0)
        else:
            customZoom = st.slider('Zoom Factor', min_value = 0, max_value = 7, value = 3)
        customRadius = st.slider('Circle Radius', min_value = 1000, max_value = 60000, value = 30000)
        HEXcolor = st.color_picker('Pick A Color', '#ffff33')
        bugLink = 'https://github.com/streamlit/streamlit/pull/3500'
        txt = '*ColorPicker cannot work on Streamlit(0.84.0) Sharing, please try it on localhost.'
        st.write(f'{txt} [Question]({str(bugLink)})')
        RGBcolor = convertColor(HEXcolor)
    # set value for map
    view_state = pdk.ViewState(
        latitude = dataFrame["Latitude"].mean(),
        longitude = dataFrame["Longitude"].mean(),
        zoom = customZoom)
    layer = pdk.Layer('ScatterplotLayer',
                        data = dataFrame,
                        pickable = True,
                        opacity = 0.40, # the transparency of the circle
                        get_position = '[Longitude,Latitude]',
                        get_radius = customRadius,
                        get_color = RGBcolor)
    tool_tip = {"html": "<b>Volcano Name:<b><br/> {Volcano Name} <br/> Region: {Region} <br/> Type: {Primary Volcano Type} <br/>Lat: {Latitude} Long: {Longitude}",
                "style": {"color": "white", "font-family": customFont}}
    map = pdk.Deck(
        map_style = customMode,
        layers = [layer],
        initial_view_state = view_state,
        tooltip = tool_tip
    )
    st.pydeck_chart(map)

# display circleChart
def circleChart(data):
    dataFrame = pd.DataFrame(data)
    if len(data) > 1:
        scale = alt.Scale(zero = False)
    else:
        scale = alt.Scale(zero = True)
    Cchart = alt.Chart(dataFrame).mark_circle(
            opacity = 0.5,
            stroke = 'black',
            strokeWidth = 1).encode(
                                    alt.X('Longitude', scale = scale), 
                                    alt.Y('Latitude', scale = scale),
                                    alt.Size('Elevation (m)', 
                                        scale = alt.Scale(range = [-500, 6000]),
                                        legend = alt.Legend(title = 'Elevation (m)')),
                                    alt.Color('Primary Volcano Type', 
                                        legend = alt.Legend(title = 'Primary Volcano Type'))
                            ).properties(
                                    width = 700,
                                    height = 500).transform_filter(
                                                                    alt.datum.Entity != 'All natural disasters'
                                                                )
    col1, col2, col3 = st.beta_columns([1,3,1])
    with col2:
        st.write('Relationship between Lon/Lat and Elevation')
    st.write(Cchart)


# Get link of the single volcano by the number of filtered result is 1.
def link(data):
    dataFrame = pd.DataFrame(data)
    name = dataFrame['Volcano Name'].to_string(index = False)
    link = dataFrame['Link'].to_string(index = False)
    click = f'[here]({str(link)})'
    st.subheader(f'click {click} to get the link of {name}')


# Draw pie chart if the results of filtered data more than 1.
def pieChart(data, columnName):
    # Find the top value by users' custom, which the pieces of pie more than 6.
    def findTopValue(pieNumberList, numberOfTop):
        topNumberList = []
        for times in range(0, numberOfTop): 
            maxValue = pieNumberList[0] - 1
            # Finding max
            for n in range(len(pieNumberList)):     
                if pieNumberList[n] > maxValue:
                    maxValue = pieNumberList[n]
            # Delete for next time        
            pieNumberList.remove(maxValue)
            topNumberList.append(maxValue)
        return topNumberList
    
    
    # Setting data frame and data list
    dataFrame = pd.DataFrame(data)
    dataList = dataFrame[columnName].to_list()
    # Getting the wordlist and numberlist for draw pie.
    uniqueWords = list(set(dataList))
    numberList = []
    for word in uniqueWords:
        numberList.append(dataList.count(word))
    # if the number of pieces of pie over 6, Do Not show all pieces!
    # let user set pieces:
    if len(uniqueWords) > 6:
        st.warning('A large amount of data cannot be displayed completely.')
        col1, col2 = st.beta_columns([2, 1])
        with col1:
            st.write('')
        with col2:
            input = st.selectbox('Please select the top number to display.', [1, 2, 3, 4, 5, 6], index = 3)
        # Prevent all items in an element are appearing only once, thus chaos the new word list.
        if abs(len(uniqueWords) - len(dataList)) > 0:
            numberListCopy = numberList.copy()
            shortNumberList = findTopValue(numberList, input)
            shortWordList = []
            for number in shortNumberList:
                pos = numberListCopy.index(number)
                if uniqueWords[pos] not in shortWordList:
                    shortWordList.append(uniqueWords[pos])
                    numberListCopy.remove(numberListCopy[pos])
                    uniqueWords.remove(uniqueWords[pos])
            otherName = 'Other'
            otherNumber = 0
            for number in numberList:
                otherNumber += number
            shortWordList.append(otherName)
            shortNumberList.append(otherNumber)
        # Very few special cases will come here：
        # (The length of the unique word list is greater than 6, and the number of times each word appears in the total data is 1)
        # example: Country:China, PieChart:Last Known Eruption.
        else:
            shortNumberList = numberList[0:input]
            shortWordList = uniqueWords[0:input]
            otherName = 'Other'
            otherNumber = 0
            for number in numberList[input:]:
                otherNumber += number
            shortWordList.append(otherName)
            shortNumberList.append(otherNumber)
        numberList = shortNumberList
        uniqueWords = shortWordList
        explode = [0] * len(uniqueWords)
        explode[0] = .1
    #Other normal values will look for the largest part and crack out
    else:
        explode = [0] * len(uniqueWords)
        pos = numberList.index(max(numberList))
        explode[pos] = .1
    # Plotting Pie
    fig, ax = plt.subplots()
    ax.pie(numberList, explode = explode, labels = uniqueWords, autopct = '%.1f%%')
    plt.style.use('bmh')
    st.pyplot(fig)
            

# Draw bar chart if the results of filtered data more than 1.
# Because of the large amount of all data and the same data type of 'Elevation (m)',
# if all data is True or the filter primary choice is 'Elevation (m)', there is no access to draw a bar chart.
def barChart(data, columnName, sideBar):
    # Setting the data frame and elevation list.
    dataFrame = pd.DataFrame(data)
    elevationList = dataFrame[columnName].to_list()
    nameList = dataFrame['Volcano Name'].to_list()
    # Plotting bar chart
    col1, col2, col3 = st.beta_columns([1, 6, 1])
    with col2:
        st.subheader(f'This is the {columnName} of {sideBar[0]}:{sideBar[1]}')
    fig, ax = plt.subplots()
    ax.bar(nameList, elevationList)
    # if the element over 10 there is no X-axis tick lables.
    if len(nameList) >= 10:
        st.info('Due to the large number of volcanoes, the name of the volcanoes has been hidden.')
        plt.setp(ax.get_xticklabels(), visible = False)
    # other rotation of xticks are depending on the length of filtered data:
    # example: Country:Armenia:BarChart:'Elevation (m)', len(dataFrame) = 3, rotation = 0
    # example: Country:China:BarChart:'Elevation (m)', len(dataFrame) = 9, rotation = 90
    elif len(nameList) > 3 and len(nameList) < 10:
        rotation = int(len(nameList)) * 10
        plt.xticks(rotation = rotation)
    st.pyplot(fig)


# the filter of the charts part.
def chartChoice(data, sideBar):
    # Setting data frame.
    dataFrame = pd.DataFrame(data)
    # Setting the chart selection box.
    col1, col2 = st.beta_columns(2)
    with col1:
        chartTypeList = ['-- Select a chart --', 'Pie Chart', 'Bar Chart']
        if sideBar[0] == 'Elevation (m)' or sideBar[2]:
            chartTypeList.remove('Bar Chart')
        primaryChartChoice = st.selectbox('Please select a chart type', chartTypeList)
    # Setting the data type selection box.
    # The data type here cannot be duplicated with the filter in side bar.
    with col2:
        if primaryChartChoice == 'Pie Chart':
            pieDefault = '-- Select a data type --'
            pieSelectList = dataFrame.columns.values.tolist()
            deleteList = ['Latitude', 'Longitude', 'Link', 'Elevation (m)', 'Volcano Name']
            if not sideBar[2] and sideBar[0] != 'Elevation (m)':
                deleteList.append(sideBar[0])
            for column in deleteList:
                pieSelectList.remove(column)
            pieSelectList.insert(0, pieDefault)
            secondaryChartChoice = st.selectbox('Please select a data type', pieSelectList)
        elif primaryChartChoice == 'Bar Chart':
            secondaryChartChoice = st.selectbox('Please select a data type', ['-- Select a data type --', 'Elevation (m)'])
    # Depends on the chart choice, calling the different chart functions.
    if primaryChartChoice == 'Pie Chart' and secondaryChartChoice != '-- Select a data type --':
        col1, col2, col3 = st.beta_columns([1, 6, 1])
        with col2:
            if sideBar[2]:
                st.write(f'Here is the pie chart is about {str(secondaryChartChoice)} based on all data.'  )
            else:
                st.write(f'Here is the pie chart based on {str(sideBar[0])}: {str(sideBar[1])}, and {str(secondaryChartChoice)}.') 
        pieChart(dataFrame, secondaryChartChoice)
    elif primaryChartChoice == 'Bar Chart' and secondaryChartChoice != '-- Select a data type --':
        barChart(dataFrame, secondaryChartChoice, sideBar)
    

# Organize the overall structure and order of the web page when the user selected data.
def subMain(dataFrame, sideBar):
    # Here is the image of the volcano erupting
    image2Link = 'https://www.bloomberg.com/news/articles/2021-01-17/indonesian-volcano-spews-ash-as-officials-grapple-with-disasters'
    image2 = Image.open('volcano e.jpg')
    st.image(image2, caption = 'Mount Semeru Volcano')
    col1, col2 = st.beta_columns([4, 1])
    with col1:
        st.write('')
    with col2:
        st.write(f'[Picture from]({str(image2Link)})')
    
    # Part 1: data frame
    if sideBar[2]:
        st.subheader(f'This is the Data Frame of all volcanoes.')
    else:
        st.subheader(f'This is the Data Frame of {str(sideBar[0])}: {str(sideBar[1])}.')
    st.write(dataFrame)
    st.write(f'This dataFrame showed {str(len(dataFrame))} volcano(es).')

    # Part 2:pivot table
    # Display the pivot table When there is a column selected and the length of data > 1.
    if sideBar[0] != '-- Select a type for search --':
        pivotTable(dataFrame, sideBar)

    # Part 3: map
    map(dataFrame, sideBar)

    # Part 4: Circle Chart
    # if sideBar[0] not in ['Primary Volcano Type', 'Activity Evidence']:
    circleChart(dataFrame)

    # Part 4: charts
    # if the number volcanoes more than 1, they have the significance of contrast.
    if len(dataFrame) > 1:
        st.subheader('How would you like to make a chart?')
        chartChoice(dataFrame, sideBar)
    # if there is only 1 volcano, show the link to official website
    else: # the only result here is {len(dataFrame) = 1}
        link(dataFrame)


def footer():
    # Bentley University Logo:
    col1, col2 = st.beta_columns([1,5])
    with col1:
        st.image('https://www.bentley.edu/sites/default/files/inline-images/Bentley_%20Institutional_Seal_Final%20Comp.jpg')
    with col2:
        st.markdown('***')
    # Footer information    
    col1, col2, col3, col4= st.beta_columns([1,2,3,1])
    with col2:
        st.write('Author: Haoze Tan')
    with col3:
        volcanoOrgLink = 'https://volcano.si.edu'
        st.write(f'Source from [volcano.si.edu]({volcanoOrgLink})')
    with col4:
        viewDataLink = 'https://github.com/260456141/cs602/blob/main/volcanoes.csv'
        st.write(f'[View Data]({viewDataLink})')


# The main part realizes the following actions:
#       1, Read files by pandas.
#       2, Filter date in side bar.
#       3, All volcanoes data check box.
#       4, Show welcome pages.
#       5, Show link for single volcano, and making plots for multi-volcanoes.
#       6, Footer.
def main():
    # Read file.
    originalData = readFile(FILENAME)

    # Search filter data.
    filteredData, filterPrimaryChoice, filterSecondaryChoice = filter(originalData)

    # All data Check box.
    allData = allDataCheck()
    if allData:
        dataFrame = originalData
    else:
        dataFrame = filteredData 
    sideBarValue = [filterPrimaryChoice, filterSecondaryChoice, allData]

    # Welcome page.
    if filterPrimaryChoice == '-- Select a type for search --' and not allData:
        welcomePage(True, None)

    # Using data, when user finish select the data.
    else:
        st.sidebar.markdown(f'{str(len(dataFrame))} results')
        if sideBarValue[2]:
            st.title('Erupting')
            st.subheader('The following data is based on the All Data')
            subMain(dataFrame, sideBarValue)
        else:
            if sideBarValue[0] != '-- Select a type for search --' and sideBarValue[1] == f'-- Select {sideBarValue[0]} --':
                st.sidebar.markdown(f'Please continue selecting a {str(sideBarValue[0])}.')
                welcomePage(False, sideBarValue[0])
            else:
                st.title('Erupting')
                st.subheader('The following data is based on the filter')
                subMain(dataFrame, sideBarValue)
    # Footer
    footer()


FILENAME = 'volcanoes.csv'
main()




