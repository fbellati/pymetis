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
        lines = file_content.split('\n')
        lines = [line for line in lines if not line.startswith('0') and line.strip() != '']
        print("Finished to split lines")
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
        print("Created array with nodes and elements")
        print("Creating adjacency array...")
        adjacency_array = convert_to_adjacency_list(elements)
        print("Created adjacency array")
        pymetis_opts = pymetis.Options(contig=1)
        print("Option.ptype=",pymetis_opts.ptype)
        print("Option.objtype=",pymetis_opts.objtype)
        print("Option.ctype=",pymetis_opts.ctype)
        print("Option.iptype=",pymetis_opts.iptype)
        print("Option.rtype=",pymetis_opts.rtype)
        print("Option.dbglvl=",pymetis_opts.dbglvl)
        print("Option.niter=",pymetis_opts.niter)
        print("Option.ncuts=",pymetis_opts.ncuts)
        print("Option.seed=",pymetis_opts.seed)
        print("Option.no2hop=",pymetis_opts.no2hop)
        print("Option.minconn=",pymetis_opts.minconn)
        print("Option.contig=",pymetis_opts.contig)
        print("Option.compress=",pymetis_opts.compress)
        print("Option.ccorder=",pymetis_opts.ccorder)
        print("Option.pfactor=",pymetis_opts.pfactor)
        print("Option.nseps=",pymetis_opts.nseps)
        print("Option.ufactor=",pymetis_opts.ufactor)
        print("Option.numbering=",pymetis_opts.numbering)
        print("Option.help=",pymetis_opts.help)
        print("Option.tpwgts=",pymetis_opts.tpwgts)
        print("Option.ncommon=",pymetis_opts.ncommon)
        print("Option.nooutput=",pymetis_opts.nooutput)
        print("Option.balance=",pymetis_opts.balance)
        print("Option.gtype=",pymetis_opts.gtype)
        print("Option.ubvec=",pymetis_opts.ubvec)
        print("Calling pymetys ...")
        n_cuts, membership = pymetis.part_graph(nparts, adjacency=adjacency_array, options=pymetis_opts)
        print("PyMetis finished!")
        print("Number of cuts: ",n_cuts)
        #print(membership)

        # Extract node coordinates for plotting
        x_coords = [nodes[node][0] for node in nodes]
        y_coords = [nodes[node][1] for node in nodes]

        # Extract element connectivity for triangulation
        triangles = [(elements[i][0], elements[i][1], elements[i][2]) for i in range(len(elements))]

        # Create a plotly figure for the entire graph
        fig = go.Figure()

        # Add triangles to the figure
        #for triangle in triangles:
        #    fig.add_trace(go.Scatter(
        #        x=[x_coords[triangle[0]], x_coords[triangle[1]], x_coords[triangle[2]], x_coords[triangle[0]]],
        #        y=[y_coords[triangle[0]], y_coords[triangle[1]], y_coords[triangle[2]], y_coords[triangle[0]]],
        #        mode='lines',
        #        line=dict(color='blue')
        #    ))
        #    print(".",end='')

        # Creare liste per tutte le coordinate x e y
        x_coords_all = []
        y_coords_all = []
        for triangle in triangles:
            x_coords_all.extend([x_coords[triangle[0]], x_coords[triangle[1]], x_coords[triangle[2]], None])
            y_coords_all.extend([y_coords[triangle[0]], y_coords[triangle[1]], y_coords[triangle[2]], None])
        print("AllCoords created!")
        # Creare una singola traccia Scattergl
        fig.add_trace(go.Scattergl(
            x=x_coords_all,
            y=y_coords_all,
            mode='lines',
            line=dict(color='blue')
        ))
        print("First Figure created! (in blue)")

        # Create figures for each part with different colors
        colors = [
            'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan',
            'magenta', 'yellow', 'black', 'white', 'lime', 'maroon', 'teal', 'aqua', 'fuchsia',
            'gold', 'silver', 'coral', 'indigo', 'khaki', 'lavender', 'plum', 'salmon', 'tan', 'violet',
            'wheat', 'crimson', 'chartreuse', 'amber', 'mint', 'peach', 'burgundy', 'turquoise', 'beige',
            'mustard', 'periwinkle', 'apricot'
        ]

        for part in range(nparts):
            part_nodes = [node for node in nodes if membership[node] == part]
            part_elements = [element for i, element in enumerate(elements) if all(membership[node] == part for node in element)]
            
            ##Gestione dei nodi di confine
            #part_elements = [element for i, element in enumerate(elements) if sum(membership[node] == part for node in element) >= 2]
            ## Aggiungi il terzo nodo alla partizione di cui non fa parte
            #for element in part_elements:
            #    for node in element:
            #        if membership[node] != part:
            #            part_nodes.append(node)
			#
            ## Rimuovi duplicati
            #part_nodes = list(set(part_nodes))

            # Create a mapping from global node indices to local indices
            node_mapping = {node: idx for idx, node in enumerate(part_nodes)}
            
            part_x_coords = [nodes[node][0] for node in part_nodes]
            part_y_coords = [nodes[node][1] for node in part_nodes]
            
            part_triangles = [(node_mapping[element[0]], node_mapping[element[1]], node_mapping[element[2]]) for element in part_elements]
            
            #for triangle in part_triangles:
            #    fig.add_trace(go.Scatter(
            #        x=[part_x_coords[triangle[0]], part_x_coords[triangle[1]], part_x_coords[triangle[2]], part_x_coords[triangle[0]]],
            #        y=[part_y_coords[triangle[0]], part_y_coords[triangle[1]], part_y_coords[triangle[2]], part_y_coords[triangle[0]]],
            #        mode='lines',
            #        line=dict(color=colors[part % len(colors)])
            #    ))

            # Creare liste per tutte le coordinate x e y
            part_x_coords_all = []
            part_y_coords_all = []
        
            for triangle in part_triangles:
                part_x_coords_all.extend([part_x_coords[triangle[0]], part_x_coords[triangle[1]], part_x_coords[triangle[2]], part_x_coords[triangle[0]], None])
                part_y_coords_all.extend([part_y_coords[triangle[0]], part_y_coords[triangle[1]], part_y_coords[triangle[2]], part_y_coords[triangle[0]], None])
            print("AllPartitionedCoords created!")
            # Creare una singola traccia Scattergl per ogni parte
            fig.add_trace(go.Scattergl(
                x=part_x_coords_all,
                y=part_y_coords_all,
                mode='lines',
                line=dict(color=colors[part % len(colors)])
            ))
            print("Add Trace executed")
        # Update layout for better visualization
        fig.update_layout(
            title='Triangulated Grid from .grd file',
            xaxis_title='X Coordinate',
            yaxis_title='Y Coordinate',
            showlegend=True,
            width=2000,
            height=1200
        )

        # Convert the plotly figure to HTML
        plot_html += pio.to_html(fig, full_html=False)

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