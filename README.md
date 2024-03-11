Generate audio file for a guided visualization of a freedive.
## Dependency
ImageMagick
## Install
```
pip install git+https://github.com/djaney/imagine-freediving.git
```

## Example
- 30m depth
- charge at 10
- freefall at 20

Generate audio
```
freedive visualize 30m.mp4 30 --charge 10 --freefall 20
```

Overlay telemetry to video
```
overlay <video input path> <garmin fit file path> <garmin fit file dive index, starts with 0> <video output path> --dive_start_seconds <sync video and telemetry by specifying the time that the dive started>
```