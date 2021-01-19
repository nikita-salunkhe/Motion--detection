# importing library
import cv2
import time
import pandas
from datetime import datetime
import math



def find_centroid():
    frame_list =[38,300]
    vid_file_path = "ballmotionwhite.m4v"
   
    dict = {}
    cap = cv2.VideoCapture(vid_file_path)
    
    for i in frame_list:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i-1)
        _, frame_i = cap.read()
        gray_i = cv2.cvtColor(frame_i, cv2.COLOR_BGR2GRAY) 
        frame_name = "frame_{}".format(i)
        frame_file = "frame_{}.png".format(i)
        
        height, width = gray_i.shape
        thresh = 30
        
        blur = cv2.GaussianBlur(gray_i,(5,5),0)
        edges = cv2.Canny(blur,thresh,thresh*2)
        contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[1]
        cv2.drawContours(gray_i,contours,-1,(0,255,0),-1)

        M = cv2.moments(cnt)
        x = int(M['m10']/M['m00'])
        y = int(M['m01']/M['m00'])
        cv2.circle(frame_i,(x,y),1,(0,0,255),2)
        cv2.putText(frame_i,"center of ball", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 5)
        cv2.circle(frame_i ,(int(width/2),int(height/2)),1,(255,0,0),2)
        cv2.imshow(frame_name ,frame_i)
        cv2.imwrite(frame_file,frame_i)
       
        list_i = []
        print("location of "+ str(i)+ " th frame: " , end ="  ")
        print(x, y)
        list_i.append(x)
        list_i.append(y)
        dict[i] = list_i
        
      
        
    return dict
     


def find_velocity(dict, interval_seconds):

    sx= (dict[300][0] - dict[38][0])
    sy= (dict[300][1] - dict[38][1])
    vx= (sx*2.54/96)/interval_seconds
    vy = (sy*2.54/96)/interval_seconds
    print("velocity vector of ball: ", end =" ")
    print(str(vx)+"i"+ " + " + str(vy) +"j ")
    print("velocity of ball: ", end =" ")
    print(math.sqrt(vx*vx + vy*vy), end =" ")
    print("cm/sec")
    print("=================================================")
    
    #using euclidean formula
    #a= math.sqrt(((dict[100][0]- dict[38][0])*(dict[100][0]- dict[38][0])) +  ((dict[100][1]- dict[38][1])*(dict[100][1]- dict[38][1])))
    #print(a/interval_seconds)
    return 0


if __name__ == '__main__':
    print('\n============================================')
    
    #initializing parameters
    #Time of movement /motion
    time = []
    #frame wise timing
    time_start_frame=[]
    time_end_frame=[]
    
    # Assigning our static_back to None
    static_back = None
    motion_list = [ None, None ]
    frame_count = 1
   
    
    
     # Initializing DataFrame
     #dataframe for motion start and end
    df = pandas.DataFrame(columns = ["motion_Start", "motion_End"])
 
    # Initializing DataFrame, one column is frame_number, second  start_time
    # and third  is end time
    time_of_frame = pandas.DataFrame(columns = ["frame", "start_time", "end_time"])
    

    # read video
    cap = cv2.VideoCapture("ballmotionwhite.m4v")
    

    
    while (frame_count < int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
       check, frame = cap.read()
       

       
       #append start time of every frame
       time_start_frame.append(datetime.now())
       
       # Initializing motion = 0(no motion)    
       motion=0

       # Converting color image to gray_scale image
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

       # Converting gray scale image to GaussianBlur
       # so that change can be find easily
       gray = cv2.GaussianBlur(gray, (21, 21), 0)

       # In first iteration we assign the value
       # of static_back to our first frame
       if static_back is None:
           static_back = gray
           
           continue

       # Difference between static background
       # and current frame(which is GaussianBlur)
       diff_frame = cv2.absdiff(static_back, gray)

       #applying thresholding over the video values above 30 gets 255 value 
       thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
       thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

       # Finding contour of moving object
       cnts,_  = cv2.findContours(thresh_frame.copy(),
                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

       for contour in cnts:
           if cv2.contourArea(contour) < 10000:        
               continue       
           motion=1

           

           (x, y, w, h) = cv2.boundingRect(contour)
           # making green rectangle arround the moving object
           cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

   
      
       #display difference frame
       cv2.imshow("Difference Frame", diff_frame)

       #display thresholding
       cv2.imshow("Threshold Frame", thresh_frame)

       # Displaying color frame with contour of motion of object
       cv2.imshow("Color Frame", frame)    
       # Appending status of motion
       motion_list.append(motion)
       

       motion_list = motion_list[-2:]

      # Appending Start time of motion
       if motion_list[-1] == 1 and motion_list[-2] == 0:
            time.append(datetime.now())
            
            frame_count_excel=frame_count
            print("frame no. when motion starts", end =":")
            print(frame_count)
            
            print("start time of frame 38 : ", end ="")
            print(datetime.now())
            
          

     # Appending End time of motion
       if motion_list[-1] == 0 and motion_list[-2] == 1:
            time.append(datetime.now())
           
           
       
       key = cv2.waitKey(1)
       # if q entered whole process will qstop
       if key == ord('q'):
      # if something is movingthen it append the end time of movement
          if motion == 1:
              time.append(datetime.now())
          break
       time_end_frame.append(datetime.now())
       frame_count = frame_count+1
       
    
    print("number of frames when motion ends", end =" : ")
    print(frame_count)
 
    
    # Appending time of motion in DataFrame
    for i in range(0, len(time), 2):
        df = df.append({"motion_Start":time[i], "motion_End":time[i + 1]}, ignore_index = True)

   

    # Creating a csv file in which time of movements will be saved
    df.to_csv("Time_of_movements.csv")
    # Appending time of motion in DataFrame    
    for k in range(0, frame_count-1, 1):
         time_of_frame= time_of_frame.append({"frame": k+1, "start_time": time_start_frame[k], "end_time": time_end_frame[k]}, ignore_index = True)

    
    # Creating a csv file in which time of movements will be saved
    time_of_frame.to_csv("Time_of_frames.csv")
    print("start time  of 300 th frame", end= ":")
    print(time_start_frame[299])
    
    print("time_interval between 38 and 400 th frame ", end =":")
    time_interval =time_start_frame[299]- time[0]
    #print(time_interval)
    interval_seconds = time_interval.total_seconds()
    print(str(interval_seconds) +" sec")
    
    
    dict ={}
    print("\n")
    dict = find_centroid()
    print("\n")
    find_velocity(dict, interval_seconds)
    key= cv2.waitKey(0)
    cap.release()
    # Destroying all the windows
    cv2.destroyAllWindows()
      
   

    
    
