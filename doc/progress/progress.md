# Progress

## Collision detection for ground shapes
### 6/18/2024
![Luna standing on the ground](images/004.jpg)

New collision detection for resolving the ground just dropped, it's much smoother.

## Collision Detection and Resolution
### 6/4/2024
![Luna sitting on the ground](images/003.jpg)

I implemented a simple polygon collision detection and resolution algorithm and now Luna can jump up and down on
the ground. All map regions are triangulated now. 


## Gravity, texture drawing
### 6/2/2024
![Blue box showing Luna](images/002.jpg)
The background "tile" (it's just one huge map tile) is being drawn now.
You can't tell from this shot but rotation works too. Luna can jump and
fall, but there's no collision detection yet. The origin (0, 0) is drawn
as a red star in a white circle.


## Collision Geometry
### 5/31/2024
![First thing worth showing](images/001.png)

This screenshot shows the polygons loaded from the Tiled test map with the classes loaded (green = collision geometry, red = death zone).
The PlayView is using `Camera2D` now.