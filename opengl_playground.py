import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

rad = 1

colors = (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (0,1,0),
    (1,1,1),
    (0,1,1),
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (1,0,0),
    (1,1,1),
    (0,1,1),
    )

cube_vertices= (
    (.5, -.5, -.5),
    (.5, .5, -.5),
    (-.5, .5, -.5),
    (-.5, -.5, -.5),
    (.5, -.5, .5),
    (.5, .5, .5),
    (-.5, -.5, .5),
    (-.5, .5, .5)
    )

cube_edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

tetrahedron_vertices= (
    (1,-1,-1),
    (-1,-1,1),
    (-1,1,-1),
    (1,1,1)
    )

tetrahedron_triangles = (
    (0,1,2),
    (0,1,3),
    (0,2,3),
    (1,2,3)
    )

octahedron_vertices= (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (-1,0,0),
    (0,-1,0),
    (0,0,-1)
    )

octahedron_triangles= (
    (0,1,2),
    (1,2,3),
    (2,3,4),
    (0,2,4),
    (0,1,5),
    (1,3,5),
    (3,4,5),
    (0,4,5)
    )

def Cube():
    glBegin(GL_LINES)
    for edge in cube_edges:
        for vertex in edge:
            glVertex3fv(cube_vertices[vertex])
    glEnd()

def draw_triangle(a,b,c):
    glBegin(GL_LINES)
    glVertex3f(a[0],a[1],a[2])
    glVertex3f(b[0],b[1],b[2])
    glVertex3f(a[0],a[1],a[2])
    glVertex3f(c[0],c[1],c[2])
    glVertex3f(b[0],b[1],b[2])
    glVertex3f(c[0],c[1],c[2])
    glEnd()

#a,b,c are point, x,y,z are origin
def distance(a,b,c,x,y,z):
    dx = x - a
    dy = y - b
    dz = z - c
    distance = math.sqrt((dx*dx)+(dy*dy)+(dz*dz))
    return distance

def norm(a, b, c, length):
    #get components and divide them by distance
    x = a/distance(a,b,c,0,0,0)
    y = b/distance(a,b,c,0,0,0)
    z = c/distance(a,b,c,0,0,0)
    return (x,y,z)

#recursively split triangle into smaller triangles
def subdivide_triangle(a,b,c,depth):
    if depth == 0:
        #a,b,c are triples (vertices)
        a = norm(a[0],a[1],a[2],1)
        b = norm(b[0],b[1],b[2],1)
        c = norm(c[0],c[1],c[2],1)
        draw_triangle(a,b,c)
    else:
        #calculate the midpoint of each side of the triangle, call subdivide on each sub-triangle
        ab = ((a[0] + b[0])/2, (a[1] + b[1])/2, (a[2] + b[2])/2)
        ac = ((a[0] + c[0])/2, (a[1] + c[1])/2, (a[2] + c[2])/2)
        bc = ((c[0] + b[0])/2, (c[1] + b[1])/2, (c[2] + b[2])/2)

        subdivide_triangle(a,ab,ac,depth-1)
        subdivide_triangle(b,ab,bc,depth-1)
        subdivide_triangle(c,ac,bc,depth-1)
        subdivide_triangle(ab,ac,bc,depth-1)

def Sphere():
    for triangle in octahedron_triangles:
        #draw_triangle(tetrahedron_vertices[triangle[0]],tetrahedron_vertices[triangle[1]],tetrahedron_vertices[triangle[2]])
        subdivide_triangle(octahedron_vertices[triangle[0]],octahedron_vertices[triangle[1]],octahedron_vertices[triangle[2]],4)

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        Sphere()
        pygame.display.flip()
        pygame.time.wait(10)

main()
