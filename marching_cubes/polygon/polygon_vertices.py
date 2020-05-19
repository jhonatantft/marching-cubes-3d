# Global scope

# Cube vertices in (x,y,z) coordinates
VERTICES = [
    (0,0,0),
    (1,0,0),
    (1,1,0),
    (0,1,0),
    (0,0,1),
    (1,0,1),
    (1,1,1),
    (0,1,1)
]

# Cube edges as combination of two vertices
EDGES = [
    (0,1),
    # (1,1),
    (1,2),
    (2,3),
    (0,3),
    (0,4),
    (1,5),
    (2,6),
    (3,7),
    (4,5),
    (5,6),
    (6,7),
    (4,7)
]

def marchingCubesPolygons(edgeTable, threshold):
	activeEdges = []		# active edges
	polygonVertices = []	# vertices to draw

	# active edges
	for edge in EDGES:
		# active if it exceeds the threshold crossing
		if  ( (edgeTable[edge[0]] > threshold) != (edgeTable[edge[1]] > threshold) ):
			activeEdges.append(edge)

	# creates a list of vertices for polygon as midpoints of edges
	for edge in activeEdges:
		midpoint = tuple( (a + b) / 2 for a,b in zip(VERTICES[edge[0]], VERTICES[edge[1]]) )
		polygonVertices.append(midpoint)

	# sort array of polygon vertices by distance to one another
	for index in range(len(polygonVertices)):
		a = polygonVertices[index]
		polygonVertices[index+1:] = sorted(polygonVertices[index + 1:], 
			key=lambda item: ((item[0] - a[0])**2 + (item[1] - a[1])**2 + (item[2] - a[2])**2)**(1 / 2)
			)

	return polygonVertices