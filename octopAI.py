import pygame
import neat
import time
import os
import random
pygame.font.init()

from octopAI_display_accessories import Octopus, Base, Obstacle, draw_window, WIN_WIDTH, WIN_HEIGHT


GEN = 0
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

"""
In this file, the octopAI display would be called to show how the octopus is doing as
it learns to navigate the perils of the underwater world.

In this first version, the NEAT genetic algorithm is used
https://neat-python.readthedocs.io/en/latest/index.html

The main motivation and the initial version of the code comes from the tutorial

https://www.youtube.com/playlist?list=PLzMcBGfZo4-lwGZWXz5Qgta_YNX3_vLS2

"""
#################### MAIN #######################

def main(genomes, config):

    global GEN, WIN
    GEN +=1

    win = WIN

    nets = []
    ge = []
    octopi = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        octopi.append(Octopus(230,350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    obstacles = [Obstacle(700)]
    score = 0


    clock = pygame.time.Clock()


    run = True
    while run and len(octopi) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break


        # Which obstacle is being observed (if there are more than one obstacle)
        obstacle_ind = 0
        if len(octopi) > 0:
            if len(obstacles) > 1 and octopi[0].x > obstacles[0].x + obstacles[0].OBSTACLE_TOP.get_width():
                # x positions are same for all octopi
                obstacle_ind = 1

        for x, octopus in enumerate(octopi):
            ge[x].fitness += 0.1 # so low because this will execute 30 times per second
            octopus.move()

            output = nets[x].activate((octopus.y, abs(octopus.y - obstacles[obstacle_ind].height),
                                        abs(octopus.y - obstacles[obstacle_ind].bottom)))

            if output[0] > 0.5:
                octopus.jump()


        base.move()

        add_obstacle = False
        rem = [] # to remove obstacles to remove
        for obstacle in obstacles:
            obstacle.move()

            for x, octopus in enumerate(octopi):
                if obstacle.collide(octopus):
                    ge[x].fitness -= 1 # To make a octopus colliding to be less fit
                    octopi.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # If the octopus has passed the obstacle, generate a new one
                if not obstacle.passed and obstacle.x < octopus.x:
                    obstacle.passed = True
                    add_obstacle = True

            if obstacle.x + obstacle.OBSTACLE_TOP.get_width() < 0:
                rem.append(obstacle)



            obstacle.move()

        if add_obstacle:
            score += 1
            for g in ge:
                g.fitness += 5

            obstacles.append(Obstacle(700))

        for r in rem:
            obstacles.remove(r)

        for x, octopus in enumerate(octopi):
            if octopus.y + octopus.img.get_height() >= 730 or octopus.y< -50:
                octopi.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, octopi, obstacles, base, score, GEN)

        if score > 25:
            break # stopping criteria




def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50) #fitness function

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config-feedforward.txt")
    run(config_path)


# main()
