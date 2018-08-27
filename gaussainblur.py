for y in range(0, int(img_h)):
    for x in range(0, int(img_w)):
        r, g, b, temp_r, temp_g, temp_b, temp_a, count = 0, 0, 0, 0, 0, 0, 0, 0

        for kernel_offset_y in range(0 - kernel_half, 0 + kernel_half):
            for kernel_offset_x in range(0 - kernel_half, 0 + kernel_half):
                # Don't check outside screen edges...
                if (x + kernel_offset_x > 0
                        and x + kernel_offset_x < img_w
                        and y + kernel_offset_y > 0
                        and y + kernel_offset_y < img_h):
                    temp_r, temp_g, temp_b, temp_a = img.get_at((x + kernel_offset_x,
                                                                 y + kernel_offset_y))

                r += temp_r
                g += temp_g
                b += temp_b
                count += 1

        if (r > 0):
            r = r / count
        if (g > 0):
            g = g / count
        if (b > 0):
            b = b / count


