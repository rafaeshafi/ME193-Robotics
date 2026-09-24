"""
Install first:
    pip install legoeducation
Then copy lelib.py from the SimpleLE repo into this project's folder.

"""

import time
import tkinter as tk
import webbrowser

import legoeducation as le
from lelib import colorSensor, controller, doubleMotor

# --- Bluetooth card info for your hardware -------------------------------
# Fill these in with the color/serial printed on your LEGO connection card.
# Valid values: le.LEGO_COLOR_RED, _YELLOW, _BLUE, _GREEN, _PURPLE,
# _MAGENTA, _AZURE, _ORANGE.
COLOR_SENSOR_CARD_COLOR = le.LEGO_COLOR_ORANGE
COLOR_SENSOR_CARD_SERIAL = 7552

CONTROLLER_CARD_COLOR = le.LEGO_COLOR_ORANGE
CONTROLLER_CARD_SERIAL = 7552

# The Double Motor connects without a card (it grabs the first one it sees),
# so it needs no color/serial here.

POLL_DELAY_S = 0.1  # seconds between reads

# Shared handle to the drive base. main() fills this in; every Do*() below
# reads it. Keeping it module-level is what lets the behavior functions stay
# zero-argument, so everyone's stubs keep the same signature.
robot = None

YELLOW_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"



# --- Empty handler functions ----------------------------------------------
# Fill these in with whatever behavior you want.

def DoRed():
    print("red")
    print("Shanmugam has done red; red is the color of his enemies (from blood" \
    ", not due to hair)")


def DoYellow():
    print("yellow")

    # Pop-up window with a button that opens the video in the browser.
    # The window blocks the main loop until it's closed, so it won't spam
    # new windows every poll while the sensor keeps seeing yellow.
    root = tk.Tk()
    root.title("Yellow detected!")
    root.geometry("300x120")

    tk.Label(root, text="You found yellow! Click for your reward:").pack(pady=10)

    def open_video():
        webbrowser.open(YELLOW_VIDEO_URL)
        root.destroy()

    tk.Button(root, text="Watch video", command=open_video).pack()

    root.lift()
    root.attributes("-topmost", True)
    root.mainloop()


def DoBlue():
    print("blue")
    print(r"""
          /\
          ||
          ||
          ||
          ||
          ||
          ||
          ||
          ||
    o=====||=====o
          ##
          ##
          ##
          ()
""")


def DoTeal():
    print("teal")



def DoGreen():
    print("green")



def DoPurple():
    print("purple")



def DoWhite():
    print("white")



def DoMagenta():
    print("magenta")



# Drive speeds for this block, as percentages. Positive runs forward.
CREEP_SPEED = 30
DASH_SPEED = 80


def DoOrange():
    """Orange: creep forward, for lining the robot up by hand."""
    robot.set_speed(CREEP_SPEED)
    robot.run(CREEP_SPEED)



def DoAzure():
    """Azure: run forward at full speed."""
    robot.set_speed(DASH_SPEED)
    robot.run(DASH_SPEED)



def DoNoColor():
    """Nothing under the sensor: stop.

    This fires on every poll where no card is present, so it is what makes
    the robot halt the moment you pull a color card away -- a dead-man
    switch rather than an error case.
    """
    robot.stop()



def DoUnknownColor():
    """Sensor read a color outside lelib's table: stop and say so.

    Failing safe beats guessing -- an unreadable card almost always means
    bad lighting or the sensor sitting too far off the surface.
    """
    print("unknown color -- stopping (check lighting / sensor height)")
    robot.stop()



# Tank drive: each stick drives its own wheel. Counterclockwise is "forward"
# for both motors, matching lelib's run_left()/run_right().
STICK_SPEED = 50

# Whether each wheel is currently being driven by its stick. Released only
# stops a wheel on the transition out of up/down, so an idle stick doesn't
# cancel a color behavior (like Orange/Azure) on every poll.
left_driving = False
right_driving = False


def DoLeftUp():
    """Left stick up: left wheel forward."""
    global left_driving
    robot.set_speed_left(STICK_SPEED)
    robot.motor_run(direction=le.MOTOR_MOVE_DIRECTION_COUNTERCLOCKWISE, motor=le.MOTOR_LEFT)
    left_driving = True



def DoLeftDown():
    """Left stick down: left wheel backward."""
    global left_driving
    robot.set_speed_left(STICK_SPEED)
    robot.motor_run(direction=le.MOTOR_MOVE_DIRECTION_CLOCKWISE, motor=le.MOTOR_LEFT)
    left_driving = True



def DoLeftReleased():
    """Left stick centered: stop the left wheel (once, on release)."""
    global left_driving
    if left_driving:
        robot.motor_stop(motor=le.MOTOR_LEFT)
        left_driving = False



def DoRightUp():
    """Right stick up: right wheel forward."""
    global right_driving
    robot.set_speed_right(STICK_SPEED)
    robot.motor_run(direction=le.MOTOR_MOVE_DIRECTION_COUNTERCLOCKWISE, motor=le.MOTOR_RIGHT)
    right_driving = True



def DoRightDown():
    """Right stick down: right wheel backward."""
    global right_driving
    robot.set_speed_right(STICK_SPEED)
    robot.motor_run(direction=le.MOTOR_MOVE_DIRECTION_CLOCKWISE, motor=le.MOTOR_RIGHT)
    right_driving = True



def DoRightReleased():
    """Right stick centered: stop the right wheel (once, on release)."""
    global right_driving
    if right_driving:
        robot.motor_stop(motor=le.MOTOR_RIGHT)
        right_driving = False



# --- Dispatch helpers -------------------------------------------------

def handle_color(color_name):
    """Big switch statement on the color sensor's detected color."""
    match color_name:
        case "Red":
            DoRed()
        case "Yellow":
            DoYellow()
        case "Blue":
            DoBlue()
        case "Teal":
            DoTeal()
        case "Green":
            DoGreen()
        case "Purple":
            DoPurple()
        case "White":
            DoWhite()
        case "Magenta":
            DoMagenta()
        case "Orange":
            DoOrange()
        case "Azure":
            DoAzure()
        case "No color":
            DoNoColor()
        case _:
            DoUnknownColor()



def handle_controller(ctl):
    """Big switch statement on the controller's joystick state."""
    if ctl.left_up():
        left_state = "up"
    elif ctl.left_down():
        left_state = "down"
    else:
        left_state = "released"

    if ctl.right_up():
        right_state = "up"
    elif ctl.right_down():
        right_state = "down"
    else:
        right_state = "released"

    match left_state:
        case "up":
            DoLeftUp()
        case "down":
            DoLeftDown()
        case "released":
            DoLeftReleased()

    match right_state:
        case "up":
            DoRightUp()
        case "down":
            DoRightDown()
        case "released":
            DoRightReleased()



# --- Main loop -------------------------------------------------------------

def main():
    global robot

    sensor = colorSensor()
    sensor.connect(card_serial=COLOR_SENSOR_CARD_SERIAL, card_color=COLOR_SENSOR_CARD_COLOR)

    ctl = controller()
    ctl.connect(card_serial=CONTROLLER_CARD_SERIAL, card_color=CONTROLLER_CARD_COLOR)

    robot = doubleMotor()
    robot.connect()      # no card needed: first Double Motor advertising
    robot.reset_heading()

    try:
        while True:
            handle_color(sensor.detect_color())
            handle_controller(ctl)
            time.sleep(POLL_DELAY_S)
    except KeyboardInterrupt:
        pass
    finally:
        robot.stop()



if __name__ == "__main__":
    main()
