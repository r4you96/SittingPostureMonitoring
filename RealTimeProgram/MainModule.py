import PykinectRealTime.communication_module as cm
import threading
import time
import json

class module_communicator:
    def __init__(self, server):
        self.server = server
        self.handler = threading.Thread(target=self.run, args=())
        self.handler.start()
        self.send_sitting_threads = threading.Thread(target=self.send_sitting_thread, args=())
        self.send_sitting_threads.start()

    def run(self):
        # 무한 루프로 돌려버립니다.
        while True:
            # 클라이언트 목록을 향상된 for문으로 참조합니다.
            for c in self.server.client_handler_list:
                # 만일 해당 클라이언트의 리퀘스트가 NO REQUEST가 아니라면
                if c.request != cm.order_enum.NO_REQUEST:
                    try:
                        if c.request == cm.order_enum.JUST_MESSAGE:
                            content = c.recv_msg.get('msg_content')
                            print(content)
                            self.just_message(content)
                        elif c.request == cm.order_enum.EXCUTE_QUERY:
                            content = c.recv_msg.get('msg_content')
                            self.db.excute_query(content)
                        elif c.request == cm.order_enum.LIST_REQUEST:
                            self.list_request(c)
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

    def send_sitting_thread(self):
        while True :
            for i in range(0,5):
                self.send_sitting_posture(i)
                time.sleep(1)


    def send_sitting_posture(self, sit_num):
        sit_message = {'msg_type' : 'sitting_posture', 'msg_content' : sit_num}
        sit_message = json.dumps(sit_message).encode('utf-8')

        for c in self.server.client_handler_list:
            c.sock.sendall(sit_message)


    def just_message(self, content):
        print(content)

# end of funtion
# end of class
def clear_all(server, db):  # video stream will be terminated automatically
    server.clear()
    db.clear()

def main():
    server = cm.server_class()
    module_communicator( server = server)

if __name__ == "__main__":
    main()
