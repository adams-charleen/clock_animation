import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image
import imageio.v2 as imageio
import tensorflow as tf

# Load images
background = Image.open("old_young.png").convert("RGBA")
bg_width, bg_height = background.size
gif_reader = imageio.get_reader("clockwise.gif")
gif_frames = [Image.fromarray(frame).convert("RGBA").resize((400, 400), Image.Resampling.LANCZOS) for frame in gif_reader]
gif_reader.close()

# Precompute rotation matrices with TensorFlow
num_steps = 360  # Full rotation over 360 frames
theta = tf.linspace(0.0, 2 * np.pi, num_steps)
rot_y = tf.stack([
    tf.stack([tf.cos(theta), tf.zeros_like(theta), tf.sin(theta)], axis=-1),
    tf.stack([tf.zeros_like(theta), tf.ones_like(theta), tf.zeros_like(theta)], axis=-1),
    tf.stack([-tf.sin(theta), tf.zeros_like(theta), tf.cos(theta)], axis=-1)
], axis=-2)  # [360, 3, 3]
rotation_matrices = rot_y.numpy()

# Initialize Pygame and OpenGL
pygame.init()
display = (bg_width, bg_height)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)
glEnable(GL_TEXTURE_2D)

# Load background texture
bg_data = np.array(background)[:, :, :3][::-1]
bg_texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, bg_texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, bg_width, bg_height, 0, GL_RGB, GL_UNSIGNED_BYTE, bg_data)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# Load GIF frame textures
gif_textures = []
for frame in gif_frames:
    frame_data = np.array(frame)[:, :, :4][::-1]
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 400, 400, 0, GL_RGBA, GL_UNSIGNED_BYTE, frame_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    gif_textures.append(tex)

# Animation variables
rot_idx = 0
frame_idx = 0
clock = pygame.time.Clock()
frames = []  # To store frames for saving

# Main loop (limited to 360 frames for output)
running = True
frame_count = 0
max_frames = 360  # Match rotation steps
while running and frame_count < max_frames:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Draw background
    glDisable(GL_DEPTH_TEST)
    glBindTexture(GL_TEXTURE_2D, bg_texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-2.5, -2.5, 0)
    glTexCoord2f(1, 0); glVertex3f(2.5, -2.5, 0)
    glTexCoord2f(1, 1); glVertex3f(2.5, 2.5, 0)
    glTexCoord2f(0, 1); glVertex3f(-2.5, 2.5, 0)
    glEnd()

    # Draw 3D clock
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPushMatrix()
    rot_matrix = rotation_matrices[rot_idx]
    glMultMatrixf(np.array([
        [rot_matrix[0, 0], rot_matrix[1, 0], rot_matrix[2, 0], 0],
        [rot_matrix[0, 1], rot_matrix[1, 1], rot_matrix[2, 1], 0],
        [rot_matrix[0, 2], rot_matrix[1, 2], rot_matrix[2, 2], 0],
        [0, 0, 0, 1]
    ], dtype=np.float32).T.flatten())
    glBindTexture(GL_TEXTURE_2D, gif_textures[frame_idx])
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-1, -1, 0)
    glTexCoord2f(1, 0); glVertex3f(1, -1, 0)
    glTexCoord2f(1, 1); glVertex3f(1, 1, 0)
    glTexCoord2f(0, 1); glVertex3f(-1, 1, 0)
    glEnd()
    glPopMatrix()

    # Capture frame
    frame_data = glReadPixels(0, 0, bg_width, bg_height, GL_RGB, GL_UNSIGNED_BYTE)
    frame_array = np.frombuffer(frame_data, dtype=np.uint8).reshape(bg_height, bg_width, 3)
    frame_array = frame_array[::-1]  # Flip Y-axis back
    frames.append(frame_array)

    # Update animation
    rot_idx = (rot_idx + 1) % num_steps
    frame_idx = (frame_idx + 1) % len(gif_textures)
    pygame.display.flip()
    clock.tick(30)  # ~30 FPS
    frame_count += 1

# Save as MP4 and GIF
imageio.mimwrite('3d_clock_overlay.mp4', frames, fps=30)
imageio.mimwrite('3d_clock_overlay.gif', frames, fps=30)

pygame.quit()
