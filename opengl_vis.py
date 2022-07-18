import pygame
import pyaudio
import struct
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import opensimplex as osp
import random
import numpy as np

'''
degrees of freedom:
-depth of bumps (scalars)
    -overall rms? would need some smoothing function
        -or log rms
-oscillation frequency (counter size/sin wave period)
    -some derivative function, d(rms)/d(x)? goal is busier music drives faster oscillations
        -this would probably merit a small dynamic range, implement last.
-size of bumps (noise base multiplier, currently 2)
    -frequency curve? (higher avg = smaller bumps)
        -calculate median energy band per frame?
-size of base sphere
    -low pass rms (some bass freq cutoff so it pulses on kicks)
-colors? (eventually)
All these need some mapping function (probably a sigmoid) to keep
them from enlarging/reducing too far in any direction, need to tune the dynamic
range of that function for optimal art. maybe make it configurable in some gui later?
'''

osp.seed(random.randint(1,1000))

#the sine wave needs to go really slowly so we can resample it
sigmoid_bins = 500
sin_times = np.linspace(0,2*np.pi,sigmoid_bins)
sin = (np.sin(sin_times)*.5) + 1

sigmoid_times = np.linspace(-3,3,500)
sigmoid = 1/(1+np.exp(-sigmoid_times))

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
    x = (a*length)/distance(a,b,c,0,0,0)
    y = (b*length)/distance(a,b,c,0,0,0)
    z = (c*length)/distance(a,b,c,0,0,0)
    return (x,y,z)

#recursively split triangle into smaller triangles
def subdivide_triangle(a, b, c, depth, bump_depth, noise_mult, base_rad, counter):
    if depth == 0:
        #a,b,c are triples (vertices)
        #print((osp.noise3(a[0],a[1],a[2])*.2))
        a = norm(a[0],a[1],a[2],base_rad+(osp.noise3((a[0])*(noise_mult+sin[counter]),(a[1])*(noise_mult+sin[counter]),(a[2])*(noise_mult+sin[counter]))*bump_depth))
        b = norm(b[0],b[1],b[2],base_rad+(osp.noise3((b[0])*(noise_mult+sin[counter]),(b[1])*(noise_mult+sin[counter]),(b[2])*(noise_mult+sin[counter]))*bump_depth))
        c = norm(c[0],c[1],c[2],base_rad+(osp.noise3((c[0])*(noise_mult+sin[counter]),(c[1])*(noise_mult+sin[counter]),(c[2])*(noise_mult+sin[counter]))*bump_depth))
        draw_triangle_lines(a,b,c)
    else:
        #calculate the midpoint of each side of the triangle, call subdivide on each sub-triangle
        ab = ((a[0] + b[0])/2, (a[1] + b[1])/2, (a[2] + b[2])/2)
        ac = ((a[0] + c[0])/2, (a[1] + c[1])/2, (a[2] + c[2])/2)
        bc = ((c[0] + b[0])/2, (c[1] + b[1])/2, (c[2] + b[2])/2)

        subdivide_triangle(a, ab, ac, depth-1, bump_depth, noise_mult, base_rad, counter)
        subdivide_triangle(b, ab, bc, depth-1, bump_depth, noise_mult, base_rad, counter)
        subdivide_triangle(c, ac, bc, depth-1, bump_depth, noise_mult, base_rad, counter)
        subdivide_triangle(ab, ac, bc, depth-1, bump_depth, noise_mult, base_rad, counter)

def Sphere(bump_depth, noise_mult, base_rad, counter):
    octahedron_triangles_sorted = sort_by_dist(octahedron_triangles, octahedron_vertices, camera_pos)
    for triangle in octahedron_triangles_sorted:
        #draw_triangle(tetrahedron_vertices[triangle[0]],tetrahedron_vertices[triangle[1]],tetrahedron_vertices[triangle[2]])
        subdivide_triangle(octahedron_vertices[triangle[0]],octahedron_vertices[triangle[1]],octahedron_vertices[triangle[2]], 4, bump_depth, noise_mult, base_rad, counter)

def main():
    pygame.init()
    display = (1200,900)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(camera_pos[0],camera_pos[1], camera_pos[2])

    counter = 0
    bump_depth = .5
    sin_period = 3 #this only affects counter
    noise_mult = 2
    base_rad = 1

    current_avg_rms = 0
    current_curr_band = 300

    #setup pyaudio stream
    WIDTH = 2
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024*2
    FORMAT = pyaudio.paInt16

    p = pyaudio.PyAudio()

    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

    #select an input source
    input_id = int(input("Desired input source: "))

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=False,
                    input_device_index=input_id,
                    frames_per_buffer=CHUNK)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                stream.stop_stream()
                stream.close()

                p.terminate()
                quit()

        counter = counter + sin_period
        if counter > 499:
            counter = 0

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        #calculate the appropriate values
        #audio time
        in_data = stream.read(CHUNK)
        int_data = struct.unpack(str(CHUNK) + 'h',in_data)
        fft_data = np.fft.fft(int_data)
        fft_data = np.sqrt(np.abs(fft_data))
        log_fft = np.log(fft_data)

        total_rms = np.sqrt(np.mean(np.asarray(int_data) ** 2))
        #print(total_rms)
        #total_rms_scaled = sigmoid[math.floor(min(total_rms/4000, 1) * (sigmoid_bins-1))]
        current_avg_rms = (current_avg_rms*.75) + (total_rms*.25)
        total_rms_scaled = sigmoid[math.floor(min(current_avg_rms/6000, 1) * (sigmoid_bins-1))]

        med_energy = np.sum(fft_data[0:1024])/2
        curr_band = 0
        e_count = 0
        while e_count < med_energy:
            e_count += fft_data[curr_band]
            curr_band += 1

        current_curr_band = (current_curr_band * .8) + (curr_band * .2)
        curr_band_scaled = sigmoid[math.floor(min(current_curr_band/500,1) * (sigmoid_bins-1))]

        bump_depth = total_rms_scaled/2
        sin_period = 3 #this only affects counter
        noise_mult = 2 + (curr_band_scaled*2)
        base_rad = 1

        #scalars (bump depth), noise base multiplier (currently 2), base sphere radius
        Sphere(bump_depth, noise_mult, base_rad, counter)
        pygame.display.flip()
        pygame.time.wait(20)

main()
