import pygame
import sys

pygame.init()

W, H = 800, 600
CELL = 80
ROWS, COLS = 5, 5
MARGIN_X = (W - COLS * CELL) // 2
MARGIN_Y = 120
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (220, 50, 50)
GREEN = (50, 180, 80)
BLUE = (70, 130, 220)

# 修复后的方向定义： (行变化 dr, 列变化 dc)
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
ARROW_TEXT = {'U': '↑', 'D': '↓', 'L': '←', 'R': '→'}

# 重新设计的三个关卡，确保逻辑清晰，且都能通关
LEVELS = [
    # 第一关：两个箭头互不阻挡，先熟悉操作
    ["R....",
     ".....",
     ".....",
     ".....",
     "....U"],

    # 第二关：体验阻挡。R向右会被U挡住，需要先点U
    ["R...U",
     ".....",
     ".....",
     ".....",
     "D...L"],

    # 第三关：稍微增加一点挑战
    ["R..U.",
     ".....",
     "L..D.",
     ".....",
     "U..R."],
]


class Arrow:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.shake = 0
        self.x = MARGIN_X + col * CELL + CELL // 2
        self.y = MARGIN_Y + row * CELL + CELL // 2
        self.vx = 0
        self.vy = 0

    def start_fly(self):
        dr, dc = DIRS[self.direction]
        self.vx = dc * 18   # 列变化影响 x 轴
        self.vy = dr * 18   # 行变化影响 y 轴


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()
        # 修复 Python 3.13 下 SysFont 崩溃问题，直接指定 Windows 自带字体路径
        self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 26)
        self.big_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 46)

        self.state = "menu"
        self.level_index = 0
        self.max_mistakes = 3
        self.tip_text = ""
        self.tip_timer = 0
        self.reset_level()

    def reset_level(self):
        self.mistakes = 0
        self.arrows = []
        self.flying = []
        level = LEVELS[self.level_index]

        for r, row in enumerate(level):
            for c, ch in enumerate(row):
                if ch in DIRS:
                    self.arrows.append(Arrow(r, c, ch))

        self.state = "playing"

    def can_fly(self, arrow):
        dr, dc = DIRS[arrow.direction]
        r = arrow.row + dr
        c = arrow.col + dc

        while 0 <= r < ROWS and 0 <= c < COLS:
            for a in self.arrows:
                if a is not arrow and a.row == r and a.col == c:
                    return False
            r += dr
            c += dc

        return True

    def handle_click(self, pos):
        if self.state != "playing":
            return

        x, y = pos
        col = (x - MARGIN_X) // CELL
        row = (y - MARGIN_Y) // CELL

        if not (0 <= row < ROWS and 0 <= col < COLS):
            return

        for a in self.arrows:
            if a.row == row and a.col == col:
                if self.can_fly(a):
                    a.start_fly()
                    self.arrows.remove(a)
                    self.flying.append(a)
                else:
                    a.shake = 15
                    self.mistakes += 1
                    self.tip_text = "被阻挡！"
                    self.tip_timer = 60
                    if self.mistakes >= self.max_mistakes:
                        self.state = "lose"
                break

    def update(self):
        if self.tip_timer > 0:
            self.tip_timer -= 1

        for a in self.flying[:]:
            a.x += a.vx
            a.y += a.vy
            if a.x < -CELL or a.x > W + CELL or a.y < -CELL or a.y > H + CELL:
                self.flying.remove(a)

        for a in self.arrows:
            if a.shake > 0:
                a.shake -= 1

        if self.state == "playing" and not self.arrows and not self.flying:
            if self.level_index + 1 < len(LEVELS):
                self.state = "win"
            else:
                self.state = "all_win"

    def draw(self):
        self.screen.fill(WHITE)

        if self.state == "menu":
            title = self.big_font.render("一箭又一箭", True, BLACK)
            tip = self.font.render("按空格开始", True, BLACK)
            self.screen.blit(title, (W // 2 - title.get_width() // 2, 200))
            self.screen.blit(tip, (W // 2 - tip.get_width() // 2, 300))
            pygame.display.flip()
            return

        info = f"关卡 {self.level_index + 1}/{len(LEVELS)}   剩余箭头 {len(self.arrows)}   失误 {self.mistakes}/{self.max_mistakes}"
        self.screen.blit(self.font.render(info, True, BLACK), (20, 20))

        pygame.draw.rect(self.screen, GRAY, (W - 150, 20, 120, 40))
        self.screen.blit(self.font.render("重新开始", True, BLACK), (W - 140, 28))

        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(MARGIN_X + c * CELL, MARGIN_Y + r * CELL, CELL, CELL)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

        for a in self.arrows + self.flying:
            x, y = a.x, a.y
            if a.shake > 0:
                x += (a.shake % 2) * 6 - 3
            color = RED if a.shake > 0 else BLUE
            text = self.big_font.render(ARROW_TEXT[a.direction], True, color)
            self.screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

        if self.state == "win":
            txt = self.big_font.render("通关！按空格进入下一关", True, GREEN)
            self.screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2))
        elif self.state == "lose":
            txt = self.big_font.render("失败！按 R 重开", True, RED)
            self.screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2))
        elif self.state == "all_win":
            txt = self.big_font.render("全部通关！按 R 重开", True, GREEN)
            self.screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2))

        if self.tip_timer > 0:
            tip = self.font.render(self.tip_text, True, RED)
            self.screen.blit(tip, (W // 2 - tip.get_width() // 2, H - 50))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.state == "menu" and event.key == pygame.K_SPACE:
                        self.reset_level()
                    elif self.state == "win" and event.key == pygame.K_SPACE:
                        self.level_index += 1
                        self.reset_level()
                    elif self.state in ("lose", "all_win") and event.key == pygame.K_r:
                        if self.state == "all_win":
                            self.level_index = 0
                        self.reset_level()

                if event.type == pygame.MOUSEBUTTONDOWN and self.state == "playing":
                    if W - 150 <= event.pos[0] <= W - 30 and 20 <= event.pos[1] <= 60:
                        self.reset_level()
                    else:
                        self.handle_click(event.pos)

            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()