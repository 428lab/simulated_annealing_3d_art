# Run training
python simulated_annealing_3d_art.py --target-img love.bmp --num-cubes 200 --max-iter 40000 --start-temp 10.0 --end-temp 0.1 --min-cube-size 0.1 --max-cube-size 0.5

# View the result.
python viewer_3d_art.py --cubes-file love_cubes.pkl --img-size 128 
