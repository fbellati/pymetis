import requests
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template_string

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

# Create a plotly figure
fig = go.Figure()

# Add triangles to the figure
for triangle in triangles:
    fig.add_trace(go.Scatter(
        x=[x_coords[triangle[0]], x_coords[triangle[1]], x_coords[triangle[2]], x_coords[triangle[0]]],
        y=[y_coords[triangle[0]], y_coords[triangle[1]], y_coords[triangle[2]], y_coords[triangle[0]]],
        mode='lines',
        line=dict(color='blue')
    ))

# Update layout for better visualization
fig.update_layout(
    title='Triangulated Grid from venlag62.grd',
    xaxis_title='X Coordinate',
    yaxis_title='Y Coordinate',
    showlegend=False,
    width=800,
    height=800
)

# Convert the plotly figure to HTML
plot_html = pio.to_html(fig, full_html=False)

# Create a Flask web server
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <html>
        <head>
            <title>Triangulated Grid</title>
        </head>
        <body>
            <h1>Triangulated Grid from venlag62.grd</h1>
            {{ plot_html|safe }}
        </body>
    </html>
    """, plot_html=plot_html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
