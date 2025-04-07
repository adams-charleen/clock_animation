from PIL import Image
import numpy as np
import imageio.v2 as imageio

# Load the background image (old_young.png)
background = Image.open("old_young.png").convert("RGBA")
bg_width, bg_height = background.size
bg_array = np.array(background)

# Load the animated GIF frames (clockwise.gif) using imageio
gif_reader = imageio.get_reader("clockwise.gif")
gif_frames = [frame for frame in gif_reader]
gif_reader.close()

# Resize GIF frames to 400x400 and ensure RGBA
gif_frames_resized = []
for frame in gif_frames:
    pil_frame = Image.fromarray(frame).convert("RGBA")
    pil_frame = pil_frame.resize((400, 400), Image.Resampling.LANCZOS)
    gif_frames_resized.append(pil_frame)

# Calculate the center position for the clock
clock_width, clock_height = 400, 400
center_x = (bg_width - clock_width) // 2
center_y = (bg_height - clock_height) // 2

# Create frames for the animation with proper transparency
frames = []
for i in range(len(gif_frames) * 2):  # Loop the GIF twice
    frame_idx = i % len(gif_frames)
    # Create a copy of the background
    bg_copy = background.copy()
    
    # Overlay the current GIF frame at the center with transparency
    gif_frame = gif_frames_resized[frame_idx]
    # Convert to numpy arrays for alpha blending
    bg_region = np.array(bg_copy.crop((center_x, center_y, center_x + clock_width, center_y + clock_height)))
    gif_region = np.array(gif_frame)
    
    # Alpha blending
    if gif_region.shape[-1] == 4:
        alpha = gif_region[:, :, 3] / 255.0
        for c in range(3):
            bg_region[:, :, c] = (bg_region[:, :, c] * (1 - alpha) + gif_region[:, :, c] * alpha).astype(np.uint8)
    
    # Paste the blended region back
    blended = Image.fromarray(bg_region)
    bg_copy.paste(blended, (center_x, center_y))
    
    # Convert to numpy array for saving
    frame_array = np.array(bg_copy)
    # Ensure the frame is in RGB (remove alpha for saving)
    if frame_array.shape[-1] == 4:
        frame_array = frame_array[:, :, :3]
    frames.append(frame_array)

# Save as MP4
imageio.mimwrite('overlay_clock.mp4', frames, fps=10)

# Save as GIF
imageio.mimwrite('overlay_clock.gif', frames, fps=10)

# Optional: Display the first frame to verify
Image.fromarray(frames[0]).show()
