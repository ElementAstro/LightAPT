ASTAP Command Line Interface
============================

# Description

As another very famous solver , ASTAP provides some command line interface for other software to implement . The following command line options are available.
`
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
`

Example:
    Depends on astap command line tool
    astap_cli -f apod2.jpg --ra 05:38:18 -z 0  -speed -spd -02:45:19 -wcs