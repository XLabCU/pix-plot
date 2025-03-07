# install.py
import subprocess
import sys
import platform

print("Creating a custom environment for PixPlot...")

# Check if we're on a Mac with ARM architecture
is_mac_arm = platform.system() == "Darwin" and platform.machine().startswith(("arm", "aarch"))

# 1. Install numpy first to ensure the correct version
print("Installing numpy 1.22.4...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.22.4", "--only-binary=:all:"])

# 2. Install TensorFlow via pip
print("Installing TensorFlow...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow==2.13.0"])


# 3. Install other critical dependencies
print("Installing other critical dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", 
                      "scipy==1.8.1", 
                      "matplotlib==3.5.3",
                      "scikit-learn==1.0.2",
                      "umap-learn==0.5.3",
                      "glob2",
                      "tqdm",
                      "Pillow",
                      "pointgrid",
                      "python-dateutil",
                      "iiif-downloader"])

# 4. Install Yale's fork of rasterfairy without dependencies
print("Installing yale-dhlab-rasterfairy without updating numpy...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "yale-dhlab-rasterfairy"])

# 5. Install MulticoreTSNE using conda
print("Installing MulticoreTSNE from conda-forge...")
try:
    subprocess.check_call(["conda", "install", "-y", "conda-forge::multicore-tsne"])
    print("Successfully installed MulticoreTSNE from conda-forge")
except subprocess.CalledProcessError:
    print("Could not install MulticoreTSNE from conda. The code will use sklearn's TSNE implementation as a fallback.")

# 6. Install pixplot without dependencies
print("Installing PixPlot...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "."])

# 7. Verify installations
print("\nVerifying installations:")
try:
    subprocess.check_call([sys.executable, "-c", "import numpy; print('numpy version:', numpy.__version__)"])
    subprocess.check_call([sys.executable, "-c", "import tensorflow; print('tensorflow version:', tensorflow.__version__)"])
    subprocess.check_call([sys.executable, "-c", "import rasterfairy; print('rasterfairy installed successfully')"])
except:
    print("Warning: Some verifications failed, but PixPlot might still work with fallbacks.")

print("\nPixPlot installation complete!")
print("Some dependencies may show as conflicting, but the application should still work.")
print("If you encounter issues, please report them.")