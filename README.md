# PixPlot for Python 3.8+
# PixPlot Installation Guide

This guide will help you install PixPlot for Python 3.8+ environments (including Python 3.12 and 3.13). PixPlot is a tool for visualizing large image collections using WebGL, machine learning, and dimensionality reduction techniques.

## Prerequisites

- Python 3.8 or later (Python 3.12+ recommended)
- Conda or Miniconda (recommended for environment management)

## Installation Steps

### 1. Create a Python Environment

First, create a dedicated Python environment (Python 3.12+ recommended):

**Using Conda:**
```bash
conda create -n pixplot python=3.12
conda activate pixplot
```

**Using venv (if not using Conda):**
```bash
python3.12 -m venv pixplot-env
# On Windows
pixplot-env\Scripts\activate
# On macOS/Linux
source pixplot-env/bin/activate
```

### 2. Clone the Repository

```bash
https://github.com/XLabCU/pix-plot.git
cd pix-plot
```

### 3. Run the Installation Script

Run the installation script which will install all required dependencies:

```bash
python install.py
```

This script will:
- Install numpy (1.24.0+, compatible with both older and newer Python environments)
- Install TensorFlow 2.16.0+ (supports numpy 2.x for environments like Google Colab)
- Install critical dependencies (scipy, matplotlib, scikit-learn, umap-learn, etc.)
- Install the Yale fork of rasterfairy with automatic Python 3.8+ compatibility fix
- Install MulticoreTSNE (if conda is available)
- Install PixPlot itself

### 4. Verify the Installation (Automatic Rasterfairy Fix)

The installation script automatically applies the Python 3.8+ compatibility fix to rasterfairy. If for some reason the automatic fix fails, you can manually copy the rasterfairy.py file:

**Manual fix (if needed):**
```bash
# Find your Python site-packages directory
python -c "import site; print(site.getsitepackages())"

# Copy the fixed version (adjust the path based on your environment)
cp rasterfairy.py /path/to/site-packages/rasterfairy/rasterfairy.py
```

### 5. Verify Installation Success

To verify the installation was successful:

```bash
python -c "import pixplot; print('PixPlot successfully installed')"
```

If no errors appear and you see the success message, the installation is complete.

## Usage

You can now use PixPlot with Python 3.8+ (including Python 3.12 and 3.13). Basic usage:

```bash
# Process a folder of images
pixplot --images "path/to/images/*.jpg"

# With network visualization:
pixplot --images "path/to/images/*.jpg" --network_n_neighbors 5 --network_edge_threshold 0.7 --network_layout_iterations 100

# Run a local web server to view the visualization
pixplot --serve
```

### A note on the network things
You can use the stand-alone script to create network files for your own analysis and visualization. 

The 'baked-in' visualization of network neighbours uses these conventions:

1. Weight-Based Coloring: Added color gradients based on edge weights:
    - Stronger connections (higher weights) appear more white/bright
    - Weaker connections appear more blue
    - This creates a visual hierarchy where stronger connections stand out
2. Thicker Lines: Increased the linewidth from 1 to 2 to make edges more visible. Note that in WebGL, linewidth values greater than 1 are not supported on all platforms, but we've set it anyway for platforms that do support it.
3. Vertex Colors: Implemented vertex coloring to allow gradient effects along edges.
4. Weight Normalization: Added code to find the maximum weight and normalize all
  weights, ensuring consistent visual scaling regardless of the actual weight range.

## Troubleshooting

If you encounter errors after following these steps, verify that:

1. The installation script successfully applied the rasterfairy.py fix (check the installation output)
2. Your Python environment is 3.8 or later (3.12+ recommended)
3. You have a compatible numpy version (1.24.0+, will auto-install the best version for your environment)
4. If automatic rasterfairy fix failed, manually copy rasterfairy.py as shown in step 4

**Note for Google Colab users:** The installation is fully compatible with Colab's pre-installed packages including numpy 2.x

---

(original readme:)

# PixPlot

This repository contains code that can be used to visualize tens of thousands of images in a two-dimensional projection within which similar images are clustered together. The image analysis uses Tensorflow's Inception bindings, and the visualization layer uses a custom WebGL viewer.

See the [change log](https://github.com/YaleDHLab/pix-plot/wiki/Change-Log) for recent updates.

![App preview](./pixplot/web/assets/images/preview.png?raw=true)

## Installation & Dependencies

We maintain several platform-specific [installation cookbooks](https://github.com/YaleDHLab/pix-plot/wiki) online.

Broadly speaking, to install the Python dependencies, we recommend you [install Anaconda](https://www.anaconda.com/products/individual#Downloads) and then create a conda environment with Python 3.8 or later:

```bash
conda create --name=pixplot python=3.12
conda activate pixplot
```

Then you can install the dependencies by running:

```
bash
pip install https://github.com/yaledhlab/pix-plot/archive/master.zip
```

The website that PixPlot eventually creates requires a WebGL-enabled browser.

## Quickstart

If you have a WebGL-enabled browser and a directory full of images to process, you can prepare the data for the viewer by installing the dependencies above then running:

```bash
pixplot --images "path/to/images/*.jpg"
```

To see the results of this process, you can start a web server by running:

```bash
# for python 3.x
python -m http.server 5000

# for python 2.x
python -m SimpleHTTPServer 5000
```

The visualization will then be available at `http://localhost:5000/output`.

## Sample Data

To acquire some sample data with which to build a plot, feel free to use some data prepared by Yale's DHLab:

```bash
pip install image_datasets
```

Then in a Python script:

```python
import image_datasets
image_datasets.oslomini.download()
```

The `.download()` command will make a directory named `datasets` in your current working directory. That `datasets` directory will contain a subdirectory named 'oslomini', which contains a directory of images and another directory with a CSV file of image metadata. Using that data, we can next build a plot:

```bash
pixplot --images "datasets/oslomini/images/*" --metadata "datasets/oslomini/metadata/metadata.csv"
```

## Creating Massive Plots

If you need to plot more than 100,000 images but don't have an expensive graphics card with which to visualize huge WebGL displays, you might want to specify a smaller "cell_size" parameter when building your plot. The "cell_size" argument controls how large each image is in the atlas files; smaller values require fewer textures to be rendered, which decreases the GPU RAM required to view a plot:

```bash
pixplot --images "path/to/images/*.jpg" --cell_size 10
```

## Controlling UMAP Layout

The [UMAP algorithm](https://github.com/lmcinnes/umap) is particularly sensitive to three hyperparemeters:

```
--min_dist: determines the minimum distance between points in the embedding
--n_neighbors: determines the tradeoff between local and global clusters
--metric: determines the distance metric to use when positioning points
```

UMAP's creator, Leland McInnes, has written up a [helpful overview of these hyperparameters](https://umap-learn.readthedocs.io/en/latest/parameters.html). To specify the value for one or more of these hyperparameters when building a plot, one may use the flags above, e.g.:

```bash
pixplot --images "path/to/images/*.jpg" --n_neighbors 2
```

## Curating Automatic Hotspots

If installed and available, PixPlot uses [Hierarchical density-based spatial clustering of applications with noise](https://hdbscan.readthedocs.io/en/latest/index.html), a refinement of the earlier [DBSCAN](https://en.wikipedia.org/wiki/DBSCAN) algorithm, to find hotspots in the visualization. You may be interested in consulting this [explanation of how HDBSCAN works](https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html).

Tip: If you are using HDBSCAN and find that PixPlot creates too few (or only one) 'automatic hotspots', try lowering the `--min_cluster_size` from its default of 20. This often happens with smaller datasets (less than a few thousand.)

If HDBSCAN is not available, PixPlot will fall back to [scikit-learn](https://scikit-learn.org/)'s  implementation of [KMeans](https://scikit-learn.org/stable/modules/clustering.html#k-means).


## Adding Metadata

If you have metadata associated with each of your images, you can pass in that metadata when running the data processing script. Doing so will allow the PixPlot viewer to display the metadata associated with an image when a user clicks on that image.

To specify the metadata for your image collection, you can add ` --metadata=path/to/metadata.csv` to the command you use to call the processing script. For example, you might specify:

```bash
pixplot --images "path/to/images/*.jpg" --metadata "path/to/metadata.csv"
```

Metadata should be in a comma-separated value file, should contain one row for each input image, and should contain headers specifying the column order. Here is a sample metadata file:

| filename | category  | tags    | description   | permalink   | Year     |
| -------- | --------- | ------- | ------------- | ----------- | -------- |
| bees.jpg | yellow    | a\|b\|c | bees' knees   | https://... | 1776     |
| cats.jpg | dangerous | b\|c\|d | cats' pajamas | https://... | 1972     |

The following column labels are accepted:

| *Column*         | *Description*                                           |
| ---------------- | ------------------------------------------------------- |
| **filename**     | the filename of the image                               |
| **category**     | a categorical label for the image                       |
| **tags**         | a pipe-delimited list of categorical tags for the image |
| **description**  | a plaintext description of the image's contents         |
| **permalink**    | a link to the image hosted on another domain            |
| **year**         | a year timestamp for the image (should be an integer)   |
| **label**        | a categorical label used for supervised UMAP projection |
| **lat**          | the latitudinal position of the image                   |
| **lng**          | the longitudinal position of the image                  |

## IIIF Images

If you would like to process images that are hosted on a IIIF server, you can specify a newline-delimited list of IIIF image manifests as the `--images` argument. For example, the following could be saved as `manifest.txt`:

```bash
https://manifests.britishart.yale.edu/manifest/40005
https://manifests.britishart.yale.edu/manifest/40006
https://manifests.britishart.yale.edu/manifest/40007
https://manifests.britishart.yale.edu/manifest/40008
https://manifests.britishart.yale.edu/manifest/40009
```

One could then specify these images as input by running `pixplot --images manifest.txt --n_clusters 2`


## Demonstrations (Developed with PixPlot 2.0 codebase)

| Link | Image Count | Collection Info | Browse Images | Download for PixPlot
| ---------- | -------- | --------------- | ------------ | ------------ |
| [NewsPlot: 1910-1912](http://pixplot.yale.edu/v2/loc/) | 24,026 | [George Grantham Bain Collection](https://www.loc.gov/pictures/collection/ggbain/) | [News in the 1910s](https://www.flickr.com/photos/library_of_congress/albums/72157603624867509/with/2163445674/) | [Images](http://pixplot.yale.edu/datasets/bain/photos.tar), [Metadata](http://pixplot.yale.edu/datasets/bain/metadata.csv) |
| [Bildefelt i Oslo](http://pixplot.yale.edu/v2/oslo/) | 31,097 | [oslobilder](http://oslobilder.no) | [Advanced search, 1860-1924](http://oslobilder.no/search?advanced_search=1&query=&place=&from_year=1860&to_year=1924&id=&name=&title=&owner_filter=&producer=&depicted_person=&material=&technique=&event_desc=) | [Images](http://pixplot.yale.edu/datasets/oslo/photos.tar), [Metadata](http://pixplot.yale.edu/datasets/oslo/metadata.csv) |

## Acknowledgements

The DHLab would like to thank [Cyril Diagne](http://cyrildiagne.com/) and [Nicolas Barradeau](http://barradeau.com), lead developers of the spectacular [Google Arts Experiments TSNE viewer](https://artsexperiments.withgoogle.com/tsnemap/), for generously sharing ideas on optimization techniques used in this viewer, and [Lillianna Marie](https://github.com/lilliannamarie) for naming this viewer PixPlot.
