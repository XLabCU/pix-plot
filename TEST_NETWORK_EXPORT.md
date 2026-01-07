# Testing the Network Export Script

## Prerequisites
1. Install PixPlot following the updated installation instructions
2. Process some images to generate PixPlot output

## Test Procedure in Google Colab

```python
# After installing pixplot and running it on some test images...

# Test the network export script
!python pixplot_network_export.py \
  --data_dir output \
  --n_neighbors 5 \
  --output network_edges.csv \
  --layout umap \
  --include_thumbs \
  --include_metadata
```

## Expected Output

The script should:
1. Find the manifest.json in the output directory
2. Load the image list and UMAP layout data
3. Calculate nearest neighbors for each image
4. Generate two CSV files:
   - `network_edges.csv` - contains edge relationships with weights
   - `network_edges_nodes.csv` - contains node attributes and metadata

## Verification

Check that the CSV files were created:

```python
import pandas as pd

# Load and inspect the edges
edges = pd.read_csv('network_edges.csv')
print(f"Edges: {len(edges)} rows")
print(edges.head())

# Load and inspect the nodes
nodes = pd.read_csv('network_edges_nodes.csv')
print(f"Nodes: {len(nodes)} rows")
print(nodes.head())
```

## Compatibility Notes

The script is compatible with:
- NumPy 1.24.0+ (including NumPy 2.x)
- SciPy 1.11.0+
- Python 3.8+

No deprecated functions are used:
- ✅ Uses `scipy.spatial.distance.cdist()` (stable API)
- ✅ Uses `scipy.spatial.distance.euclidean()` (stable API)
- ✅ Uses `np.array()` and `np.argsort()` (stable API)
- ✅ No `np.float` or other deprecated type aliases

## Troubleshooting

If the script fails to find files, ensure:
1. The `--data_dir` points to the correct pixplot output directory
2. The output directory contains a `manifest.json` file
3. The layout files (in `layouts/` subdirectory) exist
4. The image list (in `imagelists/` subdirectory) exists
