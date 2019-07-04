# coding=utf-8
import cv2
import cv2.cv as cv
import numpy as np
from collections import Counter

def peca_boa():
    def distance(one, other):
        return sum([(one[i] - other[i])**2 for i in range(len(one))]) ** 0.5

    captura = cv2.VideoCapture(0)
    n_observations = 50
    observations = []

    def nothing(x):
        pass
    # cv2.namedWindow('Video')
    # cv2.createTrackbar('1','Video',35,100,nothing)
    # cv2.createTrackbar('2','Video',40,100,nothing)
    # p1 = 35
    # p2 = 40
    for _ in range(n_observations):
    # while True:
        ret, img_original = captura.read()
        # print(img_original.shape)
        img_original = img_original[80:380, 100:540]
        cimg = cv2.resize(img_original, (0,0), fx=1, fy=1) 
        img = cv2.resize(img_original, (0,0), fx=1, fy=1) 
        img_original = cv2.resize(img_original, (0,0), fx=1, fy=1) 
        cimg = cv2.cvtColor(cimg,cv2.COLOR_BGR2GRAY)
        ret,cimg = cv2.threshold(cimg,127,255,cv2.THRESH_BINARY)

        circles = cv2.HoughCircles(cimg,cv.CV_HOUGH_GRADIENT,1,20,
                                    param1=60,param2=10,minRadius=3,maxRadius=40)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # draw the outer circle
                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
            # print(circles)
            observations.append(circles)


        cv2.imshow("Video", img)
        # p1 = cv2.getTrackbarPos('1','Video')
        # p2 = cv2.getTrackbarPos('2','Video')
        # cv2.imshow("Video2", cimg)


        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    # print(len(observations))
    most_common_len = Counter([len(arr[0]) for arr in observations]).most_common()[0][0]
    frequent_n_observations = [arr[0] for arr in observations if len(arr[0]) == most_common_len]

    sorted_frequent_n_observations = []
    for arr in frequent_n_observations:
        s = sorted(arr.tolist(), key=lambda d: distance(d, frequent_n_observations[0][0].tolist()))
        sorted_frequent_n_observations.append(s)

    circles_processed = []
    arr = np.array(sorted_frequent_n_observations)
    for i in range(most_common_len):
        circles_processed.append([arr[:, i, j].mean().tolist() for j in range(3)])


    circles = np.uint16(np.around(np.array(circles_processed)))
    for i in circles:
        # print(i)
        # draw the outer circle
        cv2.circle(img_original,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(img_original,(i[0],i[1]),2,(0,0,255),3)

    # while True:
    #     cv2.imshow('final', img_original)

    #     k = cv2.waitKey(30) & 0xff
    #     if k == 27:
    #         break
    cv2.imwrite('/home/feliciano/pi-19-1/pi_vi/static/img.jpg', img_original)
    captura.release()
    cv2.destroyAllWindows()


    tol = 7
    expected_circles = [[365, 107, 28], [274, 85, 10], [272, 197, 11]]
    if most_common_len == 3:
        for circle in circles_processed:
            if not any([np.allclose(circle, expected, atol=tol) for expected in expected_circles]):
                print('Visão: furos não correspondem às dimensões esperadas')
                return False
    else:
        print('Visão: peça não tem número de furos esperado')
        return False
    print('Visão: peça aprovada')
    return True
