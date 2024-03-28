from pytube import YouTube
import os
import cv2
import pandas as pd
import csv

import utils


#url을 전달하면 유투브에서 해당 비디오를 추출하여 저장한다
#return으로 저장한 비디오들의 경로 리스트를 반환한다.
def download_data(url_list, path):
    VIDEO_SAVE_PATH = path
    # 다운로드할 유튜브 링크 리스트
    youtube_url_links = url_list
    #videos_dir = []#저장된 비디오드르이 디렉토리를 저장할 리스트

    #유투브 다운로드할 비디오들을 저장할 디렉토리가 있는지 확인. 없다면 생성
    if os.path.isdir(VIDEO_SAVE_PATH): 
        print('directory exist!')
    else:
        print("다운받은 비디오를 저장할 디렉토리가 없습니다.")
        print("디렉토리를 만듭니다.")
        os.mkdir(VIDEO_SAVE_PATH)
        print(f"{VIDEO_SAVE_PATH} 디렉토리 생성 성공")
        
    #유튜브 다운로드
    for link, i in zip(youtube_url_links, range(len(youtube_url_links))):
        yt = YouTube(link)  
        try:
            yt.streams.filter(progressive = True, file_extension = "mp4").first().download(output_path = VIDEO_SAVE_PATH, filename = "video"+str(i+1)+".avi")
            print("Download Success : ", link)
        except:
            print("Some Error!")
    return

def get_franme_from_youtube_video(YOUTUBE_DOWNLOAD_PATH, FRAME_SAVE_PATH, min):
    for i in range(10):
        VIDEO_PATH = os.path.join(YOUTUBE_DOWNLOAD_PATH,'video'+str(i+1)+'.avi')
        print(VIDEO_PATH)

        video = cv2.VideoCapture(VIDEO_PATH)
        fps = video.get(cv2.CAP_PROP_FPS)

        if not video.isOpened():
            print("could not open :",VIDEO_PATH)
        else:
             #비디오를 일정 시간으로 나눠서 플레임별로 저장
            cnt = 1
            while(video.isOpened()):
                ret, frame = video.read()
                if not ret:
                    print("다음 영상 프레임 추출 시작\n")
                    break
                if(int(video.get(1)) % (fps*min*60) == 0): #앞서 불러온 fps 값을 사용하여 1분마다 추출
                    FRAME_NAME = 'frame'+str(i+1)+'_'+str(cnt)+'.jpg'
                    FRAME_PATH = os.path.join(FRAME_SAVE_PATH,FRAME_NAME)
                    #저장되는 프레임의 사이즈를  (360,640,3)으로 resize
                    resize_frame = cv2.resize(frame, dsize=(640,360), interpolation=cv2.INTER_LINEAR)
                    utils._imwrite(FRAME_PATH, resize_frame)
                    print('Saved frame number :', str(int(video.get(1))), '  ',FRAME_NAME)
                    cnt += 1
            print(i," 개의 frame 추출")
            video.release()
    return


def make_CSV_file(CSV_PATH):
    fields = ['frame_path', 'points', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8']

    #파일이 이미 존재한다면 삭제하고 다시 생성
    if os.path.isfile(CSV_PATH):
        os.remove(CSV_PATH)
        with open(CSV_PATH, 'a', newline="") as csvfile: 
            csvwriter = csv.writer(csvfile) 
            csvwriter.writerow(fields)
    #파일이 존재하지 않는다면 그냥 바로 생성
    else:                       
        with open(CSV_PATH, 'a', newline="") as csvfile: 
            csvwriter = csv.writer(csvfile) 
            csvwriter.writerow(fields) 
    return

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:#왼쪽 마우스 클릭
        print(x, y)
        points.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN: #오른쪽 마우스 클릭
        points.append((None, None))
        print('(None, None)')
    elif event == cv2.EVENT_MBUTTONDOWN: #가운데 마우스 클릭
        points.pop()
        print('pop')
    
def get_point(CSV_PATH, FRAME_PATH):
    #csv파일 생성
    make_CSV_file(CSV_PATH)
        
    #포인트를 추출할 프레임 지정
    frame_list = os.listdir(FRAME_PATH)
    full_frame_path_list = []
    for list in frame_list:
        full_frame_path = os.path.join(FRAME_PATH,list)
        full_frame_path_list.append(full_frame_path)

    for list in full_frame_path_list:
        global points
        points = []

        frame = utils._imread(list)
        cv2.namedWindow("image")
        cv2.imshow("image", frame)
        cv2.setMouseCallback("image", mouse_callback)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        with open(CSV_PATH, 'a', newline="") as csvfile:   
            csvwriter = csv.writer(csvfile) 
            # writing the fields
            try:
                csvwriter.writerow([list, points, points[0], points[1], points[2], points[3], points[4], points[5], points[6], points[7]]) 
            except:
                print('not enough point data')
        print(points)
        print('show next frame\n')
    return
