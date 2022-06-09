import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

rad = 1
camera_pos = (0.0,0.0,-5)

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

#a,b,c are point, x,y,z are origin
def distance(a,b,c,x,y,z):
    dx = x - a
    dy = y - b
    dz = z - c
    distance = math.sqrt((dx*dx)+(dy*dy)+(dz*dz))
    return distance

#list of all the triangles, list of all the vertices, camera loc
def sort_by_dist(polygons, vertices, camera):
    #biggest distance first
    distances = []
    for polygon in polygons:
        #find the center of each triangle- we can average the vertices on a regular polygon to find this.
        #vertices[polygon[0]] = 3d coordinate of first point on a triangle
        #center = average of 3 xs, ys, zs.
        center_x = (vertices[polygon[0]][0] + vertices[polygon[1]][0] + vertices[polygon[2]][0])/3
        center_y = (vertices[polygon[0]][1] + vertices[polygon[1]][1] + vertices[polygon[2]][1])/3
        center_z = (vertices[polygon[0]][2] + vertices[polygon[1]][2] + vertices[polygon[2]][2])/3
        #sorting happens least to greatest, so invert the list so the biggest magnitude comes out as 'least'
        distances.append(-1*distance(center_x, center_y, center_z, camera_pos[0], camera_pos[1], camera_pos[2]))

    #now we have a list of all the distances
    #return sorted list of polygons- a very short list so ill do it the naive way for now.
    out_polygons = list(polygons)
    for i in range(1, len(distances)):
        key = distances[i]
        p_key = polygons[i]
        # Move elements of arr[0..i-1], that are
        # greater than key, to one position ahead
        # of their current position
        j = i-1
        while j >=0 and key < distances[j] :
                distances[j+1] = distances[j]
                out_polygons[j+1] = out_polygons[j]
                j -= 1
        distances[j+1] = key
        out_polygons[j+1] = p_key

    return out_polygons

def draw_triangle_lines(a,b,c):
    glBegin(GL_LINES)
    glVertex3f(a[0],a[1],a[2])
    glVertex3f(b[0],b[1],b[2])
    glVertex3f(a[0],a[1],a[2])
    glVertex3f(c[0],c[1],c[2])
    glVertex3f(b[0],b[1],b[2])
    glVertex3f(c[0],c[1],c[2])
    glEnd()

def draw_triangle_surfaces(a,b,c):
    glBegin(GL_TRIANGLES)
    glColor3fv(colors[0])
    glVertex3f(a[0],a[1],a[2])
    glColor3fv(colors[1])
    glVertex3f(b[0],b[1],b[2])
    glColor3fv(colors[2])
    glVertex3f(c[0],c[1],c[2])
    glEnd()

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
        draw_triangle_surfaces(a,b,c)
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
    octahedron_triangles_sorted = sort_by_dist(octahedron_triangles, octahedron_vertices, camera_pos)
    for triangle in octahedron_triangles_sorted:
        #draw_triangle(tetrahedron_vertices[triangle[0]],tetrahedron_vertices[triangle[1]],tetrahedron_vertices[triangle[2]])
        subdivide_triangle(octahedron_vertices[triangle[0]],octahedron_vertices[triangle[1]],octahedron_vertices[triangle[2]],4)

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(camera_pos[0],camera_pos[1], camera_pos[2])

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
