### Description

Script takes video, extracts frames with given step and resizes them

### Usage
`python prepare_images.py -h` for help

`python prepare_images.py -s <start-second> -e <end-second> -i <input> -o <output> -d <frame-distance> -w <width> -l <height>`

- `-s` / `--start-second` **required** – first second of the video which be processed. Should be in range positive integer.
- `-e` / `--end-second` **required** – last second of the video which be processed. Should be not less than start second. Cuts to last second of the video if larger.
- `-i` / `--input` **required**  – absolute path to video being processed.
- `-o` / `--output` **required** – path to directory, in which output images would be stored.
- `-d` / `--frame-distance` **required** – distance between frames being saved. Should be positive integer.
- `-w` / `--width` – width of output images. Should be positive integer. Frame width by default.
- `-l` / `--height` – height of output images. Should be positive integer. Frame height by default.
