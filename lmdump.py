import sys, struct, subprocess, os, binascii
file = sys.argv[1]

filesize = 0


def main():
    with open(file, "rb") as fp:
        fp.seek(0)
        if fp.read(3) != b'LMB':
            print("This is not a valid lumen file")
        else:
            log = file.replace('.lm', '.log')
            with open(log, "w") as fpw:
                header(fp, fpw)
                chunk = fp.read(4)
                while chunk != bytes.fromhex('0000FF00'):
                    if chunk == bytes.fromhex('0000F001'):
                        symbol_list = symbols(fp, fpw)

                    elif chunk == bytes.fromhex('0000F002'):
                        color_list = colors(fp, fpw)

                    elif chunk == bytes.fromhex('0000F003'):
                        transforms_list = transforms(fp, fpw)

                    elif chunk == bytes.fromhex('0000F004'):
                        bounds_list = bounds(fp, fpw)

                    elif chunk == bytes.fromhex('0000F005'):
                        as_list = actionscript(fp, fpw)

                    elif chunk == bytes.fromhex('0000F007'):
                        atlas_list = atlas(fp, fpw)

                    elif chunk == bytes.fromhex('0000F008'):
                        F008_list = (unknowns(fp, fpw, "F008"))

                    elif chunk == bytes.fromhex('0000F009'):
                        F009_list = (unknowns(fp, fpw, "F009"))

                    elif chunk == bytes.fromhex('0000F00A'):
                        F00A_list = (unknowns(fp, fpw, "F00A"))

                    elif chunk == bytes.fromhex('0000000A'):
                        unk_000A_list = (unknowns(fp, fpw, "000A"))

                    elif chunk == bytes.fromhex('0000F00B'):
                        F00B_list = (unknowns(fp, fpw, "F00B"))

                    elif chunk == bytes.fromhex('0000F00C'):
                        p_list = properties(fp, fpw)

                    elif chunk == bytes.fromhex('0000F00D'):
                        defines_list = defines(fp, fpw)

                    elif chunk == bytes.fromhex('0000F024'):
                        graphic_list = graphic(fp, fpw)

                    elif chunk == bytes.fromhex('0000F037'):
                        color_matrix_list = color_matrix(fp, fpw)

                    elif chunk == bytes.fromhex('0000F103'):
                        positions_list = positions(fp, fpw)

                    elif chunk == bytes.fromhex('00000025'):
                        Dynamic_text_list = dynamic_text(fp, fpw)

                    else:
                        fpw.writelines(["\nsomething broke at the below address: \n", format((fp.tell() - 0x4), "<8X")])
                        fpw.writelines(["\n", format((int.from_bytes(chunk, "big")), "0>8X")])
                        fpw.writelines(["\n", str(chunk)])
                        exit()
                    while fp.tell() % 4 != 0:
                        fp.seek(1, 1)
                    chunk = fp.read(4)
                    if chunk == bytes.fromhex('00000000'):
                        chunk = fp.read(4)

def header(fp, fpw):
    global filesize
    fp.seek(0x1C)
    filesize = fp.read(4)
    fp.seek(0x40)

def symbols(fp, fpw):
    fpw.writelines(["Symbols # Offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n{"])

    dword_length = int.from_bytes(fp.read(4), "big")
    num_strings = int.from_bytes(fp.read(4), "big")

    str_len = 0
    longest = 0
    counter = 0
    symbol_list = []
    symbol_offset = []

    while counter < int(num_strings):
        while fp.tell() % 4 != 0:
            fp.seek(1, 1)
        symbol_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        str_len = int.from_bytes(fp.read(4), "big")
        actual_str_len = 0

        if str_len == 0:
            str_len = int.from_bytes(fp.read(4), "big")

        string = []
        x = 0
        while x < str_len:
            try:
                string.append(fp.read(1).decode("utf-8"))
                x += 1
                actual_str_len += 1
            except:
                fp.seek(-1, 1)
                item = int.from_bytes(fp.read(3), "big")
                string.append(format(item, "X"))
                x += 3
                actual_str_len += 6
        if longest < actual_str_len:
            longest = actual_str_len

        symbol_list.append(''.join(string))
        counter += 1

    for x in range(len(symbol_list)):
        fpw.writelines(['\n\t"', format(symbol_list[x] + '"', ("<" + str(longest + 4) + "s")), " # 0x",format(x, "0>4X"), "; Offset: ", format(symbol_offset[x])])

    fpw.writelines(["\n}"])

    return symbol_list

def colors(fp, fpw):
    fpw.writelines(["\nColors # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])
    
    dword_length = int.from_bytes(fp.read(4), "big")
    num_colors = int.from_bytes(fp.read(4), "big")
    counter = 0
    color_list = []
    color_offset = []
    
    while counter < int(num_colors):
        color_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        r = int.from_bytes(fp.read(2), "big")
        g = int.from_bytes(fp.read(2), "big")
        b = int.from_bytes(fp.read(2), "big")
        a = int.from_bytes(fp.read(2), "big")
        color_list.append([["0x" + format(r, "0^4X"), "0x" + format(g, "0^4X"), "0x" + format(b, "0^4X"), "0x" + format(a, "0^4X")], ""])
        counter += 1
    for x in range(len(color_list)):
        fpw.writelines(["\n\t", str(color_list[x]).replace("'", ""), " # 0x",format(x, "0>4X"), "; Offset: ", color_offset[x]])
    fpw.writelines(["\n]"])
    return color_list

def transforms(fp, fpw):
    fpw.writelines(["\n\nTransforms # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])

    dword_length = int.from_bytes(fp.read(4), "big")
    num_transforms = int.from_bytes(fp.read(4), "big")
    counter = 0
    transforms_list = []
    transforms_offset = []

    while counter < num_transforms:
        transforms_piece = []
        transforms_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        for nani in range(3):
            x = struct.unpack('>f', fp.read(4))
            y = struct.unpack('>f', fp.read(4))
            temp = [float(format(x[0], "4.2F")), float(format(y[0], "4.2F"))]
            transforms_piece.append(temp)
        transforms_list.append(transforms_piece)
        counter += 1
    for z in range(len(transforms_list)):
        fpw.writelines(["\n\n\t[ # 0x",format(z, "0>4X"), "; Offset: ", transforms_offset[z]])
        fpw.writelines(["\n\t\t", str(transforms_list[z]).replace('], ', ']\n\t\t').replace(']\n', '],\n').replace(']]', ']').replace('[[', '[')])
        if not (z + 1) == len(transforms_list):
            fpw.writelines(["\n\t],"])
        else:
            fpw.writelines(["\n\t]\n]"])

def positions(fp, fpw):
    fpw.writelines(["\n\nPositions # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])

    dword_length = int.from_bytes(fp.read(4), "big")
    num_positions = int.from_bytes(fp.read(4), "big")
    positions_list = []
    positions_offset = []
    counter = 0

    while counter < num_positions:
        positions_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        x = struct.unpack('>f', fp.read(4))
        y = struct.unpack('>f', fp.read(4))
        temp = [float(format(x[0], "4.2F")), float(format(y[0], "4.2F"))]
        positions_list.append(temp)
        counter += 1

    for z in range(num_positions):
        if not (z + 1) == len(positions_list):
            eol = ","
        else:
            eol = ""
        fpw.writelines(["\n\t", format(str(positions_list[z]) + eol, "<20s"), format(" # 0x", ">7s"), format(z, "0>4X"), "; Offset: ", positions_offset[z]])
    fpw.writelines(["\n]"])

def bounds(fp, fpw):
    fpw.writelines(["\n\nBounds # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])

    dword_length = int.from_bytes(fp.read(4), "big")
    num_bounds = int.from_bytes(fp.read(4), "big")
    counter = 0
    bounds_list = []
    bounds_offset = []

    while counter < num_bounds:
        bounds_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        left = struct.unpack('>f', fp.read(4))
        top = struct.unpack('>f', fp.read(4))
        right = struct.unpack('>f', fp.read(4))
        bottom = struct.unpack('>f', fp.read(4))
        temp = [float(format(left[0], "4.2F")), float(format(top[0], "4.2F")), float(format(right[0], "4.2F")), float(format(bottom[0], "4.2F"))]
        counter += 1
        bounds_list.append(temp)

    for z in range(num_bounds):
        if not (z + 1) == len(bounds_list):
            eol = ","
        else:
            eol = ""
        fpw.writelines(["\n\t", format(str(bounds_list[z]) + eol, "<31s"), format(" # 0x", ">7s"), format(z, "0>4X"), "; Offset: ", bounds_offset[z]])
    fpw.writelines(["\n]"])

    return bounds_list

def actionscript(fp, fpw):
    dword_length = int.from_bytes(fp.read(4), "big")
    num_scripts = int.from_bytes(fp.read(4), "big")
    fp.seek(dword_length * 4 - 4, 1)
    fpw.writelines(["\n\nTO DO: https://globeriz.blogspot.com/2014/01/flash-vm-instruction-reference.html MAKE THIS WORK"])

def atlas(fp, fpw):
    fpw.writelines(["\n\nAtlases # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])
    dword_length = int.from_bytes(fp.read(4), "big")
    num_atlases = int.from_bytes(fp.read(4), "big")
    counter = 0
    atlases_list = []
    atlases_offset = []
    
    while counter < num_atlases:
        atlases_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        texture_id = int.from_bytes(fp.read(4), "big")
        unk = int.from_bytes(fp.read(4), "big")
        width = struct.unpack('>f', fp.read(4))
        height = struct.unpack('>f', fp.read(4))
        atlases_list.append([texture_id, unk, width, height])
        counter += 1
        
    for x in range(len(atlases_list)):
        fpw.writelines(["\n\tAtlas # 0x", format(x, "0>4X"), "; Offset: ", atlases_offset[x], "\n\t{"])
        fpw.writelines(["\n\t\tTexture ID: ", str(texture_id), ","])
        fpw.writelines(["\n\t\tUnk: ", format(unk, "8X"), ","])
        fpw.writelines(["\n\t\tWidth: ", format(width[0], "4.0f"), ","])
        fpw.writelines(["\n\t\tHeight: ", format(height[0], "4.0f")])
        fpw.writelines(["\n\t}"])
    fpw.writelines(["\n]"])

def unknowns(fp, fpw, type):
    fpw.writelines(["\n\nUnk ", type, " # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    type_list = []
    
    if dword_length == 1:
        unk = int.from_bytes(fp.read(4), "big")
        fpw.writelines(["\n\tunk: 0x", format(unk, "0>8X")])
        type_list.append(unk)
    else:
        for x in range(dword_length):
            unk = int.from_bytes(fp.read(4), "big")
            fpw.writelines(["\n\tunk_", str(x), ": 0x", format(unk, "0>8X")])
            type_list.append(unk)
    fpw.writelines(["\n}"])

def properties(fp, fpw):
    fpw.writelines(["\n\nProperties # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    p_list = []

    for x in range(7):
        unk = int.from_bytes(fp.read(4), "big")
        fpw.writelines(["\n\tunk_", str(x), ": 0x", format(unk, "0>8X")])
        p_list.append(unk)

    fps = struct.unpack('>f', fp.read(4))
    height = struct.unpack('>f', fp.read(4))
    width = struct.unpack('>f', fp.read(4))
    unk8 = int.from_bytes(fp.read(4), "big")
    unk9 = int.from_bytes(fp.read(4), "big")
    
    p_list.extend([fps, height, width, unk8, unk9])

    fpw.writelines(["\n\tfps: ", format(fps[0], "4.0f")])
    fpw.writelines(["\n\theight: ", format(height[0], "4.0f")])
    fpw.writelines(["\n\twidth: ", format(width[0], "4.0f")])
    fpw.writelines(["\n\tunk_8", ": 0x", format(unk8, "0>8X")])
    fpw.writelines(["\n\tunk_9", ": 0x", format(unk9, "0>8X")])
    fpw.writelines(["\n}"])
    return p_list

def defines(fp, fpw):
    fpw.writelines(["\n\nDefines  # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    defines_list = []
    
    num_shapes = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    num_sprites = int.from_bytes(fp.read(4), "big")
    unk1 = int.from_bytes(fp.read(4), "big")
    num_texts = int.from_bytes(fp.read(4), "big")
    unk2 = int.from_bytes(fp.read(4), "big")
    unk3 = int.from_bytes(fp.read(4), "big")
    unk4 = int.from_bytes(fp.read(4), "big")
    
    fpw.writelines(["\n\tNum shapes: ", str(num_shapes)])
    fpw.writelines(["\n\tunk0: 0x", format(unk0, "0>8X")])
    fpw.writelines(["\n\tnum_sprites: ", str(num_sprites)])
    fpw.writelines(["\n\tunk1: ", format(unk1, "0>8X")])
    fpw.writelines(["\n\tnum_texts: ", str(num_texts)])
    fpw.writelines(["\n\tunk2: 0x", format(unk2, "0>8X")])
    fpw.writelines(["\n\tunk3: 0x", format(unk3, "0>8X")])
    fpw.writelines(["\n\tunk4: 0x", format(unk4, "0>8X")])
    fpw.writelines(["\n\n\tShapes\n\t{"])
    
    shape_count = 0
    sprite_count = 0
    text_count = 0
    
    for x in range(num_shapes):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('0000F022'):
            shape_list = shape(fp, fpw, shape_count)
            shape_count += 1
        else:
            fpw.writelines(["\nSomething broke here"])

    fpw.writelines(["\n\t}\n\n\tSprites\n\t{"])
            
    for x in range(num_sprites):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000027'):
            sprite_list = sprite(fp, fpw, sprite_count)
            sprite_count += 1
        else:
            fpw.writelines(["\nSomething broke here"])
            
    fpw.writelines(["\n\t}\n}"])
    
    defines_list.extend([num_shapes, unk0, num_sprites, unk1, num_texts, unk2, unk3, unk4])
    return defines_list

def shape(fp, fpw, x):
    fpw.writelines(["\n\n\t\tShape ", str(x), " offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    shape_list = []

    chr_id = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    bounds_id = int.from_bytes(fp.read(4), "big")
    unk1 = int.from_bytes(fp.read(4), "big")
    num_graphics = int.from_bytes(fp.read(4), "big")

    fpw.writelines(["\n\t\t\tCharacter ID: ", str(chr_id)])
    fpw.writelines(["\n\t\t\tUnk 0: ",format(unk0, "0>8X")])
    fpw.writelines(["\n\t\t\tBounds ID: ", str(bounds_id)])
    fpw.writelines(["\n\t\t\tUnk 1: ",format(unk1, "0>8X")])
    fpw.writelines(["\n\t\t\tNum Graphics: ", str(num_graphics)])
    fpw.writelines(["\n\t\t\t{"])
    
    for x in range(num_graphics):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('0000F024'):
            graphic_list = graphic(fp, fpw, x)
        else:
            fpw.writelines(["\nYou're fucked in shape", format((fp.tell() - 0x4), "<8X")])
    

    fpw.writelines(["\n\t\t\t}\n\t\t}"])

def graphic(fp, fpw, x):
    fpw.writelines(["\n\t\t\t\tGraphic ", str(x), " # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    
    graphic_list = []
    vert_list = []
    index_list = []
    
    atlas_id = int.from_bytes(fp.read(4), "big")
    fill_type = int.from_bytes(fp.read(2), "big")
    num_verts = int.from_bytes(fp.read(2), "big")
    num_indices = int.from_bytes(fp.read(4), "big")

    fpw.writelines(["\n\t\t\t\t\tAtlas ID: ", str(atlas_id)])
    fpw.writelines(["\n\t\t\t\t\tFill Type: ", format(fill_type, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\tNum Verts: ", str(num_verts)])
    fpw.writelines(["\n\t\t\t\t\tNum Indices: ", str(num_indices)])
    
    for x in range(num_verts):
        single_vert = []
        pos_x = struct.unpack('>f', fp.read(4))
        pos_y = struct.unpack('>f', fp.read(4))
        u = struct.unpack('>f', fp.read(4))
        v = struct.unpack('>f', fp.read(4))
        
        single_vert.append([float(format(pos_x[0], "4.2f")), float(format(pos_y[0], "4.2f"))])
        single_vert.append([float(format(u[0], "4.2f")), float(format(v[0], "4.2f"))])
        fpw.writelines(["\n\t\t\t\t\t", str(single_vert)])
        vert_list.append(single_vert)
        
    for x in range(num_indices):
        single_index = int.from_bytes(fp.read(2), "big")
        index_list.append(single_index)
    fpw.writelines(["\n\t\t\t\t\t", str(index_list), "\n\t\t\t\t}"])

def sprite(fp, fpw, x):
    fpw.writelines(["\n\t\tSprite: ", str(x), " # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    
    chr_id = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    unk1 = int.from_bytes(fp.read(4), "big")
    num_labels = int.from_bytes(fp.read(4), "big")
    num_frames = int.from_bytes(fp.read(4), "big")
    num_key_frames = int.from_bytes(fp.read(4), "big")
    unk2 = int.from_bytes(fp.read(4), "big")
    
    fpw.writelines(["\n\t\t\tCharacter ID: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    fpw.writelines(["\n\t\t\tUnk1: 0x", format(unk1, "0>8X")]) 
    fpw.writelines(["\n\t\t\tNum_labels: 0x", format(num_labels, "0>8X")])
    fpw.writelines(["\n\t\t\tNum_frames: 0x", format(num_frames, "0>8X")])
    fpw.writelines(["\n\t\t\tNum_key_frames: 0x", format(num_key_frames, "0>8X")])
    fpw.writelines(["\n\t\t\tUnk2: 0x", format(unk2, "0>8X")])
    
    fpw.writelines(["\n\t\t\t{"])
    
    
    for x in range(num_frames + num_labels + num_key_frames):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000001'):
            show_frame(fp, fpw)
        elif chunk == bytes.fromhex('0000002B'):
            frame_label(fp, fpw)
        elif chunk == bytes.fromhex('0000F105'):
            key_frame(fp, fpw)
        else:
            fpw.writelines(["\nsprite broke at:", format((fp.tell() - 0x4), ">4X")])
            fpw.writelines(["\n", format(int.from_bytes(chunk, "big"), "0>8X")])
    fpw.writelines(["\n\t\t\t}\n\t\t}"])

def frame_label(fp, fpw):
    fpw.writelines(["\n\t\t\t\tFrame Label # offset: 0x", format((fp.tell() - 0x4), ">4X")])
    dword_length = int.from_bytes(fp.read(4), "big")
    
    name_id = int.from_bytes(fp.read(4), "big")
    start_frame = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    
    fpw.writelines([" Name: ", str(name_id), " Start Frame: ", str(start_frame), "Unk 0: ", str(unk0)])

def show_frame(fp, fpw):
    fpw.writelines(["\n\t\t\t\tShow frame # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    num_items = int.from_bytes(fp.read(4), "big")
    
    fpw.writelines(["\n\t\t\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\tnum_items: 0x", format(num_items, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t{"])
    
    for x in range(num_items):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000004'):
            place_object(fp, fpw)
        elif chunk == bytes.fromhex('0000000C'):
            do_action(fp, fpw)
        elif chunk == bytes.fromhex('00000005'):
            remove_object(fp, fpw)
        else:
            fpw.writelines(["\nshow frame broke at:", format((fp.tell() - 0x4), ">4X")])
            fpw.writelines(["\n", format(int.from_bytes(chunk, "big"), "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t}\n\t\t\t\t}"])

def key_frame(fp, fpw):
    fpw.writelines(["\n\t\t\tKey frame # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    num_items = int.from_bytes(fp.read(4), "big")

    fpw.writelines(["\n\t\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    fpw.writelines(["\n\t\t\t\tnum_items: 0x", format(num_items, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t{"])
    
    for x in range(num_items):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000004'):
            place_object(fp, fpw)
        elif chunk == bytes.fromhex('0000000C'):
            do_action(fp, fpw)
        else:
            fpw.writelines(["\nkey frame broke at:", format((fp.tell() - 0x4), ">4X")])
            fpw.writelines(["\n", format(int.from_bytes(chunk, "big"), "0>8X")])
    
    fpw.writelines(["\n\t\t\t\t\t}\n\t\t\t\t}"])

def do_action(fp, fpw):
    dword_length = int.from_bytes(fp.read(4), "big")
    
    action_id = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    
    fpw.writelines(["\n\t\t\t\t\t\tAction ID: ", format(action_id, "0>8X"), " unk0: ", format(unk0, "0>8X"), " # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n"])

def place_object(fp, fpw):
    fpw.writelines(["\n\t\t\t\t\t\tPlace Object # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n\t\t\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    
    chr_id = int.from_bytes(fp.read(4), "big")
    placement_id = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    name_id = int.from_bytes(fp.read(4), "big")
    place_flag = int.from_bytes(fp.read(2), "big") # something else here
    blend_mode = int.from_bytes(fp.read(2), "big")
    depth = int.from_bytes(fp.read(2), "big")
    unk1 = int.from_bytes(fp.read(2), "big")
    unk2 = int.from_bytes(fp.read(2), "big")
    unk3 = int.from_bytes(fp.read(2), "big")
    position_flags = int.from_bytes(fp.read(2), "big")
    position_id = int.from_bytes(fp.read(2), "big")
    color_mult_id = int.from_bytes(fp.read(4), "big")
    color_add_id = int.from_bytes(fp.read(4), "big")
    
    has_color_matrix = int.from_bytes(fp.read(4), "big")
    has_unk_f014 = int.from_bytes(fp.read(4), "big")
    
    if place_flag == 1:
        place_type = "Place"
    elif place_flag == 2:
        place_type = "Move"
    else:
        place_type = "Unknown " + str(place_flag)
        
    fpw.writelines(["\n\t\t\t\t\t\t\tCharacter ID: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tPlacement ID: 0x", format(placement_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tunk0: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tName ID: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tPlace Flag: ", place_type])
    fpw.writelines(["\n\t\t\t\t\t\t\tBlend Mode: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tDepth: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tunk1: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tunk2: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tunk3: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tposition_flags: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tposition_id: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tcolor_mult_id: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\tcolor_add_id: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\thas_color_matrix: 0x", format(chr_id, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t\t\thas_add_id: 0x", format(chr_id, "0>8X")])
    
    fpw.writelines(["\n\t\t\t\t\t\t}"])

def remove_object(fp, fpw):
    dword_length = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    id = int.from_bytes(fp.read(2), "big")
    unk1 = int.from_bytes(fp.read(2), "big")
    
    fpw.writelines(["\n\t\t\t\t\t\tRemove object\n\t\t\t\t\t\t\tUnk0: ", str(unk0), "ID: ", str(id), "unk1: ", str(unk1)])

def color_matrix(fp, fpw):
    fpw.writelines(["\n\nColor_matrix (WIP) # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    type_list = []
    
    if dword_length == 1:
        unk = int.from_bytes(fp.read(4), "big")
        fpw.writelines(["\n\t\tunk: 0x", format(unk, "0>8X")])
        type_list.append(unk)
    else:
        for x in range(dword_length):
            unk = int.from_bytes(fp.read(4), "big")
            fpw.writelines(["\n\t\tunk_", str(x), ": 0x", format(unk, "0>8X")])
            type_list.append(unk)
    fpw.writelines(["\n\t}"])

def dynamic_text(fp, fpw):
    fpw.writelines(["\n\nDynamic Text # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n{"])
    dword_length = int.from_bytes(fp.read(4), "big")
    dynamic_text_list = []

    chr_id = int.from_bytes(fp.read(4), "big")
    unk0 = int.from_bytes(fp.read(4), "big")
    placeholder_text_id = int.from_bytes(fp.read(4), "big")
    unk1 = int.from_bytes(fp.read(4), "big")
    stroke_color_id = int.from_bytes(fp.read(4), "big")
    unk2 = int.from_bytes(fp.read(4), "big")
    unk3 = int.from_bytes(fp.read(4), "big")
    unk4 = int.from_bytes(fp.read(4), "big")
    text_alignment = int.from_bytes(fp.read(2), "big")
    unk5 = int.from_bytes(fp.read(2), "big")
    unk6 = int.from_bytes(fp.read(4), "big")
    unk7 = int.from_bytes(fp.read(4), "big")
    size = struct.unpack('>f', fp.read(4))
    unk8 = int.from_bytes(fp.read(4), "big")
    unk9 = int.from_bytes(fp.read(4), "big")
    unk10 = int.from_bytes(fp.read(4), "big")
    unk11 = int.from_bytes(fp.read(4), "big")

    if text_alignment == 0:
        text_type = "left"
    elif text_alignment == 1:
        text_type = "right"
    elif text_alignment == 2:
        text_type = "center"
    else:
        text_type = "invalid ID: " + str(text_alignment)

    dynamic_text_list.extend([chr_id, unk0, unk1, stroke_color_id, unk2, unk3, unk4, text_type, unk5, unk6, unk7, size, unk8, unk9, unk10, unk11])

    fpw.writelines(["\n\t\tCharacter_ID: ", str(chr_id)])
    fpw.writelines(["\n\t\tunk 0: ", format(unk0, "0>8X")])
    fpw.writelines(["\n\t\tPlaceholder Text ID: ", format(placeholder_text_id, "0>8X")])
    fpw.writelines(["\n\t\tunk 1: ", format(unk1, "0>8X")])
    fpw.writelines(["\n\t\tStroke Color ID: ", format(stroke_color_id, "0>8X")])
    fpw.writelines(["\n\t\tunk 2: ", format(unk2, "0>8X")])
    fpw.writelines(["\n\t\tunk 3: ", format(unk3, "0>8X")])
    fpw.writelines(["\n\t\tunk 4: ", format(unk4, "0>8X")])
    fpw.writelines(["\n\t\tText Alignment: ", str(text_type)])
    fpw.writelines(["\n\t\tunk 5: ", format(unk5, "0>8X")])
    fpw.writelines(["\n\t\tunk 6: ", format(unk6, "0>8X")])
    fpw.writelines(["\n\t\tunk 7: ", format(unk7, "0>8X")])
    fpw.writelines(["\n\t\tSize: ", str(float(format(size[0], "4.2F")))])
    fpw.writelines(["\n\t\tunk 8: ", format(unk8, "0>8X")])
    fpw.writelines(["\n\t\tunk 9: ", format(unk9, "0>8X")])
    fpw.writelines(["\n\t\tunk 10: ", format(unk10, "0>8X")])
    fpw.writelines(["\n\t\tunk 11: ", format(unk11, "0>8X")])

    fpw.writelines(["\n}"])

def end(fp, fpw):
    dword_length = int.from_bytes(fp.read(4), "big")
    for x in range(dword_length):
        print(int.from_bytes(fp.read(4), "big"))

def metadata(fp, fpw):
    dword_length = int.from_bytes(fp.read(4), "big")
    for x in range(dword_length):
        print(int.from_bytes(fp.read(4), "big"))

main()