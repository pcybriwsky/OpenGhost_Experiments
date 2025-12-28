#!/usr/bin/env python3

"""
Snowflakes visualization with py5

Optimized for Pepper's Ghost effect: black background, neon blue snowflakes
"""

from py5 import *
import py5
import random

# Display settings
WIDTH = 720
HEIGHT = 720
NUM_SNOWFLAKES = 50

# Snowflake class - each snowflake has a unique pattern
class Snowflake:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = random.uniform(0.5, 2)
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.02, 0.02)
        
        # Create unique snowflake pattern
        self.branches = random.randint(6, 11)  # 6-11 branches
        self.arm_length = size * random.uniform(0.8, 1.2)
        self.complexity = random.randint(2, 4)  # 2-4 levels of detail
        self.pattern = random.randint(0, 3)  # Different pattern types (0-3)
    
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        
        # Wrap around when off screen
        if self.y > HEIGHT + self.size * 2:
            self.y = -self.size * 2
            self.x = random.uniform(0, WIDTH)
    
    def draw(self):
        push_matrix()
        translate(self.x, self.y)
        rotate(self.rotation)
        
        # Neon blue color (bright cyan)
        stroke(0, 255, 255)  # Bright cyan/blue
        stroke_weight(1.5)
        no_fill()
        
        # Draw snowflake based on pattern type
        if self.pattern == 0:
            self.draw_classic()
        elif self.pattern == 1:
            self.draw_star()
        elif self.pattern == 2:
            self.draw_crystal()
        else:  # pattern == 3
            self.draw_fractal()
        
        pop_matrix()
    
    def draw_classic(self):
        """Classic 6-pointed snowflake"""
        for i in range(self.branches):
            angle = (TWO_PI / self.branches) * i
            push_matrix()
            rotate(angle)
            
            # Main branch
            line(0, 0, 0, -self.arm_length)
            
            # Side branches
            for j in range(1, self.complexity + 1):
                branch_pos = (self.arm_length / (self.complexity + 1)) * j
                branch_len = self.size * 0.3 * (1 - j * 0.2)
                
                # Left branch
                push_matrix()
                translate(0, -branch_pos)
                rotate(-PI / 6)
                line(0, 0, 0, -branch_len)
                pop_matrix()
                
                # Right branch
                push_matrix()
                translate(0, -branch_pos)
                rotate(PI / 6)
                line(0, 0, 0, -branch_len)
                pop_matrix()
            
            pop_matrix()
        
        # Center hexagon
        begin_shape()
        for i in range(6):
            angle = (TWO_PI / 6) * i
            r = self.size * 0.15
            vertex(cos(angle) * r, sin(angle) * r)
        end_shape(CLOSE)
    
    def draw_star(self):
        """Star-like pattern"""
        for i in range(self.branches):
            angle = (TWO_PI / self.branches) * i
            push_matrix()
            rotate(angle)
            
            # Main arm
            line(0, 0, 0, -self.arm_length)
            
            # Star points along the arm
            for j in range(1, self.complexity + 1):
                pos = (self.arm_length / (self.complexity + 1)) * j
                point_size = self.size * 0.2
                
                push_matrix()
                translate(0, -pos)
                begin_shape()
                for k in range(5):
                    a = (TWO_PI / 5) * k - PI / 2
                    r = point_size
                    vertex(cos(a) * r, sin(a) * r)
                end_shape(CLOSE)
                pop_matrix()
            
            pop_matrix()
    
    def draw_crystal(self):
        """Crystal/geometric pattern"""
        for i in range(self.branches):
            angle = (TWO_PI / self.branches) * i
            push_matrix()
            rotate(angle)
            
            # Main branch with segments
            current_y = 0
            for j in range(self.complexity):
                segment_len = self.arm_length / self.complexity
                width = self.size * 0.1 * (1 - j * 0.15)
                
                begin_shape()
                vertex(-width, current_y)
                vertex(width, current_y)
                vertex(width * 0.5, current_y - segment_len)
                vertex(-width * 0.5, current_y - segment_len)
                end_shape(CLOSE)
                
                current_y -= segment_len
            
            # Side crystals
            for j in range(1, self.complexity):
                pos = (self.arm_length / self.complexity) * j
                crystal_size = self.size * 0.25
                
                # Left crystal
                push_matrix()
                translate(0, -pos)
                rotate(-PI / 4)
                self.draw_diamond(crystal_size)
                pop_matrix()
                
                # Right crystal
                push_matrix()
                translate(0, -pos)
                rotate(PI / 4)
                self.draw_diamond(crystal_size)
                pop_matrix()
            
            pop_matrix()
    
    def draw_diamond(self, size):
        """Helper method to draw a diamond shape"""
        begin_shape()
        vertex(0, -size)
        vertex(size * 0.7, 0)
        vertex(0, size)
        vertex(-size * 0.7, 0)
        end_shape(CLOSE)
    
    def draw_fractal(self):
        """Fractal-like recursive pattern"""
        def draw_branch(len_val, depth, max_depth):
            if depth > max_depth:
                return
            
            line(0, 0, 0, -len_val)
            
            if depth < max_depth:
                push_matrix()
                translate(0, -len_val)
                
                # Three sub-branches
                for i in range(3):
                    push_matrix()
                    rotate((i - 1) * PI / 6)
                    draw_branch(len_val * 0.6, depth + 1, max_depth)
                    pop_matrix()
                
                pop_matrix()
        
        for i in range(self.branches):
            angle = (TWO_PI / self.branches) * i
            push_matrix()
            rotate(angle)
            draw_branch(self.arm_length, 0, self.complexity)
            pop_matrix()


# Global snowflakes list
snowflakes = []


def settings():
    size(WIDTH, HEIGHT, py5.P2D)


def setup():
    global snowflakes
    color_mode(RGB, 255)
    frame_rate(60)
    
    # Pure black background for Pepper's Ghost
    background(0)
    
    # Create snowflakes
    snowflakes = []
    for i in range(NUM_SNOWFLAKES):
        x = random.uniform(0, WIDTH)
        y = random.uniform(-HEIGHT, 0)  # Start above screen
        size_val = random.uniform(15, 40)  # Distinct sizes
        snowflakes.append(Snowflake(x, y, size_val))


def draw():
    # Hide cursor for clean display
    no_cursor()
    
    # Pure black background (critical for Pepper's Ghost)
    background(0)
    
    # Update and draw all snowflakes
    for snowflake in snowflakes:
        snowflake.update()
        snowflake.draw()


def key_pressed():
    """Save frame with 's' key"""
    if key == 's' or key == 'S':
        save_frame("snowflakes.png")
        print("Frame saved as snowflakes.png")


run_sketch()

