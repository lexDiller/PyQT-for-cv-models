from app import EasyocrQT, YOLOwithQT


# rtsp_url = "http://10.11.254.101:8080/video"
# language = 'ru'
#
# EasyocrQT(rtsp_url, language)


video = "rtsp://operator:Ukfp77Ltvjyf@10.14.4.248/video"
model = '/home/user/Загрузки/license_plate_detector.pt'
YOLOwithQT(video, model, verbose=False, conf=0.5)