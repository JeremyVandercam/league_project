import streamlit as st
import cv2
import numpy as np
from pytubefix import YouTube


def apply_transform(frame, model):
    # Update frame count
    st.session_state.frame_count += 1

    # Crop the frame
    crop_x, crop_y, crop_width, crop_height = 1650, 800, 1900, 1050
    cropped_frame = frame[crop_y : crop_y + crop_height, crop_x : crop_x + crop_width]

    # Run YOLO tracking
    results = model.track(cropped_frame, persist=True)

    # Projection length (in pixels)
    projection_length = 200

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Track IDs seen in current frame
    current_track_ids = []

    # Check if tracking IDs exist
    if hasattr(results[0].boxes, "id") and results[0].boxes.id is not None:
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        current_track_ids = track_ids

        # Update tracks with new positions
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            # Use the session state to store tracking history
            st.session_state.track_history[track_id].append((float(x), float(y)))
            st.session_state.last_seen[track_id] = st.session_state.frame_count

    # Draw all tracks that are either visible or recently disappeared
    for track_id, track in st.session_state.track_history.items():
        # Only draw if the track has points and is visible in current frame
        if track_id in current_track_ids or track_id in st.session_state.last_seen:
            if len(track) > 1:
                # Draw the tracking line
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(
                    annotated_frame,
                    [points],
                    isClosed=False,
                    color=(230, 230, 230),
                    thickness=10,
                )
            # Draw an arrow at the end of the line
            if len(track) >= 15:
                # Get the last two points to determine direction
                p1 = np.array(track[-2])
                p2 = np.array(track[-1])

                # Calculate direction vector
                direction = p2 - p1
                if np.linalg.norm(direction) > 0:  # Avoid division by zero
                    # Normalize the direction vector
                    direction = direction / np.linalg.norm(direction)

                    # Calculate the arrow points
                    arrow_size = 7
                    arrow_angle = np.pi / 6  # 30 degrees

                    # Calculate the two points that form the arrow
                    p_arrow1 = p2 - arrow_size * (
                        direction * np.cos(arrow_angle)
                        + np.array([direction[1], -direction[0]]) * np.sin(arrow_angle)
                    )
                    p_arrow2 = p2 - arrow_size * (
                        direction * np.cos(arrow_angle)
                        - np.array([direction[1], -direction[0]]) * np.sin(arrow_angle)
                    )

                    # Draw the arrow
                    cv2.line(
                        annotated_frame,
                        tuple(p2.astype(int)),
                        tuple(p_arrow1.astype(int)),
                        (0, 0, 255),
                        4,
                    )
                    cv2.line(
                        annotated_frame,
                        tuple(p2.astype(int)),
                        tuple(p_arrow2.astype(int)),
                        (0, 0, 255),
                        4,
                    )

                    # Project the movement to the edge of the frame
                    if len(track) >= 15:
                        # Use the last few points to get a better direction estimate
                        p_prev = np.array(track[-3])
                        p_curr = np.array(track[-2])
                        p_last = np.array(track[-1])

                        # Calculate direction based on the last movement segments
                        dir1 = p_curr - p_prev
                        dir2 = p_last - p_curr

                        # Use a weighted average of the last two directions
                        # (giving more weight to the most recent movement)
                        if np.linalg.norm(dir1) > 0 and np.linalg.norm(dir2) > 0:
                            avg_dir = 0.3 * dir1 + 0.7 * dir2
                            if np.linalg.norm(avg_dir) > 0:
                                avg_dir = avg_dir / np.linalg.norm(avg_dir)

                                # Project the point forward
                                projection_end = p_last + projection_length * avg_dir

                                # Draw the projection line (dashed)
                                # Create a dashed line manually since LINE_DASH is not available
                                dash_length = 10
                                start_point = p_last.astype(int)
                                end_point = projection_end.astype(int)

                                # Calculate total distance and direction
                                dist = np.linalg.norm(end_point - start_point)
                                if dist > 0:
                                    unit_dir = (end_point - start_point) / dist

                                    # Draw dashed segments
                                    for i in range(0, int(dist), dash_length * 2):
                                        p_start = start_point + i * unit_dir
                                        p_end = (
                                            start_point
                                            + min(i + dash_length, dist) * unit_dir
                                        )
                                        cv2.line(
                                            annotated_frame,
                                            tuple(p_start.astype(int)),
                                            tuple(p_end.astype(int)),
                                            (0, 255, 0),
                                            2,
                                        )

                                # Add an arrow at the end of the projection
                                p_proj_arrow1 = projection_end - arrow_size * (
                                    avg_dir * np.cos(arrow_angle)
                                    + np.array([avg_dir[1], -avg_dir[0]])
                                    * np.sin(arrow_angle)
                                )
                                p_proj_arrow2 = projection_end - arrow_size * (
                                    avg_dir * np.cos(arrow_angle)
                                    - np.array([avg_dir[1], -avg_dir[0]])
                                    * np.sin(arrow_angle)
                                )

                                cv2.line(
                                    annotated_frame,
                                    tuple(projection_end.astype(int)),
                                    tuple(p_proj_arrow1.astype(int)),
                                    (0, 255, 0),
                                    2,
                                )
                                cv2.line(
                                    annotated_frame,
                                    tuple(projection_end.astype(int)),
                                    tuple(p_proj_arrow2.astype(int)),
                                    (0, 255, 0),
                                    2,
                                )

    return annotated_frame


def download_yt_video(url):
    st.write("Downloading video...")
    yt = YouTube(url)
    video = (
        yt.streams.filter(file_extension="mp4").order_by("resolution").desc().first()
    )
    path = video.download()
    return path


if __name__ == "__main__":
    apply_transform()
