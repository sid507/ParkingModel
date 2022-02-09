import pandas as pd
from xgboost import XGBRegressor
import datetime

def getCurrentTime():
  time = datetime.datetime.now().time()
  return f"{time.hour}:{time.minute}:{time.second}"

def convertToDataFrame(dataList,columnName):
    df = pd.DataFrame(dataList,columns=columnName)
    return df

def timeToSeconds(time_string):
  values = time_string.split(':')
  return int(values[0]) * 3600 + int(values[1]) * 60 + int(values[2])
  
def addMissingDay(startDate,endDate,exitdate,day,entryTime,exitTime):
    def handleMissingDay(row):
      if row['Day']==0:
        return row['ExitDate'].day_name().lower()
      else:
        return row['Day']

    # NOTE LOGIC:
    dateSeries = pd.date_range(startDate,endDate)
    row_test=[]
    for i in range(len(day)):
      row_test.append([exitdate[i],day[i],exitTime[i],entryTime[i]])
    
    s_df = pd.DataFrame(row_test,columns=['ExitDate','Day','Exit','Entry'])

    s_df= s_df.set_index('ExitDate').reindex(dateSeries).fillna(0).rename_axis('ExitDate').reset_index()
    s_df['Day']=s_df.apply(lambda row:handleMissingDay(row),axis=1)
    return s_df


def calculateMean(data2):
  weekdaysExitMean={}
  totalDayWeekly={}
  totalRow=data2.shape[0]
  for i in range(totalRow):
    if data2.iloc[i]['sec_exit']!=0:
      if data2.iloc[i]['Day'] in weekdaysExitMean:
        weekdaysExitMean[data2.iloc[i]['Day']]+=data2.iloc[i]['sec_exit']
        totalDayWeekly[data2.iloc[i]['Day']]+=1
      else:
        weekdaysExitMean[data2.iloc[i]['Day']]=data2.iloc[i]['sec_exit']
        totalDayWeekly[data2.iloc[i]['Day']]=1

  for day in totalDayWeekly:
    # if totalDayWeekly[day]>=3:
    weekdaysExitMean[day]=weekdaysExitMean[day]/totalDayWeekly[day]
  return weekdaysExitMean,totalDayWeekly


def calculateVariance(data2,totalDayWeekly,weekdaysExitMean):
  weekdayVariance={}
  totalRow=data2.shape[0]
  for i in range(totalRow):
    if data2.iloc[i]['sec_exit']!=0:
      day=data2.iloc[i]['Day']
      exit=data2.iloc[i]['sec_exit']
      if totalDayWeekly[day]>=3:
        if day in weekdayVariance:
          weekdayVariance[day]+=(pow(abs(weekdaysExitMean[day]-exit),1))
        else:
          weekdayVariance[day]=(pow(abs(weekdaysExitMean[day]-exit),1))
  for key in weekdayVariance:
    weekdayVariance[key]=weekdayVariance[key]/float(totalDayWeekly[key])
  return weekdayVariance

def checkIrregularity(data2):
    weekdaysExitMean,totalDayWeekly=calculateMean(data2)
    print(totalDayWeekly)
    return calculateVariance(data2,totalDayWeekly,weekdaysExitMean)

# It will train and predict the time 
# NOTE: Pass only regular data into it

def predict(data2,x_time,x_day):
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
      
    def secToTime(row):
      hr=(row//3600)
      minute=(row%3600)//60
      sec = (row%3600)%60
      return str(datetime.timedelta(seconds = row))

    # Convert the day into number
    def convertMe(row):
        
        day=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        return day.index(row['Day'])

    # Adding the proprocessed Data into dataframe
    data2['sec']=data2.apply(lambda row:dateToSec(row),axis=1)
    data2['sec_exit']=data2.apply(lambda row:dateToSec2(row),axis=1)
    data2['day2']=data2.apply(lambda row:convertMe(row),axis=1)
    day=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
#   Calculate variance of each day in week
    weeklyVariance = checkIrregularity(data2)

    print(weeklyVariance)
    # Creating data for training
    feature=['sec_exit','day2']
    label=['sec']
    # Taking all data leaving last data for test
    x_train=data2[feature][:-1]
    y_train=data2[label][:-1]
    # Prepare the test data
    x_test = pd.DataFrame([[x_time.hour * 3600 + x_time.minute * 60 + x_time.second,day.index(x_day)]],columns=feature)
    
#   Check the threshold for irregularity
    if day[x_test['day2'].iloc[0]] not in weeklyVariance or weeklyVariance[day[x_test['day2'].iloc[0]]]>=1000:
      return "Irregular Data"
    
    #Training the model
    reg = XGBRegressor(n_estimators=500, learning_rate=0.01)
    reg.fit(x_train, 
            y_train,
            eval_metric='mae')
    # eval_set=[(x_train, y_train),(x_test, y_test)],
    y_pred=reg.predict(x_test)
    print(secToTime(int(y_pred[0])))
    # Returning the R2 score
    return secToTime(int(y_pred[0]))

    
    