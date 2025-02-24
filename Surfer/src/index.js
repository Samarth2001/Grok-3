import Phaser from "phaser";

// MainScene: gameplay scene
class MainScene extends Phaser.Scene {
  constructor() {
    super("MainScene");
  }

  create() {
    // Flag to prevent multiple game-over transitions
    this.isGameOver = false;

    // Create textures programmatically
    this.createTextures();

    // Create dynamic ocean background
    this.createOceanBackground();

    // Create the surfer sprite
    this.surfer = this.textures.exists("surfer")
      ? this.physics.add.sprite(150, 300, "surfer")
      : this.physics.add.rectangle(150, 300, 64, 64, 0x000000); // Black rectangle fallback
    this.surfer.body.allowGravity = false;
    this.surfer.setCollideWorldBounds(true);

    // Movement variables
    this.inputDirectionX = 0; // Left/right (-1, 0, 1)
    this.inputDirectionY = 0; // Up/down (-1 for duck, 1 for jump, 0 for none)
    this.surferVelocityX = 0; // Horizontal speed (px/s)
    this.surferVelocityY = 0; // Vertical speed for jump/duck (px/s)
    this.maxSpeedX = 200; // Max horizontal speed (px/s)
    this.accelerationRateX = 500; // Horizontal acceleration (px/s²)
    this.jumpSpeed = -300; // Jump velocity (upward, px/s)
    this.duckSpeed = 100; // Downward speed for ducking (px/s)
    this.isJumping = false; // Track jump state
    this.isDucking = false; // Track duck state

    // Score initialization
    this.score = 0;
    this.scoreText = this.add.text(16, 16, "Score: 0", {
      fontSize: "32px",
      fill: "#FFF",
    });

    // Physics groups for obstacles and collectibles
    this.obstacles = this.physics.add.group();
    this.collectibles = this.physics.add.group();

    // Collision setup
    this.physics.add.overlap(
      this.surfer,
      this.obstacles,
      this.hitObstacle,
      null,
      this
    );
    this.physics.add.overlap(
      this.surfer,
      this.collectibles,
      this.collectItem,
      null,
      this
    );

    // Timers for scoring and spawning
    this.scoreTimer = this.time.addEvent({
      delay: 1000, // 1 second
      callback: this.incrementScore,
      callbackScope: this,
      loop: true,
    });

    this.spawnObstacleTimer = this.time.addEvent({
      delay: 2000, // Initial 2 seconds
      callback: this.spawnObstacle,
      callbackScope: this,
      loop: false,
    });

    this.spawnCollectibleTimer = this.time.addEvent({
      delay: 5000, // 5 seconds
      callback: this.spawnCollectible,
      callbackScope: this,
      loop: true,
    });

    // Input setup (keyboard and touch)
    this.cursors = this.input.keyboard.createCursorKeys();
    this.swipeStartX = null;
    this.swipeStartY = null;

    this.input.on(
      "pointerdown",
      (pointer) => {
        this.swipeStartX = pointer.x;
        this.swipeStartY = pointer.y;
      },
      this
    );

    this.input.on(
      "pointerup",
      (pointer) => {
        if (!this.swipeStartX || !this.swipeStartY) return;
        let swipeDistanceX = pointer.x - this.swipeStartX;
        let swipeDistanceY = pointer.y - this.swipeStartY;
        const swipeThreshold = 20;

        if (Math.abs(swipeDistanceX) > Math.abs(swipeDistanceY)) {
          // Horizontal swipe (left/right)
          if (swipeDistanceX > swipeThreshold) {
            this.inputDirectionX = 1;
          } else if (swipeDistanceX < -swipeThreshold) {
            this.inputDirectionX = -1;
          }
        } else {
          // Vertical swipe (up/down)
          if (swipeDistanceY < -swipeThreshold) {
            this.inputDirectionY = 1; // Jump
          } else if (swipeDistanceY > swipeThreshold) {
            this.inputDirectionY = -1; // Duck
          }
        }

        // Reset input after a short delay
        this.time.delayedCall(
          200,
          () => {
            this.inputDirectionX = 0;
            this.inputDirectionY = 0;
          },
          [],
          this
        );

        this.swipeStartX = null;
        this.swipeStartY = null;
      },
      this
    );
  }

  createTextures() {
    // Ocean texture (simple blue gradient for fallback)
    try {
      let oceanCanvas = this.textures.createCanvas("ocean", 100, 100);
      let ctx = oceanCanvas.context;
      let gradient = ctx.createLinearGradient(0, 0, 0, 100);
      gradient.addColorStop(0, "#00008B"); // Deep blue
      gradient.addColorStop(1, "#87CEEB"); // Light blue
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 100, 100);
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 1;
      for (let y = 20; y < 100; y += 20) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(100, y);
        ctx.stroke();
      }
    } catch (e) {
      console.warn("Failed to create ocean texture:", e);
    }

    // Surfer texture (stick figure on surfboard)
    try {
      let surferCanvas = this.textures.createCanvas("surfer", 64, 64);
      let ctx = surferCanvas.context;
      ctx.fillStyle = "#000000";
      ctx.beginPath();
      ctx.arc(32, 20, 10, 0, 2 * Math.PI); // Head
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(32, 30);
      ctx.lineTo(32, 50); // Body
      ctx.stroke();
      ctx.moveTo(32, 35);
      ctx.lineTo(22, 45); // Left arm
      ctx.moveTo(32, 35);
      ctx.lineTo(42, 45); // Right arm
      ctx.moveTo(32, 50);
      ctx.lineTo(27, 60); // Left leg
      ctx.moveTo(32, 50);
      ctx.lineTo(37, 60); // Right leg
      ctx.stroke();
      ctx.beginPath();
      ctx.ellipse(32, 60, 20, 5, 0, 0, 2 * Math.PI); // Surfboard
      ctx.fillStyle = "#8B4513"; // Brown surfboard
      ctx.fill();
    } catch (e) {
      console.warn("Failed to create surfer texture:", e);
    }

    // Rock texture (obstacle)
    try {
      let rockCanvas = this.textures.createCanvas("rock", 50, 50);
      let ctx = rockCanvas.context;
      ctx.fillStyle = "#808080"; // Gray rock
      ctx.beginPath();
      ctx.arc(25, 25, 20, 0, 2 * Math.PI);
      ctx.fill();
    } catch (e) {
      console.warn("Failed to create rock texture:", e);
    }

    // Shark texture (obstacle)
    try {
      let sharkCanvas = this.textures.createCanvas("shark", 60, 30);
      let ctx = sharkCanvas.context;
      ctx.fillStyle = "#000000"; // Black shark
      ctx.beginPath();
      ctx.moveTo(0, 15); // Tail
      ctx.lineTo(20, 5);
      ctx.lineTo(20, 25);
      ctx.lineTo(0, 15);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(20, 15); // Body
      ctx.quadraticCurveTo(40, 5, 60, 15); // Nose
      ctx.lineTo(50, 25); // Fin
      ctx.lineTo(40, 15);
      ctx.lineTo(50, 5);
      ctx.lineTo(60, 15);
      ctx.fill();
    } catch (e) {
      console.warn("Failed to create shark texture:", e);
    }

    // Seashell texture (collectible)
    try {
      let seashellCanvas = this.textures.createCanvas("seashell", 20, 20);
      let ctx = seashellCanvas.context;
      ctx.fillStyle = "#FFD700"; // Gold seashell
      ctx.beginPath();
      ctx.moveTo(10, 0);
      ctx.lineTo(12, 8);
      ctx.lineTo(20, 10);
      ctx.lineTo(12, 12);
      ctx.lineTo(10, 20);
      ctx.lineTo(8, 12);
      ctx.lineTo(0, 10);
      ctx.lineTo(8, 8);
      ctx.closePath();
      ctx.fill();
    } catch (e) {
      console.warn("Failed to create seashell texture:", e);
    }
  }

  createOceanBackground() {
    // Create a tile sprite with a dynamic ocean effect
    let oceanCanvas = this.textures.createCanvas("oceanDynamic", 100, 100);
    let ctx = oceanCanvas.context;
    let gradient = ctx.createLinearGradient(0, 0, 0, 100);
    gradient.addColorStop(0, "#00008B"); // Deep blue
    gradient.addColorStop(1, "#87CEEB"); // Light blue
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 100, 100);
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 1;
    for (let y = 20; y < 100; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(100, y);
      ctx.stroke();
    }

    this.background = this.add
      .tileSprite(0, 0, 800, 600, "oceanDynamic")
      .setOrigin(0, 0);
    this.backgroundWaveOffset = 0;

    // Add particle system for subtle water ripples
    this.particles = this.add.particles("oceanDynamic");
    this.emitter = this.particles.createEmitter({
      x: { min: 0, max: 800 },
      y: { min: 0, max: 600 },
      lifespan: 2000,
      speed: { min: -50, max: 50 },
      angle: { min: 0, max: 360 },
      scale: { start: 0.1, end: 0 },
      quantity: 5,
      frequency: 100,
      alpha: { start: 0.5, end: 0 },
      tint: 0x00008b, // Deep blue for ripples
    });
  }

  update(time, delta) {
    if (this.isGameOver) return;

    let deltaSec = delta / 1000;

    // Animate background waves
    this.backgroundWaveOffset += 50 * deltaSec; // Wave speed (px/s)
    this.background.tilePositionX = this.backgroundWaveOffset % 100;

    // Handle horizontal input (left/right)
    let currentInputX = this.inputDirectionX;
    if (this.cursors.left.isDown) currentInputX = -1;
    else if (this.cursors.right.isDown) currentInputX = 1;

    // Update horizontal velocity with inertia
    if (currentInputX !== 0) {
      this.surferVelocityX += currentInputX * this.accelerationRateX * deltaSec;
      this.surferVelocityX = Phaser.Math.Clamp(
        this.surferVelocityX,
        -this.maxSpeedX,
        this.maxSpeedX
      );
    } else {
      if (this.surferVelocityX > 0) {
        this.surferVelocityX -= this.accelerationRateX * deltaSec;
        if (this.surferVelocityX < 0) this.surferVelocityX = 0;
      } else if (this.surferVelocityX < 0) {
        this.surferVelocityX += this.accelerationRateX * deltaSec;
        if (this.surferVelocityX > 0) this.surferVelocityX = 0;
      }
    }

    // Handle vertical input (jump/duck)
    if (this.inputDirectionY === 1 && !this.isJumping) {
      // Jump
      this.surferVelocityY = this.jumpSpeed;
      this.isJumping = true;
    } else if (this.inputDirectionY === -1 && !this.isDucking) {
      // Duck
      this.surferVelocityY = this.duckSpeed;
      this.isDucking = true;
    }

    // Apply velocities
    this.surfer.setVelocityX(this.surferVelocityX);
    this.surfer.setVelocityY(this.surferVelocityY);

    // Update surfer position and handle jumping/ducking
    let surferY = this.surfer.y;
    if (this.isJumping) {
      surferY += this.surferVelocityY * deltaSec;
      if (surferY <= 200) {
        // Max jump height
        surferY = 200;
        this.surferVelocityY = 0;
      }
    } else if (this.isDucking) {
      surferY += this.surferVelocityY * deltaSec;
      if (surferY >= 400) {
        // Max duck height
        surferY = 400;
        this.surferVelocityY = 0;
      }
    } else {
      // Return to default position (300)
      if (surferY < 300) {
        surferY += 300 * deltaSec; // Gravity-like return
        if (surferY > 300) surferY = 300;
      } else if (surferY > 300) {
        surferY -= 300 * deltaSec;
        if (surferY < 300) surferY = 300;
      }
      this.surferVelocityY = 0;
    }

    // Set surfer position
    this.surfer.y = surferY;
    if (surferY === 300) {
      this.isJumping = false;
      this.isDucking = false;
    }

    // Enforce horizontal boundaries
    if (this.surfer.x < 100) {
      this.surfer.x = 100;
      this.surferVelocityX = 0;
      this.surfer.setVelocityX(0);
    } else if (this.surfer.x > 700) {
      this.surfer.x = 700;
      this.surferVelocityX = 0;
      this.surfer.setVelocityX(0);
    }

    // Clean up off-screen objects
    this.obstacles.getChildren().forEach((obstacle) => {
      if (obstacle.active && obstacle.x < -60) obstacle.destroy();
    });
    this.collectibles.getChildren().forEach((item) => {
      if (item.active && item.x < -20) item.destroy();
    });
  }

  incrementScore() {
    if (!this.isGameOver) {
      this.score += 1;
      this.scoreText.setText("Score: " + this.score);
    }
  }

  spawnObstacle() {
    if (this.isGameOver) return;
    let y = Phaser.Math.Between(200, 400); // Adjust for jump/duck range
    let obstacleType = Phaser.Math.Between(0, 1); // 0 for rock, 1 for shark
    let obstacle = this.textures.exists(obstacleType ? "shark" : "rock")
      ? this.obstacles.create(850, y, obstacleType ? "shark" : "rock")
      : this.obstacles
          .create(850, y)
          .setSize(obstacleType ? 60 : 50, obstacleType ? 30 : 50)
          .setDisplaySize(obstacleType ? 60 : 50, obstacleType ? 30 : 50)
          .setTint(obstacleType ? 0x000000 : 0x808080); // Black for shark, gray for rock
    obstacle.body.allowGravity = false;
    obstacle.setVelocityX(-200);

    // Dynamic spawn delay based on score
    let nextDelay = this.score >= 200 ? 1000 : this.score >= 100 ? 1500 : 2000;
    this.spawnObstacleTimer = this.time.addEvent({
      delay: nextDelay,
      callback: this.spawnObstacle,
      callbackScope: this,
      loop: false,
    });
  }

  spawnCollectible() {
    if (this.isGameOver) return;
    let y = Phaser.Math.Between(200, 400);
    let collectible = this.textures.exists("seashell")
      ? this.collectibles.create(850, y, "seashell")
      : this.collectibles
          .create(850, y)
          .setSize(20, 20)
          .setDisplaySize(20, 20)
          .setTint(0xffd700); // Gold for seashell
    collectible.body.allowGravity = false;
    collectible.setVelocityX(-200);
  }

  hitObstacle(surfer, obstacle) {
    if (!this.isGameOver && obstacle.active) {
      this.isGameOver = true;
      this.scene.start("GameOverScene", { score: this.score });
    }
  }

  collectItem(surfer, collectible) {
    if (collectible.active) {
      this.score += 10;
      this.scoreText.setText("Score: " + this.score);
      collectible.destroy();
    }
  }

  shutdown() {
    // Clean up timers
    if (this.scoreTimer) this.time.removeEvent(this.scoreTimer);
    if (this.spawnObstacleTimer) this.time.removeEvent(this.spawnObstacleTimer);
    if (this.spawnCollectibleTimer)
      this.time.removeEvent(this.spawnCollectibleTimer);

    // Clear physics groups
    if (this.obstacles) this.obstacles.clear(true, true);
    if (this.collectibles) this.collectibles.clear(true, true);

    // Clean up background and particles
    if (this.background) this.background.destroy();
    if (this.particles) this.particles.destroy();
  }
}

// GameOverScene: end screen
class GameOverScene extends Phaser.Scene {
  constructor() {
    super("GameOverScene");
  }

  init(data) {
    this.finalScore = data.score || 0;
  }

  create() {
    this.add.text(300, 250, "Game Over", { fontSize: "48px", fill: "#FFF" });
    this.add.text(300, 320, "Score: " + this.finalScore, {
      fontSize: "32px",
      fill: "#FFF",
    });
    this.add
      .text(300, 400, "Restart", { fontSize: "32px", fill: "#0F0" })
      .setInteractive()
      .on("pointerdown", () => this.scene.start("MainScene"));
  }
}

// Game configuration
const config = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  physics: {
    default: "arcade",
    arcade: { debug: false },
  },
  scene: [MainScene, GameOverScene],
};

// Initialize game
const game = new Phaser.Game(config);
