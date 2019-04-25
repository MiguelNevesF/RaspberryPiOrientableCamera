import sys
import json
import requests 
import time
import datetime
import serial
import qrcode 
from picamera import PiCamera 
import Tkinter
from PIL import Image, ImageTk
tkinter = Tkinter
import warnings 
import serial.tools.list_ports

#-------arduino set up-------
arduino_ports=[
    p.device
    for p in serial.tools.list_ports.comports()
]
if not arduino_ports:
    raise IOError("No Arduino found")

elif len(arduino_ports)>1:
    warnings.warn("Multiple Arduinos found-using the first one")

elif len(arduino_ports)==1:
    ard=serial.Serial(arduino_ports[0],9600,timeout=5)
    


#--------web set up----------
webdatafile=open('webdata.txt','r')
webdata= json.loads(webdatafile.read())
baseurl=webdata['baseurl']
userinterface=webdata['userinterface']
deviceid=webdata['deviceid']
gloval=webdata['gloval']
webdatafile.close()
gtokenurl= baseurl + "gettoken.php"
registree = {'deviceid':deviceid,
        'global':gloval}
camera= PiCamera()



#-----define functions-------

# setup for html communications
def register(registree) :
    regurl= baseurl + "register.php"
    reg= requests.post(regurl,data=registree)

# passes forward the position of the servos to the Arduino
def talkard(az,el):

    ard.write(str(az))
    ard.write(",")
    ard.write(str(el))
    ard.write(";")
    ard.flush()
    ans=ard.readline()
    ans =ard.readline()
    

# gets a command from the webpage
def getcmnd(registree):
    cmndurl= baseurl + "getcmd.php"
    cmnd=requests.post(cmndurl, data =registree)
    jsnd_cmnd= json.loads(cmnd.text)
    stat=jsnd_cmnd["code"]
    command=jsnd_cmnd["contents"]
    az=command["az"]
    el= command["el"]
    ts= command ["ts"]
    return {'status': stat,
        'azimuth': az,
        'elevacion':el,
        'time':ts}

# post the image and the servo's current position

def post(registree,az,el):
    post=registree.copy();
    post['az']=az
    post['el']=el
    files={'image': open('camera.jpg','rb')}
    resulturl= baseurl+"postresult.php"
    result=requests.post(resulturl,data=post,files=files)
    return result

# digest the timestamp to it can be compared with the old one

def newtimestamp(result):
    jsndresult=json.loads(result.text)
    contents=jsndresult['contents']
    return contents['tstamp']

# setup to show the QR

def showPIL(pilImage):
    root= tkinter.Tk()
    w,h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w,h))
    root.focus_set()
    root.bind("<Button>", lambda e : e.widget.quit())
    canvas= tkinter.Canvas (root, width=w, height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight= pilImage.size
    if imgWidth > w or imgHeight>h:
        ratio= min (w/imgWidth, h/imgHeight)
        imgWidth= int (imgWidth*ratio) 
        imgHeight= int (imgHeight*ratio) 
        pilImage= pilImage.resize((imgWidth,imgHeight),Image.ANTIALIAS)
    image=ImageTk.PhotoImage(pilImage)
    imagesprite= canvas.create_image(w/2,h/2, image=image)
    root.mainloop()
    root.destroy()

#shows the QR
def showqr(registree): 
    gtoken= requests.post(gtokenurl,data=registree)
    jsnd_gtoken= json.loads(gtoken.text)
    token=jsnd_gtoken["contents"]["token"]
    img=qrcode.make(userinterface + token)
    img.save("test.png")
    pilImage = Image.open("test.png")
    showPIL(pilImage)

#picture

def takepic(camera):
    camera.capture("camera.jpg")


#------------Main Program--------------
showqr(registree)
while(True):
    
    prevdate=open("date","r")
    tsold=datetime.datetime.strptime(prevdate.read(), "%Y-%m-%d %H:%M:%S")
    prevdate.close()
    data= getcmnd(registree)
    ts =data['time']
    tsnew= datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    print("Requesting...")


    if (tsnew>tsold):

        
        az =data['azimuth']
        el =data['elevacion']
        talkard(str(az),str(el))
        time.sleep(1)
        takepic(camera)
        result=post(registree, az,el)   
        time.sleep(5)
        f=open("date","w")
        f.write(newtimestamp(result))
        f.close()
        print(result.text)
        print(tsold)
        print(tsnew)
        print(az)
        print(el)

    else:
        print("Nothing new...")
    
    time.sleep(5)
  
    



    
    
