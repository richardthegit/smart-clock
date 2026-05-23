import framebuf


def scaled_text(dest_fbuf, string, x, y, scale, color, bg_color = 0):
    if scale < 1:
        scale = 1
        
    # The native font is always 8 pixels high
    src_width = len(string) * 8
    src_height = 8
    
    # Allocate a temporary buffer for the unscaled text strip
    # MONO_HLSB format uses 1 byte per 8 horizontal pixels
    buf_size = (src_width * src_height) // 8
    src_buf = bytearray(buf_size)
    src_fbuf = framebuf.FrameBuffer(src_buf, src_width, src_height, framebuf.MONO_HLSB)
    
    # Render the unscaled text to our temporary buffer
    src_fbuf.fill(0)
    src_fbuf.text(string, 0, 0, 1)
    
    # Read back the bits and scale them up onto the destination buffer
    for src_y in range(src_height):
        dest_y = y + (src_y * scale)
        for src_x in range(src_width):
            dest_x = x + (src_x * scale)
            
            # Check if the pixel is turned on in the source text strip
            if src_fbuf.pixel(src_x, src_y):
                dest_fbuf.fill_rect(dest_x, dest_y, scale, scale, color)
            elif bg_color is not None:
                dest_fbuf.fill_rect(dest_x, dest_y, scale, scale, bg_color)
