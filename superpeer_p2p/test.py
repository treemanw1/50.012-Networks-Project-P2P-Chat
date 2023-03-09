import sys
sys.stdout.write("Line 1\nLine 2\nLine 3")
sys.stdout.write('Moving the cursor up one line with \033[F')
sys.stdout.write('This is on the same line as Line 3\n\033[F This is on the same line as Line 2')
sys.stdout.write('Moving the cursor up one line with \033[1A ')
sys.stdout.write('This is on the same line as Line 2\n \033[1A This is on the same line as Line 1')
