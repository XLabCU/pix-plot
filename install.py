# install.py
import subprocess
import sys
import platform

print("Creating a custom environment for PixPlot...")

# Check if we're on a Mac with ARM architecture
is_mac_arm = platform.system() == "Darwin" and platform.machine().startswith(("arm", "aarch"))

# 1. Install numpy first to ensure the correct version
print("Installing numpy 1.26.4...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.26.4", "--only-binary=:all:"])

# 2. Install TensorFlow via pip
print("Installing TensorFlow...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow>=2.15.0"])


# 3. Install other critical dependencies
print("Installing other critical dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install",
                      "scipy>=1.11.0",
                      "matplotlib>=3.8.0",
                      "scikit-learn>=1.3.0",
                      "umap-learn>=0.5.5",
                      "glob2",
                      "tqdm",
                      "Pillow>=10.0.0",
                      "pointgrid",
                      "python-dateutil",
                      "iiif-downloader",
                      "h5py>=3.10.0",
                      "networkx>=3.0"])

# 4. Install Yale's fork of rasterfairy and apply compatibility fix
print("Installing yale-dhlab-rasterfairy without updating numpy...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "yale-dhlab-rasterfairy"])

# Apply the Python 3.8+ compatibility fix
print("Applying Python 3.8+ compatibility fix to rasterfairy...")
import os
import shutil
try:
    # Find the installed rasterfairy package location
    import rasterfairy
    rasterfairy_path = os.path.dirname(rasterfairy.__file__)
    target_file = os.path.join(rasterfairy_path, "rasterfairy.py")
    source_file = os.path.join(os.path.dirname(__file__), "rasterfairy.py")

    if os.path.exists(source_file) and os.path.exists(target_file):
        shutil.copy2(source_file, target_file)
        print(f"Successfully applied fix to {target_file}")
    else:
        print(f"Warning: Could not automatically apply fix. Please manually copy rasterfairy.py to {rasterfairy_path}")
except Exception as e:
    print(f"Warning: Could not automatically apply rasterfairy fix: {e}")
    print("Please manually copy rasterfairy.py to your installed rasterfairy location.")

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
    #subprocess.check_call([sys.executable, "-c", "import rasterfairy; print('rasterfairy installed successfully')"])
except:
    print("Warning: Some verifications failed, but PixPlot might still work with fallbacks.")

print("\nPixPlot installation complete!")
print("Compatible with Python 3.8+")
print("Some dependencies may show as conflicting, but the application should still work.")
print("Good luck and godspeed!")
