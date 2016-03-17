#update.py
#a test callback function for testing createvm.py
def updateProgress(rq, percent, message, *url):
        print("Current progress for " + rq + ": " + str(percent) + "%, " + message)