import streamlit as st
import cv2
from PIL import Image
from collections import defaultdict
from ultralytics import YOLO
from video_functions import apply_transform

VIDEO_FILE = "/Users/maximiliangust/code/JeremyVandercam/league_project/notebooks/BAR VS Z10 - MAPA 1 - EMEA MASTERS 2025 - DIA 2 - LEAGUE OF LEGENDS.mp4"
START_TIME = 3000
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


def main():
    st.title("Video Processing with OpenCV")
    # Create a placeholder for the video
    video_placeholder = st.empty()
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
                st.session_state.cap = cv2.VideoCapture(VIDEO_FILE)
                st.session_state.cap.set(cv2.CAP_PROP_POS_MSEC, START_TIME * 1000)
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
