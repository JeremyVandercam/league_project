import streamlit as st
import cv2
from PIL import Image
from collections import defaultdict

# from ultralytics import YOLO
from video_functions import apply_transform, download_yt_video
# from ultralytics import


MAX_INVISIBLE_FRAMES = 30
PROJECTION_LENGTH = 200
BASE_PATH = "/Users/maximiliangust/code/JeremyVandercam/league_project"
NOTEBOOKS_PATH = f"{BASE_PATH}/notebooks"
MODEL_PATH = "frontend/best.pt"

# Initialize session state variables for tracking
if "track_history" not in st.session_state:
    st.session_state.track_history = defaultdict(list)
if "last_seen" not in st.session_state:
    st.session_state.last_seen = {}
if "frame_count" not in st.session_state:
    st.session_state.frame_count = 0
if "video_file" not in st.session_state:
    st.session_state.video_file = None
if "video_duration_minutes" not in st.session_state:
    st.session_state.video_duration_minutes = 0
if "display_width" not in st.session_state:
    st.session_state.display_width = 900  # Default display width
if "timestamp_changed" not in st.session_state:
    st.session_state.timestamp_changed = False
if "timestamp_minutes" not in st.session_state or isinstance(
    st.session_state.timestamp_minutes, list
):
    st.session_state.timestamp_minutes = 0.0
if "prev_timestamp_minutes" not in st.session_state:
    st.session_state.prev_timestamp_minutes = 0.0


def get_video_duration(video_path):
    """Get the duration of a video file in minutes"""
    if not video_path:
        return 0

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0

    # Get total frame count
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Get frames per second
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Calculate duration in minutes
    duration_minutes = (total_frames / fps) / 60

    cap.release()
    return duration_minutes


def main():
    st.set_page_config(layout="wide")  # Use wide layout for more space

    st.title("League of Legends Video Analysis")

    # Create sidebar for controls
    with st.sidebar:
        st.header("Controls")

        # Video size control
        st.session_state.display_width = st.slider(
            "Video Size",
            min_value=500,
            max_value=1500,
            value=st.session_state.display_width,
            step=50,
            help="Adjust the display width of the video",
        )

        # Input field for YouTube link
        st.subheader("Video Source")
        yt_link = st.text_input("Enter YouTube Video URL:")
        if st.button("Download Video") and yt_link:
            st.session_state.video_file = download_yt_video(yt_link)
            # Get video duration
            st.session_state.video_duration_minutes = get_video_duration(
                st.session_state.video_file
            )
            st.success(f"Video downloaded: {st.session_state.video_file}")
            # Reset tracking data when a new video is loaded
            st.session_state.track_history = defaultdict(list)
            st.session_state.last_seen = {}
            st.session_state.frame_count = 0
            if hasattr(st.session_state, "heatmap"):
                del st.session_state.heatmap
            st.session_state.timestamp_changed = True

        # Store previous timestamp value
        st.session_state.prev_timestamp_minutes = float(
            st.session_state.timestamp_minutes
        )

        # Update the timestamp with slider value
        max_duration = max(
            st.session_state.video_duration_minutes, 1.0
        )  # at least 1 minute

        st.subheader("Timeline")
        timestamp_slider = st.slider(
            "Start Time (minutes)",
            min_value=0.0,
            max_value=max_duration,
            step=0.1,
            value=float(st.session_state.timestamp_minutes),
            disabled=st.session_state.video_file
            is None,  # Disable until video is loaded
            help="Select the starting point for video analysis in minutes.",
        )

        # Check if timestamp has changed
        if timestamp_slider != st.session_state.timestamp_minutes:
            st.session_state.timestamp_minutes = timestamp_slider
            st.session_state.timestamp_changed = True

        # Play/Stop button
        if "is_playing" not in st.session_state:
            st.session_state.is_playing = False
        if "cap" not in st.session_state:
            st.session_state.cap = None

        play_button = st.button("Start/Stop Video")
        if play_button:
            st.session_state.is_playing = not st.session_state.is_playing
            if st.session_state.is_playing:
                if st.session_state.cap is None:
                    st.session_state.cap = cv2.VideoCapture(st.session_state.video_file)
                    # Convert minutes to milliseconds
                    timestamp_ms = float(st.session_state.timestamp_minutes) * 60 * 1000
                    st.session_state.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
            else:
                if st.session_state.cap is not None:
                    st.session_state.cap.release()
                    st.session_state.cap = None

    # Main content area for video display
    # Check if timestamp changed
    timestamp_changed = (
        st.session_state.timestamp_minutes != st.session_state.prev_timestamp_minutes
    )

    # Create a placeholder for the video with a container for styling
    video_container = st.container()
    with video_container:
        video_placeholder = st.empty()

    model = YOLO(MODEL_PATH)

    # Apply timestamp change if slider was adjusted
    if (
        timestamp_changed
        and st.session_state.is_playing
        and st.session_state.cap is not None
    ):
        # Convert minutes to milliseconds
        timestamp_ms = float(st.session_state.timestamp_minutes) * 60 * 1000
        st.session_state.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        st.session_state.track_history = defaultdict(list)
        st.session_state.timestamp_changed = True
        # Also clear the heatmap when timeline changes
        if hasattr(st.session_state, "heatmap"):
            del st.session_state.heatmap

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

            # Resize the frame based on user preference
            height, width = processed_frame.shape[:2]
            new_width = st.session_state.display_width
            new_height = int(height * (new_width / width))
            processed_frame = cv2.resize(
                processed_frame, (new_width, new_height), interpolation=cv2.INTER_AREA
            )

            # Convert BGR to RGB
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            image = Image.fromarray(processed_frame)
            # Display the image
            video_placeholder.image(image, use_container_width=False, width=new_width)
    else:
        if st.session_state.video_file:
            st.write("Video is stopped")
        else:
            st.write("Please upload a video using the sidebar controls")


if __name__ == "__main__":
    main()
