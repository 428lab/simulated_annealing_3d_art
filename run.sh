# Run training
python simulated_annealing_3d_art.py --target-img love.bmp --num-cubes 200 --cube-size 0.2 --max-iter 10000 --start-temp 10.0 --end-temp 0.1

# View the result.
python viewer_3d_art.py
