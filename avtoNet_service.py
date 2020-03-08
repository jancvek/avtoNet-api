import avtoNet
from datetime import datetime,timedelta

today = datetime.now()
today2 = today - timedelta(minutes=60)
dt_string = today2.strftime("%Y-%m-%d %H:%M:%S")

avtoNet.searchNewCars()
avtoNet.notifyByEmail(dt_string)