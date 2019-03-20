import cv2


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
