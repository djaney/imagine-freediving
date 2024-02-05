Generate audio file for a guided visualization of a freedive.

## Install
```
pip install git+https://github.com/djaney/imagine-freediving.git
```

## Example
- 30m depth
- charge at 10
- freefall at 20
- 1m/s descent and ascent

Generate audio
```
freedive-visualize-mp3 30m.mp3 30 1 1 --charge 10 --freefall 20
```

Generate video
```
freedive-visualize-mp4 30m.mp3 30 1 1 --charge 10 --freefall 20
```