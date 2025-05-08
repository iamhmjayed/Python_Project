import tkinter as tk
import random
from PIL import Image, ImageDraw, ImageTk

# Game settings
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
BIRD_SIZE = 30
PIPE_WIDTH = 70
GAP_SIZE = 180
GRAVITY = 0.25
JUMP_STRENGTH = -6
BASE_SPEED = 3
SPEED_INCREMENT = 0.002


class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird - Enhanced Edition")

        # Try to load images
        self.use_images = False
        try:
            self.bird_img_up = self.create_bird_image(angle=-20)
            self.bird_img_down = self.create_bird_image(angle=20)
            self.bird_img_normal = self.create_bird_image(angle=0)
            self.pipe_top_img = self.create_pipe_image(top=True)
            self.pipe_bottom_img = self.create_pipe_image(top=False)
            self.use_images = True
        except:
            self.use_images = False

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#87CEEB", highlightthickness=0)
        self.canvas.pack()

        # Game state variables
        self.game_state = "start"  # start, running, over
        self.score = 0
        self.high_score = 0
        self.speed = BASE_SPEED

        # Bird properties
        self.bird_velocity = 0
        self.bird_rotation = 0
        self.bird_flap = False

        # Game elements
        self.bird = None
        self.pipes = []
        self.background_elements = []

        # Create game elements
        self.create_background()
        self.create_start_screen()

        # Bind controls
        self.root.bind("<space>", self.handle_space)
        self.root.bind("<Button-1>", self.handle_space)

        # Start game loop
        self.update_game()

    def create_bird_image(self, angle=0):
        """Create a simple bird image with rotation"""
        size = BIRD_SIZE * 2
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Body (yellow oval)
        body_pos = (size // 4, size // 4, size * 3 // 4, size * 3 // 4)
        draw.ellipse(body_pos, fill="yellow")

        # Eye
        eye_pos = (size // 2 + 5, size // 2 - 5, size // 2 + 10, size // 2)
        draw.ellipse(eye_pos, fill="black")

        # Beak
        beak_pos = [(size * 3 // 4, size // 2), (size * 4 // 4, size // 2 - 5), (size * 4 // 4, size // 2 + 5)]
        draw.polygon(beak_pos, fill="orange")

        # Wings
        wing_y = size // 2
        wing_left = [(size // 4 + 5, wing_y), (size // 4 - 10, wing_y - 15), (size // 4 - 10, wing_y + 15)]
        wing_right = [(size * 3 // 4 - 5, wing_y), (size * 3 // 4 + 10, wing_y - 15), (size * 3 // 4 + 10, wing_y + 15)]
        draw.polygon(wing_left, fill="yellow")
        draw.polygon(wing_right, fill="yellow")

        # Rotate the image
        if angle != 0:
            img = img.rotate(angle, center=(size // 2, size // 2))

        return ImageTk.PhotoImage(img)

    def create_pipe_image(self, top=False):
        """Create a pipe image with gradient"""
        width, height = PIPE_WIDTH, WINDOW_HEIGHT
        img = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Create gradient
        for y in range(height):
            green = 100 + int(100 * (y / height))
            color = (0, min(255, green), 0)
            draw.line([(0, y), (width, y)], fill=color)

        # Add pipe rim
        rim_height = 20
        rim_color = (0, 180, 0)
        if top:
            draw.rectangle([(0, height - rim_height), (width, height)], fill=rim_color)
        else:
            draw.rectangle([(0, 0), (width, rim_height)], fill=rim_color)

        return ImageTk.PhotoImage(img)

    def create_background(self):
        """Create background elements (clouds)"""
        self.canvas.delete("background")
        for _ in range(5):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT // 2)
            size = random.randint(30, 70)
            cloud = self.canvas.create_oval(
                x, y, x + size, y + size // 2,
                fill="white", outline="white", tags="background"
            )
            self.background_elements.append(cloud)

    def create_start_screen(self):
        """Create the start screen"""
        self.canvas.delete("all")
        self.background_elements = []
        self.create_background()

        # Title
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3,
            text="FLAPPY BIRD", font=("Arial", 32, "bold"),
            fill="white", tags="start"
        )

        # Instructions
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
            text="Press SPACE or CLICK to start",
            font=("Arial", 16), fill="black", tags="start"
        )

        # High score
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3,
            text=f"High Score: {self.high_score}",
            font=("Arial", 14), fill="black", tags="start"
        )

        # Create bird preview
        if self.use_images:
            self.bird = self.canvas.create_image(
                WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50,
                image=self.bird_img_normal, tags="start"
            )
        else:
            self.bird = self.canvas.create_oval(
                WINDOW_WIDTH // 2 - BIRD_SIZE // 2, WINDOW_HEIGHT // 2 + 50 - BIRD_SIZE // 2,
                WINDOW_WIDTH // 2 + BIRD_SIZE // 2, WINDOW_HEIGHT // 2 + 50 + BIRD_SIZE // 2,
                fill="yellow", tags="start"
            )

    def start_game(self):
        """Start a new game"""
        self.game_state = "running"
        self.score = 0
        self.speed = BASE_SPEED
        self.bird_velocity = 0
        self.bird_rotation = 0
        self.pipes = []

        # Clear canvas and create initial elements
        self.canvas.delete("all")
        self.background_elements = []
        self.create_background()

        # Create bird
        bird_x, bird_y = WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2
        if self.use_images:
            self.bird = self.canvas.create_image(bird_x, bird_y, image=self.bird_img_normal)
        else:
            self.bird = self.canvas.create_oval(
                bird_x - BIRD_SIZE // 2, bird_y - BIRD_SIZE // 2,
                bird_x + BIRD_SIZE // 2, bird_y + BIRD_SIZE // 2,
                fill="yellow"
            )

        # Score display
        self.score_text = self.canvas.create_text(
            WINDOW_WIDTH // 2, 30,
            text=f"{self.score}", font=("Arial", 24, "bold"),
            fill="white"
        )

        # Start pipe spawning
        self.spawn_pipe()

    def spawn_pipe(self):
        """Spawn a new pipe pair"""
        if self.game_state != "running":
            return

        # Calculate gap position
        min_gap_y = WINDOW_HEIGHT * 0.2
        max_gap_y = WINDOW_HEIGHT * 0.7
        gap_y = random.randint(int(min_gap_y), int(max_gap_y))

        # Create pipes
        if self.use_images:
            top_pipe = self.canvas.create_image(
                WINDOW_WIDTH, gap_y - WINDOW_HEIGHT // 2,
                image=self.pipe_top_img, anchor="s"
            )
            bottom_pipe = self.canvas.create_image(
                WINDOW_WIDTH, gap_y + GAP_SIZE + WINDOW_HEIGHT // 2,
                image=self.pipe_bottom_img, anchor="n"
            )
        else:
            top_pipe = self.canvas.create_rectangle(
                WINDOW_WIDTH, 0, WINDOW_WIDTH + PIPE_WIDTH, gap_y,
                fill="green", outline="black"
            )
            bottom_pipe = self.canvas.create_rectangle(
                WINDOW_WIDTH, gap_y + GAP_SIZE,
                WINDOW_WIDTH + PIPE_WIDTH, WINDOW_HEIGHT,
                fill="green", outline="black"
            )

        self.pipes.append((top_pipe, bottom_pipe, False))  # Last value tracks if scored

        # Schedule next pipe
        if self.game_state == "running":
            delay = max(1000, 2000 - self.score * 10)
            self.root.after(delay, self.spawn_pipe)

    def update_game(self):
        """Main game update loop"""
        if self.game_state == "running":
            self.update_bird()
            self.update_pipes()
            self.update_background()
            self.check_collisions()

        # Schedule next update
        self.root.after(16, self.update_game)

    def update_bird(self):
        """Update bird position and rotation"""
        if not self.bird:
            return

        # Apply gravity
        self.bird_velocity += GRAVITY
        self.bird_velocity = min(self.bird_velocity, 10)  # Terminal velocity

        # Update position
        bird_coords = self.canvas.coords(self.bird)
        if not bird_coords:  # Bird object doesn't exist
            return

        self.canvas.move(self.bird, 0, self.bird_velocity)

        # Update rotation based on velocity
        self.bird_rotation = max(-90, min(45, self.bird_velocity * -10))

        # Update bird image if using images
        if self.use_images:
            if self.bird_flap:
                self.canvas.itemconfig(self.bird, image=self.bird_img_up)
                self.bird_flap = False
            elif self.bird_velocity < 0:
                self.canvas.itemconfig(self.bird, image=self.bird_img_up)
            elif self.bird_velocity > 5:
                self.canvas.itemconfig(self.bird, image=self.bird_img_down)
            else:
                self.canvas.itemconfig(self.bird, image=self.bird_img_normal)

        # Keep bird within screen bounds (top only)
        if len(bird_coords) >= 2 and bird_coords[1] < 0:
            self.canvas.move(self.bird, 0, -bird_coords[1])
            self.bird_velocity = 0

    def update_pipes(self):
        """Update pipe positions and check scoring"""
        self.speed += SPEED_INCREMENT  # Gradually increase speed

        new_pipes = []
        for top_pipe, bottom_pipe, scored in self.pipes:
            # Move pipes
            self.canvas.move(top_pipe, -self.speed, 0)
            self.canvas.move(bottom_pipe, -self.speed, 0)

            # Get pipe position
            top_coords = self.canvas.coords(top_pipe)

            # Check if pipe is off screen
            if not top_coords or top_coords[0] + PIPE_WIDTH < 0:
                self.canvas.delete(top_pipe)
                self.canvas.delete(bottom_pipe)
                continue

            new_pipes.append((top_pipe, bottom_pipe, scored))

            # Check for scoring
            bird_coords = self.canvas.coords(self.bird)
            if bird_coords and not scored and top_coords[0] + PIPE_WIDTH < bird_coords[0]:
                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"{self.score}")
                new_pipes[-1] = (top_pipe, bottom_pipe, True)  # Mark as scored

        self.pipes = new_pipes

    def update_background(self):
        """Update background elements (clouds)"""
        for cloud in self.background_elements:
            self.canvas.move(cloud, -0.5, 0)
            coords = self.canvas.coords(cloud)
            if not coords or coords[2] < 0:
                # Move cloud to right side
                self.canvas.move(cloud, WINDOW_WIDTH + random.randint(50, 100), 0)

    def check_collisions(self):
        """Check for collisions with pipes and screen bounds"""
        if not self.bird:
            return

        bird_coords = self.canvas.coords(self.bird)
        if not bird_coords or len(bird_coords) < 4:  # Check if bird exists and has valid coordinates
            return

        # Check ground collision
        if bird_coords[3] > WINDOW_HEIGHT:
            return self.game_over()

        # Check pipe collisions
        for top_pipe, bottom_pipe, _ in self.pipes:
            top_coords = self.canvas.coords(top_pipe)
            bottom_coords = self.canvas.coords(bottom_pipe)

            if (top_coords and self.rect_collision(bird_coords, top_coords)) or \
               (bottom_coords and self.rect_collision(bird_coords, bottom_coords)):
                return self.game_over()

    def rect_collision(self, rect1, rect2):
        """Improved rectangle collision detection"""
        if not rect1 or not rect2 or len(rect1) < 4 or len(rect2) < 4:
            return False

        return not (rect1[2] < rect2[0] or
                   rect1[0] > rect2[2] or
                   rect1[3] < rect2[1] or
                   rect1[1] > rect2[3])

    def handle_space(self, event):
        """Handle space bar or mouse click"""
        if self.game_state == "start":
            self.start_game()
        elif self.game_state == "running":
            self.bird_velocity = JUMP_STRENGTH
            self.bird_flap = True
        elif self.game_state == "over":
            self.create_start_screen()
            self.game_state = "start"

    def game_over(self):
        """Handle game over"""
        self.game_state = "over"

        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score

        # Create game over screen
        self.canvas.create_rectangle(
            WINDOW_WIDTH // 4, WINDOW_HEIGHT // 3,
            WINDOW_WIDTH * 3 // 4, WINDOW_HEIGHT * 2 // 3,
            fill="white", outline="black", width=2
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30,
            text="GAME OVER", font=("Arial", 24, "bold"),
            fill="red"
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
            text=f"Score: {self.score}", font=("Arial", 18),
            fill="black"
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30,
            text=f"High Score: {self.high_score}", font=("Arial", 14),
            fill="black"
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70,
            text="Click or SPACE to restart", font=("Arial", 12),
            fill="blue"
        )


if __name__ == "__main__":
    root = tk.Tk()
    game = FlappyBirdGame(root)
    root.mainloop()