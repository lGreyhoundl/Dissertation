from flask import Flask, Response, render_template
import cv2

app = Flask(__name__)

def generate_frames():
    camera = cv2.VideoCapture(0)  # 0은 일반적으로 시스템의 기본 카메라를 가리킵니다.
    
    while True:
        success, frame = camera.read()  # 카메라로부터 현재 프레임을 읽음
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)  # 프레임을 JPEG 형식으로 인코딩
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # 컨텐츠 타입과 함께 프레임 데이터를 전송

@app.route('/')
def index():
    # 'index.html' 템플릿을 렌더링합니다. 이 HTML 파일은 아래에 설명되어 있습니다.
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # 비디오 스트리밍 경로
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
