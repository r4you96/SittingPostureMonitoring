from itertools import count
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from enum import Enum
import ctypes
import _ctypes
import pygame
import sys
import math
import threading
import time
class kinect_flag(Enum) :
    ongoing = 1
    capture = 2
    saving = 3
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
        pygame.display.set_caption("Kinect for Windows v2 Body Game")

        # Loop until the user clicks the close button.
        self._done = False

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Kinect runtime object, we want only color and body frames
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_Depth)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface(
            (self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data
        self._bodies = None

        self.SKELETON_COLORS = [pygame.color.THECOLORS["red"],
                           pygame.color.THECOLORS["blue"],
                           pygame.color.THECOLORS["green"],
                           pygame.color.THECOLORS["orange"],
                           pygame.color.THECOLORS["purple"],
                           pygame.color.THECOLORS["yellow"],
                           pygame.color.THECOLORS["violet"]]

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
        self.ccw_jointType = [PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck,
                         PyKinectV2.JointType_SpineShoulder,
                         PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase,
                         PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_HipRight,
                         PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_KneeRight,
                         PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_AnkleRight
                         ]

        self.flag = kinect_flag.ongoing
        self.file = open("C:\\Users\\Choi CheolWoo\\Downloads\\get_skeletal.csv", 'a')
        self.type = 1


    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
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

    def get_depth(self, joints):
        data_str = ""
        acos_sequence = [(PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck),
                         (PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder),
                         (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid),
                         (PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase),
                         (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight),
                         (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft),
                         (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight),
                         (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight),
                         (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft),
                         (PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)]

        depth_points = self._kinect.body_joints_to_depth_space(joints)
        if self._kinect.has_new_depth_frame():
            self._depth = self._kinect.get_last_depth_frame() #마지막 깊이 프레임 추출

        for joint_type in self.ccw_jointType :
            jointState = joints[joint_type].TrackingState; #현재 좌표값을 알고자 하는 관절이 추적 되었는가
            if (jointState == PyKinectV2.TrackingState_NotTracked) or (jointState == PyKinectV2.TrackingState_Inferred): #추적되지 않았다면, ,0,0,0 추가
                data_str = data_str + ",0,0,0"
                continue

            x = round(depth_points[joint_type].x)
            y = round(depth_points[joint_type].y)
            z = self._depth[y * 512 + x]
            # print(self._depth[round(y) * 512 + round(x)])
            data_str = data_str + ','+ str(x)+',' + str(y)+',' + str(z)


        for joint_couple in acos_sequence :
            one = []
            two = []

            joint0State = joints[joint_couple[0]].TrackingState;  # 현재 각도값을 알고자 하는 0번 관절이 추적 되었는가
            joint1State = joints[joint_couple[1]].TrackingState;  # 현재 각도값을 알고자 하는 1번 관절이 추적 되었는가
            if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint0State == PyKinectV2.TrackingState_Inferred):  # 추적되지 않았다면, ,0,0,0 추가
                data_str = data_str + ',' + str(0)
                continue
            if (joint1State == PyKinectV2.TrackingState_NotTracked) or ( joint1State == PyKinectV2.TrackingState_Inferred):  # 추적되지 않았다면, ,0,0,0 추가
                data_str = data_str + ',' + str(0)
                continue

            x = depth_points[joint_couple[0]].x
            y = depth_points[joint_couple[0]].y
            z = self._depth[round(y) * 512 + round(x)]

            one.append(x)
            one.append(y)
            one.append(z)

            x = depth_points[joint_couple[1]].x
            y = depth_points[joint_couple[1]].y
            z = self._depth[round(y) * 512 + round(x)]

            two.append(x)
            two.append(y)
            two.append(z)

            # print(self._depth[round(y) * 512 + round(x)])
            data_str = data_str + ',' + str(self.get_angle(one, two))

        return data_str

    def get_angle(self, one, two):
        #[a,b,c] 와 [d,e,f] 라고 가정
        molecular = one[0]*two[0] + one[1]*two[1] + one[2]*two[2]
        denominator = math.sqrt(one[0]*one[0] + one[1]*one[1] + one[2]*one[2]) * math.sqrt(two[0]*two[0] + two[1]*two[1] + two[2]*two[0])
        print(one)
        print(two)
        print(molecular)
        print(denominator)
        print(molecular/denominator)

        return math.acos(float(molecular)/float(denominator))

    def draw_body(self, joints, jointPoints, color):
        draw_sequence = [(PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck), (JointType_Neck, PyKinectV2.JointType_SpineShoulder),
                         (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid),(PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase),
                         (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight),(PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft),
                         (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight),(PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft),
                         (PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight), (PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight),
                         (PyKinectV2.JointType_ShoulderLeft,PyKinectV2.JointType_ElbowLeft), (PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft),
                         (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight), (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight),
                         (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft),(PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)]

        for drawing_bone in draw_sequence :
            self.draw_body_bone(joints, jointPoints, color, drawing_bone[0], drawing_bone[1])

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def check_joint(self, joint_check):
        if len(joint_check) <11 :
            return

        game_font = pygame.font.Font(None, 40)
        joint_num = 0
        kinect_jointType_str = ["PyKinectV2.JointType_Head", "PyKinectV2.JointType_Neck",
                                 "PyKinectV2.JointType_SpineShoulder",
                                 "PyKinectV2.JointType_SpineMid", "PyKinectV2.JointType_SpineBase",
                                 "PyKinectV2.JointType_HipLeft", "PyKinectV2.JointType_HipRight",
                                 "PyKinectV2.JointType_KneeRight", "PyKinectV2.JointType_AnkleRight",
                                 "PyKinectV2.JointType_KneeLeft", "PyKinectV2.JointType_AnkleLeft"
                                 ]
        joint_str = game_font.render(str(joint_num), True, (255, 255, 255))
        for strs in joint_check:
            if strs == 0 :
                joint_str = game_font.render(kinect_jointType_str[joint_num] + " : X", True, (255, 0, 0))
            else :
                joint_str = game_font.render(kinect_jointType_str[joint_num] + " : O", True, (255, 255, 255))
            self._screen.blit(joint_str, (700, joint_num*40 +20))
            joint_num = joint_num + 1


    def skeletal_tracking(self):
        # -------- Main Program Loop -----------
        self.flag = kinect_flag.ongoing
        while not self._done:
            while self.flag is kinect_flag.ongoing :
                joint_num_array = []
                joint_tracked_check = []
                data = None
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

                #관절이 추적 되었는가?
                self.check_joint(joint_tracked_check)

                """
                for strs in joint_num_array:
                    self._screen.blit(strs[0], strs[1])
                """

                surface_to_draw = None
                pygame.display.update()
                # --- Go ahead and update the screen with what we've drawn.
                pygame.display.flip()
                # --- Limit to 60 frames per second
                self._clock.tick(60)

                try:
                    if self.flag is kinect_flag.capture:
                        data = self.get_depth(joints)
                        print(data)
                except Exception as e:
                    print(e)
            if self.flag == kinect_flag.saving:
                self.file.write(str.format(str(self.type) + data) + "\n")
                print("saving...")
                self.flag = kinect_flag.ongoing

        self.file.close()
        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()


if __name__ == '__main__':
    game = BodyGameRuntime();

    game.skeletal_tracking()