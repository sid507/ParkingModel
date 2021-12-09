import pandas as pd
from xgboost import XGBRegressor

def convertToDataFrame(dataList,columnName):
    df = pd.DataFrame(dataList,columns=columnName)
    return df

def addMissingDay(day,entryTime,exitTime):
    # NOTE LOGIC:
    # Iterate the day(parameter) and if it is not equal to previous day then append 0 
    seq = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    row=[]
    n=len(day)
    for i in range(n):
        if i==0:
            row.append([day[i],entryTime[i],exitTime[i]])
        else:
            if seq[(seq.index(row[-1][0])+1)%7]==day[i]:
                row.append([day[i],entryTime[i],exitTime[i]])
            else:
                while seq[(seq.index(row[-1][0])+1)%7]!=day[i]:
                    row.append([seq[(seq.index(row[-1][0])+1)%7],0,0])
                row.append([day[i],entryTime[i],exitTime[i]])
    return row




# It will train and predict the time 
# NOTE: Pass only regular data into it

def predict(data2):
    # Convert EntryTime to sec
    def dateToSec(row):
        if row['Entry']==0:
            return 0
        return row['Entry'].hour * 3600 + row['Entry'].minute * 60 + row['Entry'].second
    # Convert ExitTime to sec
    def dateToSec2(row):
        if row['Exit']==0:
            return 0
        return row['Exit'].hour * 3600 + row['Exit'].minute * 60 + row['Exit'].second

    # Convert the day into number
    def convertMe(row):

        day=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        return day.index(row['Day'])

    # Adding the proprocessed Data into dataframe
    data2['sec']=data2.apply(lambda row:dateToSec(row),axis=1)
    data2['sec_exit']=data2.apply(lambda row:dateToSec2(row),axis=1)
    data2['day2']=data2.apply(lambda row:convertMe(row),axis=1)

    # Creating data for training
    feature=['sec_exit','day2']
    label=['sec']
    # Taking all data leaving last data for test
    x_train=data2[feature][:-1]
    y_train=data2[label][:-1]
    # Taking last data
    x_test=data2[feature][-1:]
    y_test=data2[label][-1:]

    #Training the model
    reg = XGBRegressor(n_estimators=500, learning_rate=0.01)
    reg.fit(x_train, 
            y_train,
            eval_set=[(x_train, y_train), (x_test, y_test)],
            eval_metric='mae')
    y_pred=reg.predict(x_test)
    print(y_test)
    print(y_pred)
    # Returning the R2 score
    return str(reg.score(x_train,y_train))

    
