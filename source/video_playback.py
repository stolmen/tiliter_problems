"""

Solution to "Video playback" candidate problem.

"""

import click
import cv2


DISPLAY_RESOLUTION_DO_NOT_SCALE = (0, 0)


def play_video(video_file_path, fps, display_resolution, monochrome):
    """ Plays the video at the given path. """

    print("Playing video")

    capture = cv2.VideoCapture(video_file_path)

    paused = False
    while capture.isOpened():
        if not paused:
            _, frame = capture.read()

            if display_resolution != DISPLAY_RESOLUTION_DO_NOT_SCALE:
                frame = cv2.resize(frame, display_resolution)

            if monochrome:
                transformed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                transformed_frame = frame

            cv2.imshow('frame', transformed_frame)

        wait_key_result_char = chr(cv2.waitKey(1000//fps) & 0xFF)

        if wait_key_result_char == 'q':
            break
        elif wait_key_result_char == 'p':
            paused = not paused

    capture.release()
    cv2.destroyAllWindows()


@click.command()
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
        monochrome=kwargs['monochrome']
    )


if __name__ == "__main__":
    play_video_command()
