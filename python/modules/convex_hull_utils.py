import hou
import scipy.spatial as spatial
import numpy as np


def create_convex_hull(geo, points ,normalize_parm = True,flip_normals_parm = True, simplify_parm = False, level_detail = 0):
    '''
    Creates a conves hull based on the geo and points
    Args:
        geo = python node.geometry()
        points = the geometry points to be used
        normalize_parm, flip_normals_parm, simplify_parm, level_detail = extra params to adjust normals and details
    '''

    try:
        # Conver points into a numpy array
        points_array = np.array([(p.x(), p.y(), p.z()) for p in points])

        # Simplify the points
        if simplify_parm and level_detail > 0:
            # Create a grid for clustering
            grid_size = level_detail
            # Round position to grid anr remove duplicate points
            grid_points = np.round(points_array / grid_size) * grid_size
            unique_points = np.unique(grid_points, axis=0)

            hull_input = unique_points
        else:
            hull_input = points_array

        # Create the convex hull

        hull = spatial.ConvexHull(hull_input)

        # Find the centroid of the hull to fix normal issues

        hull_points_pos = hull_input[hull.vertices]
        centroid = np.mean(hull_points_pos, axis=0)
        centroid_vector = hou.Vector3(centroid[0], centroid[1], centroid[2])

        # Create the new points for the convex hull geo

        geo.clear()

        hull_points = []

        for point in range(len(hull.vertices)):
            pt = geo.createPoint()
            pos = hull_input[hull.vertices[point]]
            pt.setPosition((pos[0], pos[1], pos[2]))
            hull_points.append(pt)

        # Create the polygons for each face with consistent orientation

        for face in hull.simplices:
            polygon = geo.createPolygon()

            # Convert the face indices to vertex indices in the points array
            face_points = []
            for id_ in face:
                vertex_id = np.where(hull.vertices == id_)[0][0]
                face_points.append(hull_points[vertex_id])

            # Calculate the face normal
            if len(face_points) >= 3 and normalize_parm:
                v1 = face_points[1].position() - face_points[0].position()
                v2 = face_points[2].position() - face_points[0].position()
                normal = v1.cross(v2)
                normal = normal.normalized()

                # Need to check if normal is pointing outward from the centroid
                center_to_face = face_points[0].position() - centroid_vector
                dot_product = normal.dot(center_to_face)

                # Determine if we need to flip the face
                should_reverse_face = (dot_product < 0)

                if flip_normals_parm:
                    should_reverse_face = not should_reverse_face

                if should_reverse_face:
                    face_points.reverse()

            for pt in face_points:
                polygon.addVertex(pt)



    except:
        hou.ui.displayMessage(F"Scipy and Numpy modules not found", severity = hou.severityType.Error)



