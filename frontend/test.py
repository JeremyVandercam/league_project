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
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False
if "cap" not in st.session_state:
    st.session_state.cap = None


def main():
    st.title("League of Legends Video Analysis")
    # Create a placeholder for the video
    video_placeholder = st.empty()

    start_time_slider = st.slider(
        "Start Time (minutes)",
        min_value=0.0,
        max_value=30.0,  # Always 30 minutes
        value=0.0,  # Default to 0
        step=1.0,  # Step of 0.1 minutes (6 seconds)
        format="%.1f",
        disabled=st.session_state.video_file is None,  # Disable until video is loaded
        key="start_time_slider",  # Add a key for uniqueness
        help="Select the starting point for video analysis.",
    )

    # Input field for YouTube link
    yt_link = st.text_input("Enter YouTube Video URL:")
    if st.button("Download Video") and yt_link:
        st.session_state.video_file = download_yt_video(yt_link)
        st.success(f"Video downloaded: {st.session_state.video_file}")
    model = YOLO(MODEL_PATH)
    # Create a button to start/stop the video

    # --- Control Buttons (Start/Stop) ---
    col1, col2, col3 = st.columns([1, 1, 5])  # Adjust column widths as needed

    with col1:
        if st.button("Start"):
            if st.session_state.video_file:
                st.session_state.is_playing = True
                if st.session_state.cap is None:
                    st.session_state.cap = cv2.VideoCapture(st.session_state.video_file)
                    st.session_state.cap.set(
                        cv2.CAP_PROP_POS_MSEC, start_time_slider * 60 * 1000
                    )
            elif not st.session_state.video_file:
                st.warning("Please download a video first.")

    with col2:
        if st.button("Stop"):
            st.session_state.is_playing = False
            # Release only, don't set to None here to allow resuming

    # --- Video Processing Loop ---
    if st.session_state.is_playing and st.session_state.cap:
        model = YOLO(MODEL_PATH)  # Load model here to avoid multiple loadings

        while st.session_state.is_playing:
            ret, frame = st.session_state.cap.read()

            if not ret:
                st.write("End of video reached, or error reading frame.")
                st.session_state.is_playing = False  # Stop playback
                break

            with st.spinner("Processing frame..."):
                processed_frame = apply_transform(frame, model)
                processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(processed_frame)
                video_placeholder.image(image, use_column_width=True)

    elif st.session_state.video_file and not st.session_state.is_playing:
        st.write("Video is paused.  Press 'Start' to resume.")
    elif not st.session_state.video_file:
        st.write("Please enter a YouTube URL and click 'Download Video'.")

    # --- Clean up (important to release the capture) ---
    if st.session_state.cap is not None and not st.session_state.is_playing:
        st.session_state.cap.release()
        st.session_state.cap = None
        print("Video capture released.")


if __name__ == "__main__":
    main()
