"""

Solution to "Video playback" candidate problem.

"""

import click
import cv2

from tkinter import *
from tkinter import ttk

DISPLAY_RESOLUTION_DO_NOT_SCALE = (0, 0)


def play_video(
        video_file_path, fps, display_resolution, monochrome,
        destination_file, perform_segmentation, control_class_instance,
        frame_action_callback):
    """ Plays the video at the given path.

    TODO: perform image segmentation properly."""

    print("Playing video")

    capture = cv2.VideoCapture(video_file_path)
    paused = False
    back_up_frame = False
    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

    if fps is None:
        fps = int(capture.get(cv2.CAP_PROP_FPS))

    if destination_file is not None:
        # extract parameters from the video file itself
        if display_resolution is DISPLAY_RESOLUTION_DO_NOT_SCALE:
            display_resolution_actual = (
                int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )

        print(f"fps={fps}")
        print(f"display_resolution_actual={display_resolution_actual}")
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(destination_file, -1, fps, display_resolution_actual, isColor=True)

    # Read all the frames
    frames = []
    while capture.isOpened():
        ret, frame = capture.read()
        if ret == False:
            break
        frames.append(frame)
    capture.release()
    print(f"Read {len(frames)} frames..")

    # Traverse the frames and do things.
    idx = 0
    while idx < len(frames):
        frame = frames[idx]

        # Process the frame
        if perform_segmentation:
            frame = fgbg.apply(frame)
        if display_resolution != DISPLAY_RESOLUTION_DO_NOT_SCALE:
            frame = cv2.resize(frame, display_resolution)
        if monochrome:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Action the frame
        if destination_file is not None:
            # Write to file
            out.write(frame)
        else:
            # Display frame
            if frame_action_callback:
                frame_action_callback(frame)
            else:
                cv2.imshow('frame', frame)

            wait_key_result_char = chr(cv2.waitKey(1000//fps) & 0xFF)

            # Real-time controls
            if control_class_instance is None:
                if wait_key_result_char == 'q':
                    break
                elif wait_key_result_char == 'p':
                    paused = not paused
                elif wait_key_result_char == 'b':
                    back_up_frame = True
            else:
                #print(control_class_instance)
                paused = control_class_instance.dopause
                if control_class_instance.doquit:
                    print('executing quit')
                    break
                elif control_class_instance.dobackup:
                    print('executing backup')
                    back_up_frame = True
                    control_class_instance.dobackup = False


        if back_up_frame:
            idx -= 1
            back_up_frame = False
        elif not paused:
            idx += 1

    # Finalise
    if destination_file is None:
        cv2.destroyAllWindows()
    else:
        out.release()


class VideoControl(object):
    def __init__(self):
        self.doquit = False
        self.dopause = False
        self.dobackup = False


@click.group()
def master():
    pass

@master.command("play_video")
@click.argument("video_file_path")
@click.option("--frame_rate", default=None, type=int)
@click.option("--display_resolution", default=DISPLAY_RESOLUTION_DO_NOT_SCALE, type=(int, int))
@click.option("--monochrome", is_flag=True)
def play_video_command(**kwargs):
    """ Handling of command line arguments """
    print(f"playing video with {kwargs}")
    play_video(
        video_file_path=kwargs['video_file_path'],
        fps=kwargs['frame_rate'],
        display_resolution=kwargs['display_resolution'],
        monochrome=kwargs['monochrome'],
        destination_file=None,
        perform_segmentation=False,
    )


@master.command("mask_video")
@click.argument("original_file")
@click.option("--destination_file", default=None)
def mask_video_commnand(**kwargs):
    print(f"Creating masked video with the following arguments: {kwargs}")

    if kwargs['destination_file'] is None:
        base, ext = kwargs["original_file"].split('.')
        destination_file = base + '_processed.' + ext
        print(f'saving to {destination_file}')
    play_video(
        video_file_path=kwargs["original_file"],
        destination_file=destination_file,
        perform_segmentation=True,
        fps=None,
        display_resolution=DISPLAY_RESOLUTION_DO_NOT_SCALE,
        monochrome=False
    )


import threading

@master.command("launch_player")
#@click.argument("video_file_path")
#@click.option("--frame_rate", default=None, type=int)
#@click.option("--display_resolution", default=DISPLAY_RESOLUTION_DO_NOT_SCALE, type=(int, int))
#@click.option("--monochrome", is_flag=True)
def launch_gui_video_player(**kwargs):

    ctrl = VideoControl()

    def play_video_process():
        ctrl.dobackup=False
        ctrl.dopause=False
        ctrl.doquit=False
        play_video(
            video_file_path=video_path.get(),
            destination_file=None,
            perform_segmentation=False,
            fps=None,
            display_resolution=DISPLAY_RESOLUTION_DO_NOT_SCALE,
            monochrome=False,
            control_class_instance=ctrl,
            frame_action_callback=None,
        )

    def play(*args):

        thread = threading.Thread(target=play_video_process)
        thread.start()
        

    def frame_action(frame):
        pass


    def pause(*args):
        print('pausing')
        ctrl.dopause=not ctrl.dopause

    def back(*args):
        ctrl.dobackup=True

    def quit(*args):
        ctrl.doquit=True

    root = Tk()
    root.title("Video player")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    video_path = StringVar()
    #meters = StringVar()

    path_entry = ttk.Entry(mainframe, width=7, textvariable=video_path)
    path_entry.grid(column=2, row=1, sticky=(W, E))
    path_entry.insert(0, r"E:\tilter\candidate_problem_solution\tiliter_data\video_2.mp4")

    #ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))
    ttk.Button(mainframe, text="PLAY", command=play).grid(column=1, row=2, sticky=W)
    ttk.Button(mainframe, text="Toggle pause", command=pause).grid(column=1, row=3, sticky=W)
    ttk.Button(mainframe, text="Back up 1 frame", command=back).grid(column=2, row=3, sticky=W)
    ttk.Button(mainframe, text="QUIT", command=quit).grid(column=2, row=2, sticky=W)

    ttk.Label(mainframe, text="path").grid(column=1, row=1, sticky=W)
    #ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
    #ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    path_entry.focus()
    # root.bind('<Return>', calculate)

    try:
        root.mainloop()
    except:
        print()


if __name__ == "__main__":
    master()
