import pygame, threading, sys
from style import Style
from pathfinder import PathFinder, Path

### Constants ###
SCREEN_SIZE = (800, 800)
PADDING = (5, 5, 100, 10)
TILE_SIZE = (20, 20)
SCREEN_BORDER = 5
FINDER_DELAY = 0.001
PATH_SIZE = (((SCREEN_SIZE[0]-2*SCREEN_BORDER-PADDING[1]-PADDING[3])//TILE_SIZE[0], (SCREEN_SIZE[1]-2*SCREEN_BORDER-PADDING[0]-PADDING[2])//TILE_SIZE[0]))

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Path Finder')

clock = pygame.time.Clock()

def get_click_coord(mx, my):
    col = (mx - PADDING[3] - SCREEN_BORDER) / TILE_SIZE[0]
    row = (my - PADDING[0] - SCREEN_BORDER) / TILE_SIZE[1]

    if col < 0 or col >= PATH_SIZE[0]:
        col = -1
    if row < 0 or row >= PATH_SIZE[1]:
        row = -1

    return int(col), int(row)

def write_text(text, x, y, font, size, color):
    text_font = pygame.font.SysFont(font, size)
    text_surface = text_font.render(text, False, color)
    screen.blit(text_surface, (x, y))

def draw_static_screen():
    screen.fill(Style['background_color'])
    pygame.draw.rect(
        screen, 
        (255, 255, 255), 
        [
            PADDING[3], PADDING[0], 
            PATH_SIZE[0]*TILE_SIZE[0]+SCREEN_BORDER*2,
            PATH_SIZE[1]*TILE_SIZE[1]+SCREEN_BORDER*2
        ], 
        SCREEN_BORDER
    )

    write_text('F: Fill', PADDING[3], PATH_SIZE[1]*TILE_SIZE[1]+SCREEN_BORDER*2+20, 'Comic Sans MS', 25, (255, 255, 255))
    write_text('R: Reset', PADDING[3], PATH_SIZE[1]*TILE_SIZE[1]+SCREEN_BORDER*2+40, 'Comic Sans MS', 25, (255, 255, 255))
    write_text('SPACE: Start', PADDING[3], PATH_SIZE[1]*TILE_SIZE[1]+SCREEN_BORDER*2+60, 'Comic Sans MS', 25, (255, 255, 255))
    write_text('ESC: Exit', PADDING[3], PATH_SIZE[1]*TILE_SIZE[1]+SCREEN_BORDER*2+80, 'Comic Sans MS', 25, (255, 255, 255))


def draw_grid(grid):
    screen.fill(Style['background_color'])

    for i in range(len(grid)):
        for j in range(len(grid[i])):

            if grid[i][j]:
                if type(grid[i][j]) == Path:
                    style = Style['locked_path'] if grid[i][j].locked else Style['path']
                else:
                    style = Style[grid[i][j]]
            else:
                style = Style['none']

            pygame.draw.rect(
                screen, 
                style['color'], 
                [
                    i*TILE_SIZE[0]+PADDING[3]+SCREEN_BORDER, j*TILE_SIZE[1]+PADDING[0]+SCREEN_BORDER, 
                    TILE_SIZE[0], TILE_SIZE[1]
                ], 
                style['style']
            )


def main():
    path_finder = PathFinder(PATH_SIZE[0], PATH_SIZE[1], FINDER_DELAY)

    running = True
    click_action = 'initial'
    setting_obstacle = False
    removing = False
    started = False

    draw_static_screen()
    pygame.display.update()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


            elif event.type == pygame.MOUSEBUTTONDOWN and not started:
                mx, my = pygame.mouse.get_pos()
                col, row = get_click_coord(mx, my)
                
                if col > -1 and row > -1:
                    if event.button == 1:
                        if click_action == 'initial':
                            ## Set the initial pos
                            stts = path_finder.set_initial(col, row)
                            if not stts:
                                if path_finder.target:
                                    click_action = 'obstacle'
                                else:
                                    click_action = 'target'
                        elif click_action == 'target':
                            ## Set the target pos
                            stts = path_finder.set_target(col, row)
                            if not stts:
                                if path_finder.initial:
                                    click_action = 'obstacle'
                                else:
                                    click_action = 'initial'
                        elif click_action == 'obstacle':
                            setting_obstacle = True

                    elif event.button == 3:
                        removing = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                setting_obstacle = False
                removing = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    ## Start finding the path
                    if path_finder.ready():
                        finder = threading.Thread(target=path_finder.start)
                        finder.start()
                        started = True
                        setting_obstacle = False
                        removing = False
                    
                
                elif event.key == pygame.K_r:
                    ## Reset
                    main()

                elif event.key == pygame.K_f and not started:
                    ## Fill everything with obstacles
                    for i in range(len(path_finder.grid)):
                        for j in range(len(path_finder.grid[i])):
                            if not path_finder.grid[i][j] == 'initial' and not path_finder.grid[i][j] == 'target':
                                path_finder.set_obstacle(i, j)

                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        mx, my = pygame.mouse.get_pos()
        col, row = get_click_coord(mx, my)
        if col > -1 and row > -1:
            if setting_obstacle:
                path_finder.set_obstacle(col, row)
            elif removing:
                removed = path_finder.remove(col, row)
                if removed == 'initial':
                    click_action = 'initial'
                elif removed == 'target':
                    click_action = 'target'

        ## draw screen
        draw_grid(path_finder.grid)

        ## Draw current click action
        pygame.draw.rect(
            screen, 
            Style[click_action]['color'], 
            [
                PATH_SIZE[0]*TILE_SIZE[0] - 80, PATH_SIZE[1]*TILE_SIZE[1]+SCREEN_BORDER*2 + 30,
                40, 40
            ], 
            0
        )

        pygame.display.update([
            pygame.Rect(
                PADDING[3]+SCREEN_BORDER, PADDING[0]+SCREEN_BORDER, 
                PATH_SIZE[0]*TILE_SIZE[0],PATH_SIZE[1]*TILE_SIZE[1]
            ),
            pygame.Rect(
                PATH_SIZE[0]*TILE_SIZE[0] - 80, PATH_SIZE[1]*TILE_SIZE[1]+SCREEN_BORDER*2 + 30,
                40, 40
            )
        ])

        clock.tick(60)

main()