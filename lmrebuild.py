import sys, struct
file = sys.argv[1]

def main():
    with open(file, "r") as fp:
        lumen = file.replace(".log", "_import.lm")
        temp = open(lumen, "wb") # I'm a lazy fuck
        temp.write(bytes(1))
        temp.close()
        with open(lumen, "r+b") as fpw:
            header_write(fpw)
            chunk = get_line_without_comments(fp)
            while chunk != "":
                if chunk == "Symbols":
                    symbol_chunk(fp, fpw)
                elif chunk == "Colors":
                    colors_chunk(fp, fpw)
                elif chunk == "Transforms":
                    transforms_chunk(fp, fpw)
                elif chunk == "Positions":
                    positions_chunk(fp, fpw)
                elif chunk == "Bounds":
                    bounds_chunk(fp, fpw)
                elif chunk == "ActionScript":
                    actionscript_chunk(fp, fpw)
                elif chunk == "Atlases":
                    atlas_chunk(fp, fpw)
                elif chunk == "Unk F008":
                    unk_chunk(fp, fpw, '0000F00800000000')
                elif chunk == "Unk F009":
                    unk_chunk(fp, fpw, '0000F00900000000')
                elif chunk == "Unk F00A":
                    unk_chunk(fp, fpw, '0000F00A00000000')
                elif chunk == "Unk 000A":
                    unk_chunk(fp, fpw, '0000000A00000000')
                elif chunk == "Unk F00B":
                    unk_chunk(fp, fpw, '0000F00B00000000')
                elif chunk == "Properties":
                    properties_chunk(fp, fpw)
                elif chunk == "Defines":
                    defines_chunk(fp, fpw)
                else:
                    print("This did not work (back in main):", chunk, "\nPosition:", fp.tell(), "\nLast chunk:", last_chunk)
                    exit()
                fp.readline()
                last_chunk = chunk
                chunk = get_line_without_comments(fp)

def get_line_without_comments(fp):
    item = fp.readline()
    l = item.split("#")
    string = l[0]
    return string.strip()
    
def be_float(num):
    float_bytes = struct.pack("f", float(num))
    return float_bytes[::-1] # Best endian swap method

def hex_to_byte(value, padding = ""):
    thing = value.split("x")
    return bytes.fromhex(padding.join(thing[1]))

def close_chunk(fpw, chunk_start, end_pos, count):
    fpw.seek(chunk_start + 4)
    fpw.write(((end_pos - chunk_start - 8) // 4).to_bytes(4, byteorder='big'))
    fpw.write(count.to_bytes(4, byteorder='big'))
    fpw.seek(end_pos)
    
def close_smol_chunk(fpw, chunk_start, end_pos):
    fpw.seek(chunk_start + 4)
    fpw.write(((end_pos - chunk_start - 8) // 4).to_bytes(4, byteorder='big'))
    fpw.seek(end_pos)

def header_write(fpw):
    fpw.write(bytes.fromhex('4C4D42000000001010010200000000000000000200000000000000000000CF940000000000000000000000000000000000000000000000000000000000000000'))

def symbol_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F0010000000000000000'))
    fp.readline()
    string = get_line_without_comments(fp)
    strings_count = 0
    while string != "}":
        if string == "{":
            while string != "}":
                string = get_line_without_comments(fp)
        else:
            strings_count += 1
            string = string.strip('"')
            write_buffer = []
            string_len = len(string)
            x = 0
            while x < len(string):
                thing = bytes([ord(string[x])])
                x += 1
                if thing == bytes([ord('\\')]):
                    thing = bytes([ord(string[x])])
                    x += 1
                    if thing == bytes([ord('x')]):
                        thing = bytes.fromhex(string[x:x+2])
                        x += 2
                        string_len -= 3
                write_buffer.append(thing)
            fpw.write(string_len.to_bytes(4, byteorder='big'))
            for x in write_buffer:
                fpw.write(x)
            fpw.write(bytes(1))
            while fpw.tell() % 4 != 0:
                fpw.write(bytes(1))
        string = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_chunk(fpw, chunk_start, end_pos, strings_count)

def colors_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F002FFFFFFFFFFFFFFFF'))
    fp.readline()
    color_item = get_line_without_comments(fp)
    colors_count = 0
    while color_item != "]":
        color_item = color_item.strip("[]")
        color_list = color_item.split(", ")
        for x in color_list[0:4]:
            hex_x = int(x.strip("]"), 16)
            fpw.write(hex_x.to_bytes(2, byteorder='big'))
        color_item = get_line_without_comments(fp)
        colors_count += 1
    end_pos = fpw.tell()
    close_chunk(fpw, chunk_start, end_pos, colors_count)

def transforms_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F0030000000000000000'))
    fp.readline()
    transform_line = get_line_without_comments(fp)
    transforms_count = 0
    while transform_line == "[":
        transforms_count += 1
        for x in range(3):
            transform_item = get_line_without_comments(fp)
            transform_item = transform_item.strip("[],")
            transform_list = transform_item.split(", ")
            for x in transform_list:
                fpw.write(be_float(x))
        fp.readline()
        fp.readline()
        transform_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_chunk(fpw, chunk_start, end_pos, transforms_count)

def positions_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F1030000000000000000'))
    fp.readline()
    position_line = get_line_without_comments(fp)
    positions_count = 0
    while position_line != "]":
        if position_line != "":
            positions_count += 1
            position_line = position_line.strip("[], ")
            position_list = position_line.split(", ")
            for x in position_list:
                fpw.write(be_float(x))
        position_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_chunk(fpw, chunk_start, end_pos, positions_count)

def bounds_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F0040000000000000000'))
    fp.readline()
    bounds_line = get_line_without_comments(fp)
    bounds_count = 0
    while bounds_line != "]":
        bounds_count += 1
        bounds_line = bounds_line.strip("[], ")
        bounds_list = bounds_line.split(", ")
        for x in bounds_list:
            fpw.write(be_float(x))
        bounds_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_chunk(fpw, chunk_start, end_pos, bounds_count)

def actionscript_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F0050000000000000000'))
    fp.readline()
    fp.readline()
    fp.readline()
    num_scripts = (fp.readline()).strip()
    num_scripts_list = num_scripts.split(": ")
    actionscript_line = get_line_without_comments(fp)
    while actionscript_line != "}":
        actionscript_list = actionscript_line.split(" ")
        for x in actionscript_list:
            fpw.write(bytes.fromhex(x))
        actionscript_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_chunk(fpw, chunk_start, end_pos, int(num_scripts_list[1]))

def atlas_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F0070000000000000000'))
    fp.readline()
    atlas_line = get_line_without_comments(fp)
    atlas_count = 0
    while atlas_line != "}":
        if atlas_line == "Atlas":
            atlas_count += 1
            atlas_line = get_line_without_comments(fp)
            while atlas_line == "":
                atlas_line = get_line_without_comments(fp)
            atlas_line = get_line_without_comments(fp)
            painful_anti_float_check = 0
            for x in range(4):
                line = atlas_line.strip(",")
                line_list = line.split(": ")
                if painful_anti_float_check == 0:
                    fpw.write(int(line_list[1]).to_bytes(4, byteorder='big'))

                elif painful_anti_float_check == 1:
                    fpw.write(hex_to_byte(line_list[1]))
                else:
                    fpw.write(be_float(float(line_list[1])))

                painful_anti_float_check += 1
                atlas_line = get_line_without_comments(fp)
        atlas_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_chunk(fpw, chunk_start, end_pos, atlas_count)

def unk_chunk(fp, fpw, header):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex(header))
    fp.readline()
    unk_line = get_line_without_comments(fp)
    unk_count = 0
    while unk_line != "}":
        unk_count += 1
        thing = unk_line.split(": ")
        fpw.write(hex_to_byte(thing[1]))
        unk_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)

def properties_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F00C00000000'))
    fp.readline()
    properties_line = get_line_without_comments(fp)
    properties_count = 0
    for x in range(7):
        properties_count += 1
        thing = properties_line.split(": ")
        fpw.write(hex_to_byte(thing[1]))
        properties_line = get_line_without_comments(fp)

    for x in range(3):
        properties_count += 1
        thing = properties_line.split(": ")
        fpw.write(be_float(float(thing[1])))
        properties_line = get_line_without_comments(fp)

    while properties_line != "}":
        properties_count += 1
        thing = properties_line.split(": ")
        fpw.write(hex_to_byte(thing[1]))
        properties_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)

def defines_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F00D00000000'))
    fp.readline()
    defines_line = get_line_without_comments(fp)
    for x in range(8):
        thing = defines_line.split(": ")
        try:
            fpw.write(hex_to_byte(thing[1]))
        except:
            fpw.write(int(thing[1]).to_bytes(4, byteorder="big"))
        defines_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)

    #fp.readline()

    object_line = get_line_without_comments(fp)
    while object_line != "":
        if object_line == "Shapes":
            shape_counter = 0
            fp.readline()
            fp.readline()
            object_line = get_line_without_comments(fp)
            while object_line != "}":
                if object_line == "Shape":
                    fp.readline() # opening bracket
                    shape_counter += 1
                    shape_chunk(fp, fpw)
                elif object_line == "":
                    pass
                else:
                    print("Error while parsing shapes in defines:", object_line, "Loc:", fp.tell())
                    exit()
                object_line = get_line_without_comments(fp)
        elif object_line == "Sprites":
            sprite_counter = 0
            fp.readline()
            object_line = get_line_without_comments(fp)
            while object_line != "}":
                if object_line == "Sprite":
                    sprite_counter += 1
                    sprite_chunk(fp, fpw)
                elif object_line == "":
                    pass
                else:
                    print("Error while parsing sprites in defines:", object_line, "Loc:", fp.tell())
                    exit()
                fp.readline()
                fp.readline()
                object_line = get_line_without_comments(fp)
        elif object_line == "Texts":
            texts_counter = 0
            fp.readline()
            fp.readline()
            object_line = get_line_without_comments(fp)
            while object_line != "}":
                if object_line == "Dynamic Text":
                    texts_counter += 1
                    dynamic_text_chunk(fp, fpw)
                elif object_line == "":
                    pass
                else:
                    print("Error while parsing texts in defines:", object_line, "Loc:", fp.tell())
                    exit()
                object_line = get_line_without_comments(fp)
        else:
            print("Error", object_line, "Loc:", fp.tell())
            exit()
        fp.readline()
        object_line = get_line_without_comments(fp)

    fpw.write(bytes.fromhex('0000FF0000000000'))
    file_len = fpw.tell()

    fpw.seek(chunk_start + 8)
    fpw.write(shape_counter.to_bytes(4, byteorder='big'))
    fpw.seek(4, 1)
    fpw.write(sprite_counter.to_bytes(4, byteorder='big'))
    fpw.seek(4, 1)
    fpw.write(texts_counter.to_bytes(4, byteorder='big'))
    
    fpw.seek(0, 2)
    fpw.seek(0x1C)
    fpw.write(file_len.to_bytes(4, byteorder='big'))

def shape_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F02200000000'))

    object_line = get_line_without_comments(fp)
    for x in range(5):
        if x == 0: # chr_id
            chr_id = object_line.split("(")
            fpw.write(hex_to_byte(chr_id[1].strip(")")))
        elif x == 1 or x == 3:
            object = object_line.split(": ")
            fpw.write(hex_to_byte(object[1]))
        elif x == 2 or x == 4:
            object = object_line.split(": ")
            fpw.write(int(object[1]).to_bytes(4, byteorder="big"))
        object_line = get_line_without_comments(fp)

    object_line = get_line_without_comments(fp) # "Graphic"
    graphic_count = 0
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)

    while object_line != "}":
        if object_line == "Graphic":
            graphic_count += 1
            graphic_chunk(fp, fpw)
        else:
            print("Error while parsing graphics in shapes\n", object_line, "Loc:", fp.tell())
            exit()
        object_line = get_line_without_comments(fp)
    closed = fpw.tell()
    fpw.seek(chunk_start + 0x18)
    fpw.write(graphic_count.to_bytes(4, byteorder='big'))
    fpw.seek(closed)
    fp.readline() # brackets

def graphic_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F02400000000'))
    fp.readline()
    graphic_line = get_line_without_comments(fp)
    for x in range(4):
        graphic_list = graphic_line.split(": ")
        if x == 0 or x == 3:
            fpw.write(int(graphic_list[1]).to_bytes(4, byteorder='big'))
        elif x == 2:
            fpw.write(int(graphic_list[1]).to_bytes(2, byteorder='big'))
        else:
            fpw.write(hex_to_byte(graphic_list[1]))
        graphic_line = get_line_without_comments(fp)
    vert_count = 0
    while graphic_line[0:2] == "[[":
        vert_count += 1
        graphic_list = graphic_line.split(", ")
        for x in range(len(graphic_list)):
            try:
                fpw.write(be_float(float(graphic_list[x].strip("[],'"))))
            except:
                pass
        graphic_line = get_line_without_comments(fp)

    index_line = graphic_line.strip("[]")
    index_list = index_line.split(", ")
    index_count = len(index_list)
    for x in index_list:
        fpw.write(int(x).to_bytes(2, byteorder='big'))
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    close_pos = fpw.tell()
    fpw.seek(chunk_start + 0xE)
    fpw.write(vert_count.to_bytes(2, byteorder='big'))
    fpw.write(index_count.to_bytes(4, byteorder='big'))
    fpw.seek(close_pos)
    fp.readline()

def sprite_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000002700000000'))
    fp.readline()
    sprite_line = get_line_without_comments(fp)
    chr_id = sprite_line.split("(")
    fpw.write(hex_to_byte(chr_id[1].strip(")")))
    sprite_line = get_line_without_comments(fp)
    for x in range(6):
        object = sprite_line.split(": ")
        fpw.write(hex_to_byte(object[1]))
        sprite_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    
    sprite_line = get_line_without_comments(fp)
    
    show_frame_count = 0
    key_frame_count = 0
    frame_labels_count = 0

    while sprite_line != "}":
        if sprite_line == "Show Frame":
            show_frame_count += 1
            show_frame_chunk(fp, fpw)
        elif sprite_line == "Key Frame":
            key_frame_count += 1
            key_frame_chunk(fp, fpw)
        elif sprite_line == "Frame Label":
            frame_labels_count += 1
            frame_label_chunk(fp, fpw)
        else:
            print("Error in sprite sub chunk parsing:", sprite_line, "Loc:", fp.tell())
            exit()
        sprite_line = get_line_without_comments(fp)
    close_pos = fpw.tell()
    fpw.seek(chunk_start + 0x14)
    fpw.write(frame_labels_count.to_bytes(4, byteorder='big'))
    fpw.write(show_frame_count.to_bytes(4, byteorder='big'))
    fpw.write(key_frame_count.to_bytes(4, byteorder='big'))
    fpw.seek(close_pos)

def show_frame_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000000100000000'))
    fp.readline()
    frame_line = get_line_without_comments(fp)
    for x in range(2):
        object = frame_line.split(": ")
        fpw.write(hex_to_byte(object[1]))
        frame_line = get_line_without_comments(fp)
    frame_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    
    item_count = 0

    while frame_line != "}":
        item_count += 1
        if frame_line == "Place Object":
            place_object_chunk(fp, fpw)
        elif frame_line == "Do Action":
            do_action_chunk(fp, fpw)
        elif frame_line == "Remove Object":
            remove_object_chunk(fp, fpw)
        elif frame_line == "":
            pass
        else:
            print("Error in show frame sub chunk parsing", frame_line, "Loc:", fp.tell())
            exit()
        frame_line = get_line_without_comments(fp)
    if item_count == 0:
        fp.readline()
    close_pos = fpw.tell()
    fpw.seek(chunk_start + 0xC)
    fpw.write(item_count.to_bytes(4, byteorder='big'))
    fpw.seek(close_pos)

def key_frame_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000F10500000000'))
    fp.readline()
    frame_line = get_line_without_comments(fp)
    for x in range(2):
        object = frame_line.split(": ")
        fpw.write(hex_to_byte(object[1]))
        frame_line = get_line_without_comments(fp)
    frame_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    
    item_count = 0

    while frame_line != "}":
        item_count += 1
        if frame_line == "Place Object":
            place_object_chunk(fp, fpw)
        elif frame_line == "Do Action":
            do_action_chunk(fp, fpw)
        elif frame_line == "Remove Object":
            remove_object_chunk(fp, fpw)
        else:
            print("Error in key frame sub chunk parsing", frame_line, "Loc:", fp.tell())
            exit()
        frame_line = get_line_without_comments(fp)
    if item_count == 0:
        fp.readline()
    close_pos = fpw.tell()
    fpw.seek(chunk_start + 0xC)
    fpw.write(item_count.to_bytes(4, byteorder='big'))
    fpw.seek(close_pos)

def place_object_chunk(fp, fpw): # 00000004
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000000400000000'))
    fp.readline()
    object_line = get_line_without_comments(fp)

    chr_id = object_line.split("(")
    fpw.write(hex_to_byte(chr_id[1].strip(")")))
    object_line = get_line_without_comments(fp)

    for x in range(15):
        object = object_line.split(": ")
        if x == 3:
            if object[1] == "Place":
                fpw.write(bytes.fromhex('0001'))
            elif object[1] == "Move":
                fpw.write(bytes.fromhex('0002'))
            else:
                flag = object[1].split(" ")
                fpw.write(bytes.fromhex(flag[1]))
        else:
            fpw.write(hex_to_byte(object[1]))
        object_line = get_line_without_comments(fp)
        
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)

    while object_line == "{":
        object_line = get_line_without_comments(fp)
        if object_line == "Color_matrix (WIP)":
            color_matrix_chunk(fp, fpw)
        else:
            print("Error while parsing place object sub chunks:", object_line_)
        object_line = get_line_without_comments(fp)
    
    fp.readline()

def frame_label_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000002B00000000'))
    fp.readline()
    label_line = get_line_without_comments(fp)
    for x in range(3):
        object = label_line.split(": ")
        fpw.write(hex_to_byte(object[1]))
        label_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)

def do_action_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000000C00000000'))
    fp.readline()
    action_line = get_line_without_comments(fp)
    for x in range(2):
        object = action_line.split(": ")
        fpw.write(hex_to_byte(object[1]))
        action_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    fp.readline()

def color_matrix_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fp.readline()
    fpw.write(bytes.fromhex('0000F03700000000'))
    matrix_line = get_line_without_comments(fp)
    while matrix_line != "}":
        object = matrix_line.split(": ")
        fpw.write(hex_to_byte(object[1]))
        matrix_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    fp.readline()

def remove_object_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000000500000000'))
    fp.readline()
    object_line = get_line_without_comments(fp)
    for x in range(3):
        object = object_line.split(": ")
        fpw.write(hex_to_byte(object[1]))
        object_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    fp.readline()

def dynamic_text_chunk(fp, fpw):
    chunk_start = fpw.tell()
    fpw.write(bytes.fromhex('0000002500000000'))
    fp.readline()
    texts_line = get_line_without_comments(fp)

    chr_id = texts_line.split("(")
    fpw.write(hex_to_byte(chr_id[1].strip(")")))
    texts_line = get_line_without_comments(fp)
    
    for x in range(16):
        object = texts_line.split(": ")
        if x == 7:
            if object[1] == "left":
                fpw.write(bytes.fromhex('0000'))
            elif object[1] == "right":
                fpw.write(bytes.fromhex('0001'))
            elif object[1] == "center":
                fpw.write(bytes.fromhex('0002'))
            else:
                print("Invalid text alignment type for texts.:", object[1], "\nWriting value anyways")
                alignment = object[1].split(": ")
                fpw.write(bytes.fromhex(alignment[1]))
        elif x == 11:
            fpw.write(be_float(object[1]))
        else:
            fpw.write(hex_to_byte(object[1]))
        texts_line = get_line_without_comments(fp)
    end_pos = fpw.tell()
    close_smol_chunk(fpw, chunk_start, end_pos)
    fp.readline()

main()
print("I don't like how this ended in 665 lines.")