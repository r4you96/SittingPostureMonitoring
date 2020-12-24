from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime
import ctypes
import pygame
import math
import numpy as np
import joblib
import PykinectRealTime.communication_module as cm
import json

# colors for drawing different bodies
class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()
        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()
        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1),
                                               pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)
        pygame.display.set_caption("Kinect for Profer Sitting")

        # Loop until the user clicks the close button.
        self._done = False
        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()
        # Kinect runtime object, we want only color and body frames
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_Depth)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data
        self._bodies = None

        self.SKELETON_COLORS = [pygame.color.THECOLORS["red"],
                           pygame.color.THECOLORS["blue"],
                           pygame.color.THECOLORS["green"],
                           pygame.color.THECOLORS["orange"],
                           pygame.color.THECOLORS["purple"],
                           pygame.color.THECOLORS["yellow"],
                           pygame.color.THECOLORS["violet"]]

        #키넥트에서 인식하는 관절의 리스트
        self.kinect_jointType = [PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck,
                            PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft,
                            PyKinectV2.JointType_ShoulderRight,
                            PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase,
                            PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight,
                            PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft,
                            PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_HipRight,
                            PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight,
                            PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft
                            ]
        #분류에 활용할 관절 리스트
        self.ccw_jointType = [PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck,
                         PyKinectV2.JointType_SpineShoulder,
                         PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase,
                         PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_HipRight,
                         PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_KneeRight,
                         PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_AnkleRight
                         ]
        self.type = 1
        self.model = joblib.load('saved_model.pkl')

        self.server = cm.server_class()

    #관절과 관절을 잇는 선을 그리는 메소드
    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State is PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return

        # ok, at least one is good
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
        except:  # need to catch it due to possible invalid positions (with inf)
            pass

    #연결 되는 관절의 쌍들을 순차적으로 그려주는 메소드
    def draw_body(self, joints, jointPoints, color):
        draw_sequence = [(PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck), (PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder),
                         (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid),(PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase),
                         (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight),(PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft),
                         (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight),(PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft),
                         (PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight), (PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight),
                         (PyKinectV2.JointType_ShoulderLeft,PyKinectV2.JointType_ElbowLeft), (PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft),
                         (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight), (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight),
                         (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft),(PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)]

        for drawing_bone in draw_sequence :
            self.draw_body_bone(joints, jointPoints, color, drawing_bone[0], drawing_bone[1])

    #관절 번호 붙이기
    def writing_joint(self, joints, jointPoints):
        game_font = pygame.font.Font(None, 40)
        joint_num_array = []
        joint_tracked_check = []
        joint_num = 0
        for joint_type in self.ccw_jointType :
            joint_num = joint_num + 1

            # both joints are not tracked / both joints are not *really* tracked
            joint_state = joints[joint_type].TrackingState;
            if joint_state == PyKinectV2.TrackingState_NotTracked or joint_state == PyKinectV2.TrackingState_Inferred:
                joint_tracked_check.append(0)
                continue
            else :
                joint_tracked_check.append(1)

            #화면크기 변화에 따른 리스케일링
            pos = (round(jointPoints[joint_type].x * ( 960.0/ 1920.0)), round(jointPoints[joint_type].y * (540.0 / 1080.0)))
            joint_str = game_font.render(str(joint_num), True, (255, 255, 255))
            joint_num_array.append([joint_str, pos])

        return joint_num_array, joint_tracked_check

    # 관절의 3차원 좌표를 얻어내는 메소드
    def get_depth(self, joints):
        depth_array = []

        depth_points = self._kinect.body_joints_to_depth_space(joints)
        if self._kinect.has_new_depth_frame():
            self._depth = self._kinect.get_last_depth_frame() #마지막 깊이 프레임 추출

        for joint_type in self.ccw_jointType :
            jointState = joints[joint_type].TrackingState; #현재 좌표값을 알고자 하는 관절이 추적 되었는가
            if (jointState == PyKinectV2.TrackingState_NotTracked) or (jointState == PyKinectV2.TrackingState_Inferred): #추적되지 않았다면, ,0,0,0 추가
                depth_array.append([0,0,0])
                continue

            x = round(depth_points[joint_type].x)
            y = round(depth_points[joint_type].y)
            z = self._depth[y * 512 + x] / 10
            # print(self._depth[round(y) * 512 + round(x)])

            depth_array.append([x,y,z])

        return depth_array
    #관절 간의 거리를 계산
    def get_distance(self, one, two):
        for pos in one :
            if pos == 0 :
                return 0

        for pos in one :
            if pos == 0:
                return 0

        return math.sqrt(pow(one[0] - two[0], 2) + pow(one[1] - two[1], 2) + pow(one[2] - two[2], 2))

    #현재 관절 길이를 정규화 하고 이를 모델에 입력하여 현재 자세를 분류
    def get_datas(self, depth_array):
        #경추와 미추의 거리를 구해 정규화에 활용
        spine_length = self.get_distance(depth_array[2], depth_array[4])
        distance_ratio = spine_length/70

        data_array = []
        print(depth_array)
        for element in depth_array:
            for data in element :
                data_array.append(data)

        for i in range(0,9) :
            for j in range(i+1,9):
                distance = self.get_distance(depth_array[i], depth_array[j])/distance_ratio
                data_array.append(distance)

        print(data)
        list = []
        list.append(data_array[33:70])
        data = np.array(list)

        result = int(self.model.predict(data)[0])
        print(result)
        return result

    #화면을 다시 그려주기 위한 메소드
    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def skeletal_tracking(self):
        # -------- Main Program Loop -----------
        result = 0
        tracking_num = 0

        game_font = pygame.font.Font(None, 150)
        while not self._done:
            tracking_num = tracking_num + 1
            joints = None
            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self._done = True  # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE:  # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'],
                                                           pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)
            # --- Game logic should go here
            # --- Getting frames and drawing
            # --- Woohoo! We've got a color frame! Let's fill out back buffer surface with frame's data
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame()

            # --- draw skeletons to _frame_surface
            if self._bodies is not None:
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked:
                        continue
                    joints = body.joints
                    # convert joint coordinates to color space
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.draw_body(joints, joint_points, self.SKELETON_COLORS[i])
                    joint_num_array, joint_tracked_check = self.writing_joint(joints, joint_points)

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) pre 1920x1080 / now 960x540
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0, 0))

            #60프레임에 한번씩 자세 분류
            try :
                if tracking_num == 60 :
                    tracking_num = 0
                    if joints is not None :
                        depth_array = self.get_depth(joints)
                        result = self.get_datas(depth_array)

            except Exception as e:
                print(e)

            self._screen.blit(game_font.render(str(result), True, (255, 255, 255)), (0,0)) #현재 자세 번호

            #서버와 연결되어 있다면 현재 자세를 소켓통신으로 전송
            if self.server.ch != None :
                dict = {'msg_type' : 'sitting_posture', 'msg_content' : result-1}
                self.server.ch.sock.sendall(json.dumps(dict).encode('utf-8'))

            surface_to_draw = None
            pygame.display.update()
            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
            # --- Limit to 60 frames per second
            self._clock.tick(60)
        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()


if __name__ == '__main__':
    game = BodyGameRuntime();

    game.skeletal_tracking()