import requests
import pymetis
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from flask import Flask, request, render_template_string

def convert_to_adjacency_list(elements):
    adjacency_list = {}
    
    for element in elements:
        for i in range(3):
            if element[i] not in adjacency_list:
                adjacency_list[element[i]] = set()
            adjacency_list[element[i]].add(element[(i+1) % 3])
            adjacency_list[element[i]].add(element[(i+2) % 3])
    
    # Convert sets to sorted lists
    for node in adjacency_list:
        adjacency_list[node] = sorted(list(adjacency_list[node]))
    
    # Convert to array of NumPy arrays
    adjacency_array = [np.array(adjacency_list[node]) for node in sorted(adjacency_list)]
    
    return adjacency_array

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_html = ""
    if request.method == 'POST':
        url = request.form['url']
        nparts = int(request.form['nparts'])
        print(f"URL: {url}")
        print(f"Number of parts: {nparts}")
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
                node_number = int(parts[1])-1
                x_coord = float(parts[3])
                y_coord = float(parts[4])
                nodes[node_number] = (x_coord, y_coord)
            elif line.startswith('2'):
                parts = line.split()
                element_nodes = [int(parts[4])-1, int(parts[5])-1, int(parts[6])-1]
                elements.append(element_nodes)

        adjacency_array = convert_to_adjacency_list(elements)
        n_cuts, membership = pymetis.part_graph(nparts, adjacency=adjacency_array)
        print(n_cuts)
        print(membership)

        # Extract node coordinates for plotting
        x_coords = [nodes[node][0] for node in nodes]
        y_coords = [nodes[node][1] for node in nodes]

        # Extract element connectivity for triangulation
        triangles = [(elements[i][0], elements[i][1], elements[i][2]) for i in range(len(elements))]

        # Create a plotly figure for the entire graph
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
            title='Triangulated Grid from .grd file',
            xaxis_title='X Coordinate',
            yaxis_title='Y Coordinate',
            showlegend=False,
            width=800,
            height=800
        )

        # Convert the plotly figure to HTML
        plot_html += pio.to_html(fig, full_html=False)

        # Create figures for each part
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        for part in range(nparts):
            fig_part = go.Figure()
            
            part_nodes = [node for node in nodes if membership[node] == part]
            part_elements = [element for i, element in enumerate(elements) if all(membership[node] == part for node in element)]
            
            # Create a mapping from global node indices to local indices
            node_mapping = {node: idx for idx, node in enumerate(part_nodes)}
            
            part_x_coords = [nodes[node][0] for node in part_nodes]
            part_y_coords = [nodes[node][1] for node in part_nodes]
            
            part_triangles = [(node_mapping[element[0]], node_mapping[element[1]], node_mapping[element[2]]) for element in part_elements]
            
            for triangle in part_triangles:
                fig_part.add_trace(go.Scatter(
                    x=[part_x_coords[triangle[0]], part_x_coords[triangle[1]], part_x_coords[triangle[2]], part_x_coords[triangle[0]]],
                    y=[part_y_coords[triangle[0]], part_y_coords[triangle[1]], part_y_coords[triangle[2]], part_y_coords[triangle[0]]],
                    mode='lines',
                    line=dict(color=colors[part % len(colors)])
                ))
            
            fig_part.update_layout(
                title=f'Part {part + 1}',
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate',
                showlegend=False,
                width=800,
                height=800
            )
            
            plot_html += pio.to_html(fig_part, full_html=False)

    return render_template_string("""
    <html>
        <head>
            <title>Triangulated Grid from .grd file</title>
        </head>
        <body>
            <h1>Triangulated Grid from .grd file</h1>
            <form method="post">
                <label for="url">Enter the URL of the .grd file:</label>
                <input type="text" id="url" name="url" required>
                <br>
                <label for="nparts">Enter the number of parts (nparts):</label>
                <input type="number" id="nparts" name="nparts" required>
                <br>
                <button type="submit">Submit</button>
            </form>
            <div>
                {{ plot_html|safe }}
            </div>
        </body>
    </html>
    """, plot_html=plot_html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)