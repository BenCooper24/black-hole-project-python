# camera.py

# Import necessary modules
import numpy as np
import pygame

class Camera:

    # Initialize the camera with default parameters
    def __init__(self):

        """

        Initialize camera parameters

        Inputs: none

        Outputs: none

        """

        # Camera polar coordinates
        self.radius = 50
        self.theta = 0
        self.phi = 0

        # Camera control parameters
        self.fov = np.radians(50)
        self.mouse_sensitivity = 0.005
        self.dragging = False
        self._dirty = True


    # Handle mouse events for camera control
    def handle_event(self, event):

        """ 

        Handle mouse events to control camera orientation

        Inputs: event (pygame event)

        Outputs: none

        """

        # If mouse button pressed, start dragging
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.dragging = True
        
        # If mouse button released, stop dragging
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        # If mouse moved while dragging, update camera orientation
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx, dy = event.rel
            self.theta += dx * self.mouse_sensitivity
            self.phi -= dy * self.mouse_sensitivity
            self.phi = max(-np.pi/2, min(np.pi/2, self.phi))
            self._dirty = True


    # Update the camera position based on time delta
    def update(self, dt):
        pass  


    # Get the Cartesian coordinates of the camera
    def position(self):

        """ 

        Convert spherical coordinates to Cartesian coordinates

        Inputs: none

        Outputs: numpy array of camera position [x, y, z]

        """
        
        # Convert spherical coordinates to Cartesian coordinates
        x = self.radius * np.cos(self.phi) * np.cos(self.theta)
        y = self.radius * np.sin(self.phi)
        z = self.radius * np.cos(self.phi) * np.sin(self.theta)

        # Return position as numpy array
        return np.array([x, y, z])


    # Draw camera information on the screen
    def draw(self, screen, width, height):

        """

        Draw camera position text on the screen

        Inputs: screen (pygame surface), width (int), height (int)

        Outputs: none

        """
        # Get camera position
        pos = self.position()

        # Render position text
        text = f"Camera pos: {pos.round(2)}"

        # Get font and render text
        font = pygame.font.SysFont(None, 24)
        img = font.render(text, True, (255, 255, 255))
        screen.blit(img, (10, 10))


    # Get camera basis vectors
    def basis_vectors(self):
        """

        Returns camera basis vectors: forward, right, up

        Inputs: none

        Outputs: forward, right, up vectors as numpy arrays

        """

        # Get camera position
        pos = self.position()

        # Compute forward vector looking at origin
        forward = -pos / np.linalg.norm(pos)

        # Compute right vector as cross product with world up
        world_up = np.array([0, 1, 0])
        right = np.cross(world_up, forward)
        right /= np.linalg.norm(right)

        # Compute up vector as cross product with forward and right
        up = np.cross(forward, right)

        # Return basis vectors
        return forward, right, up

    
    # Get ray direction through pixel
    def ray_direction(self, px, py, img_w, img_h):

        """
        
        Compute the ray direction from the camera through pixel (px, py)

        Inputs: px (int), py (int), img_w (int), img_h (int)

        Outputs: numpy array of ray direction [dx, dy, dz]

        """

        # Get camera basis vectors
        forward, right, up = self.basis_vectors()

        # Convert pixel coord to Normalized Device Coordinates (NDC) in [-1, 1]
        # Note: +0.5 aims at the pixel center
        x_ndc = ( (px + 0.5) / img_w ) * 2.0 - 1.0
        y_ndc = 1.0 - ( (py + 0.5) / img_h ) * 2.0

        # Account for aspect ratio
        aspect = img_w / img_h

        # Convert NDC to a direction in camera space using FOV
        tan_half_fov = np.tan(self.fov / 2.0)
        x_cam = x_ndc * aspect * tan_half_fov
        y_cam = y_ndc * tan_half_fov
        z_cam = 1.0

        # Convert camera-space direction to world-space direction
        dir_world = (x_cam * right) + (y_cam * up) + (z_cam * forward)
        dir_world /= np.linalg.norm(dir_world)
        return dir_world


    # Check and consume dirty flag
    def consume_dirty(self):

        """

        Check if the camera state was dirty and reset the flag

        Inputs: none

        Outputs: was_dirty (bool)

        """

        # Check if the camera state was dirty
        was_dirty = self._dirty

        # Reset dirty flag
        self._dirty = False

        # Return whether it was dirty
        return was_dirty
