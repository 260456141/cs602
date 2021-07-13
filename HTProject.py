'''

Name:    Haoze Tan
CS230:   Section 1
Data:    Volcanic Eruptions
URL:

Description:
This program ... (a few sentences about your program and the queries and charts)

'''




import streamlit as st
import pandas as pd
from PIL import Image
import webbrowser
import matplotlib.pyplot as plt


#1,read file
#2,search
#3,AllData
#4,welcome page
#5,use data


#1 ok
def readFile(fileName):
    data = pd.read_csv(fileName, encoding = 'ISO-8859-1')
    dataFrame = pd.DataFrame(data, columns =['Volcano Name', 'Country', 'Primary Volcano Type', 'Activity Evidence', 'Last Known Eruption', 'Region', 'Latitude', 'Longitude', 'Elevation (m)', 'Link'])
    return dataFrame
#2--1 ok
def findClosest(NumbersList, specificValue):
    return NumbersList[min(range(len(NumbersList)), key = lambda i: abs(NumbersList[i] - specificValue))]
#2-- main ok 
def filter(originalData):

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
        # special 1
        if primaryChoice == 'Elevation (m)':
            maxElevation = dataFrame['Elevation (m)'].max()
            minElevation = dataFrame['Elevation (m)'].min()
            secondaryChoice = st.sidebar.slider('Please select an elevation', int(minElevation), int(maxElevation), 670, 10)
            elevationList = sorted(dataFrame[primaryChoice].unique())
            if secondaryChoice not in elevationList:
                txt = 'Sorry, there is no data with the elevation = ' + str(secondaryChoice) + '. This is the closest result after adjustment.' 
                adjust = int(findClosest(elevationList, secondaryChoice))
                secondaryChoice = st.sidebar.slider(txt, int(minElevation), int(maxElevation), adjust, 10)
        # special 2
        elif primaryChoice == 'Activity Evidence':
            secondaryList.remove(secondaryList[0])
            secondaryChoice = st.sidebar.radio("Select an Activity Evidence: ", secondaryList)
        # others
        else: 
            secondaryChoice = st.sidebar.selectbox('Which ' + primaryChoice.lower() + ' you are searching?', secondaryList)
        # setting new data and return to main
        filteredData = dataFrame[dataFrame[primaryChoice] == secondaryChoice]
        return filteredData, primaryChoice, secondaryChoice

    return None, primaryChoice, None
#3--ok
def allDataCheck():
    return st.sidebar.checkbox('All Data', False)

#4--ok
def welcomePage(showTitle, primaryChoice):
    if showTitle:
        st.title('Welcome to Volcanoes Data Page')
        st.write("This volcano doesn't look like it's going to erupt. Try to change the filter and look for erupting volcanoes!")
        image1Link = 'https://en.wikipedia.org/wiki/Mount_Sinabung#/media/File:Sinabung-Gundaling-20100913.JPG'
        image1 = Image.open('volcano ne.jpg')
        st.image(image1, caption = 'Mount Sinabung')
        col1, col2 = st.beta_columns([4, 1])
        with col1:
            st.write('')
        with col2:
            if st.button('picture from'):
                webbrowser.open_new_tab(image1Link)
    else:
        st.title('Almost Erupt!')
        st.subheader('Please continue selecting a ' + str(primaryChoice) + '.')
        video = open('volcano.mov', 'rb')
        videoLink = 'https://www.youtube.com/watch?v=VNGUdObDoLk'
        videoBytes = video.read()
        st.video(videoBytes)
        col1, col2 = st.beta_columns([4, 1])
        with col1:
            st.write('')
        with col2:
            if st.button('Video from'):
                webbrowser.open_new_tab(videoLink)

#5--1 ok
def map(data):
    st.subheader('This is the Map')
    dataFrame = pd.DataFrame(data)
    dataFrame = dataFrame.rename(columns = {'Latitude': 'lat', 'Longitude': 'lon'}, inplace = False)
    st.map(dataFrame)


#5--2--1 ok 
def link(data):
    dataFrame = pd.DataFrame(data)
    name = dataFrame['Volcano Name'].to_string(index = False)
    link = dataFrame['Link'].to_string(index = False)
    st.subheader('This is the link of ' + name)
    if st.button('Go to official website of ' + name):
        webbrowser.open_new_tab(link)

def findTopValue(pieNumberList, numberOfTop):
    topNumberList = []

    for times in range(0, numberOfTop): 
        maxValue = pieNumberList[0] - 1
          
        for n in range(len(pieNumberList)):     
            if pieNumberList[n] > maxValue:
                maxValue = pieNumberList[n]
                  
        pieNumberList.remove(maxValue)
        topNumberList.append(maxValue)
    return topNumberList
    

#5--2--2--1
def pieChart(data, columnName):
    dataFrame = pd.DataFrame(data)
    dataFrame = dataFrame[columnName].to_list()
    uniqueWords = list(set(dataFrame))

    numberList = []
    for word in uniqueWords:
        numberList.append(dataFrame.count(word))

    # change the pie legend here
    if len(uniqueWords) > 6:
        st.write('可以让用户下拉栏来选择想要显示top几')
        input = st.selectbox('选数字', [3,4,5,6,7,8])

        numberListCopy = numberList.copy()
        shortNumberList = findTopValue(numberList, input)
        shortWordList = []
        for number in shortNumberList:
            pos = numberListCopy.index(number)
            shortWordList.append(uniqueWords[pos])
        otherName = 'Other'
        otherNumber = 0
        for number in numberList:
            otherNumber += number
        shortWordList.append(otherName)
        shortNumberList.append(otherNumber)
        uniqueWords = shortWordList
        numberList = shortNumberList
        
        explode = [0] * len(uniqueWords)
        explode[0] = .1

    else:
        explode = [0] * len(uniqueWords)
        pos = numberList.index(max(numberList))
        explode[pos] = .1

    fig, ax = plt.subplots()
    ax.pie(numberList, explode = explode, labels = uniqueWords, autopct = '%.1f%%')
    st.pyplot(fig)

#5--2--2--2
def barChart(data, columnName):
    dataFrame = pd.DataFrame(data)
    elevationList = dataFrame[columnName].to_list()
    nameList = dataFrame['Volcano Name'].to_list()

    st.subheader('This is the bar chart')
    fig, ax = plt.subplots()
    ax.bar(nameList, elevationList)
    if len(nameList) >= 10:
        plt.setp(ax.get_xticklabels(), visible=False)
    elif len(nameList) > 3 and len(nameList) < 10:
        rotation = int(len(nameList)) * 10
        plt.xticks(rotation = rotation)


    st.pyplot(fig)

#5--2-main ok
def chartChoice(data, sideBar):

    dataFrame = pd.DataFrame(data)

    #设置选择框
    col1, col2 = st.beta_columns(2)
    with col1:
        chartTypeList = ['-- Select a chart --', 'Pie Chart', 'Bar Chart']
        if sideBar[0] == 'Elevation (m)' or sideBar[2]:
            chartTypeList.remove('Bar Chart')
        primaryChartChoice = st.selectbox('Please select a chart type', chartTypeList)
    with col2:
        if primaryChartChoice == 'Pie Chart':
            pieDefault = '-- Select a data type --'
            pieSelectList = dataFrame.columns.values.tolist()
            deleteList = ['Latitude', 'Longitude', 'Link', 'Elevation (m)', 'Volcano Name']
            if not sideBar[2] and sideBar[0] != 'Elevation (m)':
                deleteList.append(sideBar[0])
            for i in deleteList:
                pieSelectList.remove(i)
            pieSelectList.insert(0, pieDefault)

            secondaryChartChoice = st.selectbox('Please select a data type', pieSelectList)
        elif primaryChartChoice == 'Bar Chart':
            secondaryChartChoice = st.selectbox('Please select a data type', ['-- Select a data type --', 'Elevation (m)'])
        else:
            st.write('⬅ Please select a chart type')
    
    # 识别选择框
    if primaryChartChoice == 'Pie Chart' and secondaryChartChoice != '-- Select a data type --':
        if sideBar[2]:
            st.write('Here is the pie chart is about ' + str(secondaryChartChoice) + ' based on all data.'  )
        else:
            st.write('Here is the pie chart based on ' + str(sideBar[0]) + ': ' + str(sideBar[1]) + ', and ' + str(secondaryChartChoice) + '.') 
        pieChart(dataFrame, secondaryChartChoice)

    elif primaryChartChoice == 'Bar Chart' and secondaryChartChoice != '-- Select a data type --':
        barChart(dataFrame, secondaryChartChoice)
    


#5--main ok
def subMain(dataFrame, sideBar):
    #来张图先 火山爆发图
    image2Link = 'https://theconversation.com/krakatoa-is-still-active-and-we-are-not-ready-for-the-tsunamis-another-eruption-would-generate-147250'
    image2 = Image.open('volcano e.jpg')
    st.image(image2, caption = 'Krakatoa volcano')
    col1, col2 = st.beta_columns([4, 1])
    with col1:
        st.write('')
    with col2:
        st.write([picture from](https://theconversation.com/krakatoa-is-still-active-and-we-are-not-ready-for-the-tsunamis-another-eruption-would-generate-147250))
        if st.button('picture from'):
            webbrowser.open_new_tab(image2Link)
    
    #1 data frame
    if sideBar[2]:
        st.subheader('This is the Data Frame of ' + str(sideBar[0]) + ': ' + str(sideBar[1]))
    else:
        st.subheader('This is the Data Frame of ' + str(sideBar[0]) + ': ' + str(sideBar[1]))
    st.write(dataFrame)
    if len(dataFrame) > 1:
        st.write('This dataFrame showed ' + str(len(dataFrame)) + ' volcanoes.')
    else: # the only result here is {len(dataFrame) = 1}
        st.write('This dataFrame showed ' + str(len(dataFrame)) + ' volcanoe.')

    #2 map
    map(dataFrame)

    #3 charts
    if len(dataFrame) > 1:
        st.subheader('This is chart part')
        chartChoice(dataFrame, sideBar)
    else: # the only result here is {len(dataFrame) = 1}
        link(dataFrame)




#ok
#1,read file
#2,search
#3,AllData
#4,welcome page
#5,use data
def main():

    #1 read file
    fileName = 'volcanoes.csv'
    originalData = readFile(fileName)

    #2 search filter data
    filteredData, filterPrimaryChoice, filterSecondaryChoice = filter(originalData)

    #3 AllData
    allData = allDataCheck()
    if allData:
        dataFrame = originalData
    else:
        dataFrame = filteredData 
    sideBarValue = [filterPrimaryChoice, filterSecondaryChoice, allData]

    #4 welcome page
    if filterPrimaryChoice == '-- Select a type for search --' and not allData:
        welcomePage(True, None)

    #5 use data  选择好数据的界面
    else:
        
        st.sidebar.markdown(str(len(dataFrame)) + ' results')
        if sideBarValue[2]:
            st.title('Erupting')
            st.subheader('The following data is based on the All Data')
            subMain(dataFrame, sideBarValue)
        else:
            if sideBarValue[0] != '-- Select a type for search --' and sideBarValue[1] == '-- Select '+ sideBarValue[0] + ' --':
                st.sidebar.markdown('Please continue selecting a ' + str(sideBarValue[0]) + '.')
                welcomePage(False, sideBarValue[0])
            else:
                st.title('Erupting')
                st.subheader('The following data is based on the filter')
                subMain(dataFrame, sideBarValue)

main()




