# MusicVis

This is an OpenGL-based music visualizer.

The visualizer is based on a sphere with simplex noise (https://pypi.org/project/opensimplex/) as its modulation. Several parameters are controllable in the visualizer, and tuning them differently yields vastly different results:
1. The displacement magnitude of the noise (currently scales with RMS)
2. The speed at which the noise oscillates (currently scales with median frequency content value)
3. The base size of the sphere (currently turned off)
4. The size of the bumps in the noise (currently turned off)

Note that the file used to run the full program is opengl_vis.py, the other files are intermediary steps in my process of learning to use OpenGL!

Also note that before any display is shown, please select the preferred input audio channel to read from. If you also want to listen to the music you are visualizing, be sure to use a channel that offers passthrough, such as a virtual audio cable, soundflower, etc.
