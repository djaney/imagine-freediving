```
usage: freedive-visualize-mp3 [-h] [--charge CHARGE] [--freefall FREEFALL] [--float FLOAT] filename targe_depth descent_rate ascent_rate

Generate audio file for a guided visualization of a freedive

positional arguments:
  filename             file name with .mp3
  targe_depth          Target depth in meters
  descent_rate         Descent rate in positive meters per second
  ascent_rate          Ascent rate in positive meters per second

optional arguments:
  -h, --help           show this help message and exit
  --charge CHARGE      Depth to charge mouthfill
  --freefall FREEFALL  Depth to freefall
  --float FLOAT        Depth to let neutral buoyancy take over
```