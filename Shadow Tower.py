
# Setup Python ----------------------------------------------- #
import pygame, sys, random, time, os, math
import data.engine as e
# Version ---------------------------------------------------- #
Version = '1.0'
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.display.set_caption('Shadow Tower')
scale = 3
WINDOWWIDTH = 200
WINDOWHEIGHT = 150
screen = pygame.display.set_mode((WINDOWWIDTH*scale, WINDOWHEIGHT*scale),0,32)
display = pygame.Surface((WINDOWWIDTH,WINDOWHEIGHT))

# Images ----------------------------------------------------- #
def load_img(path):
    img = pygame.image.load('data/images/' + path + '.png').convert()
    img.set_colorkey((255,0,255))
    return img

tile_img = load_img('tile')
spikes_img = load_img('spikes')
apple_img = load_img('apple')
ghost_img = load_img('ghost')
timer_img = load_img('timer')
end_img = load_img('end')

controls_1_img = load_img('controls_1')
controls_2_img = load_img('controls_2')

e.set_global_colorkey((255,0,255))
e.load_animations('data/images/entities/')
e.load_particle_images('data/images/particles/')

# SFX -------------------------------------------------------- #
jump_s = pygame.mixer.Sound('data/sfx/jump.wav')
apple_s = pygame.mixer.Sound('data/sfx/apple.wav')
death_s = pygame.mixer.Sound('data/sfx/death.wav')
end_s = pygame.mixer.Sound('data/sfx/end.wav')
ghost_s = pygame.mixer.Sound('data/sfx/ghost.wav')
ghost_s.set_volume(0.2)
jump_s.set_volume(0.4)
apple_s.set_volume(0.6)
end_s.set_volume(0.8)
death_s.set_volume(0.7)

# Music ------------------------------------------------------ #
pygame.mixer.music.load('data/music.wav')
pygame.mixer.music.play(-1)

# Functions -------------------------------------------------- #
def get_angle(pos_1,pos_2):
    dif_x = pos_2[0]-pos_1[0]
    dif_y = pos_2[1]-pos_1[1]
    return math.atan2(dif_y,dif_x)

def load_map(path):
    img = pygame.image.load('data/' + path + '.png')
    markers = []
    tiles = []
    for y in range(img.get_height()):
        tiles.append([])
        for x in range(img.get_width()):
            color = img.get_at((x,y))
            color = (color[0],color[1],color[2])
            if color == (36,27,46):
                tiles[-1].append(1)
            else:
                tiles[-1].append(0)
            if color == (156,69,82):
                markers.append(['apple',[x,y],0])
            if color == (136,0,21):
                markers.append(['spikes',[x,y]])
            if color == (255,242,0):
                markers.append(['left',[x,y],0])
            if color == (255,127,39):
                markers.append(['right',[x,y],0])
            if color == (34,177,76):
                markers.append(['up',[x,y],0])
            if color == (0,162,232):
                markers.append(['down',[x,y],0])
    return tiles, markers

# Setup ------------------------------------------------------ #

tiles, markers = load_map('map')
markers.append(['end',[12*21-10,18]])

player = e.entity(25,57*18,6,11,'player')
player.set_offset([-1,-1])
player_grav = 0
ground_timer = 0

jumps = 1

scroll = [player.x-WINDOWWIDTH/2,player.y-WINDOWHEIGHT/2]

game_timer = 0

last_save = [25,57*18+7]

circle_center = [player.get_center()[0]-scroll[0],player.get_center()[1]-scroll[1]]

ghosts = []
particles = []

dead = False

life_timer = 60*7

view_radius = 0
view_center = [player.get_center()[0]-scroll[0],player.get_center()[1]-scroll[1]]

apples = 0

moved = False

right = False
left = False

gold = -1

# Loop ------------------------------------------------------- #
while True:
    
    # Background --------------------------------------------- #
    if gold == -1:
        display.fill((0,0,0))
    else:
        display.fill((255,255,255))
    
    # Game Timer --------------------------------------------- #
    game_timer += 1
    
    # Scroll ------------------------------------------------- #
    scroll[0] += ((player.get_center()[0]-WINDOWWIDTH/2)-scroll[0])/20
    scroll[1] += ((player.get_center()[1]-WINDOWHEIGHT/2)-scroll[1])/20
    if scroll[0] < 0:
        scroll[0] = 0
    if scroll[0] > 18*21-WINDOWWIDTH:
        scroll[0] = 18*21-WINDOWWIDTH
    if scroll[1] > 61*18-WINDOWHEIGHT:
        scroll[1] = 61*18-WINDOWHEIGHT
        
    # Tiles -------------------------------------------------- #
    tile_rects = []
    base_pos = int((scroll[1])/18)-1
    for y in range(11):
        y_pos = base_pos + y
        if (y_pos >= 0) and (y_pos <= len(tiles)-1):
            x = 0
            for tile in tiles[y_pos]:
                if tile == 1:
                    display.blit(tile_img,(x*21-int(scroll[0]),y_pos*18-int(scroll[1])))
                    tile_rects.append(pygame.Rect(x*21,y_pos*18,21,18))
                x += 1
                
    # Particles ---------------------------------------------- #
    remove_list = []
    n = 0
    for particle in particles:
        running = particle.update()
        particle.draw(display,scroll)
        if not running:
            remove_list.append(n)
        n += 1
    remove_list.sort(reverse=True)
    for particle in remove_list:
        particles.pop(particle)
        
    # Markers ------------------------------------------------ #
    apple_pos = []
    for marker in markers:
        marker_r = pygame.Rect(marker[1][0]*21,marker[1][1]*18,21,18)
        if marker[0] == 'spikes':
            marker_r = pygame.Rect(marker[1][0]*21+1,marker[1][1]*18+8,19,10)
            display.blit(spikes_img,(marker[1][0]*21-int(scroll[0]),marker[1][1]*18-int(scroll[1])))
            if player.obj.rect.colliderect(marker_r):
                dead = True
        elif marker[0] == 'apple':
            if marker[2] == 0:
                marker_r = pygame.Rect(marker[1][0]*21+2,marker[1][1]*18+1,17,16)
                if game_timer % 50 < 17:
                    offset = 1
                else:
                    offset = 0
                display.blit(apple_img,(marker[1][0]*21-int(scroll[0]),marker[1][1]*18+offset-int(scroll[1])))
                apple_pos.append([marker[1][0]*21+10,marker[1][1]*18+9])
                if random.randint(1,20) == 1:
                    particles.append(e.particle(marker[1][0]*21+10,marker[1][1]*18+9,'p',[random.randint(0,10)/10-0.5,random.randint(0,10)/10-0.5],0.05,random.randint(20,40)/10,(255,255,255)))
                if player.obj.rect.colliderect(marker_r):
                    apple_s.play()
                    for i in range(10):
                        particles.append(e.particle(marker[1][0]*21+10,marker[1][1]*18+9,'p',[random.randint(0,30)/10-1.5,random.randint(0,30)/10-1.5],0.1,random.randint(10,30)/10,(255,255,255)))
                    apples += 1
                    life_timer = 60*7
                    last_save = [marker[1][0]*21+7,marker[1][1]*18+7]
                    for marker2 in markers:
                        if marker2[0] == 'apple':
                            if marker2[2] == 1:
                                marker2[2] = 2
                    marker[2] = 1
        elif marker[0] == 'end':
            marker_r = pygame.Rect(marker[1][0]+2,marker[1][1]+1,17,16)
            if player.obj.rect.colliderect(marker_r):
                if gold == -1:
                    end_s.play()
                    pygame.mixer.music.fadeout(1000)
                    gold = 0
            display.blit(end_img,(marker[1][0]-int(scroll[0]),marker[1][1]-int(scroll[1])))
            particles.append(e.particle(marker[1][0]+13,marker[1][1]+12,'p',[random.randint(0,30)/10-1.5,random.randint(0,30)/10-1.5],0.1,random.randint(10,30)/10,(247,215,140)))
        elif player.obj.rect.colliderect(marker_r):
            if marker[2] == 0:
                marker[2] = 1
                ghost_s.play()
                if marker[0] == 'up':
                    ghosts.append(['up',[marker[1][0]*21+10,scroll[1]+WINDOWHEIGHT+80],0])
                if marker[0] == 'down':
                    ghosts.append(['down',[marker[1][0]*21+10,scroll[1]-80],0])
                if marker[0] == 'right':
                    ghosts.append(['right',[scroll[0]-80,marker[1][1]*18+9],0])
                if marker[0] == 'left':
                    ghosts.append(['left',[scroll[0]+WINDOWWIDTH+80,marker[1][1]*18+9],0])

    # Dead --------------------------------------------------- #
    if apples != 0:
        if gold == -1:
            life_timer -= 1
        if life_timer <= 0:
            dead = True
    if dead:
        death_s.play()
        dead = False
        for i in range(10):
            particles.append(e.particle(player.get_center()[0],player.get_center()[1],'p',[random.randint(0,30)/10-1.5,random.randint(0,30)/10-1.5],0.1,random.randint(10,30)/10,(156,69,82)))
        player.set_pos(last_save[0],last_save[1])
        for i in range(10):
            particles.append(e.particle(player.get_center()[0],player.get_center()[1],'p',[random.randint(0,30)/10-1.5,random.randint(0,30)/10-1.5],0.1,random.randint(10,30)/10,(255,255,255)))
        right = False
        left = False
        for marker in markers:
            if marker[0] not in ['apple','spikes','end']:
                marker[2] = 0
        life_timer = 60*7
        
    # Player ------------------------------------------------- #
    player.display(display,[int(scroll[0]),int(scroll[1])])
    player_movement = [0,0]
    player_grav += 0.3
    if player_grav > 3:
        player_grav = 3
    if gold == -1:
        if right:
            player_movement[0] += 1.6
        if left:
            player_movement[0] -= 1.6
    if player_movement[0] > 0:
        if player.flip == False:
            particles.append(e.particle(player.x,player.y+player.size_y,'p',[-1,0.25],0.2,2.5,(255,255,255)))
        player.flip = True
    if player_movement[0] < 0:
        if player.flip == True:
            particles.append(e.particle(player.x+player.size_x,player.y+player.size_y,'p',[1,0.25],0.2,2.5,(255,255,255)))
        player.flip = False
    if player_movement[0] != 0:
        moved = True
    if ground_timer > 5:
        player.set_action('jump')
    elif player_movement[0] == 0:
        player.set_action('idle')
    else:
        player.set_action('run')
    player.change_frame(1)
    player_movement[1] = player_grav
    if abs((scroll[1]+WINDOWHEIGHT/2)-player.y) < WINDOWHEIGHT/2:
        collisions = player.move(player_movement,tile_rects,[])
    if player.x < 0:
        player.set_pos(0,player.y)
    if player.x > 18*21-player.size_x:
        player.set_pos(18*21-player.size_x,player.y)
    if collisions['bottom']:
        player_grav = 0
        jumps = 2
        ground_timer = 0
    else:
        ground_timer += 1
    if collisions['top']:
        player_grav = 0
        
    # Overlay ------------------------------------------------ #
    overlay = display.copy()
    overlay.fill((0,0,0))
    
    # Ghosts ------------------------------------------------- #
    r_list = []
    n = 0
    for ghost in ghosts:
        if game_timer % 3 == 0:
            particles.append(e.particle(ghost[1][0],ghost[1][1],'p',[0,0],0.1,random.randint(0,20)/10,(156,69,82)))
        if ghost[0] == 'right':
            current_img = ghost_img
            ghost[1][0] += 4
        if ghost[0] == 'left':
            current_img = pygame.transform.flip(pygame.transform.rotate(ghost_img,180),False,True)
            ghost[1][0] -= 4
        if ghost[0] == 'up':
            current_img = pygame.transform.rotate(ghost_img,90)
            ghost[1][1] -= 4
        if ghost[0] == 'down':
            current_img = pygame.transform.rotate(ghost_img,270)
            ghost[1][1] += 4
        ghost[2] += 1
        e.blit_center(display,current_img,(ghost[1][0]-int(scroll[0]),ghost[1][1]-int(scroll[1])))
        ghost_r = pygame.Rect(ghost[1][0]-6,ghost[1][1]-6,12,12)
        dis = math.hypot(abs(player.get_center()[0]-ghost[1][0]),abs(player.get_center()[1]-ghost[1][1]))
        val = (200-dis)/3
        if val < 0:
            val = 0
        pygame.draw.circle(overlay,(255,255,255),(int(ghost[1][0]-scroll[0]),int(ghost[1][1]-scroll[1])),abs(int(val)))
        if player.obj.rect.colliderect(ghost_r):
            dead = True
        if ghost[2] > 120:
            r_list.append(n)
        n += 1
    r_list.sort(reverse=True)
    for ghost in r_list:
        ghosts.pop(ghost)

    # UI ----------------------------------------------------- #
    if not moved:
        if game_timer % 60 < 50:
            display.blit(controls_1_img,(player.get_center()[0]-int(scroll[0])-11,player.y-20-int(scroll[1])))
        else:
            display.blit(controls_2_img,(player.get_center()[0]-int(scroll[0])-11,player.y-20-int(scroll[1])))
        
    # Overlay 2 ---------------------------------------------- #
    if game_timer % 70 < 35:
        mod = (game_timer % 70)/4
    else:
        mod = 8.75-((game_timer % 70)-35)/4
    target_view_radius = 10 + mod + int(life_timer/8)
    view_radius += (target_view_radius - view_radius) / 20
    target_view_center = [int(player.get_center()[0]-scroll[0]),int(player.get_center()[1]-scroll[1])]
    view_center[0] += (target_view_center[0]-view_center[0])/30
    view_center[1] += (target_view_center[1]-view_center[1])/30
    pygame.draw.circle(overlay,(255,255,255),[int(view_center[0]),int(view_center[1])],int(view_radius) + gold)
    for apple in apple_pos:
        pygame.draw.circle(overlay,(255,255,255),[apple[0]-int(scroll[0]),apple[1]-int(scroll[1])],15 + int(mod/2))
    overlay.set_colorkey((255,255,255))
    display.blit(overlay,(0,0))
    
    # Timers ------------------------------------------------- #
    if gold == -1:
        mod = (game_timer % 36)
        for i in range(10):
            circle_center[0] += (view_center[0]-circle_center[0])/200
            circle_center[1] += (view_center[1]-circle_center[1])/200
            pos = [circle_center[0]+scroll[0]+math.cos(math.radians(i*36+mod))*(view_radius-10),circle_center[1]+scroll[1]+math.sin(math.radians(i*36+mod))*(view_radius-10)]
            display.blit(timer_img,(int(pos[0]-scroll[0]-4),int(pos[1]-scroll[1]-4)))
            angle = get_angle(player.get_center(),pos)
            if game_timer % 3 == 0:
                particles.append(e.particle(pos[0],pos[1],'p',[math.cos(angle)*2,math.sin(angle)*2],0.1,random.randint(0,20)/10,(36,27,46)))

    # End ---------------------------------------------------- #
    if gold != -1:
        gold += 1
        display = e.swap_color(display,(36,27,46),(247,215,140))

    if gold > 120:
        alpha = gold-120
        black_surf = display.copy()
        black_surf.fill((0,0,0))
        black_surf.set_alpha(alpha)
        display.blit(black_surf,(0,0))
        if gold > 375:
           pygame.quit()
           sys.exit()
    # Buttons ------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_RIGHT:
                right = True
            if event.key == K_LEFT:
                left = True
            if event.key == K_UP:
                if jumps > 0:
                    jump_s.play()
                    for i in range(3):
                        particles.append(e.particle(player.get_center()[0],player.y+player.size_y,'p',[random.randint(0,10)/10-0.5,0.25],0.2,random.randint(20,30)/10,(255,255,255)))
                    jumps -= 1
                    player_grav = -4.5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                right = False
            if event.key == K_LEFT:
                left = False
                
    # Update ------------------------------------------------- #
    screen.blit(pygame.transform.scale(display,(WINDOWWIDTH*scale,WINDOWHEIGHT*scale)),(0,0))
    pygame.display.update()
    mainClock.tick(60)
    
