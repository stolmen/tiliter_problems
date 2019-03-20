import cv2


DISPLAY_RESOLUTION_DO_NOT_SCALE = (0, 0)
QUIT_IDX = -10  # Arbitrary

# TODO: get rid of these
# Variables to keep track of playback state
paused = False
back_up_frame = False


def play_video(
        video_file_path, fps, display_resolution, convert_to_monochrome,
        perform_segmentation, control_class_instance):

    print("Playing video")
    capture, fps_of_source, resolution_of_source = get_capture_and_properties(
        video_file_path)

    fps = fps_of_source if fps is None else fps
    display_resolution = \
        resolution_of_source if any([i is None for i in display_resolution]) \
            else display_resolution

    def frame_action_fn(frame, idx, fps):
        # TODO: get rid of these
        global back_up_frame
        global paused

        cv2.imshow('frame', frame)

        wait_key_result_char = chr(cv2.waitKey(1000//fps) & 0xFF)

        # Real-time video playback controls
        if control_class_instance is None:
            # Controlled by keyboard
            if wait_key_result_char == 'p':
                paused = not paused
            elif wait_key_result_char == 'b':
                back_up_frame = True
            elif wait_key_result_char == 'q':
                return QUIT_IDX
        else:
            # Controlled by state of controll_class_instance
            paused = control_class_instance.dopause
            if control_class_instance.dobackup:
                print('executing backup')
                back_up_frame = True
                control_class_instance.dobackup = False
            elif control_class_instance.doquit:
                print('executing quit')
                return QUIT_IDX

        if back_up_frame:
            next_idx = idx - 1
            back_up_frame = False
        elif paused:
            next_idx = idx
        else:
            next_idx = None            

        return next_idx

    common_video_things(
        capture=capture,
        target_resolution=display_resolution,
        fps=fps,
        convert_to_monochrome=convert_to_monochrome,
        perform_segmentation=perform_segmentation,
        frame_action_fn=frame_action_fn)

    cv2.destroyAllWindows()


def perform_segmentation_analysis_on_video(
        video_file_path, destination_file):

    capture, fps, resolution = get_capture_and_properties(
        video_file_path)

    out = cv2.VideoWriter(
        destination_file, -1, fps,
        resolution, isColor=True)

    def frame_action_fn(frame, idx, fps):
        out.write(frame)
        return None

    common_video_things(
        capture=capture,
        target_resolution=resolution,
        fps=fps,
        convert_to_monochrome=False,
        perform_segmentation=True,
        frame_action_fn=frame_action_fn)

    out.release()
    

def get_capture_and_properties(video_file_path):
    capture = cv2.VideoCapture(video_file_path)
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    resolution = (
        int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    )

    return capture, fps, resolution


def common_video_things(
        capture, target_resolution, fps, convert_to_monochrome,
        perform_segmentation, frame_action_fn):

    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False) if perform_segmentation \
        else None

    # Read all the frames
    frames = []
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        frames.append(frame)
    capture.release()
    print(f"Read {len(frames)} frames..")

    # Traverse and action the frames
    idx = 0
    while idx < len(frames) and idx != QUIT_IDX:
        current_frame = frames[idx]
        current_frame = process_frame(
            current_frame, fgbg,
            target_resolution, convert_to_monochrome)
        next_idx = frame_action_fn(current_frame, idx, fps)
        idx = idx + 1 if next_idx is None else next_idx
        

def process_frame(
        frame, fgbg, 
        target_resolution, convert_to_monochrome):
    
    if fgbg is not None:
        frame = fgbg.apply(frame)
    if convert_to_monochrome:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.resize(frame, target_resolution)

    return frame
