#!/usr/bin/python3
"""
    Simulation of a rotating 3D Cube
    Developed by Leonel Machava <leonelmachava@gmail.com>
    http://codeNtronix.com

    Modified by Wintermute0110 <wintermute0110@gmail.com>
"""
import sys, math, pygame, os
from operator import itemgetter

class Point3D:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def rotateX(self, angle):
        """ Rotates the point around the X axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        y = self.y * cosa - self.z * sina
        z = self.y * sina + self.z * cosa
        return Point3D(self.x, y, z)

    def rotateY(self, angle):
        """ Rotates the point around the Y axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        z = self.z * cosa - self.x * sina
        x = self.z * sina + self.x * cosa
        return Point3D(x, self.y, z)

    def rotateZ(self, angle):
        """ Rotates the point around the Z axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        x = self.x * cosa - self.y * sina
        y = self.x * sina + self.y * cosa
        return Point3D(x, y, self.z)

    def project(self, win_width, win_height, fov, viewer_distance):
        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = fov / (viewer_distance + self.z)
        x = self.x * factor + win_width / 2
        y = -self.y * factor + win_height / 2
        return Point3D(x, y, self.z)

# --- main ----------------------------------------------------------------------------------------
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.display.list_modes()
myfont = pygame.font.Font('../fonts/Inconsolata.otf', 22)

win_width = 500
win_height = 750
screen = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Simulation of a rotating 3D Cube (http://codeNtronix.com)")

clock = pygame.time.Clock()

vertices = [
    Point3D(-2,1,-1),
    Point3D(2,1,-1),
    Point3D(2,-1,-1),
    Point3D(-2,-1,-1),
    Point3D(-2,1,1),
    Point3D(2,1,1),
    Point3D(2,-1,1),
    Point3D(-2,-1,1)
]

vertices_axis = [
    Point3D(0, 0, 0),
    Point3D(3, 0, 0),
    Point3D(0, 3, 0),
    Point3D(0, 0, 3),
]

# Define the vertices that compose each of the 6 faces. These numbers are
# indices to the vertices list defined above.
faces  = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)]

# Define colors for each face
colors = [(255,0,255),(255,0,0),(0,255,0),(0,0,255),(0,255,255),(255,255,0)]

angleX = 0
angleY = 0
angleZ = 0
fov = 500
viewer_distance = 5

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if   event.key == pygame.K_e: angleX -= 5
            elif event.key == pygame.K_r: angleX += 5
            elif event.key == pygame.K_d: angleY -= 5
            elif event.key == pygame.K_f: angleY += 5
            elif event.key == pygame.K_c: angleZ -= 5
            elif event.key == pygame.K_v: angleZ += 5
            elif event.key == pygame.K_q: fov -= 10
            elif event.key == pygame.K_w: fov += 10
            elif event.key == pygame.K_a: viewer_distance -= 1
            elif event.key == pygame.K_s: viewer_distance += 1

    clock.tick(100)
    screen.fill((0, 0, 0))

    # It will hold transformed vertices.
    t = []
    for v in vertices:
        # Rotate the point around X axis, then around Y axis, and finally around Z axis.
        r = v.rotateX(angleX).rotateY(angleY).rotateZ(angleZ)
        # Transform the point from 3D to 2D
        p = r.project(screen.get_width(), screen.get_height(), fov, viewer_distance)
        # Put the point in the list of transformed vertices
        t.append(p)

    # Calculate the average Z values of each face.
    avg_z = []
    i = 0
    for f in faces:
        z = (t[f[0]].z + t[f[1]].z + t[f[2]].z + t[f[3]].z) / 4.0
        avg_z.append([i,z])
        i = i + 1

    # Draw the faces using the Painter's algorithm:
    # Distant faces are drawn before the closer ones.
    for tmp in sorted(avg_z, key=itemgetter(1), reverse=True):
        face_index = tmp[0]
        f = faces[face_index]
        pointlist = [
            (t[f[0]].x, t[f[0]].y), (t[f[1]].x, t[f[1]].y),
            (t[f[1]].x, t[f[1]].y), (t[f[2]].x, t[f[2]].y),
            (t[f[2]].x, t[f[2]].y), (t[f[3]].x, t[f[3]].y),
            (t[f[3]].x, t[f[3]].y), (t[f[0]].x, t[f[0]].y),
        ]
        pygame.draw.polygon(screen, colors[face_index], pointlist)

    # --- Draw cartesian axis ---
    t = []
    for v in vertices_axis:
        r = v.rotateX(angleX).rotateY(angleY).rotateZ(angleZ)
        p = r.project(screen.get_width(), screen.get_height(), fov, viewer_distance)
        t.append(p)
    pygame.draw.line(screen, (255, 0, 0), (t[0].x, t[0].y), (t[1].x, t[1].y), 3)
    pygame.draw.line(screen, (0, 255, 0), (t[0].x, t[0].y), (t[2].x, t[2].y), 3)
    pygame.draw.line(screen, (0, 0, 255), (t[0].x, t[0].y), (t[3].x, t[3].y), 3)

    # --- Draw text ---
    text_surface = myfont.render('angle X {}'.format(angleX), True, (255, 0, 0))
    screen.blit(text_surface, (10, 10))
    text_surface = myfont.render('angle Y {}'.format(angleY), True, (255, 0, 0))
    screen.blit(text_surface, (10, 30))
    text_surface = myfont.render('angle Z {}'.format(angleZ), True, (255, 0, 0))
    screen.blit(text_surface, (10, 50))
    text_surface = myfont.render('FOV {}'.format(fov), True, (255, 0, 0))
    screen.blit(text_surface, (10, 70))
    text_surface = myfont.render('distance {}'.format(viewer_distance), True, (255, 0, 0))
    screen.blit(text_surface, (10, 90))

    # --- Refresh screen ---
    pygame.display.flip()
