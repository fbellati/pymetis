import requests
import matplotlib.pyplot as plt
import matplotlib.tri as tri

# Download the file from the URL
url = "https://raw.githubusercontent.com/lucarpaia/shyfemcm-ismar/main/testcases/examples/venice_lagoon/GRID/venlag62.grd"
response = requests.get(url)
file_content = response.text

# Split the content into lines and remove the first 8 lines
lines = file_content.split('\n')[8:]

# Initialize dictionaries to store node coordinates and elements
nodes = {}
elements = []

# Process each line
for line in lines:
    if line.startswith('1'):
        parts = line.split()
        node_number = int(parts[1])
        x_coord = float(parts[3])
        y_coord = float(parts[4])
        nodes[node_number] = (x_coord, y_coord)
    elif line.startswith('2'):
        parts = line.split()
        element_nodes = [int(parts[4]), int(parts[5]), int(parts[6])]
        elements.append(element_nodes)

# Extract node coordinates for plotting
x_coords = [nodes[node][0] for node in nodes]
y_coords = [nodes[node][1] for node in nodes]

# Extract element connectivity for triangulation
triangles = [(elements[i][0]-1, elements[i][1]-1, elements[i][2]-1) for i in range(len(elements))]

# Create a triangulation object
triangulation = tri.Triangulation(x_coords, y_coords, triangles)

# Plot the triangulated grid with smaller points and higher resolution
plt.figure(figsize=(10, 10), dpi=600)  # Increase dpi for higher resolution
plt.triplot(triangulation, 'go-', lw=0.5, markersize=0.5)  # Set markersize to 1 for smaller points
plt.title('Triangulated Grid from venlag62.grd')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.grid(True)

# Save the plot as a jpg image with higher resolution
plt.savefig("triangulated_grid_high_res.jpg", dpi=600)
