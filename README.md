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
freedive-visualize 30m.mp4 --generate 30 1 1 --charge 10 --freefall 20
```