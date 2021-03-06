import sys, struct, time, os
#file = sys.argv[1]

rootdir = "lumen"
extensions = (".lm")

try:
    dummy = sys.argv[2]
    REFS = False # This will be swapped when it is fully implemented
except:
    REFS = True

def main():
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            if ext in extensions:
                tic = time.clock()
                file = os.path.join(subdir, file)
                with open(file, "rb") as fp:
                    fp.seek(0)
                    if fp.read(3) != b'LMB':
                        print("This is not a valid lumen file")
                    else:
                        log = file.replace('.lm', '.log')
                        with open(log, "w") as fpw:
                            header(fp, fpw)
                            offset = fp.tell()
                            chunk = fp.read(4)
                            while chunk != bytes.fromhex('0000FF00'):
                                if chunk == bytes.fromhex('0000F001'):
                                    symbol_offset = offset
                                    symbol_list = symbols(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F002'):
                                    color_offset = offset
                                    color_list = colors(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F003'):
                                    transforms_offset = offset
                                    transforms_list, transforms_list_offset = transforms(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F103'):
                                    positions_offset = offset
                                    positions_list = positions(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F004'):
                                    bounds_offset = offset
                                    bounds_list = bounds(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F005'):
                                    as_offset = offset
                                    as_list = actionscript(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F007'):
                                    atlas_offset = offset
                                    atlas_list = atlas(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F008'):
                                    F008_offset = offset
                                    F008_list = (unknowns(fp, fpw, "F008"))
                
                                elif chunk == bytes.fromhex('0000F009'):
                                    F009_offset = offset
                                    F009_list = (unknowns(fp, fpw, "F009"))
                
                                elif chunk == bytes.fromhex('0000F00A'):
                                    F00A_offset = offset
                                    F00A_list = (unknowns(fp, fpw, "F00A"))
                
                                elif chunk == bytes.fromhex('0000000A'):
                                    unk_000A_offset = offset
                                    unk_000A_list = (unknowns(fp, fpw, "000A"))
                
                                elif chunk == bytes.fromhex('0000F00B'):
                                    F00B_offset = offset
                                    F00B_list = (unknowns(fp, fpw, "F00B"))
                
                                elif chunk == bytes.fromhex('0000F00C'):
                                    p_offset = offset
                                    p_list = properties(fp, fpw)
                
                                elif chunk == bytes.fromhex('0000F00D'):
                                    defines_offset = offset
                                    an_actual_nightmare = defines(fp, fpw, symbol_list, atlas_list, positions_list, defines_offset)
                
                                else:
                                    print("something broke at the below address in main: \n", format((fp.tell() - 0x4), "0>8X"))
                                    print(format((int.from_bytes(chunk, "big")), "0>8X"))
                                    exit()
                                while fp.tell() % 4 != 0:
                                    fp.seek(1, 1)
                                offset = fp.tell()
                                chunk = fp.read(4)
                                if chunk == bytes.fromhex('00000000'):
                                    chunk = fp.read(4)
                
                            symbol_write(symbol_list, symbol_offset, fpw)
                
                            colors_write(color_list, color_offset, fpw)
                
                            transforms_write(transforms_list, transforms_offset, fpw, transforms_list_offset)
                
                            positions_write(positions_list, positions_offset, fpw)
                
                            bounds_write(bounds_list, bounds_offset, fpw)
                
                            actionscript_write(as_list, as_offset, fpw)
                
                            atlas_write(atlas_list, atlas_offset, fpw)
                
                            unknowns_write(F008_list, F008_offset, fpw, "F008")
                
                            unknowns_write(F009_list, F008_offset, fpw, "F009")
                
                            unknowns_write(F00A_list, F008_offset, fpw, "F00A")
                
                            unknowns_write(unk_000A_list, unk_000A_offset, fpw, "000A")
                
                            unknowns_write(F00B_list, F00B_offset, fpw, "F00B")
                
                            properties_write(p_list, p_offset, fpw)
                
                            everything_else_write(an_actual_nightmare, fpw)
                
                toc = time.clock()
                print("The file:", file, "finished in:", toc - tic)

def integer(fp):
    return int.from_bytes(fp.read(4), "big")

def floating(fp):
    return struct.unpack('>f', fp.read(4))

def short(fp):
    return int.from_bytes(fp.read(2), "big")

def header(fp, fpw):
    fp.seek(0x1C)
    filesize = fp.read(4) # seriously, this is probably the most useless thing here *looks at dword_length*
    fp.seek(0x40)

def symbols(fp, fpw):
    dword_length = integer(fp)
    num_strings = integer(fp)

    str_len = 0
    longest = 0
    counter = 0
    symbol_list = []
    symbol_offset = []

    while counter < int(num_strings):
        while fp.tell() % 4 != 0:
            fp.seek(1, 1)
        symbol_offset.append(fp.tell())
        str_len = integer(fp)
        actual_str_len = 0

        if str_len == 0:
            str_len = integer(fp)

        string = str(fp.read(str_len))
        if longest < actual_str_len:
            longest = actual_str_len

        symbol_list.append(string[2:(len(string) - 1)])
        counter += 1

    for x in range(len(symbol_list)):
        symbol_list[x] = ['\n\t"', format(symbol_list[x] + '"', ("<" + str(longest + 4) + "s")), " # 0x",format(x, "0>4X"), "; Offset: 0x", str(format(symbol_offset[x], "0>8X")), "\n\t{"]
    return symbol_list

def symbol_write(l, offset, fpw):
    if REFS:
        ref_str_open = "\n{"
        ref_str_close = "\n\t}"
    else:
        ref_str_open = ''
        ref_str_close = ''

    fpw.writelines(["Symbols # Offset: 0x", str(format(offset, "0>8X")), ref_str_open])
    for x in range(len(l)):
        fpw.writelines(l[x])
        fpw.writelines(ref_str_close)
    fpw.writelines(["\n}"])

def colors(fp, fpw):
    
    dword_length = integer(fp)
    num_colors = integer(fp)
    counter = 0
    color_list = []
    color_offset = []
    
    while counter < int(num_colors):
        color_offset.append("0x" + ''.join(format((fp.tell()), ">X")))
        r = short(fp)
        g = short(fp)
        b = short(fp)
        a = short(fp)
        color_list.append(["0x" + format(r, "0>4X"), "0x" + format(g, "0>4X"), "0x" + format(b, "0>4X"), "0x" + format(a, "0>4X")])
        counter += 1
    for x in range(len(color_list)):
        color_list[x] = (["\n\t", str(color_list[x]).replace("'", ""), " # 0x",format(x, "0>4X"), "; Offset: ", color_offset[x]])
    return color_list

def colors_write(l, offset, fpw):
    if REFS:
        ref_str_open = "\n{"
        ref_str_close = "\n\t}"
    else:
        ref_str_open = ''
        ref_str_close = ''

    fpw.writelines(["\n\nColors # offset: 0x", str(format(offset, "0>8X")), "\n["])
    everything_else_write(l, fpw)
    fpw.writelines(["\n]"])

def transforms(fp, fpw):

    dword_length = integer(fp)
    num_transforms = integer(fp)
    counter = 0
    transforms_list = []
    transforms_offset = []

    while counter < num_transforms:
        transforms_piece = []
        transforms_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        for nani in range(3):
            x = floating(fp)
            y = floating(fp)
            temp = [float(format(x[0], ".10F")), float(format(y[0], ".10F"))]
            transforms_piece.append(temp)
        transforms_list.append(transforms_piece)
        counter += 1
    for z in range(len(transforms_list)):
        
        transforms_list[z] = (["\n\t\t", str(transforms_list[z]).replace('], ', ']\n\t\t').replace(']\n', '],\n').replace(']]', ']').replace('[[', '[')])
    return transforms_list, transforms_offset

def transforms_write(l, offset, fpw, list_offset):
    if REFS:
        ref_str_open = "\n{"
        ref_str_close = "\n\t}"
    else:
        ref_str_open = ''
        ref_str_close = ''

    fpw.writelines(["\n\nTransforms # offset: 0x", str(format(offset, "0>8X")), "\n["])
    for z in range(len(l)):
        fpw.writelines(["\n\t[ # 0x",format(z, "0>4X"), "; Offset: ", list_offset[z]])
        fpw.writelines(l[z])
        if not (z + 1) == len(l):
            fpw.writelines(["\n\t],\n"])
        else:
            fpw.writelines(["\n\t]\n\n]"])

def positions(fp, fpw):
    dword_length = integer(fp)
    num_positions = integer(fp)
    positions_list = []
    positions_offset = []
    counter = 0

    while counter < num_positions:
        positions_offset.append("0x" + ''.join(format((fp.tell()), "0>8X")))
        x = floating(fp)
        y = floating(fp)
        temp = [float(format(x[0], ".10F")), float(format(y[0], ".10F"))]
        positions_list.append(temp)
        counter += 1

    for z in range(len(positions_list)):
        if not (z + 1) == len(positions_list):
            eol = ","
        else:
            eol = ""
        positions_list[z] = (["\n\t", format(str(positions_list[z]) + eol, "<20s"), format(" # 0x", ">7s"), format(z, "0>4X"), "; Offset: ", positions_offset[z]])

    return positions_list

def positions_write(l, offset, fpw):
    if REFS:
        ref_str_open = "\n{"
        ref_str_close = "\n\t}"
    else:
        ref_str_open = ''
        ref_str_close = ''

    fpw.writelines(["\n\nPositions # offset: 0x", str(format(offset, "0>8X")), "\n["])
    for x in range(len(l)):
        fpw.writelines(l[x])
    fpw.writelines(["\n]"])

def bounds(fp, fpw):
    dword_length = integer(fp)
    num_bounds = integer(fp)
    counter = 0
    bounds_list = []
    bounds_offset = []

    while counter < num_bounds:
        bounds_offset.append("0x" + ''.join(format((fp.tell()), "<X")))
        left = floating(fp)
        top = floating(fp)
        right = floating(fp)
        bottom = floating(fp)
        temp = [float(format(left[0], ".10F")), float(format(top[0], ".10F")), float(format(right[0], ".10F")), float(format(bottom[0], ".10F"))]
        counter += 1
        bounds_list.append(temp)

    for z in range(num_bounds):
        if not (z + 1) == len(bounds_list):
            eol = ","
        else:
            eol = ""
        bounds_list[z] = (["\n\t", format(str(bounds_list[z]) + eol, "<31s"), format(" # 0x", ">7s"), format(z, "0>4X"), "; Offset: ", bounds_offset[z]])

    return bounds_list

def bounds_write(l, offset, fpw):
    if REFS:
        ref_str_open = "\n{"
        ref_str_close = "\n\t}"
    else:
        ref_str_open = ''
        ref_str_close = ''

    fpw.writelines(["\n\nBounds # offset: 0x", str(format(offset, "0>8X")), "\n["])
    for x in range(len(l)):
        fpw.writelines(l[x])
    fpw.writelines(["\n]"])

def actionscript(fp, fpw):
    dword_length = integer(fp)
    num_scripts = integer(fp)
    items = [str(num_scripts)]
    for x in range(dword_length - 1):
        items.append(format(integer(fp), "0>8X"))
    return items

def actionscript_write(l, offset, fpw):
    if REFS:
        ref_str_open = "\n{"
        ref_str_close = "\n\t}"
    else:
        ref_str_open = ''
        ref_str_close = ''

    fpw.writelines(["\n\nActionScript # offset: 0x", str(format(offset, "0>8X")), "\n{"])
    fpw.writelines(["\nTO DO: https://globeriz.blogspot.com/2014/01/flash-vm-instruction-reference.html MAKE THIS WORK\n\n"])
    fpw.writelines(["Number of scripts: ", l[0], "\n"])
    counter = 0
    for x in range(1, len(l)):
        if counter != 15:
            fpw.writelines(l[x] + " ")
            counter += 1
        else:
            counter = 0
            fpw.writelines(l[x] + " " + "\n")
    fpw.writelines(["\n}"])

def atlas(fp, fpw):
    dword_length = integer(fp)
    num_atlases = integer(fp)
    counter = 0
    atlas_list = []
    atlas_offset = []
    atlas_temp = []

    while counter < num_atlases:
        atlas_offset.append("0x" + ''.join(format((fp.tell()), "0>8X")))
        texture_id = integer(fp)
        unk = integer(fp)
        width = floating(fp)
        height = floating(fp)
        atlas_temp.append(["\n\tAtlas # 0x", format(counter, "0>4X"), "; Offset: ", atlas_offset[counter]])
        atlas_temp.append(["\n\t{\n\t\tTexture ID:  ", str(format(texture_id, "0>2d")), ","])
        atlas_temp.append(["\n\t\tUnk: 0x", format(unk, "0>8X"), ","])
        atlas_temp.append(["\n\t\tWidth:  ", format(width[0], ">7.0f"), ","])
        atlas_temp.append(["\n\t\tHeight: ", format(height[0], ">7.0f")])
        atlas_list.append(atlas_temp)
        atlas_temp = []
        counter += 1
    return atlas_list

def atlas_write(l, offset, fpw):
    if REFS:
        ref_str_open = "\n{"
        ref_str_close = "\n\t}"
    else:
        ref_str_open = ''
        ref_str_close = ''

    fpw.writelines(["\n\nAtlases # offset: 0x", str(format(offset, "0>8X")), "\n{"])
    for x in range(len(l)):
        for item in range(5):
            fpw.writelines(l[x][item])
        if x != len(l) - 1:
            fpw.writelines(["\n\t}\n"])
        else:
            fpw.writelines(["\n\t}\n\n}"])

def unknowns(fp, fpw, type):
    dword_length = integer(fp)
    type_list = []

    if dword_length == 1:
        unk = integer(fp)
        type_list.append(["\n\tunk: 0x", format(unk, "0>8X")])
    else:
        for x in range(dword_length):
            unk = integer(fp)
            type_list.append(["\n\tunk_", str(x), ": 0x", format(unk, "0>8X")])

    return type_list

def unknowns_write(l, offset, fpw, type):
    fpw.writelines(["\n\nUnk ", type, " # offset: 0x", str(format(offset, "0>8X")), "\n{"])
    for x in range(len(l)):
        fpw.writelines(l[x])
    fpw.writelines(["\n}"])

def properties(fp, fpw):
    dword_length = integer(fp)
    p_list = []

    for x in range(7):
        unk = integer(fp)
        p_list.extend(["\n\tunk_", str(x), ": 0x", format(unk, "0>8X")])

    fps = floating(fp)
    height = floating(fp)
    width = floating(fp)
    unk8 = integer(fp)
    unk9 = integer(fp)
    

    p_list.extend(["\n\tfps: ", str(format(fps[0], "2.0f"))])
    p_list.extend(["\n\theight: ", str(format(height[0], "4.0f"))])
    p_list.extend(["\n\twidth: ", str(format(width[0], "4.0f"))])
    p_list.extend(["\n\tunk_8", ": 0x", str(format(unk8, "0>8X"))])
    p_list.extend(["\n\tunk_9", ": 0x", str(format(unk9, "0>8X"))])
    return p_list

def properties_write(l, offset, fpw):
    fpw.writelines(["\n\nProperties # offset: 0x", str(offset), "\n{"])
    fpw.writelines(l)
    fpw.writelines(["\n}"])

def defines(fp, fpw, symbol_list, atlas_list, positions_list, offset):
    dword_length = integer(fp)
    defines_list = []
    defines_temp = ["\n\nDefines  # offset: 0x", str(format(offset, "0>8X")), "\n{"]

    num_shapes = integer(fp)
    unk0 = integer(fp)
    num_sprites = integer(fp)
    unk1 = integer(fp)
    num_texts = integer(fp)
    unk2 = integer(fp)
    unk3 = integer(fp)
    unk4 = integer(fp)

    defines_temp.append(["\n\tNum shapes: ", str(num_shapes)])
    defines_temp.append(["\n\tunk0: 0x", format(unk0, "0>8X")])
    defines_temp.append(["\n\tnum_sprites: ", str(num_sprites)])
    defines_temp.append(["\n\tunk1: 0x", format(unk1, "0>8X")])
    defines_temp.append(["\n\tnum_texts: ", str(num_texts)])
    defines_temp.append(["\n\tunk2: 0x", format(unk2, "0>8X")])
    defines_temp.append(["\n\tunk3: 0x", format(unk3, "0>8X")])
    defines_temp.append(["\n\tunk4: 0x", format(unk4, "0>8X")])

    defines_list.append(defines_temp)

    graphic_global_list = []
    sprites_global_list = []
    texts_global_list = []
    shapes_list = []

    shape_obj_count = []

    shape_count = 0
    sprite_count = 0
    text_count = 0

    for x in range(num_shapes):
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('0000F022'):
            shapes_temp, graphic_temp = shape(fp, fpw, shape_count, symbol_list, atlas_list, shape_obj_count, offset)
            shapes_list.append(shapes_temp)
            graphic_global_list.append(graphic_temp)
            shape_count += 1
        else:
            print("something broke at the below address in defines (shapes): \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))

    graphic_global_list = graphic_preprocess(graphic_global_list, shape_obj_count)

    for x in range(num_sprites):
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000027'):
            sprite(fp, fpw, sprite_count, symbol_list, positions_list, sprites_global_list, graphic_global_list, shape_obj_count, offset)
            sprite_count += 1
        else:
            print("something broke at the below address in defines (sprites): \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))
    

    for x in range(num_texts):
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000025'):
            dynamic_text(fp, fpw, text_count, symbol_list, texts_global_list, offset)
            text_count += 1
        else:
            print("something broke at the below address in defines (texts): \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))

    defines_temp = []

    defines_processing(defines_list, shapes_list, graphic_global_list, shape_obj_count, sprites_global_list, texts_global_list)


    return defines_list

def defines_processing(defines_list, shapes_list, graphic_global_list, shape_obj_count, sprites_global_list, texts_global_list):
    defines_list.append(["\n\n\tShapes\n\t{"])

    graphic_global_list = graphic_postprocess(graphic_global_list, shape_obj_count)
    defines_list.append(shape_processing(shapes_list, graphic_global_list, shape_obj_count))
    defines_list.append(["\n\t}\n\n\tSprites\n\t{"])

    defines_list.append(sprites_global_list)
    defines_list.append(["\n\t}\n\n\tTexts\n\t{"])

    defines_list.append(texts_global_list)
    defines_list.append(["\n\t}\n}"])

def graphic_preprocess(graphic_list, shape_obj_count):
    graphic_temp = []
    for x in range(len(shape_obj_count)):
        for y in range(shape_obj_count[x]):
            graphic_temp.append(graphic_list[x][y])
    return graphic_temp

def graphic_postprocess(graphic_list, shape_obj_count):
    graphic_temp = []
    graphic_temp_main = []
    counter = 0
    for x in range(len(shape_obj_count)):
        for y in range(shape_obj_count[x]):
            graphic_temp.append(graphic_list[counter])
            counter += 1
        graphic_temp_main.append(graphic_temp)
        graphic_temp = []
    return graphic_temp_main
    
def shape_processing(shapes_list, graphic_list, shape_obj_count):
    for x in range(len(shape_obj_count)):
        for y in range(shape_obj_count[x]):
            shapes_list[x].insert(-2, graphic_list[x][y])
    return shapes_list

def shape(fp, fpw, x, symbol_list, atlas_list, shape_obj_count, offset):
    dword_length = integer(fp)
    shape_list = []
    graphic_list = []
    shape_temp = ["\n\n\t\tShape # ", str(x), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t{"]

    chr_id = integer(fp)
    unk0 = integer(fp)
    bounds_id = integer(fp)
    unk1 = integer(fp)
    num_graphics = integer(fp)

    shape_temp.append(["\n\t\t\tCharacter ID: 0x", str(format(chr_id, "0>8X"))])
    shape_temp.append(["\n\t\t\tUnk 0: 0x",format(unk0, "0>8X")])
    shape_temp.append(["\n\t\t\tBounds ID: ", str(bounds_id)]) # oh
    shape_temp.append(["\n\t\t\tUnk 1: 0x",format(unk1, "0>8X")])
    shape_temp.append(["\n\t\t\tNum Graphics: ", str(num_graphics)])
    shape_temp.append(["\n\t\t\t{"])
    
    shape_list = shape_temp

    for z in range(num_graphics):
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('0000F024'):
            graphic_list.append(graphic(fp, fpw, z, atlas_list, x, offset))
        else:
            print("something broke at the below address in shape: \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))
    #shape_list.append(graphic_list)
    shape_list.append(["\n\t\t\t}\n\t\t}"])
    shape_obj_count.append(num_graphics)
    return shape_list, graphic_list

def graphic(fp, fpw, x, atlas_list, shape_id, offset):
    dword_length = integer(fp)

    graphic_list = []
    vert_list = []
    index_list = []

    graphic_temp = ["\n\t\t\t\tGraphic # ", str(x), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t\t\t{"]

    atlas_id = integer(fp)
    fill_type = short(fp)
    num_verts = short(fp)
    num_indices = integer(fp)
    try:
        atlas_list[atlas_id][0].append("\n\t# ref in (Shape, Graphic): (" + str(shape_id) + ", " + str(x) + ")")
    except:
        print("Probably either invalid Atlas reference, or it's external. If you did not do this, ignore it. Details: ID:", atlas_id, "chunk offset:", offset)

    graphic_temp.append(["\n\t\t\t\t\tAtlas ID: ", str(atlas_id)])
    graphic_temp.append(["\n\t\t\t\t\tFill Type: 0x", format(fill_type, "0>4X")])
    graphic_temp.append(["\n\t\t\t\t\tNum Verts: ", str(num_verts)])
    graphic_temp.append(["\n\t\t\t\t\tNum Indices: ", str(num_indices)])

    for z in range(num_verts):
        single_vert = []
        pos_x = floating(fp)
        pos_y = floating(fp)
        u = floating(fp)
        v = floating(fp)

        single_vert.append(["Pos X: ", float(format(pos_x[0], ".10F")), "Pos Y: ", float(format(pos_y[0], ".10F"))])
        single_vert.append(["U: ", float(format(u[0], ".10F")), "V: ", float(format(v[0], ".10F"))])
        graphic_temp.append(["\n\t\t\t\t\t", str(single_vert)])
        vert_list.append(single_vert)

    for z in range(num_indices):
        single_index = short(fp)
        index_list.append(single_index)
    graphic_temp.append(["\n\t\t\t\t\t", str(index_list), "\n\t\t\t\t\t{"])
    graphic_temp.append(["\n\t\t\t\t\t}\n\t\t\t\t}"])
    graphic_list.append(graphic_temp)
    return graphic_list

def sprite(fp, fpw, sprite_num, symbol_list, positions_list, sprite_list, graphic_list, shape_obj_count, offset):
    dword_length = integer(fp)
    
    # [0] is the list of sprite items; [1:-1] contains each frame or label; [-1] contains the closing brace
    sprite_temp = ["\n\t\tSprite # ", str(sprite_num), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t{"]

    chr_id = integer(fp)
    unk0 = integer(fp)
    unk1 = integer(fp)
    num_labels = integer(fp)
    num_frames = integer(fp)
    num_key_frames = integer(fp)
    unk2 = integer(fp)

    sprite_temp.append(["\n\t\t\tCharacter ID: 0x", str(format(chr_id, "0>8X"))])
    sprite_temp.append(["\n\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    sprite_temp.append(["\n\t\t\tUnk1: 0x", format(unk1, "0>8X")]) 
    sprite_temp.append(["\n\t\t\tNum_labels: 0x", format(num_labels, "0>8X")])
    sprite_temp.append(["\n\t\t\tNum_frames: 0x", format(num_frames, "0>8X")])
    sprite_temp.append(["\n\t\t\tNum_key_frames: 0x", format(num_key_frames, "0>8X")])
    sprite_temp.append(["\n\t\t\tUnk2: 0x", format(unk2, "0>8X")])

    sprite_temp.append(["\n\t\t\t{"])
    
    sprite_list.append(sprite_temp)
    
    show_frame_count = 0
    frame_label_count = 0
    key_frame_count = 0

    for x in range(num_frames + num_labels + num_key_frames):
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000001'):
            sprite_list.append(show_frame(fp, fpw, symbol_list, show_frame_count, positions_list, graphic_list, shape_obj_count, offset, x))
            show_frame_count += 1
        elif chunk == bytes.fromhex('0000002B'):
            sprite_list.append(frame_label(fp, fpw, symbol_list, frame_label_count, offset, x))
            frame_label_count += 1
        elif chunk == bytes.fromhex('0000F105'):
            sprite_list.append(key_frame(fp, fpw, symbol_list, key_frame_count, graphic_list, shape_obj_count, positions_list, offset, x))
            key_frame_count += 1
        else:
            print("something broke at the below address in sprite: \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))
    sprite_list.append(["\n\t\t\t}\n\t\t}\n"])

def frame_label(fp, fpw, symbol_list, count, offset, item_num):
    dword_length = integer(fp)
    
    frame_list = ["\n\t\t\t\tFrame Label # ", str(count), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t\t\t{"]

    name_id = integer(fp)
    start_frame = integer(fp)
    unk0 = integer(fp)

    frame_list.append(["\n\t\t\t\t\tName: 0x", str(format(name_id, "0>8X")), "\n\t\t\t\t\tStart Frame: 0x", str(format(start_frame, "0>8X")), "\n\t\t\t\t\tUnk 0: 0x", str(format(unk0, "0>8X")), "\n\t\t\t\t}"])
    return frame_list

def show_frame(fp, fpw, symbol_list, count, positions_list, graphic_list, shape_obj_count, offset, item_num):
    dword_length = integer(fp)
    unk0 = integer(fp)
    num_items = integer(fp)

    frame_list = []
    frame_temp = ["\n\t\t\t\tShow Frame # ", str(count), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t\t\t{"]

    frame_temp.append(["\n\t\t\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    frame_temp.append(["\n\t\t\t\t\tnum_items: 0x", format(num_items, "0>8X")])
    frame_temp.append(["\n\t\t\t\t\t{"])

    frame_list.append(frame_temp)

    place_obj_counter = 0
    do_act_counter = 0
    remove_obj_counter = 0

    for x in range(num_items):
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000004'):
            frame_list.append(place_object(fp, fpw, place_obj_counter, "Show Frame", symbol_list, positions_list, graphic_list, shape_obj_count, count, offset, item_num))
            place_obj_counter += 1
        elif chunk == bytes.fromhex('0000000C'):
            frame_list.append(do_action(fp, fpw, do_act_counter, count, offset, item_num))
            do_act_counter += 1
        elif chunk == bytes.fromhex('00000005'):
            frame_list.append(remove_object(fp, fpw, "Show Frame", symbol_list, count, offset, item_num))
            remove_obj_counter += 1
        else:
            print("something broke at the below address in Show Frame: \n", format((fp.tell() - 0x4), "0>8X"))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))
        if (x + 1) != num_items:
            frame_list.append(["\n"])
    frame_list.append(["\n\t\t\t\t\t}\n\t\t\t\t}"])
    return frame_list

def key_frame(fp, fpw, symbol_list, count, positions_list, graphic_list, shape_obj_count, offset, item_num):
    dword_length = integer(fp)
    unk0 = integer(fp)
    num_items = integer(fp)

    frame_list = [] # [0] is key frame; [1:-1] are items; [-1] is the closer
    frame_temp = ["\n\t\t\tKey Frame # ", str(count), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t\t\t{"]

    frame_temp.append(["\n\t\t\t\tUnk0: 0x", format(unk0, "0>8X")])
    frame_temp.append(["\n\t\t\t\tnum_items: 0x", format(num_items, "0>8X")])
    frame_temp.append(["\n\t\t\t\t\t{"])

    frame_list.append(frame_temp)

    place_obj_counter = 0
    do_act_counter = 0
    remove_obj_counter = 0

    for x in range(num_items):
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('00000004'):
            frame_list.append(place_object(fp, fpw, place_obj_counter, "Key Frame", symbol_list, positions_list, graphic_list, shape_obj_count, count, offset, item_num))
            place_obj_counter += 1
        elif chunk == bytes.fromhex('0000000C'):
            frame_list.append(do_action(fp, fpw, do_act_counter, count, offset, item_num))
            do_act_counter += 1
        elif chunk == bytes.fromhex('00000005'):
            frame_list.append(remove_object(fp, fpw, "Key Frame", symbol_list, count, offset, item_num))
            remove_obj_counter += 1
        else:
            print("Something broke at the below address in Key Frame: \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))
        if (x + 1) != num_items:
            frame_list.append(["\n"])

    frame_list.append(["\n\t\t\t\t\t}\n\t\t\t\t}"])

    return frame_list

def do_action(fp, fpw, x, count, offset, item_num):
    dword_length = integer(fp)

    action_id = integer(fp)
    unk0 = integer(fp)

    return(["\n\t\t\t\t\t\tDo Action # ", str(x), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t\t\t\t\t{", "\n\t\t\t\t\t\t\tAction ID num: 0x", str(format(action_id, "0>8X")), "\n\t\t\t\t\t\t\tunk0: 0x", str(format(unk0, "0>8X")), "\n\t\t\t\t\t\t}"])

def place_object(fp, fpw, x, frame, symbol_list, positions_list, graphic_list, shape_obj_count, count, offset, item_num):
    dword_length = integer(fp)

    place_list = ["\n\t\t\t\t\t\tPlace Object # ", str(x), " offset: 0x", str(format(offset, "0>8X")), "\n\t\t\t\t\t\t{"]

    shape_id = integer(fp)
    placement_id = integer(fp)
    unk0 = integer(fp)
    name_id = integer(fp)
    place_flag = short(fp)
    blend_mode = short(fp)
    depth = short(fp)
    unk1 = short(fp)
    unk2 = short(fp)
    unk3 = short(fp)
    position_flags = short(fp)
    position_id = short(fp)
    color_mult_id = integer(fp)
    color_add_id = integer(fp)

    has_color_matrix = integer(fp)
    has_unk_f014 = integer(fp)

    if place_flag == 1:
        place_type = "Place"
    elif place_flag == 2:
        place_type = "Move"
    else:
        place_type = "Unknown " + format(place_flag, "0>4X")

    try:
        if shape_id > 0:
            graphic_list[shape_id][0].insert(-1, "\n\t\t\t\t\t\t# ref in (" + frame + ", Place Object): (" +  + str(x))
    except:
        pass

    place_list.append(["\n\t\t\t\t\t\t\tShape ID: ", "0x", str(format(shape_id, "0>8X"))])
    place_list.append(["\n\t\t\t\t\t\t\tPlacement ID: 0x", format(placement_id, "0>8X")])
    place_list.append(["\n\t\t\t\t\t\t\tunk0: 0x", format(unk0, "0>8X")])
    place_list.append(["\n\t\t\t\t\t\t\tName ID: 0x", format(name_id, "0>8X")])
    place_list.append(["\n\t\t\t\t\t\t\tPlace Flag: ", place_type])
    place_list.append(["\n\t\t\t\t\t\t\tBlend Mode: 0x", format(blend_mode, "0>4X")])
    place_list.append(["\n\t\t\t\t\t\t\tDepth: 0x", format(depth, "0>4X")])
    place_list.append(["\n\t\t\t\t\t\t\tunk1: 0x", format(unk1, "0>4X")])
    place_list.append(["\n\t\t\t\t\t\t\tunk2: 0x", format(unk2, "0>4X")])
    place_list.append(["\n\t\t\t\t\t\t\tunk3: 0x", format(unk3, "0>4X")])
    place_list.append(["\n\t\t\t\t\t\t\tposition_flags: 0x", format(position_flags, "0>4X")])
    place_list.append(["\n\t\t\t\t\t\t\tposition_id: 0x", format(position_id, "0>4X")])
    place_list.append(["\n\t\t\t\t\t\t\tcolor_mult_id: 0x", format(color_mult_id, "0>8X")])
    place_list.append(["\n\t\t\t\t\t\t\tcolor_add_id: 0x", format(color_add_id, "0>8X")])
    place_list.append(["\n\t\t\t\t\t\t\thas_color_matrix: 0x", format(has_color_matrix, "0>8X")])
    place_list.append(["\n\t\t\t\t\t\t\thas_add_id: 0x", format(has_unk_f014, "0>8X")])

    if has_color_matrix != 0:
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('0000F037'):
            place_list.append(color_matrix(fp, fpw, offset))
        else:
            print("something broke at the below address in place object (color matrix): \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))

    if has_unk_f014 != 0:
        offset = fp.tell()
        chunk = fp.read(4)
        if chunk == bytes.fromhex('0000F014'):
            place_list.append(unknowns(fp, fpw, "F014"))
        else:
            print("something broke at the below address in place object (f014): \n", str(format(offset, "0>8X")))
            print(format((int.from_bytes(chunk, "big")), "0>8X"))
    
    place_list.append(["\n\t\t\t\t\t\t}"])
    return place_list

def color_matrix(fp, fpw, offset):
    dword_length = integer(fp)
    type_list = ["\n\t\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\tColor_matrix (WIP) # offset: 0x", str(format(offset, "0>8X")), "\n\t\t\t\t\t\t\t\t{"]

    if dword_length == 1:
        unk = integer(fp)
        type_list.append(["\n\t\t\t\t\t\t\t\t\tunk: 0x", format(unk, "0>8X")])
    else:
        for x in range(dword_length):
            unk = integer(fp)
            type_list.append(["\n\t\t\t\t\t\t\t\t\tunk_", str(x), ": 0x", format(unk, "0>8X")])
    type_list.append(["\n\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t}"])

    return type_list

def remove_object(fp, fpw, frame, symbol_list, count, offset, item_num):
    dword_length = integer(fp)
    unk0 = integer(fp)
    id = short(fp)
    unk1 = short(fp)

    remove_list = ["\n\t\t\t\t\t\tRemove Object # ", str(count), " offset: ",  str(format(offset, "0>8X")), "\n\t\t\t\t\t\t{", "\n\t\t\t\t\t\t\tUnk0: 0x", str(format(unk0, "0>8X")), "\n\t\t\t\t\t\t\tID: 0x", str(format(id, "0>4X")), "\n\t\t\t\t\t\t\tunk1: 0x", str(format(unk1, "0>4X")), "\n\t\t\t\t\t\t}"]
    return remove_list

def dynamic_text(fp, fpw, x, symbol_list, text_list, offset):
    dword_length = integer(fp)

    text_temp = ["\n\n\t\tDynamic Text # offset: 0x", str(format(offset, "0>8X")), "\n\t\t{"]

    chr_id = integer(fp)
    unk0 = integer(fp)
    placeholder_text_id = integer(fp)
    unk1 = integer(fp)
    stroke_color_id = integer(fp)
    unk2 = integer(fp)
    unk3 = integer(fp)
    unk4 = integer(fp)
    text_alignment = short(fp)
    unk5 = short(fp)
    unk6 = integer(fp)
    unk7 = integer(fp)
    size = floating(fp)
    unk8 = integer(fp)
    unk9 = integer(fp)
    unk10 = integer(fp)
    unk11 = integer(fp)

    if text_alignment == 0:
        text_type = "left"
    elif text_alignment == 1:
        text_type = "right"
    elif text_alignment == 2:
        text_type = "center"
    else:
        text_type = "invalid ID: " + str(text_alignment)

    try:
        chr_str_unformatted = ''.join(symbol_list[placeholder_text_id]).split("# 0x")
        chr_str = chr_str_unformatted[0].strip()
        if placeholder_text_id > 1:
            symbol_list[placeholder_text_id].append("\n\t\t# ref in Dynamic Text: " + str(x))
    except:
        print("Invalid chr_id:", str(placeholder_text_id), "found at Dynamic Text:", str(x))
        chr_str = "Invalid ID"

    #dynamic_text_list.extend([chr_id, unk0, unk1, stroke_color_id, unk2, unk3, unk4, text_type, unk5, unk6, unk7, size, unk8, unk9, unk10, unk11])

    text_temp.append(["\n\t\t\tCharacter ID: 0x", str(format(chr_id, "0>8X"))])
    text_temp.append(["\n\t\t\tunk 0: 0x", format(unk0, "0>8X")])
    text_temp.append(["\n\t\t\tPlaceholder Text ID: ", chr_str, "(0x", format(placeholder_text_id, "0>8X"), ")"])
    text_temp.append(["\n\t\t\tunk 1: 0x", format(unk1, "0>8X")])
    text_temp.append(["\n\t\t\tStroke Color ID: 0x", format(stroke_color_id, "0>8X")])
    text_temp.append(["\n\t\t\tunk 2: 0x", format(unk2, "0>8X")])
    text_temp.append(["\n\t\t\tunk 3: 0x", format(unk3, "0>8X")])
    text_temp.append(["\n\t\t\tunk 4: 0x", format(unk4, "0>8X")])
    text_temp.append(["\n\t\t\tText Alignment: ", str(text_type)])
    text_temp.append(["\n\t\t\tunk 5: 0x", format(unk5, "0>4X")])
    text_temp.append(["\n\t\t\tunk 6: 0x", format(unk6, "0>8X")])
    text_temp.append(["\n\t\t\tunk 7: 0x", format(unk7, "0>8X")])
    text_temp.append(["\n\t\t\tSize: ", str(float(format(size[0], ".10F")))])
    text_temp.append(["\n\t\t\tunk 8: 0x", format(unk8, "0>8X")])
    text_temp.append(["\n\t\t\tunk 9: 0x", format(unk9, "0>8X")])
    text_temp.append(["\n\t\t\tunk 10: 0x", format(unk10, "0>8X")])
    text_temp.append(["\n\t\t\tunk 11: 0x", format(unk11, "0>8X")])

    text_temp.append(["\n\t\t}"])
    
    text_list.append(text_temp)

def everything_else_write(l, fpw):
    for el in l:
        if type(el) == list:
            everything_else_write(el, fpw)
        elif type(el) == str:
            fpw.writelines(el)

def metadata(fp, fpw):
    dword_length = integer(fp)
    for x in range(dword_length):
        print(int.from_bytes(fp.read(4), "big"))

main()