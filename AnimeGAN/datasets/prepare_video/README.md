### Description

Script takes video, extracts frames with given step and resizes them

### Usage
`python prepare_images.py -h` for help

`python prepare_images.py -s <start-frame> -e <end-frame> -i <input> -o <output> -d <frame-distance> -w <width> -l <height>`

- `-s` / `--start-frame` – first frame of the video which be processed. Should be in range [1, `cnt`], where `cnt` is total frames in the video.
- `-e` / `--end-frame` – last frame of the video which be processed. Could not result in image if `e - s` is not divisible by `frame-distance`. Should be in range [`s`, `cnt`], where `s` is start frame and `cnt` is total frames in the video.
- `-i` / `--input` – absolute path to video being processed.
- `-o` / `--output` – path to directory, in which output images would be stored.
- `-d` / `--frame-distance` – distance between frames being saved. Should be positive integer.
- `-w` / `--width` – width of output images. Should be positive integer.
- `-l` / `--height` – height of output images. Should be positive integer.

All arguments are required.

