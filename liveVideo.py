import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time

# Define the video file path
VIDEO_FILE = "/Users/poloniki/code/league_project/notebooks/Bildschirmaufnahme 2025-03-19 um 12.43.44.mov"


def apply_transform(frame, transform):
    if transform == "cartoon":
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply median blur
        gray = cv2.medianBlur(gray, 5)
        # Detect edges
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
        )
        # Apply bilateral filter
        color = cv2.bilateralFilter(frame, 9, 250, 250)
        # Combine color and edges
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        return cartoon
    elif transform == "edges":
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 100, 200)
        # Convert back to BGR
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    elif transform == "rotate":
        # Get image dimensions
        height, width = frame.shape[:2]
        # Calculate rotation matrix
        center = (width // 2, height // 2)
        angle = time.time() * 45  # Rotate 45 degrees per second
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        # Apply rotation
        return cv2.warpAffine(frame, matrix, (width, height))
    else:
        return frame


def main():
    st.title("Video Processing with OpenCV")

    # Video transform options
    transform = st.selectbox(
        "Select video transform", ["none", "cartoon", "edges", "rotate"]
    )

    # Create a placeholder for the video
    video_placeholder = st.empty()

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
            processed_frame = apply_transform(frame, transform)

            # Convert BGR to RGB
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            image = Image.fromarray(processed_frame)

            # Display the image
            video_placeholder.image(image, use_column_width=True)

            # Add a small delay to control frame rate
            time.sleep(0.03)  # Approximately 30 FPS

    else:
        st.write("Video is stopped")


if __name__ == "__main__":
    main()
