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
                while chunk != bytes.fromhex('00FF0000'):
                    if chunk == bytes.fromhex('01F00000'):
                        symbol_list = symbols(fp, fpw)
                        #print(symbol_list)

                    elif chunk == bytes.fromhex('02F00000'):
                        color_list = colors(fp, fpw)
                        # print(fpw.tell())

                    elif chunk == bytes.fromhex('03F00000'):
                        transforms_list = transforms(fp, fpw)

                    elif chunk == bytes.fromhex('04F00000'):
                        bounds_list = bounds(fp, fpw)

                    elif chunk == bytes.fromhex('05F00000'):
                        as_list = actionscript(fp, fpw)

                    elif chunk == bytes.fromhex('07F00000'):
                        atlas_list = atlas(fp, fpw)

                    elif chunk == bytes.fromhex('08F00000'):
                        F008_list = (unknowns(fp, fpw, "F008"))

                    elif chunk == bytes.fromhex('09F00000'):
                        F009_list = (unknowns(fp, fpw, "F009"))

                    elif chunk == bytes.fromhex('0AF00000'):
                        F00A_list = (unknowns(fp, fpw, "F00A"))

                    elif chunk == bytes.fromhex('0A000000'):
                        unk_000A_list = (unknowns(fp, fpw, "000A"))

                    elif chunk == bytes.fromhex('0BF00000'):
                        F00B_list = (unknowns(fp, fpw, "F00B"))

                    elif chunk == bytes.fromhex('0CF00000'):
                        p_list = properties(fp, fpw)

                    elif chunk == bytes.fromhex('0DF00000'):
                        defines_list = defines(fp, fpw)

                    elif chunk == bytes.fromhex('24F00000'):
                        graphic_list = graphic(fp, fpw)

                    elif chunk == bytes.fromhex('37F00000'):
                        color_matrix_list = color_matrix(fp, fpw)

                    elif chunk == bytes.fromhex('03F10000'):
                        positions_list = positions(fp, fpw)

                    elif chunk == bytes.fromhex('25000000'):
                        Dynamic_text_list = dynamic_text(fp, fpw)

                    else:
                        fpw.writelines(["\nsomething broke at the below address: \n", format((fp.tell() - 0x4), "<8X")])
                        fpw.writelines(["\n", format((int.from_bytes(chunk, "little")), "0>8X")])
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

    dword_length = int.from_bytes(fp.read(4), "little")
    num_strings = int.from_bytes(fp.read(4), "little")

    str_len = 0
    longest = str_len
    counter = 0
    symbol_list = []
    symbol_offset = []

    while counter < int(num_strings):
        while fp.tell() % 4 != 0:
            fp.seek(1, 1)
        symbol_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        str_len = int.from_bytes(fp.read(4), "little")
        
        string = []
        if str_len == 0:
            str_len = int.from_bytes(fp.read(4), "little")
        x = 0
        while x < str_len:
            try:
                string.append(fp.read(1).decode("utf-8"))
                x += 1
            except:
                fp.seek(-1, 1)
                item = int.from_bytes(fp.read(3), "big")
                string.append(format(item, "X"))
                x += 3
        str_len *= 2

        if longest < str_len:
            longest = str_len

        symbol_list.append(''.join(string))
        counter += 1

    for x in range(len(symbol_list)):
        fpw.writelines(['\n\t"', format(symbol_list[x] + '"', ("<" + str(longest + 4) + "s")), " # 0x",format(x, "0>4X"), "; Offset: ", format(symbol_offset[x])])

    fpw.writelines(["\n}"])

    return symbol_list

def colors(fp, fpw):
    fpw.writelines(["\nColors # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])
    
    dword_length = int.from_bytes(fp.read(4), "little")
    num_colors = int.from_bytes(fp.read(4), "little")
    counter = 0
    color_list = []
    color_offset = []
    
    while counter < int(num_colors):
        color_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        r = int.from_bytes(fp.read(2), "little")
        g = int.from_bytes(fp.read(2), "little")
        b = int.from_bytes(fp.read(2), "little")
        a = int.from_bytes(fp.read(2), "little")
        color_list.append([["0x" + format(r, "0^4X"), "0x" + format(g, "0^4X"), "0x" + format(b, "0^4X"), "0x" + format(a, "0^4X")], ""])
        counter += 1
    for x in range(len(color_list)):
        fpw.writelines(["\n\t", str(color_list[x]).replace("'", ""), " # 0x",format(x, "0>4X"), "; Offset: ", color_offset[x]])
    fpw.writelines(["\n]"])
    return color_list

def transforms(fp, fpw):
    fpw.writelines(["\n\nTransforms # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])

    dword_length = int.from_bytes(fp.read(4), "little")
    num_transforms = int.from_bytes(fp.read(4), "little")
    counter = 0
    transforms_list = []
    transforms_offset = []

    while counter < num_transforms:
        transforms_piece = []
        transforms_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        for nani in range(3):
            x = struct.unpack('<f', fp.read(4))
            y = struct.unpack('<f', fp.read(4))
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

    dword_length = int.from_bytes(fp.read(4), "little")
    num_positions = int.from_bytes(fp.read(4), "little")
    positions_list = []
    positions_offset = []
    counter = 0

    while counter < num_positions:
        positions_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        x = struct.unpack('<f', fp.read(4))
        y = struct.unpack('<f', fp.read(4))
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

    dword_length = int.from_bytes(fp.read(4), "little")
    num_bounds = int.from_bytes(fp.read(4), "little")
    counter = 0
    bounds_list = []
    bounds_offset = []

    while counter < num_bounds:
        bounds_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        left = struct.unpack('<f', fp.read(4))
        top = struct.unpack('<f', fp.read(4))
        right = struct.unpack('<f', fp.read(4))
        bottom = struct.unpack('<f', fp.read(4))
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
    dword_length = int.from_bytes(fp.read(4), "little")
    num_scripts = int.from_bytes(fp.read(4), "little")
    fp.seek(dword_length * 4 - 4, 1)
    fpw.writelines(["\n\nTO DO: https://globeriz.blogspot.com/2014/01/flash-vm-instruction-reference.html MAKE THIS WORK"])

def atlas(fp, fpw):
    fpw.writelines(["\n\nAtlases # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n["])
    dword_length = int.from_bytes(fp.read(4), "little")
    num_atlases = int.from_bytes(fp.read(4), "little")
    counter = 0
    atlases_list = []
    atlases_offset = []
    
    while counter < num_atlases:
        atlases_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        texture_id = int.from_bytes(fp.read(4), "little")
        unk = int.from_bytes(fp.read(4), "little")
        width = struct.unpack('<f', fp.read(4))
        height = struct.unpack('<f', fp.read(4))
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
    dword_length = int.from_bytes(fp.read(4), "little")
    type_list = []
    
    if dword_length == 1:
        unk = int.from_bytes(fp.read(4), "little")
        fpw.writelines(["\n\tunk: 0x", format(unk, "0>8X")])
        type_list.append(unk)
    else:
        for x in range(dword_length):
            unk = int.from_bytes(fp.read(4), "little")
            fpw.writelines(["\n\tunk_", str(x), ": 0x", format(unk, "0>8X")])
            type_list.append(unk)
    fpw.writelines(["\n}"])

def properties(fp, fpw):
    fpw.writelines(["\n\nProperties # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    p_list = []

    for x in range(7):
        unk = int.from_bytes(fp.read(4), "little")
        fpw.writelines(["\n\tunk_", str(x), ": 0x", format(unk, "0>8X")])
        p_list.append(unk)

    fps = struct.unpack('<f', fp.read(4))
    height = struct.unpack('<f', fp.read(4))
    width = struct.unpack('<f', fp.read(4))
    unk8 = int.from_bytes(fp.read(4), "little")
    unk9 = int.from_bytes(fp.read(4), "little")
    
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
    dword_length = int.from_bytes(fp.read(4), "little")
    defines_list = []
    
    num_shapes = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    num_sprites = int.from_bytes(fp.read(4), "little")
    unk1 = int.from_bytes(fp.read(4), "little")
    num_texts = int.from_bytes(fp.read(4), "little")
    unk2 = int.from_bytes(fp.read(4), "little")
    unk3 = int.from_bytes(fp.read(4), "little")
    unk4 = int.from_bytes(fp.read(4), "little")
    
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
        if chunk == bytes.fromhex('22F00000'):
            shape_list = shape(fp, fpw, shape_count)
            shape_count += 1
        else:
            fpw.writelines(["\nSomething broke here"])

    fpw.writelines(["\n\t}\n\n\tSprites\n\t{"])
            
    for x in range(num_sprites):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('27000000'):
            sprite_list = sprite(fp, fpw, sprite_count)
            sprite_count += 1
        else:
            fpw.writelines(["\nSomething broke here"])
            
    fpw.writelines(["\n\t}\n}"])
    
    defines_list.extend([num_shapes, unk0, num_sprites, unk1, num_texts, unk2, unk3, unk4])
    return defines_list

def shape(fp, fpw, x):
    fpw.writelines(["\n\n\t\tShape ", str(x), " offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    shape_list = []

    chr_id = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    bounds_id = int.from_bytes(fp.read(4), "little")
    unk1 = int.from_bytes(fp.read(4), "little")
    num_graphics = int.from_bytes(fp.read(4), "little")

    fpw.writelines(["\n\t\t\tCharacter ID: ", str(chr_id)])
    fpw.writelines(["\n\t\t\tUnk 0: ",format(unk0, "0>8X")])
    fpw.writelines(["\n\t\t\tBounds ID: ", str(bounds_id)])
    fpw.writelines(["\n\t\t\tUnk 1: ",format(unk1, "0>8X")])
    fpw.writelines(["\n\t\t\tNum Graphics: ", str(num_graphics)])
    fpw.writelines(["\n\t\t\t{"])
    
    for x in range(num_graphics):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('24F00000'):
            graphic_list = graphic(fp, fpw, x)
        else:
            fpw.writelines(["\nYou're fucked in shape", format((fp.tell() - 0x4), "<8X")])
    

    fpw.writelines(["\n\t\t\t}\n\t\t}"])

def graphic(fp, fpw, x):
    fpw.writelines(["\n\t\t\t\tGraphic ", str(x), " # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    
    graphic_list = []
    vert_list = []
    index_list = []
    
    atlas_id = int.from_bytes(fp.read(4), "little")
    fill_type = int.from_bytes(fp.read(2), "little")
    num_verts = int.from_bytes(fp.read(2), "little")
    num_indices = int.from_bytes(fp.read(4), "little")

    fpw.writelines(["\n\t\t\t\t\tAtlas ID: ", str(atlas_id)])
    fpw.writelines(["\n\t\t\t\t\tFill Type: ", format(fill_type, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\tNum Verts: ", str(num_verts)])
    fpw.writelines(["\n\t\t\t\t\tNum Indices: ", str(num_indices)])
    
    for x in range(num_verts):
        single_vert = []
        pos_x = struct.unpack('<f', fp.read(4))
        pos_y = struct.unpack('<f', fp.read(4))
        u = struct.unpack('<f', fp.read(4))
        v = struct.unpack('<f', fp.read(4))
        
        single_vert.append([float(format(pos_x[0], "4.2f")), float(format(pos_y[0], "4.2f"))])
        single_vert.append([float(format(u[0], "4.2f")), float(format(v[0], "4.2f"))])
        fpw.writelines(["\n\t\t\t\t\t", str(single_vert)])
        vert_list.append(single_vert)
        
    for x in range(num_indices):
        single_index = int.from_bytes(fp.read(2), "little")
        index_list.append(single_index)
    fpw.writelines(["\n\t\t\t\t\t", str(index_list), "\n\t\t\t\t}"])

def sprite(fp, fpw, x):
    fpw.writelines(["\n\t\tSprite: ", str(x), " # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    
    chr_id = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    unk1 = int.from_bytes(fp.read(4), "little")
    num_labels = int.from_bytes(fp.read(4), "little")
    num_frames = int.from_bytes(fp.read(4), "little")
    num_key_frames = int.from_bytes(fp.read(4), "little")
    unk2 = int.from_bytes(fp.read(4), "little")
    
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
        if chunk == bytes.fromhex('01000000'):
            show_frame(fp, fpw)
        elif chunk == bytes.fromhex('2B000000'):
            frame_label(fp, fpw)
        elif chunk == bytes.fromhex('05F10000'):
            key_frame(fp, fpw)
        else:
            fpw.writelines(["\nsprite broke at:", format((fp.tell() - 0x4), ">4X")])
            fpw.writelines(["\n", format(int.from_bytes(chunk, "little"), "0>8X")])
    fpw.writelines(["\n\t\t\t}\n\t\t}"])

def frame_label(fp, fpw):
    fpw.writelines(["\n\t\t\t\tFrame Label # offset: 0x", format((fp.tell() - 0x4), ">4X")])
    dword_length = int.from_bytes(fp.read(4), "little")
    
    name_id = int.from_bytes(fp.read(4), "little")
    start_frame = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    
    fpw.writelines([" Name: ", str(name_id), " Start Frame: ", str(start_frame), "Unk 0: ", str(unk0)])

def show_frame(fp, fpw):
    fpw.writelines(["\n\t\t\t\tShow frame # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    num_items = int.from_bytes(fp.read(4), "little")
    
    fpw.writelines(["\n\t\t\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\tnum_items: 0x", format(num_items, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t{"])
    
    for x in range(num_items):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('04000000'):
            place_object(fp, fpw)
        elif chunk == bytes.fromhex('0C000000'):
            do_action(fp, fpw)
        elif chunk == bytes.fromhex('05000000'):
            remove_object(fp, fpw)
        else:
            fpw.writelines(["\nshow frame broke at:", format((fp.tell() - 0x4), ">4X")])
            fpw.writelines(["\n", format(int.from_bytes(chunk, "little"), "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t}\n\t\t\t\t}"])

def key_frame(fp, fpw):
    fpw.writelines(["\n\t\t\tKey frame # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    num_items = int.from_bytes(fp.read(4), "little")

    fpw.writelines(["\n\t\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    fpw.writelines(["\n\t\t\t\tnum_items: 0x", format(num_items, "0>8X")])
    fpw.writelines(["\n\t\t\t\t\t{"])
    
    for x in range(num_items):
        chunk = fp.read(4)
        if chunk == bytes.fromhex('04000000'):
            place_object(fp, fpw)
        elif chunk == bytes.fromhex('0C000000'):
            do_action(fp, fpw)
        else:
            fpw.writelines(["\nkey frame broke at:", format((fp.tell() - 0x4), ">4X")])
            fpw.writelines(["\n", format(int.from_bytes(chunk, "little"), "0>8X")])
    
    fpw.writelines(["\n\t\t\t\t\t}\n\t\t\t\t}"])

def do_action(fp, fpw):
    dword_length = int.from_bytes(fp.read(4), "little")
    
    action_id = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    
    fpw.writelines(["\n\t\t\t\t\t\tAction ID: ", format(action_id, "0>8X"), " unk0: ", format(unk0, "0>8X"), " # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n"])

def place_object(fp, fpw):
    fpw.writelines(["\n\t\t\t\t\t\tPlace Object # offset: 0x", format((fp.tell() - 0x4), ">4X"), "\n\t\t\t\t\t\t{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    
    chr_id = int.from_bytes(fp.read(4), "little")
    placement_id = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    name_id = int.from_bytes(fp.read(4), "little")
    place_flag = int.from_bytes(fp.read(2), "little") # something else here
    blend_mode = int.from_bytes(fp.read(2), "little")
    depth = int.from_bytes(fp.read(2), "little")
    unk1 = int.from_bytes(fp.read(2), "little")
    unk2 = int.from_bytes(fp.read(2), "little")
    unk3 = int.from_bytes(fp.read(2), "little")
    position_flags = int.from_bytes(fp.read(2), "little")
    position_id = int.from_bytes(fp.read(2), "little")
    color_mult_id = int.from_bytes(fp.read(4), "little")
    color_add_id = int.from_bytes(fp.read(4), "little")
    
    has_color_matrix = int.from_bytes(fp.read(4), "little")
    has_unk_f014 = int.from_bytes(fp.read(4), "little")
    
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
    dword_length = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    id = int.from_bytes(fp.read(2), "little")
    unk1 = int.from_bytes(fp.read(2), "little")
    
    fpw.writelines(["\n\t\t\t\t\t\tRemove object\n\t\t\t\t\t\t\tUnk0: ", str(unk0), "ID: ", str(id), "unk1: ", str(unk1)])

def color_matrix(fp, fpw):
    fpw.writelines(["\n\nColor_matrix (WIP) # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n\t{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    type_list = []
    
    if dword_length == 1:
        unk = int.from_bytes(fp.read(4), "little")
        fpw.writelines(["\n\t\tunk: 0x", format(unk, "0>8X")])
        type_list.append(unk)
    else:
        for x in range(dword_length):
            unk = int.from_bytes(fp.read(4), "little")
            fpw.writelines(["\n\t\tunk_", str(x), ": 0x", format(unk, "0>8X")])
            type_list.append(unk)
    fpw.writelines(["\n\t}"])

def dynamic_text(fp, fpw):
    fpw.writelines(["\n\nDynamic Text # offset: 0x", format((fp.tell() - 0x4), "<8X"), "\n{"])
    dword_length = int.from_bytes(fp.read(4), "little")
    dynamic_text_list = []

    chr_id = int.from_bytes(fp.read(4), "little")
    unk0 = int.from_bytes(fp.read(4), "little")
    placeholder_text_id = int.from_bytes(fp.read(4), "little")
    unk1 = int.from_bytes(fp.read(4), "little")
    stroke_color_id = int.from_bytes(fp.read(4), "little")
    unk2 = int.from_bytes(fp.read(4), "little")
    unk3 = int.from_bytes(fp.read(4), "little")
    unk4 = int.from_bytes(fp.read(4), "little")
    text_alignment = int.from_bytes(fp.read(2), "little")
    unk5 = int.from_bytes(fp.read(2), "little")
    unk6 = int.from_bytes(fp.read(4), "little")
    unk7 = int.from_bytes(fp.read(4), "little")
    size = struct.unpack('<f', fp.read(4))
    unk8 = int.from_bytes(fp.read(4), "little")
    unk9 = int.from_bytes(fp.read(4), "little")
    unk10 = int.from_bytes(fp.read(4), "little")
    unk11 = int.from_bytes(fp.read(4), "little")

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
    dword_length = int.from_bytes(fp.read(4), "little")
    for x in range(dword_length):
        print(int.from_bytes(fp.read(4), "little"))

def metadata(fp, fpw):
    dword_length = int.from_bytes(fp.read(4), "little")
    for x in range(dword_length):
        print(int.from_bytes(fp.read(4), "little"))

main()