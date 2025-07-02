# import math
# import os
import warnings
# from tqdm import tqdm

warnings.simplefilter("ignore")

# root_path = os.path.join(root_path, "new_data")

CELL_OFFSETS = [
    [-1, -1],
    [-1, 0],
    [-1, 1],
    [1, -1],
    [1, 0],
    [1, 1],
    [0, -1],
    [0, 0],
    [0, 1]
]

def squared_distance_3d(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return dx * dx + dy * dy + dz * dz

def get_closest(sources, source_indexes, targets, max_dist_squared):
    for index, source in enumerate(sources):
        min_dist = max_dist_squared
        closest = None
        for target in targets:
            dist_squared = squared_distance_3d(source, target)
            if dist_squared < min_dist:
                min_dist = dist_squared
                closest = target
        if closest:
            yield [source_indexes[index]] + source + closest

def add_to_cell(node, cells):
    cx = cells.setdefault(node['cell'][0], {})
    cy = cx.setdefault(node['cell'][1], {'nodes': [], 'positions': []})
    cy['nodes'].append(node['__index__'])
    cy['positions'].append(node['position'])
    

def distance_edges(nodes, type_field, target_type, max_dist):
    source_cells = {}
    target_cells = {}

    for node_index, node in enumerate(nodes):
        node['__index__'] = node_index
        node['position'] = [node.get('x', 0), node.get('y', 0), node.get('z', 0)]
        node['cell'] = [int(node['x'] / max_dist), int(node['y'] / max_dist)]

        if node[type_field] == target_type:
            add_to_cell(node, target_cells)
        else:
            add_to_cell(node, source_cells)

    max_dist_squared = max_dist * max_dist
    for source_cell_x, source_cell_y_dict in source_cells.items():
        for source_cell_y, sources in source_cell_y_dict.items():
            all_targets = []
            for offset_x, offset_y in CELL_OFFSETS:
                cell_x = int(source_cell_x) + offset_x
                cell_y = int(source_cell_y) + offset_y
                targets = target_cells.get(cell_x, {}).get(cell_y, None)
                if targets:
                    all_targets.extend(targets['positions'])
            if all_targets:
                yield from get_closest(sources['positions'], sources['nodes'], all_targets, max_dist_squared)

def calculate_nearest_endothelial_cell(nodes, type_field="Cell Type", target_type="Endothelial", max_dist=1000, report_progress=True):
    # nodes, type_field, target_type, max_dist = msg['data']['nodes'], msg['data']['type_field'], msg['data']['target_type'], msg['data']['maxDist']
    edges = [None] * len(nodes)
    index = 0
    report_step = len(nodes) // 10
    for edge in distance_edges(nodes, type_field, target_type, max_dist):
        edges[index] = edge
        if index % report_step == 0:
            percentage = round((index / len(nodes)) * 100)
            if report_progress:
                print({'status': 'processing', 'percentage': percentage, 'node_index': edge[0]})
        index += 1
    if report_progress:
        print({'status': 'complete', 'percentage': 100})
    return edges[:index]
