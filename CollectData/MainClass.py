import get_data as gd
from pykinect import communication_module as cm
import threading
import time
class main_class:
    def __init__(self, kinect_class, server):
        self.kinect_class =  kinect_class
        self.server = server
        self.handler = threading.Thread(target=self.run, args=())
        self.handler.start()
        self.kinect_class.skeletal_tracking()

    def run(self):
        while True:
            # 클라이언트 목록을 향상된 for문으로 참조합니다.
            for c in self.server.client_handler_list:
                # 만일 해당 클라이언트의 리퀘스트가 NO REQUEST가 아니라면
                if c.request != cm.order_enum.NO_REQUEST:
                    try:
                        if c.request == cm.order_enum.CAPTURE:
                            self.kinect_class.flag = gd.kinect_flag.capture
                        elif c.request == cm.order_enum.SAVING:
                            self.kinect_class.type = int(c.recv_msg.get('msg_content'))
                            self.kinect_class.flag = gd.kinect_flag.saving
                        elif c.request == cm.order_enum.ONGOING:
                            self.kinect_class.flag = gd.kinect_flag.ongoing
                        elif c.request == cm.order_enum.CLOSING:
                            self.kinect_class.flag = gd.kinect_flag.capture
                            self.kinect_class._done = True
                        else:
                            print("unknown request :" + c.request)
                    except Exception as e:
                        c.error_msg = str(e)
                        print(c.error_msg)
                    finally:
                        c.request = cm.order_enum.NO_REQUEST
            time.sleep(0.01)
        # end of while loop
        #clear_all(self.db, self.server)

def main():
    kinect_class = gd.BodyGameRuntime()
    server = cm.server_class()
    main_class(kinect_class = kinect_class, server = server)

if __name__ == '__main__':
    main()