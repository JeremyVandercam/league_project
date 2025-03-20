import streamlit as st
import cv2
from PIL import Image
from collections import defaultdict
from ultralytics import YOLO
from video_functions import apply_transform, download_yt_video

MAX_INVISIBLE_FRAMES = 30
PROJECTION_LENGTH = 200
BASE_PATH = "/Users/maximiliangust/code/JeremyVandercam/league_project"
NOTEBOOKS_PATH = f"{BASE_PATH}/notebooks"
MODEL_PATH = f"{NOTEBOOKS_PATH}/best.pt"

# Initialize session state variables for tracking
if "track_history" not in st.session_state:
    st.session_state.track_history = defaultdict(list)
if "last_seen" not in st.session_state:
    st.session_state.last_seen = {}
if "frame_count" not in st.session_state:
    st.session_state.frame_count = 0
if "video_file" not in st.session_state:
    st.session_state.video_file = None

if "timestamp" not in st.session_state:
    st.session_state.timestamp = [1000000]


def main():
    st.title("League of Legends Video Analysis")
    start_time_slider = st.slider(
        "Start Time (minutes)",
        min_value=3000.0,
        max_value=30000000.0,
        step=1000.0,
        disabled=st.session_state.video_file is None,  # Disable until video is loaded
        help="Select the starting point for video analysis.",
    )

    st.session_state.timestamp.append(start_time_slider)
    if len(st.session_state.timestamp) > 1:
        if st.session_state.timestamp[-1] != st.session_state.timestamp[-2]:
            st.rerun()

    # Create a placeholder for the video
    video_placeholder = st.empty()

    # Input field for YouTube link
    yt_link = st.text_input("Enter YouTube Video URL:")
    if st.button("Download Video") and yt_link:
        st.session_state.video_file = download_yt_video(yt_link)
        st.success(f"Video downloaded: {st.session_state.video_file}")
    model = YOLO(MODEL_PATH)
    # Create a button to start/stop the video
    if "is_playing" not in st.session_state:
        st.session_state.is_playing = False
    if "cap" not in st.session_state:
        st.session_state.cap = None
    if st.button("Start/Stop Video"):
        st.session_state.is_playing = not st.session_state.is_playing
        if st.session_state.is_playing:
            if st.session_state.cap is None:
                st.session_state.cap = cv2.VideoCapture(st.session_state.video_file)
                st.session_state.cap.set(
                    cv2.CAP_PROP_POS_MSEC, st.session_state.timestamp[-1]
                )
        else:
            if st.session_state.cap is not None:
                st.session_state.cap.release()
                st.session_state.cap = None
    if st.session_state.is_playing and st.session_state.cap is not None:
        while st.session_state.cap.isOpened():
            ret, frame = st.session_state.cap.read()
            if not ret:
                st.session_state.cap.set(
                    cv2.CAP_PROP_POS_FRAMES, 0
                )  # Reset to beginning
                continue
            # Apply transformation
            processed_frame = apply_transform(frame, model)
            # Convert BGR to RGB
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            image = Image.fromarray(processed_frame)
            # Display the image
            video_placeholder.image(image, use_column_width=True)
    else:
        st.write("Video is stopped")


if __name__ == "__main__":
    main()
