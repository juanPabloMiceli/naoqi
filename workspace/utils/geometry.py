import numpy as np

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array([x, y])

def distance(p1, p2):
    return np.linalg.norm(np.subtract(p2, p1))

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm

def direction(p1, p2):
    return normalize(np.subtract(p2, p1))

def rotate(p, angle):
    new_x =  p[0] * np.cos(angle) - p[1] * np.sin(angle)
    new_y =  p[0] * np.sin(angle) + p[1] * np.cos(angle)
    return np.array([new_x, new_y])

def transformed_point(p, new_center, new_coordinates_angle):
    translated_point = np.subtract(p, new_center)
    return rotate(translated_point, -new_coordinates_angle)

def angle(v):
    return np.arctan2(v[1], v[0])

def angle_between_vectors(v1, v2):
    v1 = normalize(v1)
    v2 = normalize(v2)
    return np.arccos(np.inner(v1, v2))
