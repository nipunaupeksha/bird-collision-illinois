#!/usr/bin/env python
# coding: utf-8


import pandas as pd

def main(light_levels,collision_data,flight_call,output_file):
    try:
        #Load .json files to DataFrames
        lLevels=pd.read_json(light_levels)
        cData = pd.read_json(collision_data)
        fCall=pd.read_json(flight_call)

        #Correct the fCall DataFrame columns as given in the .docx file
        fCall.columns=["Genus","Species","Family","Flight","Flight Call","Habitat","Stratum"]

        #Remove rows containing NaN values from all the DataFrames
        lLevels.dropna(subset=lLevels.columns[[0,1]], inplace=True)
        cData.dropna(subset=cData.columns[[0,1,2,3]], inplace=True)
        fCall.dropna(subset=fCall.columns[[0,1,2,3,4,5,6]], inplace=True)

        #Since the LightScore for a certain date should be unique. we should remove duplicates from the lLevels DataFrame
        lLevels.drop_duplicates(subset='Date', keep=False, inplace=True)

        #The Taxonomic Ranking is  Family > Genus > Species. So we will create a separate column in fCall and remove the duplicates in that
        fCall['tax']=fCall.apply(lambda row: row.Family.lower().strip()+" "+row.Genus.lower().strip()+" "+row.Species.lower().strip(),axis=1)

        #since the Taxonomic name we made is unique, we can remove the duplicates accordingly.
        fCall.drop_duplicates(subset='tax', keep=False, inplace=True)

        #Merge lLevels DataFrame and cData based on the Date column since Date column is unique in lLevles DataFrame
        #What this implies is the date and light score of that day when this bird if found.
        df1 = pd.merge(lLevels,cData,on='Date')

        #After merging that we need to merge df1 and fCall DataFrames. To do that we need to find a common column.
        #The common columns available in those DataFrames are Genus and Species.
        #So we will create a column called sName specifying "Specific Name"
        #Furthermore we will delete the Genus and Species columns in df1 DataFrame since it can create duplicate columns
        fCall['sName']=fCall.apply(lambda row: row.Genus.lower().strip()+" "+row.Species.lower().strip(),axis=1)
        df1['sName']=df1.apply(lambda row: row.Genus.lower().strip()+" "+row.Species.lower().strip(),axis=1)
        df1=df1.drop(columns=["Genus","Species"])

        #Now let's merge the fCall and df1 DataFrames
        #This implies the bird data when the bird is found on the particular date
        df2 = pd.merge(df1,fCall,on='sName')

        #We will remove the sName and tax columns we used for merging.
        df2=df2.drop(columns=["sName","tax"])

        #Let's sort the DataFrame by "Date"
        df2["Date"] = pd.to_datetime(df2["Date"])
        df2 = df2.sort_values(by="Date")
        #Let's send the DataFrame to a .csv file. Yo can open .csv file in Microsoft Excel or import it to MySQL database.
        df2.to_csv (output_file, index = False, header=True)
    except Exception as e:
        print(e)
        return
  

main("light_levels.json","chicago_collision_data.json","flight_call.json","output.csv")






