import pandas as pd

#read in the csv
df = pd.read_csv("~/Downloads/ShipmentsNumbers.csv")
print(df.describe())
print(df['Origin City'].unique())
df['indexyo'] = range(df['SCAC'].count())
#print(df['Origin City'].unique())

#change freight paid to float
pd.to_numeric(df[" Freight Paid "])

#calculate original freight paid
totalOriginalCost = df[" Freight Paid "].sum()
print("original cost: " + str(round(totalOriginalCost,2)))
print("original distance: " + str(df["Miles"].sum()))

#sort by destination first
df.sort_values(by=['Ship Date'], inplace=True)


#all shipments in one day
def consolidateTrucks(df, uniqueDate):

    dfSubset = df.loc[df['Ship Date'] == str(uniqueDate)]

    #loop through records of the same date
    currentCity = ""
    currentWeight = 0
    for index, row in dfSubset.iterrows():

        #if the city is changing from the previous record, add the weight, and skip the cost of the truck
        if row['Dest City'] == currentCity:

            #TODO: change to have the most be 45,000 pounds
            if currentWeight + row['Weight'] < 45000:
                currentWeight += row['Weight']
                df.loc[df['indexyo'] == index, [' Freight Paid ']] = 0
                df.loc[df['indexyo'] == index, ['Miles']] = 0
            else:
                currentWeight = 0

        else:
            currentWeight = 0

        currentCity = row['Dest City']



#this function should just return the best origin given the destination city
def getClosestOrigin(destinationSubset, cities):

    bestOriginCity = "";
    bestDistance = 1000000;
    bestFreight = 10000000;
    bestState = "";
    bestZip = "";

    #what if we argued that we could get the lowest rate if we picked 4 shipping companies

    for index, row in destinationSubset.iterrows():
        bestDestCity = row['Dest City']
        if(row['Origin City'] in cities.keys()):

            #change bestFreight to bestDistance to decide what to make the dependant variable
            if(float(row['Miles']) < bestDistance):

                #if a standardized rate value exists
                if(cities[row['Origin City']] > 0):
                    bestFreight = row['Miles']*cities[row['Origin City']]
                else:
                    bestFreight = row[' Freight Paid ']

                bestDistance = row['Miles']
                bestOriginCity = row['Origin City']

    #probs gotta check if the best city is empty
    if(bestOriginCity == ""):
        bestOriginCity = "placeholder";

        #this is an incorrect assumption... but just gonna let it work for now
        bestDistance = round(destinationSubset['Miles'].min());
        bestFreight = destinationSubset[' Freight Paid '].min();

        bestState = "placeholder";
        bestZip = "placeholder";

    best = {"destinationCity": bestDestCity, "originCity":bestOriginCity,"miles":bestDistance,"freight":bestFreight}
    return best



def updateAllInDestination(df, bestDictionary):

    arrayFreight = []
    arrayMiles = []
    arrayOrigins = []

    for index, row in df.iterrows():
        arrayFreight.append(bestDictionary[row['Dest City']]['freight'])
        arrayMiles.append(bestDictionary[row['Dest City']]['miles'])
        arrayOrigins.append(bestDictionary[row['Dest City']]['originCity'])

    df[' Freight Paid '] = arrayFreight
    df['Miles'] = arrayMiles
    df['Origin City'] = arrayOrigins


def getOriginToDestinationCosts(df, distributionCities):

    cityDictionary = {}

    #get all the destinations as unique cities and loop through them to get a map of the origins
    for city in df['Dest City'].unique():

        destinationSubset = df.loc[df['Dest City'] == str(city)]

        #get best origin for that destination
        bestObject = getClosestOrigin(destinationSubset, distributionCities)

        #add best object for each destionation
        cityDictionary[city] = bestObject

    return cityDictionary



#get all origin to destination costs first.
destinationToBestOriginDictionary = originToDestinationCosts = getOriginToDestinationCosts(df,{'FT WAYNE':2.34,'ATLANTA':2.30,'RANCHO CUCAMONGA':2.33,'CARROLLTON':2.35})

#set destination and update the cost
updateAllInDestination(df, destinationToBestOriginDictionary)

print("after origin adjustment cost: " + str(df[" Freight Paid "].sum()))
print("after origin adjustment distance: " + str(df["Miles"].sum()))


for uniqueDate in df['Ship Date'].unique():
    consolidateTrucks(df, uniqueDate)

print("after consolidation cost: " + str(round(df[" Freight Paid "].sum(),2)))
print("after consolidation distance: " + str(df["Miles"].sum()))



#output to csv
#df.to_csv('updatedShipmentsFreightzeros.csv')


