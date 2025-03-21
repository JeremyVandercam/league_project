import streamlit as st
import cv2
import numpy as np
from pytubefix import YouTube
from scipy.stats import gaussian_kde


def draw_custom_badges(frame, results):
    """
    Draw custom badges with player names and confidence scores on the frame.

    Args:
        frame: The image frame to draw on
        results: Ultralytics results object containing detections

    Returns:
        Annotated frame with custom badges and labels
    """
    annotated_frame = frame.copy()

    if not hasattr(results.boxes, "xywh"):
        return annotated_frame

    # Get bounding boxes, confidence scores, and class IDs
    # st.write(results[0])
    boxes = results.boxes.xywh.cpu().numpy()
    confidences = results.boxes.conf.cpu().numpy()
    class_ids = results.boxes.cls.cpu().numpy().astype(int)

    # Add track IDs if available
    track_ids = None
    if hasattr(results.boxes, "id") and results.boxes.id is not None:
        track_ids = results.boxes.id.int().cpu().numpy()

    # For each detection
    for i, (box, conf, cls_id) in enumerate(zip(boxes, confidences, class_ids)):
        # Extract box coordinates
        x, y, w, h = box
        x_min, y_min = int(x - w / 2), int(y - h / 2)
        x_max, y_max = int(x + w / 2), int(y + h / 2)

        # Get the class name
        class_name = results.names[cls_id]

        # Create label text with just the class name (no ID)
        label_text = f"{class_name}"

        # Draw bounding box
        cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 1)

        # Use even smaller font size for minimalist appearance
        font_scale = 0.35
        font_thickness = 1
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Calculate badge size with new font parameters
        text_size = cv2.getTextSize(label_text, font, font_scale, font_thickness)[0]
        badge_width = text_size[0] + 6  # Further reduced padding
        badge_height = text_size[1] + 4  # Further reduced padding

        # Position badge at top of bounding box
        badge_x_min = x_min
        badge_y_min = y_min - badge_height - 2  # Reduced gap even more

        # Make sure badge is within frame boundaries
        if badge_y_min < 0:
            badge_y_min = y_max + 2  # Place below if not enough space above

        # Draw badge background
        cv2.rectangle(
            annotated_frame,
            (badge_x_min, badge_y_min),
            (badge_x_min + badge_width, badge_y_min + badge_height),
            (50, 50, 200),  # Badge background color (dark blue)
            -1,  # Fill
        )

        # Draw label text with higher quality settings
        cv2.putText(
            annotated_frame,
            label_text,
            (badge_x_min + 3, badge_y_min + badge_height - 2),  # Better positioning
            font,
            font_scale,
            (255, 255, 255),  # White text
            font_thickness,
            cv2.LINE_AA,  # Anti-aliased for better quality
        )

    return annotated_frame


def generate_kde_heatmap(points, directions=None, frame_shape=None, bandwidth=0.05):
    """
    Generate a KDE heatmap for visualization, with optional directional weighting

    Args:
        points: List of (x, y) points
        directions: Optional list of directional vectors to weight the KDE
        frame_shape: Shape of the frame (height, width)
        bandwidth: Bandwidth parameter for KDE

    Returns:
        Heatmap image that can be overlaid on the frame
    """
    if len(points) < 3:  # Need at least 3 points for a meaningful KDE
        return np.zeros((frame_shape[0], frame_shape[1]), dtype=np.float32)

    # Convert points to numpy array
    points = np.array(points)

    # Downsample the grid for faster computation
    # Create a lower resolution grid first, then resize the result
    scale_factor = 8  # Reduce resolution by this factor
    small_h = frame_shape[0] // scale_factor
    small_w = frame_shape[1] // scale_factor

    # Create smaller mesh grid
    x_grid = np.linspace(0, frame_shape[1], small_w)
    y_grid = np.linspace(0, frame_shape[0], small_h)
    X, Y = np.meshgrid(x_grid, y_grid)
    positions = np.vstack([X.ravel(), Y.ravel()])

    try:
        # Create kernel density estimation
        values = np.vstack([points[:, 0], points[:, 1]])

        # If directions are provided, create a weighted KDE
        if directions is not None and len(directions) == len(points):
            # Normalize directions
            norm_directions = np.array(
                [
                    d / np.linalg.norm(d) if np.linalg.norm(d) > 0 else [0, 0]
                    for d in directions
                ]
            )

            # Create a weights array for points based on direction projection
            # Give more weight to more recent points (if properly ordered)
            weights = np.linspace(
                0.3, 1.0, len(points)
            )  # Increasing weights for more recent points

            # For each position, add extra points in the direction of movement
            augmented_values = values.copy()
            augmented_weights = weights.copy()

            # Now add more projection points for stronger directional emphasis
            projection_scale = 60  # Increased from 30 to 60 for longer projection
            num_projections = 6  # Increased from 3 to 6 for more projected points

            for i in range(len(points)):
                if np.linalg.norm(norm_directions[i]) > 0:
                    # Higher weight for more recent points' projections
                    point_weight = weights[i]

                    for j in range(1, num_projections + 1):
                        # Add points in the movement direction
                        proj_point = points[i] + norm_directions[
                            i
                        ] * projection_scale * (j / num_projections)

                        # If the projected point is within the frame
                        if (
                            0 <= proj_point[0] < frame_shape[1]
                            and 0 <= proj_point[1] < frame_shape[0]
                        ):
                            # Add to augmented values
                            augmented_values = np.hstack(
                                [
                                    augmented_values,
                                    np.array([[proj_point[0]], [proj_point[1]]]),
                                ]
                            )
                            # Projected points maintain higher weight for future positions
                            # Points further in the future get slightly less weight but still significant
                            proj_weight = point_weight * (0.9 - 0.05 * j)
                            augmented_weights = np.append(
                                augmented_weights, proj_weight
                            )

            # Use the augmented values and weights
            kernel = gaussian_kde(
                augmented_values, weights=augmented_weights, bw_method=bandwidth
            )
        else:
            kernel = gaussian_kde(values, bw_method=bandwidth)

        Z = np.reshape(kernel(positions), X.shape)

        # Normalize for better visualization
        Z = (Z - Z.min()) / (Z.max() - Z.min() + 1e-10)

        # Convert to heatmap and resize to original resolution
        small_heatmap = (Z * 255).astype(np.uint8)
        heatmap = cv2.resize(
            small_heatmap,
            (frame_shape[1], frame_shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )

        return heatmap
    except Exception as e:
        print(f"KDE generation error: {e}")
        # If KDE fails (e.g., singular matrix), return empty heatmap
        return np.zeros((frame_shape[0], frame_shape[1]), dtype=np.float32)


def apply_transform(frame, model):
    # Update frame count
    st.session_state.frame_count += 1

    # Check if the timestamp slider changed (using detection from video.py)
    # If slider changed, clear the heatmap cache
    if (
        hasattr(st.session_state, "timestamp_changed")
        and st.session_state.timestamp_changed
    ):
        # Clear the heatmap data when slider changes
        if hasattr(st.session_state, "heatmap"):
            del st.session_state.heatmap
        st.session_state.timestamp_changed = False

    # Crop the frame
    crop_x, crop_y, crop_width, crop_height = 1650, 800, 1900, 1050
    cropped_frame = frame[crop_y : crop_y + crop_height, crop_x : crop_x + crop_width]

    # Run YOLO tracking
    results = model.track(cropped_frame, persist=True)

    # Projection length (in pixels)
    projection_length = 30

    # Use custom badge drawing instead of the default plot method
    annotated_frame = draw_custom_badges(cropped_frame, results[0])

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

    # Clean up track history for IDs that haven't been seen for 60 frames
    frames_to_keep_history = 60
    cleanup_threshold = st.session_state.frame_count - frames_to_keep_history

    # Create a list of IDs to remove (can't modify dict during iteration)
    ids_to_remove = []
    for track_id, last_seen_frame in st.session_state.last_seen.items():
        if last_seen_frame < cleanup_threshold:
            ids_to_remove.append(track_id)

    # Remove the stale tracks and clear heatmap if any tracks were removed
    if ids_to_remove:
        for track_id in ids_to_remove:
            if track_id in st.session_state.track_history:
                del st.session_state.track_history[track_id]
            if track_id in st.session_state.last_seen:
                del st.session_state.last_seen[track_id]

        # Reset the heatmap when tracks are removed to force recalculation
        if hasattr(st.session_state, "heatmap"):
            del st.session_state.heatmap

    # Calculate the frame threshold for the last 20 seconds
    frames_per_second = 10
    seconds_to_show = 20
    frame_threshold = st.session_state.frame_count - (
        frames_per_second * seconds_to_show
    )
    frame_threshold = max(0, frame_threshold)  # Ensure it's not negative

    # Draw all tracks that are either visible or recently disappeared
    for track_id, track in st.session_state.track_history.items():
        # Only draw if the track has points and is visible in current frame
        if track_id in current_track_ids or track_id in st.session_state.last_seen:
            if len(track) > 1:
                # Only use points from the last 20 seconds
                # Estimate which points to keep based on frame counts
                # This is an approximation since we don't store timestamps
                points_to_keep = min(len(track), frames_per_second * seconds_to_show)
                recent_track = track[-points_to_keep:]

                # Draw the tracking line directly on the main frame
                points = np.hstack(recent_track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(
                    annotated_frame,
                    [points],
                    isClosed=False,
                    color=(230, 230, 230),
                    thickness=1,
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
                    if len(track) >= 40:
                        # Use the last few points to get a better direction estimate
                        points_for_projection = min(40, len(track))
                        p_prev = np.array(track[-min(30, points_for_projection)])
                        p_curr = np.array(track[-min(10, points_for_projection)])
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
                                dash_length = 3
                                start_point = p_last.astype(int)
                                end_point = projection_end.astype(int)

                                # Calculate total distance and direction
                                dist = np.linalg.norm(end_point - start_point)
                                if dist > 0:
                                    unit_dir = (end_point - start_point) / dist

                                    # Draw dashed segments directly on the main frame
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
                                            (0, 255, 0),  # Green color
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
                                    (0, 255, 0),  # Green color
                                    2,
                                )
                                cv2.line(
                                    annotated_frame,
                                    tuple(projection_end.astype(int)),
                                    tuple(p_proj_arrow2.astype(int)),
                                    (0, 255, 0),  # Green color
                                    1,
                                )

    # Only generate heatmap every 10 frames to improve performance
    if st.session_state.frame_count % 10 == 0 or not hasattr(
        st.session_state, "heatmap"
    ):
        # Generate KDE heatmap from all current track points within the last 20 seconds
        all_track_data = {}

        # First collect all track data separately to calculate overall directions
        for track_id, track in st.session_state.track_history.items():
            if len(track) > 0:
                # Only use points from the last 20 seconds for KDE
                points_to_keep = min(len(track), frames_per_second * seconds_to_show)
                recent_track = track[-points_to_keep:]
                all_track_data[track_id] = recent_track

        # Now process all tracks with their overall movement direction
        all_points = []
        all_directions = []

        for track_id, recent_track in all_track_data.items():
            if (
                len(recent_track) >= 3
            ):  # Need at least a few points to determine direction
                # Calculate overall movement direction for this track
                first_point = np.array(recent_track[0])
                last_point = np.array(recent_track[-1])
                overall_direction = last_point - first_point

                # Only consider tracks with significant movement
                if np.linalg.norm(overall_direction) > 10:
                    # Normalize the overall direction
                    if np.linalg.norm(overall_direction) > 0:
                        overall_direction = overall_direction / np.linalg.norm(
                            overall_direction
                        )

                    # Use all points but focus projection on the last point
                    # For recent points, add them with individual directions
                    for i, point in enumerate(recent_track):
                        all_points.append(point)

                        # Use a mix of point-to-point direction and overall direction,
                        # with more emphasis on overall direction
                        if i > 0:
                            prev_point = np.array(recent_track[i - 1])
                            curr_point = np.array(point)
                            point_direction = curr_point - prev_point

                            if np.linalg.norm(point_direction) > 0:
                                point_direction = point_direction / np.linalg.norm(
                                    point_direction
                                )
                                # Blend local and overall direction (80% overall, 20% local)
                                blended_direction = (
                                    0.8 * overall_direction + 0.2 * point_direction
                                )
                                if np.linalg.norm(blended_direction) > 0:
                                    blended_direction = (
                                        blended_direction
                                        / np.linalg.norm(blended_direction)
                                    )
                                all_directions.append(blended_direction)
                            else:
                                all_directions.append(overall_direction)
                        else:
                            all_directions.append(overall_direction)

        if len(all_points) > 3:  # Need at least a few points for KDE
            # Create KDE heatmap with directional weighting
            heatmap = generate_kde_heatmap(
                all_points,
                directions=all_directions,
                frame_shape=cropped_frame.shape[:2],
                bandwidth=0.1,
            )

            # Cache the heatmap for future frames
            st.session_state.heatmap = heatmap

    # Use the cached heatmap
    if hasattr(st.session_state, "heatmap"):
        heatmap = st.session_state.heatmap

        # Apply colormap to KDE
        heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Create transparent overlay
        overlay = annotated_frame.copy()
        cv2.addWeighted(heatmap_colored, 0.5, overlay, 0.5, 0, overlay)

        # Add transparency mask based on heatmap intensity - lower threshold for better visibility
        mask = heatmap > 8  # Even lower threshold to show more areas

        # Apply the mask to create the final frame
        result_frame = annotated_frame.copy()
        result_frame[mask] = overlay[mask]

        return result_frame

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
