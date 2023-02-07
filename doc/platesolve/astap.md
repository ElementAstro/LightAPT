ASTAP Command Line Interface
============================

# Description

ASTAP is a free stacking and astrometric solver (plate solver) program for deep sky images. In works with astronomical images in the FITS format, but can import RAW DSLR images or XISF, PGM, PPM, TIF, PNG and JPG  images. It has a powerful FITS viewer and the native astrometric solver can be used  by CCDCiel, NINA, APT or SGP imaging programs to synchronise the mount based on an image taken.

## API
```
-f  filename  {fits, tiff, png, jpg files}
-f  stdin     {read raw image from stdin}
-r  radius_area_to_search[degrees]
-z  downsample_factor[0,1,2,3,4] {Downsample prior to solving. 0 is auto}
-fov diameter_field[degrees]
-ra  center_right ascension[hours]
-spd center_south_pole_distance[degrees]
-s  max_number_of_stars  {default 500}
-t  tolerance  {default 0.007}
-m  minimum_star_size["]  {default 1.5}
-speed mode[auto/slow] {Slow is forcing small search steps to improve detection.}
-o  file {Name the output files with this base path & file name}
-d  path {specify a path to the star database}
-analyse snr_min {Analyse only and report median HFD and number of stars used}
-extract snr_min {As -analyse but additionally write a .csv file with the detected stars info}
-log   {Write the solver log to file}
-progress   {Log all progress steps and messages}
-update  {update the FITS header with the found solution. Jpg, png, tiff will be written as fits}
-wcs  {Write a .wcs file  in similar format as Astrometry.net. Else text style.}
```

Example:Depends on astap command line tool
```
astap_cli -f test.jpg -ra 05.1 -z 0 -spd 88 -wcs -update -r 90 -fov 2.8
```

AstapSolveAPI.solve(image, ra = None, dec = None, radius = None, fov = None, downsample = None, debug = False ,update = False , _wcs = True , timeout = 60)