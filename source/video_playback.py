"""

Solution to "Video playback" candidate problem.

"""

import threading
from tkinter import Tk, N, S, E, W, StringVar, ttk

import click
from video import perform_segmentation_analysis_on_video, play_video


class VideoControl(object):
    def __init__(self):
        self.doquit = False
        self.dopause = False
        self.dobackup = False


@click.group()
def master():
    pass


@master.command("play_video", help="Playback a video file")
@click.argument("video_file_path")
@click.option("--frame_rate", default=None, type=int, help="Frame rate of video in frames per second")
@click.option("--display_resolution", default=(None, None), type=(int, int), help="Playback resolution. The resolution and aspect ratio of the original video file is not honoured. All frames are decimated/interpolated to achieve the desired display resolution.")
@click.option("--monochrome", is_flag=True, help="Transform each frame into a monochrome image.")
def play_video_command(**kwargs):
    """ Handling of command line arguments """
    print(f"playing video with {kwargs}")

    play_video(
        video_file_path=kwargs['video_file_path'],
        fps=kwargs['frame_rate'],
        display_resolution=kwargs['display_resolution'],
        convert_to_monochrome=kwargs['monochrome'],
        perform_segmentation=False,
        control_class_instance=None,
    )


@master.command("segmentation_analysis", help="Perform segmentation analysis on a video and save the result.")
@click.argument("original_file")
@click.option("--destination_file", default=None, help="Location of processed video. The default location is the same directory as the source file, with '_processed' appended to the filename.")
def perform_segmentation_on_video_command(**kwargs):
    print(f"Creating masked video with the following arguments: {kwargs}")

    if kwargs['destination_file'] is None:
        base, ext = kwargs["original_file"].split('.')
        destination_file = base + '_processed.' + ext
        print(f'saving to {destination_file}')

    perform_segmentation_analysis_on_video(
        video_file_path=kwargs["original_file"],
        destination_file=destination_file,
    )


@master.command("launch_player", help="Launch GUI video player")
def launch_gui_video_player(**kwargs):

    ctrl = VideoControl()

    def play_video_process():
        ctrl.dobackup = False
        ctrl.dopause = False
        ctrl.doquit = False
        play_video(
            video_file_path=video_path.get(),
            fps=None,
            display_resolution=(None, None),
            convert_to_monochrome=False,
            perform_segmentation=False,
            control_class_instance=ctrl,
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

    def stop_video(*args):
        ctrl.doquit=True

    root = Tk()
    root.title("Video player")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    video_path = StringVar()

    path_entry = ttk.Entry(mainframe, width=7, textvariable=video_path)
    path_entry.grid(column=2, row=1, sticky=(W, E))
    path_entry.insert(0, r"E:\tilter\candidate_problem_solution\tiliter_data\video_2.mp4")

    ttk.Button(mainframe, text="PLAY", command=play).grid(column=1, row=2, sticky=W)
    ttk.Button(mainframe, text="Toggle pause", command=pause).grid(column=1, row=3, sticky=W)
    ttk.Button(mainframe, text="Back up 1 frame", command=back).grid(column=2, row=3, sticky=W)
    ttk.Button(mainframe, text="Stop video", command=stop_video).grid(column=2, row=2, sticky=W)

    ttk.Label(mainframe, text="path").grid(column=1, row=1, sticky=W)

    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    path_entry.focus()

    try:
        root.mainloop()
    except:
        print()


if __name__ == "__main__":
    master()
