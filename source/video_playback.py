"""

Solution to "Video playback" candidate problem.

"""

import click
import cv2


DISPLAY_RESOLUTION_DO_NOT_SCALE = (0, 0)


def play_video(
        video_file_path, fps, display_resolution, monochrome,
        destination_file, perform_segmentation):
    """ Plays the video at the given path.

    TODO: perform image segmentation properly."""

    print("Playing video")

    capture = cv2.VideoCapture(video_file_path)
    paused = False
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

    while capture.isOpened():
        if not paused:
            ret, frame = capture.read()

            if perform_segmentation:
                frame = fgbg.apply(frame)

            if display_resolution != DISPLAY_RESOLUTION_DO_NOT_SCALE:
                frame = cv2.resize(frame, display_resolution)

            if monochrome:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if destination_file is not None:
                out.write(frame)
            else:
                cv2.imshow('frame', frame)

            if ret == False:
                break

        wait_key_result_char = chr(cv2.waitKey(1000//fps) & 0xFF)

        if destination_file is None:
            if wait_key_result_char == 'q':
                break
            elif wait_key_result_char == 'p':
                paused = not paused

    capture.release()

    if destination_file is None:
        cv2.destroyAllWindows()
    else:
        out.release()


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


if __name__ == "__main__":
    master()
