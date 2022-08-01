# MusicVis

This is an OpenGL-based music visualizer.

The visualizer is based on a sphere with simplex noise (https://pypi.org/project/opensimplex/) as its modulation. Several parameters are controllable in the visualizer, and tuning them differently yields vastly different results:
1. The displacement magnitude of the noise (currently scales with RMS)
2. The speed at which the noise oscillates (currently scales with median frequency content value)
3. The base size of the sphere (currently turned off)
4. The size of the bumps in the noise (currently turned off)
