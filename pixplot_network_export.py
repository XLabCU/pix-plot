#!/usr/bin/env python3
"""
PixPlot Network Export

This script generates a CSV file containing nearest neighbor information for images
processed by PixPlot, suitable for import into Gephi for network analysis of visual influence.

Usage:
  python pixplot_network_export.py --data_dir path/to/pixplot/output --n_neighbors 10 --output network.csv

Arguments:
  --data_dir: Directory containing PixPlot output data (with manifest.json, imagelists, thumbs, etc.)
  --n_neighbors: Number of nearest neighbors to find for each image
  --output: Output CSV file path
  --layout: Layout to use for finding neighbors (umap, tsne, etc.) [default: umap]
  --include_thumbs: Include thumbnail paths in output
  --include_metadata: Include all available metadata in output

Note: This script should point to the main output directory that contains the manifest.json file.
"""

import os
import json
import gzip
import csv
import numpy as np
import argparse
from scipy.spatial import distance
from datetime import datetime
import glob
from collections import defaultdict

def timestamp():
    """Return a string for printing the current time"""
    return str(datetime.now()) + ':'

def read_json(path, gzipped=False, encoding='utf8'):
    """Read a JSON file, handling gzipped files if necessary"""
    try:
        if gzipped or path.endswith('.gz'):
            with gzip.GzipFile(path, 'r') as f:
                return json.loads(f.read().decode(encoding))
        else:
            with open(path) as f:
                return json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def get_layout_path(data_dir, plot_id, layout_name):
    """Find the path to a layout file"""
    layout_dir = os.path.join(data_dir, 'layouts')
    if not os.path.exists(layout_dir):
        print(f"Layout directory {layout_dir} not found")
        # Try to look for layouts in a 'data' subdirectory if available
        layout_dir_alt = os.path.join(data_dir, 'data', 'layouts')
        if os.path.exists(layout_dir_alt):
            layout_dir = layout_dir_alt
        else:
            return None
    
    # Try both compressed and uncompressed formats
    candidates = [
        # Standard layout
        os.path.join(layout_dir, f"{layout_name}-{plot_id}.json.gz"),
        os.path.join(layout_dir, f"{layout_name}-{plot_id}.json"),
        
        # For umap with different parameters
        *glob.glob(os.path.join(layout_dir, f"umap-n_neighbors_*-min_dist_*-{plot_id}.json.gz")),
        *glob.glob(os.path.join(layout_dir, f"umap-n_neighbors_*-min_dist_*-{plot_id}.json"))
    ]
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
            
    print(f"Could not find layout file for {layout_name}")
    return None

def load_metadata(data_dir, image_filenames):
    """Load metadata for all images"""
    # Try different possible metadata locations
    metadata_dirs = [
        os.path.join(data_dir, 'metadata', 'file'),
        os.path.join(data_dir, 'data', 'metadata', 'file')
    ]
    
    metadata_dir = None
    for dir_path in metadata_dirs:
        if os.path.exists(dir_path):
            metadata_dir = dir_path
            break
            
    if not metadata_dir:
        print(f"Metadata directory not found in any expected location")
        return {}
    
    metadata = {}
    for filename in image_filenames:
        base_filename = os.path.basename(filename)
        metadata_path = os.path.join(metadata_dir, base_filename + '.json')
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path) as f:
                    metadata[base_filename] = json.load(f)
            except Exception as e:
                print(f"Error reading metadata for {base_filename}: {e}")
                metadata[base_filename] = {}
        else:
            metadata[base_filename] = {}
            
    return metadata

def find_nearest_neighbors(positions, n_neighbors):
    """Find n nearest neighbors for each point based on Euclidean distance"""
    # Calculate pairwise distances
    dist_matrix = distance.cdist(positions, positions, 'euclidean')
    
    # For each point, get indices of n+1 closest points (including itself)
    # Then remove itself (which is at index 0)
    neighbors = []
    for i in range(len(positions)):
        # Get indices of closest points
        closest_indices = np.argsort(dist_matrix[i])
        # Skip the first one (itself) and take the next n
        neighbors.append(closest_indices[1:n_neighbors+1])
        
    return neighbors

def get_thumbnail_path(data_dir, filename):
    """Generate path to thumbnail for an image"""
    # Try different possible thumbnail locations
    thumb_paths = [
        os.path.join(data_dir, 'thumbs', os.path.basename(filename)),
        os.path.join(data_dir, 'data', 'thumbs', os.path.basename(filename))
    ]
    
    for path in thumb_paths:
        if os.path.exists(path):
            return path
    
    # Return a default path even if it doesn't exist
    return os.path.join(data_dir, 'thumbs', os.path.basename(filename))

def get_original_path(data_dir, filename):
    """Generate path to original image"""
    # Try different possible original image locations
    original_paths = [
        os.path.join(data_dir, 'originals', os.path.basename(filename)),
        os.path.join(data_dir, 'data', 'originals', os.path.basename(filename))
    ]
    
    for path in original_paths:
        if os.path.exists(path):
            return path
    
    # Return a default path even if it doesn't exist
    return os.path.join(data_dir, 'originals', os.path.basename(filename))

def extract_network_data(data_dir, n_neighbors, layout_name, include_thumbs=True, include_metadata=True):
    """Extract network data from PixPlot output
    
    Returns:
        tuple: (network_data, metadata_dict) where network_data is a list of edge dictionaries
               and metadata_dict is a dictionary of metadata for each image
    """
    # First identify the plot_id from the manifest
    # This will help us locate the correct files
    print(timestamp(), f"Looking for PixPlot data in: {data_dir}")
    
    # Find all possible manifest.json files
    manifest_candidates = [
        os.path.join(data_dir, 'manifest.json'),
        os.path.join(data_dir, 'data', 'manifest.json')
    ]
    
    manifest_path = None
    for path in manifest_candidates:
        if os.path.exists(path):
            manifest_path = path
            break
            
    if not manifest_path:
        print(f"Manifest file not found in any expected location")
        return None
    
    print(f"Found manifest at {manifest_path}")
    manifest = read_json(manifest_path)
    if not manifest:
        print("Failed to read manifest")
        return None
    
    plot_id = manifest.get('plot_id')
    is_gzipped = manifest.get('gzipped', False)
    print(f"Plot ID: {plot_id}, Gzipped: {is_gzipped}")
    
    # Find and load the imagelist
    imagelist_path = manifest.get('imagelist')
    if not imagelist_path:
        print("Image list path not found in manifest")
        
        # Try to find an imagelist in the expected directory
        imagelist_candidates = glob.glob(os.path.join(data_dir, 'imagelists', 'imagelist*.json*'))
        if not imagelist_candidates:
            imagelist_candidates = glob.glob(os.path.join(data_dir, 'data', 'imagelists', 'imagelist*.json*'))
            
        if imagelist_candidates:
            imagelist_path = imagelist_candidates[0]
            print(f"Found alternative imagelist at: {imagelist_path}")
        else:
            print("Could not find any imagelist files")
            return None
    else:
        # If manifest provides a path, make it absolute
        # First check if the path exists as is
        if not os.path.exists(imagelist_path):
            # Try to find the file relative to data_dir
            relative_path = os.path.basename(imagelist_path)
            imagelist_path = os.path.join(data_dir, 'imagelists', relative_path)
            if not os.path.exists(imagelist_path):
                imagelist_path = os.path.join(data_dir, 'data', 'imagelists', relative_path)
                if not os.path.exists(imagelist_path):
                    print(f"Could not find imagelist file: {relative_path}")
                    return None

    print(f"Loading imagelist from {imagelist_path}")
    image_list_data = read_json(imagelist_path, gzipped=is_gzipped)
    if not image_list_data:
        print("Failed to read imagelist")
        return None
        
    image_filenames = image_list_data.get('images', [])
    if not image_filenames:
        print("No images found in image list")
        return None
    
    print(f"Found {len(image_filenames)} images in the image list")
    
    # Get the layout for finding neighbors
    if layout_name == 'umap' and 'umap' in manifest.get('layouts', {}):
        # For UMAP, we need to handle the variants
        umap_data = manifest['layouts']['umap']
        if 'variants' in umap_data and umap_data['variants']:
            layout_path = umap_data['variants'][0]['layout']
            layout_path = os.path.join(data_dir, os.path.basename(layout_path))
            print(f"Found UMAP layout path in manifest: {layout_path}")
        else:
            layout_path = get_layout_path(data_dir, plot_id, layout_name)
    else:
        # For other layouts
        layout_path = get_layout_path(data_dir, plot_id, layout_name)
    
    if not layout_path or not os.path.exists(layout_path):
        print(f"Layout file for {layout_name} not found")
        
        # Try to look for any umap layout files
        layout_files = glob.glob(os.path.join(data_dir, 'layouts', 'umap*.json*'))
        if not layout_files:
            layout_files = glob.glob(os.path.join(data_dir, 'data', 'layouts', 'umap*.json*'))
        
        if layout_files:
            layout_path = layout_files[0]
            print(f"Found alternative layout file: {layout_path}")
        else:
            print("Could not find any layout files")
            return None
    
    # Load the positions from the layout
    print(f"Loading positions from {layout_path}")
    positions_data = read_json(layout_path, gzipped=is_gzipped)
    if not positions_data:
        print("Failed to read positions data")
        return None
    
    # If positions is a dictionary with 'positions' key, use that
    if isinstance(positions_data, dict) and 'positions' in positions_data:
        positions = positions_data['positions']
    else:
        positions = positions_data
    
    positions = np.array(positions)
    
    if len(positions) != len(image_filenames):
        print(f"Warning: Number of positions ({len(positions)}) doesn't match number of images ({len(image_filenames)})")
        # Use the smaller number to avoid index errors
        min_count = min(len(positions), len(image_filenames))
        positions = positions[:min_count]
        image_filenames = image_filenames[:min_count]
    
    # Find nearest neighbors
    print(f"Finding {n_neighbors} nearest neighbors for each image")
    neighbors = find_nearest_neighbors(positions, n_neighbors)
    
    # Load metadata if requested
    metadata = {}
    if include_metadata:
        print("Loading metadata")
        metadata = load_metadata(data_dir, image_filenames)
    
    # Prepare network data
    network_data = []
    print("Creating network data")
    
    for i, filename in enumerate(image_filenames):
        base_filename = os.path.basename(filename)
        
        # Get the nearest neighbors for this image
        neighbor_indices = neighbors[i]
        
        # Get the position data for visualization
        pos_x, pos_y = positions[i]
        
        # Create a row for each neighbor relationship
        for j, neighbor_idx in enumerate(neighbor_indices):
            neighbor_filename = os.path.basename(image_filenames[neighbor_idx])
            
            # Calculate distance between points
            distance_val = distance.euclidean(positions[i], positions[neighbor_idx])
            
            row = {
                'source': base_filename,
                'target': neighbor_filename,
                'weight': 1.0 / (distance_val + 1e-5),  # Convert distance to weight (closer = higher weight)
                'distance': distance_val,
                'rank': j + 1,  # Neighbor rank (1 = closest)
                'source_x': pos_x,
                'source_y': pos_y,
                'target_x': positions[neighbor_idx][0],
                'target_y': positions[neighbor_idx][1],
            }
            
            # No longer adding thumbnail paths to edges - they will be added to nodes instead
            
            # No longer adding metadata to edges - it will be added to nodes instead
            
            network_data.append(row)
    
    print(f"Created network data with {len(network_data)} connections")
    # Return both the network data and the metadata
    return network_data, metadata

def write_csv(network_data, output_path):
    """Write network data to CSV file"""
    if not network_data:
        print("No network data to write")
        return False
    
    # Get all unique column names
    fieldnames = set()
    for row in network_data:
        fieldnames.update(row.keys())
    
    # Make sure essential columns come first
    essential_cols = ['source', 'target', 'weight', 'distance', 'rank']
    fieldnames = essential_cols + sorted(list(fieldnames - set(essential_cols)))
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(network_data)
        print(f"Wrote {len(network_data)} relationships to {output_path}")
        return True
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return False

def create_node_csv(network_data, metadata, data_dir, include_thumbs, output_path):
    """Create a nodes CSV file with unique nodes and their attributes"""
    if not network_data:
        print("No network data to create node file")
        return False
    
    nodes = {}
    
    # Collect unique nodes and their positions
    for row in network_data:
        # Process source node
        source = row['source']
        if source not in nodes:
            nodes[source] = {
                'id': source,
                'x': row['source_x'],
                'y': row['source_y']
            }
            
            # Add thumbnail paths if requested
            if include_thumbs:
                nodes[source]['thumb'] = get_thumbnail_path(data_dir, source)
                nodes[source]['original'] = get_original_path(data_dir, source)
        
        # Process target node
        target = row['target']
        if target not in nodes:
            nodes[target] = {
                'id': target,
                'x': row['target_x'],
                'y': row['target_y']
            }
            
            # Add thumbnail paths if requested
            if include_thumbs:
                nodes[target]['thumb'] = get_thumbnail_path(data_dir, target)
                nodes[target]['original'] = get_original_path(data_dir, target)
    
    # Add metadata to nodes
    for node_id in nodes:
        if node_id in metadata:
            for key, value in metadata[node_id].items():
                if key != 'filename':  # Skip filename to avoid duplication
                    nodes[node_id][key] = value
    
    # Get all possible field names
    fieldnames = set()
    for node_data in nodes.values():
        fieldnames.update(node_data.keys())
    
    # Ensure 'id' is the first column
    fieldnames = ['id'] + sorted(list(fieldnames - {'id'}))
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(nodes.values())
        print(f"Wrote {len(nodes)} nodes to {output_path}")
        return True
    except Exception as e:
        print(f"Error writing nodes CSV: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate network data from PixPlot output for Gephi')
    parser.add_argument('--data_dir', type=str, required=True, help='Directory containing PixPlot output data (with manifest.json)')
    parser.add_argument('--n_neighbors', type=int, default=10, help='Number of nearest neighbors to find')
    parser.add_argument('--output', type=str, default='pixplot_network.csv', help='Output CSV file path')
    parser.add_argument('--layout', type=str, default='umap', help='Layout to use for finding neighbors')
    parser.add_argument('--include_thumbs', action='store_true', help='Include thumbnail paths in output')
    parser.add_argument('--include_metadata', action='store_true', help='Include metadata in output')
    
    args = parser.parse_args()
    
    print(timestamp(), f"Extracting network data for {args.n_neighbors} nearest neighbors using {args.layout} layout")
    print(timestamp(), f"Looking for PixPlot data in {args.data_dir}")
    
    # Check if the data_dir exists
    if not os.path.exists(args.data_dir):
        print(f"Error: Directory {args.data_dir} does not exist")
        return
        
    # Extract network data and metadata
    result = extract_network_data(
        args.data_dir, 
        args.n_neighbors, 
        args.layout,
        include_thumbs=args.include_thumbs,
        include_metadata=args.include_metadata
    )
    
    if not result:
        print("Failed to extract network data")
        return
        
    network_data, metadata = result
    
    if not network_data:
        print("No network data was generated")
        return
    
    # Write edges CSV
    edges_path = args.output
    success = write_csv(network_data, edges_path)
    
    if success:
        # Create and write nodes CSV
        nodes_path = os.path.splitext(args.output)[0] + "_nodes.csv"
        create_node_csv(
            network_data, 
            metadata,  # Pass the metadata directly to the node creation function
            args.data_dir,
            args.include_thumbs,
            nodes_path
        )
        
        print(timestamp(), f"Network data successfully exported to {edges_path} and {nodes_path}")
        print(f"You can now import these files into Gephi for network analysis.")
        print(f"  1. Import {os.path.basename(nodes_path)} as nodes table")
        print(f"  2. Import {os.path.basename(edges_path)} as edges table")
        print(f"  3. Use the 'weight' column for edge weight")
    else:
        print("Failed to write network data")

if __name__ == "__main__":
    main()