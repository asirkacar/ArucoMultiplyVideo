import cv2
import cv2.aruco as aruco
import numpy as np

# ArUco işaretçileri için tanımlayıcılar ve ilişkili videoları içeren bir veritabanı
database = {
    0: "isaretciVideo/23.mp4",
    1: "isaretciVideo/40.mp4",
    2: "isaretciVideo/62.mp4"
}

# ArUco işaretçileri için video oynatıcıları içeren bir sözlük
video_players = {}

# ArUco işaretçileri için ArUco özellikleri
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

# Kamera için video yakalama nesnesi
url = 'https://192.168.0.43:8080/video'
cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()

    # ArUco işaretçilerini algıla
    corners, ids, _ = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    print(corners)

    if ids is not None:
        for i in range(len(ids)):
            id = ids[i][0]

            if id in database:
                if id not in video_players:
                    # İşaretçi veritabanında bulunuyorsa ve daha önce video oynatılmamışsa, ilgili videoyu oynatıcıya yükle
                    video_path = database[id]
                    video_player = cv2.VideoCapture(video_path)
                    video_players[id] = video_player
                else:
                    video_player = video_players[id]

                # Videonun sonraki karesini al
                ret, video_frame = video_player.read()

                if ret:
                    # İşaretçinin köşe noktalarını al
                    marker_corners = corners[i][0]

                    # Videonun boyutunu al
                    video_height, video_width, _ = video_frame.shape

                    # İşaretçinin dört köşesini kullanarak dönüş dönüşüm matrisini hesaplayın
                    transform_matrix, _ = cv2.findHomography(np.float32([[0, 0], [video_width, 0], [video_width, video_height], [0, video_height]]),
                                                             np.float32(marker_corners))

                    # Videonun perspektifini işaretçiye uygulayın
                    warped_frame = cv2.warpPerspective(video_frame, transform_matrix, (frame.shape[1], frame.shape[0]))

                    cornersa = np.array([corners])

                    cv2.fillConvexPoly(frame, marker_corners.astype(int), (0, 0, 0))

                    # İşaretçinin üzerine videonun perspektifini yerleştir
                    frame = cv2.add(frame, warped_frame)

        # İşaretçileri çerçevelere çiz
        frame = aruco.drawDetectedMarkers(frame, corners, ids)


    cv2.imshow("AR Marker Detection", frame)

    # 'q' tuşuna basıldığında döngüyü kır
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break